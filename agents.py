from langchain.agents import create_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from tools import search_the_web, fetch_page_content


def build_search_agent(llm):
    return create_agent(model=llm, tools=[search_the_web])


def build_reader_agent(llm):
    return create_agent(model=llm, tools=[fetch_page_content])


writer_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an expert research writer. You write only what the evidence supports."),
    ("human", """Write a concise research report on the topic below, using ONLY the evidence provided.

Topic: {topic}
Today's date: {today}

Evidence (web search results and one scraped page):
{research}

Strict rules:
- Every sentence must be traceable to the evidence. Do NOT add numbers, benchmarks, statistics, standards, product or model names, or hardware names that do not appear in the evidence.
- If the evidence is thin or only partly relevant, say so instead of filling the gap.
- Mention the source website or publisher by name when you use a fact from it.
- Mark anything uncertain as "not confirmed in the sources".
- Do NOT write a title block, "Prepared for", or a date line.
- Do NOT use tables, placeholders like [Client], or citation markers like 【1†...】.
- Do NOT write a Sources section; it is added automatically.

Structure (markdown, at most 600 words):
## Introduction
## Key Findings (3 to 5 bullet points)
## Conclusion"""),
])

critic_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a sharp and constructive research critic. Be honest and specific."),
    ("human", """Review the research report below. You also get the evidence it was written from.

Evidence:
{research}

Report:
{report}

Check every number, name, standard and claim in the report against the evidence. Judge how well the report is supported by the evidence and how useful it is; do not demand academic methodology.

Respond in exactly this format, and include every section:

Score: X/10

Strengths:
- ...
- ...

Unsupported or doubtful claims:
- ... (quote the claim; write "None found" only if every claim is in the evidence)

Areas to Improve:
- ...
- ...

One line verdict:
..."""),
])


def build_writer_chain(llm):
    return writer_prompt | llm | StrOutputParser()


def build_critic_chain(llm):
    return critic_prompt | llm | StrOutputParser()