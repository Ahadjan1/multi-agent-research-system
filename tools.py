import os

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from langchain.tools import tool
from tavily import TavilyClient

load_dotenv()

tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))


@tool
def search_the_web(query: str) -> str:
    """Look up recent, reliable information on the internet for a given query. Returns Titles, URLs, and snippets."""
    search_results = tavily_client.search(query=query, max_results=5)
    formatted_results = []
    for item in search_results["results"]:
        formatted_results.append(
            f"Title: {item.get('title', '')}\nURL: {item.get('url', '')}\n"
            f"Snippet: {item.get('content', '')[:300]}\n"
        )
    return "\n----\n".join(formatted_results)


@tool
def fetch_page_content(url: str) -> str:
    """Fetch a webpage and extract its readable text for closer reading."""
    try:
        response = requests.get(url, timeout=8, headers={"User-Agent": "Mozilla/5.0"})
        response.raise_for_status()
        parsed_page = BeautifulSoup(response.text, "html.parser")
        for element in parsed_page(["script", "style", "nav", "footer"]):
            element.decompose()
        return parsed_page.get_text(separator=" ", strip=True)[:3000]
    except Exception as error:
        return f"Could not scrape URL: {str(error)}"