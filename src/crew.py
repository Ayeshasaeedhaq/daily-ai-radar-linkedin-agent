from __future__ import annotations

import json
import os
from getpass import getpass
from pathlib import Path
from typing import Any

from anthropic import Anthropic
from crewai import Crew, LLM, Process, Task
from dotenv import load_dotenv

from agents.post_writer import build_post_writer
from agents.qc_agent import build_qc_agent
from agents.signal_scout import build_signal_scout
from agents.strategist import build_executive_strategist
from tools.rss_reader import read_google_news
from tools.web_search import search_ddgs
from utils.date_utils import now_human, today_slug
from utils.file_io import ensure_directories, write_outputs
from utils.memory import ensure_memory_files
from utils.scoring import score_signals


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
OUTPUT_DIR = ROOT / "outputs"


def _build_llm() -> LLM:
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        api_key = getpass("Enter your Anthropic API key. It will not be saved: ").strip()
    if not api_key:
        raise RuntimeError("ANTHROPIC_API_KEY is required to run the agent.")
    model = os.getenv("ANTHROPIC_MODEL") or _resolve_available_model(api_key)
    return LLM(model=f"anthropic/{model}", api_key=api_key)


def _resolve_available_model(api_key: str) -> str:
    preferred = [
        "claude-sonnet-4-20250514",
        "claude-3-7-sonnet-20250219",
        "claude-3-5-sonnet-20241022",
        "claude-3-5-haiku-20241022",
        "claude-3-haiku-20240307",
    ]
    client = Anthropic(api_key=api_key)
    models = list(client.models.list().data)
    available = [model.id for model in models]
    for model_id in preferred:
        if model_id in available:
            print(f"Using Anthropic model: {model_id}")
            return model_id
    if available:
        print(f"Using first available Anthropic model: {available[0]}")
        return available[0]
    raise RuntimeError("No Anthropic models were returned for this API key.")


def _collect_signals() -> list[dict[str, Any]]:
    signals: list[dict[str, Any]] = []
    errors: list[str] = []
    for label, loader in [("DDGS", search_ddgs), ("Google News RSS", read_google_news)]:
        try:
            signals.extend(loader())
        except Exception as exc:
            errors.append(f"{label} failed: {exc}")
    scored = score_signals(signals)
    if errors:
        scored.append(
            {
                "title": "Collection warning",
                "company": "System",
                "sector": "Operations",
                "source": "Local runtime",
                "url": "",
                "publication_date": "",
                "summary": " | ".join(errors),
                "executive_relevance": "Search failure should be investigated before publishing.",
                "credibility_score": 0,
                "credibility_note": "Runtime warning",
                "why_it_matters": "The output may be incomplete if a source layer failed.",
                "score": 0,
                "component_scores": {},
            }
        )
    return scored[:10]


def _signals_markdown(signals: list[dict[str, Any]]) -> str:
    lines = []
    for index, signal in enumerate(signals, start=1):
        lines.append(
            "\n".join(
                [
                    f"## {index}. {signal.get('title')}",
                    f"- Score: {signal.get('score')}",
                    f"- Company: {signal.get('company')}",
                    f"- Sector: {signal.get('sector')}",
                    f"- Source: {signal.get('source')}",
                    f"- URL: {signal.get('url')}",
                    f"- Publication date: {signal.get('publication_date')}",
                    f"- Summary: {signal.get('summary')}",
                    f"- Executive relevance: {signal.get('executive_relevance')}",
                    f"- Credibility: {signal.get('credibility_score')} - {signal.get('credibility_note')}",
                    f"- Why it matters: {signal.get('why_it_matters')}",
                ]
            )
        )
    return "\n\n".join(lines)


def _load_memory_context() -> str:
    files = ["positioning_rules.md", "ai_radar_themes.md", "source_whitelist.md"]
    return "\n\n".join((DATA_DIR / file_name).read_text(encoding="utf-8") for file_name in files)


def _build_tasks(agents: dict[str, Any], signals_md: str, memory_context: str, run_time: str) -> list[Task]:
    signal_review = Task(
        description=(
            f"Review the grounded signals collected for {run_time}.\n\n"
            f"{signals_md}\n\n"
            "Return the top 10 in ranked order. Tighten company/sector labels only when supported by the source text. "
            "Do not invent facts."
        ),
        expected_output="Ranked top 10 enterprise AI signals with source URLs, credibility notes, and executive relevance.",
        agent=agents["signal_scout"],
    )

    strategy = Task(
        description=(
            "Choose the single strongest story and framing for Ayesha Saeed-Haq.\n\n"
            f"Positioning context:\n{memory_context}\n\n"
            "Possible angles: AI Radar signal, boardroom simulation, governance debt, workforce redesign, "
            "competitive intelligence, decision intelligence lesson, operator POV, executive framework, contrarian take. "
            "Optimize for VP relevance, recruiter attraction, enterprise credibility, repeat audience growth, and profile visits."
        ),
        expected_output="Selected Topic, Selected Angle, Why Today, Confidence Score, and selection reasoning.",
        agent=agents["strategist"],
        context=[signal_review],
    )

    post = Task(
        description=(
            "Write one ready-to-publish LinkedIn post in Ayesha's voice.\n"
            "Requirements: strong hook, short paragraphs, one business tension, enterprise consequence, practical implication, "
            "decision consequence, no hashtags, no emojis, no clickbait, no unsupported statistics, no fake numbers."
        ),
        expected_output="One final LinkedIn post, ready to publish.",
        agent=agents["post_writer"],
        context=[signal_review, strategy],
    )

    qc = Task(
        description=(
            "Quality-control the post and package the final run outputs. Rewrite the post if it has unsupported claims, "
            "weak hook, generic language, fake precision, repetitive framing, unclear consequence, or low executive value.\n\n"
            "Return valid JSON with exactly these keys: daily_post, visual_brief, sources, reasoning_log.\n"
            "daily_post must include: Selected Topic, Selected Angle, Why Today, Confidence Score, Final LinkedIn Post.\n"
            "visual_brief must include: Hero title, Layout recommendation, 3-5 visual blocks, Canva instructions, "
            "yellow/black/white AI Radar branding, carousel vs single-image recommendation.\n"
            "sources must include source URLs, summaries, and credibility notes.\n"
            "reasoning_log must include top 10 signals, scoring table, selection reasoning, and QC revisions."
        ),
        expected_output="Valid JSON object with daily_post, visual_brief, sources, and reasoning_log markdown strings.",
        agent=agents["qc_agent"],
        context=[signal_review, strategy, post],
    )
    return [signal_review, strategy, post, qc]


def _parse_crew_output(raw_output: Any, signals: list[dict[str, Any]]) -> dict[str, str]:
    text = str(raw_output).strip()
    if text.startswith("```"):
        text = text.strip("`")
        text = text.removeprefix("json").strip()
    try:
        parsed = json.loads(text)
        return {key: str(parsed[key]) for key in ["daily_post", "visual_brief", "sources", "reasoning_log"]}
    except Exception:
        fallback_sources = _signals_markdown(signals)
        return {
            "daily_post": text,
            "visual_brief": "# Visual Brief\n\nReview the final post above and create an AI Radar visual using yellow, black, and white branding.",
            "sources": f"# Sources\n\n{fallback_sources}",
            "reasoning_log": f"# Reasoning Log\n\nCrew output was not valid JSON. Raw output preserved in daily_post.\n\n{fallback_sources}",
        }


def run_daily_ai_radar() -> dict[str, Path]:
    load_dotenv(ROOT / ".env")
    timezone_name = os.getenv("APP_TIMEZONE", "America/Chicago")
    ensure_directories([DATA_DIR, OUTPUT_DIR])
    ensure_memory_files(DATA_DIR)

    signals = _collect_signals()
    signals_md = _signals_markdown(signals)
    memory_context = _load_memory_context()
    llm = _build_llm()

    agents = {
        "signal_scout": build_signal_scout(llm),
        "strategist": build_executive_strategist(llm),
        "post_writer": build_post_writer(llm),
        "qc_agent": build_qc_agent(llm),
    }
    tasks = _build_tasks(agents, signals_md, memory_context, now_human(timezone_name))
    crew = Crew(agents=list(agents.values()), tasks=tasks, process=Process.sequential, verbose=True)
    result = crew.kickoff()
    documents = _parse_crew_output(result, signals)
    return write_outputs(OUTPUT_DIR, today_slug(timezone_name), documents)
