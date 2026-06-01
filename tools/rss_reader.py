from __future__ import annotations

from typing import Any
from urllib.parse import quote_plus

import feedparser

from tools.source_ranker import credibility_score


RSS_QUERIES = [
    "enterprise AI governance",
    "AI workforce redesign",
    "AI capex enterprise",
    "AI decision intelligence",
    "agentic AI enterprise",
]


def read_google_news(max_results: int = 20) -> list[dict[str, Any]]:
    signals: list[dict[str, Any]] = []
    seen_urls: set[str] = set()
    for query in RSS_QUERIES:
        url = f"https://news.google.com/rss/search?q={quote_plus(query)}&hl=en-US&gl=US&ceid=US:en"
        feed = feedparser.parse(url)
        for entry in feed.entries[:5]:
            link = entry.get("link", "")
            if not link or link in seen_urls:
                continue
            seen_urls.add(link)
            score, note = credibility_score(link, entry.get("source", {}).get("title", ""))
            signals.append(
                {
                    "title": entry.get("title", "Untitled Google News signal"),
                    "company": "Unknown",
                    "sector": query,
                    "source": entry.get("source", {}).get("title", "Google News RSS"),
                    "url": link,
                    "publication_date": entry.get("published", ""),
                    "summary": entry.get("summary", ""),
                    "executive_relevance": "Fresh market signal for executive AI Radar review.",
                    "credibility_score": score,
                    "credibility_note": note,
                    "why_it_matters": "May indicate a shift in enterprise AI execution, governance, spend, or workforce design.",
                }
            )
            if len(signals) >= max_results:
                return signals
    return signals
