from __future__ import annotations

from typing import Any

from ddgs import DDGS

from tools.source_ranker import credibility_score


SEARCH_CATEGORIES = [
    "healthcare AI enterprise governance",
    "telecom AI automation workforce",
    "fintech AI risk decision systems",
    "enterprise AI execution Fortune 100",
    "AI governance enterprise lawsuits",
    "AI layoffs workforce redesign",
    "AI capex cloud infrastructure",
    "AI partnerships commercialization",
    "agentic AI operating systems enterprise",
    "boardroom AI strategy decision intelligence",
]


def search_ddgs(max_results: int = 20) -> list[dict[str, Any]]:
    signals: list[dict[str, Any]] = []
    seen_urls: set[str] = set()
    with DDGS() as ddgs:
        for query in SEARCH_CATEGORIES:
            for result in ddgs.text(query, max_results=3, timelimit="d"):
                url = result.get("href") or result.get("url") or ""
                if not url or url in seen_urls:
                    continue
                seen_urls.add(url)
                score, note = credibility_score(url, result.get("source", ""))
                signals.append(
                    {
                        "title": result.get("title", "Untitled signal"),
                        "company": "Unknown",
                        "sector": query,
                        "source": result.get("source", "DDGS"),
                        "url": url,
                        "publication_date": result.get("date", ""),
                        "summary": result.get("body", ""),
                        "executive_relevance": "Potential enterprise AI decision, governance, workforce, or commercialization signal.",
                        "credibility_score": score,
                        "credibility_note": note,
                        "why_it_matters": "Needs executive framing against operating model, governance, ROI, and decision infrastructure.",
                    }
                )
                if len(signals) >= max_results:
                    return signals
    return signals
