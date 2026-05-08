from tavily import TavilyClient
from config import TAVILY_API_KEY

tavily = TavilyClient(api_key=TAVILY_API_KEY)

def web_search(query: str, max_results: int = 5) -> list[dict]:
    """Returns list of {title, url, content} dicts."""
    response = tavily.search(
        query=query,
        search_depth="advanced",
        max_results=max_results,
        include_answer=True
    )
    return response.get("results", [])

def financial_news_search(company_or_sector: str) -> list[dict]:
    """Targeted financial news search."""
    query = f"{company_or_sector} financial results earnings 2024 2025"
    return web_search(query)