import re
from datetime import date

from agents import (
    build_search_agent,
    build_reader_agent,
    build_writer_chain,
    build_critic_chain,
)
from llm import run_with_fallback


def _tool_text(result) -> str:
    """Agent ke tools ka asli (raw) output nikalta hai, agent ka summary nahi."""
    parts = [str(m.content) for m in result["messages"] if getattr(m, "type", "") == "tool"]
    return "\n\n".join(parts)


def _clean_report(text: str) -> str:
    """Model ke nakli hisse hata do: citation markers, title lines, aur apni Sources section."""
    text = re.sub(r"【[^】]*】", "", text)
    text = re.sub(r"^\*?\s*(Prepared for|Date)\s*:.*$", "", text, flags=re.IGNORECASE | re.MULTILINE)
    m = re.search(r"^#{1,4}\s*(\d+\.?\s*)?Sources?\b.*$", text, flags=re.IGNORECASE | re.MULTILINE)
    if m:
        text = text[: m.start()]
    return text.strip()


def _sources_block(evidence_text: str) -> str:
    """Sirf wahi URLs jo writer ko evidence mein diye gaye."""
    urls = list(dict.fromkeys(re.findall(r"URL:\s*(\S+)", evidence_text)))
    if not urls:
        return "\n\n## Sources\nNo sources found."
    return "\n\n## Sources\n" + "\n".join(f"- {u}" for u in urls)


def run_research_pipeline(topic: str, on_status=None) -> dict:
    """on_status(step, status) UI ko live status batane ke liye (optional)."""

    def notify(step, status):
        if on_status:
            on_status(step, status)

    today = date.today().strftime("%d %B %Y")
    state = {}

    # Step 1: Search agent
    notify("search", "running")
    print("Step 1: Searching the web...")

    def _search(llm):
        agent = build_search_agent(llm)
        result = agent.invoke({
            "messages": [("user",
                f"Today's date is {today}. Find recent, reliable information about: {topic}. "
                f"Prefer sources from the last 12 months. "
                f"Call the search tool at most 2 times, then stop and reply 'done'."
            )]
        })
        return _tool_text(result) or result["messages"][-1].content

    state["search_results"] = run_with_fallback(_search, max_tokens=800)
    notify("search", "done")

    # Step 2: Reader agent
    notify("read", "running")
    print("Step 2: Reading top source in detail...")

    def _read(llm):
        agent = build_reader_agent(llm)
        result = agent.invoke({
            "messages": [("user",
                f"Based on the following search results about '{topic}', "
                f"pick the single most relevant URL and scrape it once.\n\n"
                f"Search Results:\n{state['search_results'][:2500]}"
            )]
        })
        return _tool_text(result) or result["messages"][-1].content

    state["scraped_content"] = run_with_fallback(_read, max_tokens=800)
    notify("read", "done")

    # Step 3: Writer (sirf evidence se, token limit ke liye chhota)
    notify("write", "running")
    print("Step 3: Writing the report...")
    search_part = state["search_results"][:3000]
    research_combined = (
        f"SEARCH RESULTS:\n{search_part}\n\n"
        f"SCRAPED PAGE:\n{state['scraped_content'][:2500]}"
    )
    report = run_with_fallback(
        lambda llm: build_writer_chain(llm).invoke(
            {"topic": topic, "today": today, "research": research_combined}
        ),
        max_tokens=1800,
    )
    report = _clean_report(report)
    state["report"] = report + _sources_block(search_part)
    notify("write", "done")

    # Step 4: Critic (evidence ke saath)
    notify("critic", "running")
    print("Step 4: Reviewing the report...")
    state["feedback"] = run_with_fallback(
        lambda llm: build_critic_chain(llm).invoke(
            {"report": report, "research": research_combined}
        ),
             max_tokens=1200,
    )
    notify("critic", "done")

    return state


if __name__ == "__main__":
    topic = input("Enter a research topic: ")
    state = run_research_pipeline(topic)
    print("\nFinal Report:\n", state["report"])
    print("\nCritic Feedback:\n", state["feedback"])