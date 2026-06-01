from __future__ import annotations

from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from typing import Any


WEIGHTS = {
    "executive_relevance": 25,
    "hiring_manager_relevance": 20,
    "ai_radar_alignment": 20,
    "freshness": 10,
    "tension": 10,
    "visual_potential": 10,
    "credibility": 5,
}

EXECUTIVE_TERMS = [
    "enterprise",
    "board",
    "governance",
    "operating model",
    "risk",
    "roi",
    "strategy",
    "decision",
    "commercial",
]

HIRING_MANAGER_TERMS = [
    "execution",
    "platform",
    "analytics",
    "automation",
    "workforce",
    "crm",
    "experimentation",
    "infrastructure",
]

AI_RADAR_TERMS = [
    "ai",
    "agent",
    "governance",
    "decision intelligence",
    "commercialization",
    "competitive",
    "capex",
    "lawsuit",
    "partnership",
]

TENSION_TERMS = [
    "lawsuit",
    "layoff",
    "risk",
    "cost",
    "capex",
    "trust",
    "regulation",
    "margin",
    "accountability",
]


def _text(signal: dict[str, Any]) -> str:
    return " ".join(str(signal.get(key, "")) for key in ["title", "summary", "sector", "company"]).lower()


def _term_score(text: str, terms: list[str]) -> float:
    hits = sum(1 for term in terms if term in text)
    return min(1.0, hits / 4)


def _freshness_score(date_value: str | None) -> float:
    if not date_value:
        return 0.4
    try:
        parsed = parsedate_to_datetime(date_value)
    except (TypeError, ValueError):
        try:
            parsed = datetime.fromisoformat(date_value.replace("Z", "+00:00"))
        except ValueError:
            return 0.4
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    age_days = max(0, (datetime.now(timezone.utc) - parsed).days)
    if age_days <= 1:
        return 1.0
    if age_days <= 3:
        return 0.8
    if age_days <= 7:
        return 0.6
    if age_days <= 14:
        return 0.4
    return 0.2


def score_signal(signal: dict[str, Any]) -> dict[str, Any]:
    text = _text(signal)
    component_scores = {
        "executive_relevance": _term_score(text, EXECUTIVE_TERMS),
        "hiring_manager_relevance": _term_score(text, HIRING_MANAGER_TERMS),
        "ai_radar_alignment": _term_score(text, AI_RADAR_TERMS),
        "freshness": _freshness_score(signal.get("publication_date")),
        "tension": _term_score(text, TENSION_TERMS),
        "visual_potential": 1.0 if any(term in text for term in ["map", "trend", "framework", "platform", "operating model", "capex"]) else 0.6,
        "credibility": float(signal.get("credibility_score", 50)) / 100,
    }
    total = sum(component_scores[key] * WEIGHTS[key] for key in WEIGHTS)
    signal["component_scores"] = component_scores
    signal["score"] = round(total)
    return signal


def score_signals(signals: list[dict[str, Any]]) -> list[dict[str, Any]]:
    scored = [score_signal(signal) for signal in signals]
    return sorted(scored, key=lambda item: item["score"], reverse=True)
