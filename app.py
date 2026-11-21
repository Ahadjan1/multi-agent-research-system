"""
Streamlit UI for the Multi-Agent Research System — "DeepTrace"

A landing-page style dashboard that shows each agent's live status
(search -> read -> write -> critique) while the pipeline runs.
"""

import streamlit as st
from pipeline import run_research_pipeline

# ----------------------------------------------------------------------
# Page config
# ----------------------------------------------------------------------
st.set_page_config(
    page_title="DeepTrace — Multi-Agent Research",
    page_icon="◈",
    layout="wide",
)

# ----------------------------------------------------------------------
# Global styling
# ----------------------------------------------------------------------
st.markdown(
    """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

        html, body, [class*="css"]  {
            font-family: 'Space Grotesk', sans-serif;
        }

        #MainMenu, header, footer {visibility: hidden;}

        .stApp {
            background: radial-gradient(circle at 20% 0%, #14141c 0%, #08080b 55%, #050506 100%);
        }

        .mono-tag {
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.7rem;
            letter-spacing: 0.25em;
            color: #6EE7D9;
            text-transform: uppercase;
        }

        .hero-title {
            font-size: 4rem;
            font-weight: 700;
            line-height: 1.05;
            margin: 0.4rem 0 0.8rem 0;
            background: linear-gradient(90deg, #E9E9F1 0%, #6EE7D9 55%, #A78BFA 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .hero-sub {
            color: #9498A8;
            font-size: 1.02rem;
            max-width: 620px;
            line-height: 1.55;
            margin-bottom: 1.6rem;
        }

        .panel {
            background: #101014;
            border: 1px solid #212129;
            border-radius: 14px;
            padding: 1.4rem 1.5rem;
        }

        .agent-card {
            background: #0D0D11;
            border: 1px solid #212129;
            border-radius: 12px;
            padding: 0.95rem 1.1rem;
            margin-bottom: 0.7rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            transition: border-color 0.3s ease;
        }
        .agent-card.active { border-color: #6EE7D9; }
        .agent-card.done { border-color: #34D399; }

        .agent-name {
            font-weight: 600;
            font-size: 0.95rem;
            color: #E9E9F1;
        }
        .agent-desc {
            font-size: 0.78rem;
            color: #6B6F80;
            margin-top: 0.1rem;
        }

        .badge {
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.65rem;
            letter-spacing: 0.1em;
            padding: 0.25rem 0.55rem;
            border-radius: 6px;
            white-space: nowrap;
        }
        .badge-waiting { background: #1A1A20; color: #5B5F70; }
        .badge-running { background: rgba(110,231,217,0.12); color: #6EE7D9; }
        .badge-done { background: rgba(52,211,153,0.12); color: #34D399; }
        .badge-error { background: rgba(248,113,113,0.12); color: #F87171; }

        .report-box {
            background: #0D0D11;
            border: 1px solid #212129;
            border-radius: 12px;
            padding: 1.6rem;
            color: #DADAE3;
            line-height: 1.6;
            white-space: pre-wrap;
        }

        div.stButton > button {
            background: linear-gradient(90deg, #6EE7D9, #A78BFA);
            color: #08080b;
            font-weight: 700;
            border: none;
            border-radius: 10px;
            padding: 0.6rem 0;
            width: 100%;
        }
        div.stButton > button:hover {
            filter: brightness(1.08);
            color: #08080b;
        }

        .chip {
            display: inline-block;
            background: #14141a;
            border: 1px solid #26262f;
            color: #9498A8;
            border-radius: 999px;
            padding: 0.25rem 0.8rem;
            font-size: 0.78rem;
            margin: 0.15rem;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

AGENTS = [
    {"key": "search", "name": "01 · Search Agent", "desc": "Gathers recent, reliable sources from the web"},
    {"key": "read", "name": "02 · Reader Agent", "desc": "Scrapes and extracts deep page content"},
    {"key": "write", "name": "03 · Writer Chain", "desc": "Drafts the full structured research report"},
    {"key": "critic", "name": "04 · Critic Chain", "desc": "Reviews, scores, and critiques the report"},
]

EXAMPLE_TOPICS = [
    "LLM agents in 2026",
    "CRISPR gene editing",
    "Quantum computing breakthroughs",
]

# ----------------------------------------------------------------------
# Session state
# ----------------------------------------------------------------------
if "statuses" not in st.session_state:
    st.session_state.statuses = {a["key"]: "waiting" for a in AGENTS}
if "result" not in st.session_state:
    st.session_state.result = None


def render_agent_cards(container, statuses):
    with container.container():
        for agent in AGENTS:
            status = statuses[agent["key"]]
            css_class = "active" if status == "running" else ("done" if status == "done" else "")
            badge_class = f"badge-{status}"
            st.markdown(
                f"""
                <div class="agent-card {css_class}">
                    <div>
                        <div class="agent-name">{agent['name']}</div>
                        <div class="agent-desc">{agent['desc']}</div>
                    </div>
                    <div class="badge {badge_class}">{status.upper()}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


# ----------------------------------------------------------------------
# Hero
# ----------------------------------------------------------------------
st.markdown('<div class="mono-tag">Multi-Agent AI System</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-title">DeepTrace</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="hero-sub">Four specialized agents work in sequence — searching, reading, '
    'writing, and critiquing — to turn any topic into a polished, sourced research report.</div>',
    unsafe_allow_html=True,
)

left, right = st.columns([1.3, 1], gap="large")

with left:
    st.markdown('<div class="mono-tag" style="margin-bottom:0.6rem;">Research Topic</div>', unsafe_allow_html=True)
    topic = st.text_input(
        "topic",
        placeholder="e.g. Quantum computing breakthroughs in 2025",
        label_visibility="collapsed",
        key="topic_box",
    )
    run_clicked = st.button("Run Research Pipeline")

    st.markdown(
        "".join(f'<span class="chip">{t}</span>' for t in EXAMPLE_TOPICS),
        unsafe_allow_html=True,
    )

with right:
    st.markdown('<div class="mono-tag" style="margin-bottom:0.8rem;">Pipeline</div>', unsafe_allow_html=True)
    pipeline_slot = st.empty()
    render_agent_cards(pipeline_slot, st.session_state.statuses)

# ----------------------------------------------------------------------
# Run pipeline with live status updates
# ----------------------------------------------------------------------
if run_clicked:
    if not topic.strip():
        st.warning("Enter a topic first.")
    else:
        statuses = {a["key"]: "waiting" for a in AGENTS}
        render_agent_cards(pipeline_slot, statuses)

        def on_status(step, status):
            statuses[step] = status
            render_agent_cards(pipeline_slot, statuses)

        try:
            state = run_research_pipeline(topic.strip(), on_status=on_status)
            st.session_state.statuses = statuses
            st.session_state.result = state
        except Exception as e:
            for key in statuses:
                if statuses[key] == "running":
                    statuses[key] = "error"
            render_agent_cards(pipeline_slot, statuses)
            st.error(
                "The pipeline stopped. This demo runs on free-tier APIs (Groq and Tavily), "
                "so it can fail when a daily limit is used up. Please try again later."
            )
            with st.expander("Technical details"):
                st.code(str(e))

# ----------------------------------------------------------------------
# Results
# ----------------------------------------------------------------------
result = st.session_state.result

if result:
    st.markdown("<br>", unsafe_allow_html=True)
    tab_report, tab_feedback, tab_search, tab_scraped = st.tabs(
        ["Report", "Critic Feedback", "Search Results", "Scraped Content"]
    )

    with tab_report:
        st.markdown(result["report"])
        st.download_button(
            "Download report (.md)",
            data=result["report"],
            file_name="research_report.md",
            mime="text/markdown",
        )

    with tab_feedback:
        st.markdown(result["feedback"])

    with tab_search:
        st.text_area("Search results", result["search_results"], height=320, label_visibility="collapsed")

    with tab_scraped:
        st.text_area("Scraped content", result["scraped_content"], height=320, label_visibility="collapsed")

st.markdown(
    '<div style="text-align:center; color:#4B4F5E; font-size:0.75rem; margin-top:3rem;">'
    "DeepTrace — Powered by LangChain multi-agent pipeline · Built with Streamlit</div>",
    unsafe_allow_html=True,
)

