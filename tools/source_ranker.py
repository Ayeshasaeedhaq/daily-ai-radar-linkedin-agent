from __future__ import annotations

from urllib.parse import urlparse


HIGH_TRUST_DOMAINS = {
    "sec.gov",
    "beckershospitalreview.com",
    "modernhealthcare.com",
    "fiercehealthcare.com",
    "healthcaredive.com",
    "wsj.com",
    "ft.com",
    "fortune.com",
    "bloomberg.com",
    "cnbc.com",
    "mckinsey.com",
    "accenture.com",
    "deloitte.com",
    "bain.com",
    "bcg.com",
    "venturebeat.com",
    "theinformation.com",
    "techcrunch.com",
    "aws.amazon.com",
    "microsoft.com",
    "googlecloud.com",
    "openai.com",
    "anthropic.com",
}

LOW_TRUST_HINTS = ["blogspot", "substack", "medium.com", "newsletter", "seo", "top10", "best-ai-tools"]


def domain_from_url(url: str) -> str:
    parsed = urlparse(url)
    return parsed.netloc.lower().removeprefix("www.")


def credibility_score(url: str, source_name: str = "") -> tuple[int, str]:
    domain = domain_from_url(url)
    source_text = f"{domain} {source_name}".lower()
    if any(domain == trusted or domain.endswith(f".{trusted}") for trusted in HIGH_TRUST_DOMAINS):
        return 90, "High-trust source or named whitelist domain."
    if any(hint in source_text for hint in LOW_TRUST_HINTS):
        return 35, "Lower trust: social, newsletter, SEO, or repost-style source."
    if any(term in source_text for term in ["investor", "press", "newsroom", "ir."]):
        return 85, "Likely primary company source."
    return 60, "Standard source; verify before making strong claims."
