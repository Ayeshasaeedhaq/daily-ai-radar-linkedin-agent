from __future__ import annotations

import csv
from pathlib import Path


PAST_POSTS_COLUMNS = ["date", "topic", "angle", "post_text", "visual_type", "notes"]
PERFORMANCE_COLUMNS = [
    "date",
    "topic",
    "angle",
    "views",
    "likes",
    "comments",
    "reposts",
    "profile_visits",
    "connection_requests",
    "recruiter_engagement",
    "executive_engagement",
    "notes",
]


POSITIONING_RULES = """# Positioning Rules

Ayesha Saeed-Haq translates enterprise AI signals into executive decision intelligence.

Emphasize:
- Enterprise AI execution
- Decision intelligence
- AI governance
- CRM/NBA systems
- Experimentation
- Risk detection
- Fortune-20 operating systems
- AI Radar positioning

Avoid:
- Generic AI commentary
- Hype language
- Beginner education
- Unsupported statistics
- Motivational filler
"""


AI_RADAR_THEMES = """# AI Radar Themes

- AI execution vs hype
- Governance debt
- Decision intelligence
- Competitive intelligence
- Agentic operating models
- Workforce redesign
- AI maturity
- AI commercialization
- Boardroom implications
"""


def _ensure_csv(path: Path, columns: list[str]) -> None:
    if path.exists():
        return
    with path.open("w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(columns)


def _ensure_text(path: Path, content: str) -> None:
    if not path.exists():
        path.write_text(content.strip() + "\n", encoding="utf-8")


def ensure_memory_files(data_dir: Path) -> None:
    data_dir.mkdir(parents=True, exist_ok=True)
    _ensure_csv(data_dir / "past_posts.csv", PAST_POSTS_COLUMNS)
    _ensure_csv(data_dir / "post_performance.csv", PERFORMANCE_COLUMNS)
    _ensure_text(data_dir / "positioning_rules.md", POSITIONING_RULES)
    _ensure_text(data_dir / "ai_radar_themes.md", AI_RADAR_THEMES)
