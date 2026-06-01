from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo


def today_slug(timezone_name: str = "America/Chicago") -> str:
    return datetime.now(ZoneInfo(timezone_name)).strftime("%Y-%m-%d")


def now_human(timezone_name: str = "America/Chicago") -> str:
    current = datetime.now(ZoneInfo(timezone_name))
    return f"{current.strftime('%B %d, %Y at')} {current.strftime('%I:%M %p %Z').lstrip('0')}"
