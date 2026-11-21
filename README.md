# DeepTrace: Multi-Agent Research System

Give it a topic and four specialized components work in sequence to produce a sourced research report: a **search agent**, a **reader agent**, a **writer chain**, and a **critic chain**. A Streamlit dashboard shows each step live.

---

## ✨ Features

- **Two tool-calling agents** (LangChain `create_agent`):
  - Search agent: web search through Tavily
  - Reader agent: scrapes one page with BeautifulSoup
- **Writer chain (LCEL):** writes a short report using _only_ the gathered evidence
- **Critic chain (LCEL):** scores the report out of 10 and lists claims that are not supported by the evidence
- **Sources added by code, not by the model:** the Sources list comes from the real search results, so it cannot be invented
- **Automatic model fallback:** if one Groq model hits a rate limit, the next one takes over
- **Live status dashboard** and report download (`.md`)

---

## 🏗️ Architecture

```
Topic
  │
  ▼
Search agent (Tavily)  ──►  search results (titles, URLs, snippets)
  │
  ▼
Reader agent (BeautifulSoup)  ──►  text of the most relevant page
  │
  ▼
Writer chain  ──►  report (evidence only)  + Sources (from real URLs)
  │
  ▼
Critic chain  ──►  score, strengths, unsupported claims, improvements
```

---

## 🧰 Tech Stack

| Layer           | Tool                                                                       |
| --------------- | -------------------------------------------------------------------------- |
| Agents & chains | `LangChain` (tool-calling agents, LCEL)                                    |
| LLM provider    | `Groq` (`gpt-oss-120b`, with `gpt-oss-20b` and `qwen3.8-27b` as fallbacks) |
| Web search      | `Tavily`                                                                   |
| Scraping        | `requests`, `BeautifulSoup`                                                |
| UI              | `Streamlit`                                                                |

---

## 📁 Project Structure

```
.
├── app.py            # Streamlit dashboard
├── pipeline.py       # Runs the 4 steps in order, builds the Sources list
├── agents.py         # Search/reader agents, writer and critic prompts
├── tools.py          # Tavily search tool and page scraper tool
├── llm.py            # Groq setup, rate limiting, model fallback
├── requirements.txt
└── .env.example
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10 or 3.11
- A free [Groq API key](https://console.groq.com/)
- A free [Tavily API key](https://app.tavily.com/)

### Installation

```bash
git clone https://github.com/Ahadjan1/multi-agent-research-system.git
cd multi-agent-research-system

python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
```

### Environment Variables

Copy `.env.example` to `.env` and fill in your keys:

```env
GROQ_API_KEY=your_groq_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here
```

Model names on Groq change over time. Check your Groq console for the models available to you and set `GROQ_MODELS` if needed.

---

## ▶️ Usage

```bash
streamlit run app.py
```

Enter a topic, press **Run Research Pipeline**, and read the report in the tabs (Report, Critic Feedback, Search Results, Scraped Content).

Command line version:

```bash
python pipeline.py
```

---

## 🗺️ Known Limitations

- **Free-tier limits:** the project runs on free Groq and Tavily plans, which have small per-minute and per-day limits. When a limit is reached, the app shows a message and you can try again later.
- **One page is read in detail:** the reader agent scrapes a single page (first ~3000 characters), so the report is based mostly on search snippets plus one page.
- **No JavaScript rendering:** pages that need JavaScript, or sit behind a paywall, may return little or no text.
- **The critic is also an LLM:** its score is a helpful check, not proof. Verify key numbers against the linked sources.
- The pipeline is sequential (one step after another), with no retries beyond model fallback.

---

## 🙏 Acknowledgments

- [LangChain](https://www.langchain.com/) for agents and chains
- [Groq](https://groq.com/) for fast inference
- [Tavily](https://tavily.com/) for web search
