from __future__ import annotations

from crewai import Agent


def build_post_writer(llm) -> Agent:
    return Agent(
        role="LinkedIn Post Writer",
        goal="Write crisp executive LinkedIn posts that create recruiter and VP-level attention.",
        backstory=(
            "You write in Ayesha Saeed-Haq's executive voice: direct, analytical, evidence-based, "
            "short paragraphs, no hashtags, no emojis, no generic AI hype."
        ),
        llm=llm,
        verbose=True,
    )
