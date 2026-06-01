from __future__ import annotations

from pathlib import Path
from typing import Mapping


def ensure_directories(paths: list[Path]) -> None:
    for path in paths:
        path.mkdir(parents=True, exist_ok=True)


def write_markdown(path: Path, content: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.strip() + "\n", encoding="utf-8")
    return path


def write_outputs(output_dir: Path, date_slug: str, documents: Mapping[str, str]) -> dict[str, Path]:
    files = {
        "daily_post": output_dir / f"{date_slug}_daily_post.md",
        "visual_brief": output_dir / f"{date_slug}_visual_brief.md",
        "sources": output_dir / f"{date_slug}_sources.md",
        "reasoning_log": output_dir / f"{date_slug}_reasoning_log.md",
    }
    for key, path in files.items():
        write_markdown(path, documents[key])
    return files
