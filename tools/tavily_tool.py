import os
from typing import Any

from tavily import TavilyClient


def search_travel(query: str, max_results: int = 4) -> list[dict[str, str]]:
    """Return a compact, safe-to-display list of web research sources."""
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        return []
    try:
        response: dict[str, Any] = TavilyClient(api_key=api_key).search(
            query=query, max_results=max_results, search_depth="basic", include_answer=True
        )
        sources = []
        if response.get("answer"):
            sources.append({"title": "Research summary", "url": "", "content": response["answer"]})
        for result in response.get("results", []):
            sources.append({"title": result.get("title", "Travel source"), "url": result.get("url", ""), "content": result.get("content", "")[:500]})
        return sources
    except Exception:
        return []
