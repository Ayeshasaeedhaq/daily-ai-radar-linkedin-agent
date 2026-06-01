from __future__ import annotations

from crewai import Agent


def build_qc_agent(llm) -> Agent:
    return Agent(
        role="Hallucination and Credibility QC Agent",
        goal="Protect credibility by removing unsupported claims, weak framing, generic language, and fake precision.",
        backstory=(
            "You are a rigorous executive editor. You rewrite anything that sounds fabricated, inflated, "
            "generic, repetitive, or unclear about business consequence."
        ),
        llm=llm,
        verbose=True,
    )
