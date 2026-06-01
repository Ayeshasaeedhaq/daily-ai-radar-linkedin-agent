# daily-ai-radar-linkedin-agent

A scheduled CrewAI system that creates a daily executive LinkedIn content intelligence package for Ayesha Saeed-Haq.

It produces:

- One executive-grade LinkedIn post
- One Canva-ready visual brief
- One source log
- One reasoning log

The system is designed to build enterprise credibility, VP/Director visibility, recruiter attraction, profile visits, consulting and speaking inbound, and repeat executive audience growth.

## Architecture

The project uses a grounded pipeline:

1. `tools/web_search.py` collects fresh enterprise AI signals with DDGS.
2. `tools/rss_reader.py` adds a Google News RSS freshness layer.
3. `tools/source_ranker.py` applies whitelist-based source credibility scoring.
4. `utils/scoring.py` ranks signals with transparent 1-100 scoring.
5. CrewAI agents select the strongest story, write the LinkedIn post, and run hallucination/QC review.
6. Markdown outputs are written to `outputs/`.

## Setup

Install Python 3.11 or newer.

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Copy the example environment file if you want the app to remember your key locally:

```bash
copy .env.example .env
```

Open `.env` and add:

```text
ANTHROPIC_API_KEY=your_anthropic_api_key_here
```

The default model is `claude-sonnet-4-20250514` and is configurable with `ANTHROPIC_MODEL`.

If you do not want to save the key anywhere, skip `.env`. The app will prompt for the Anthropic key with Python `getpass` when you run it locally. The key will be used for that run only and will not be written to disk.

## Run Locally

```bash
python main.py
```

You can also run it from the included notebook:

```text
run_daily_ai_radar.ipynb
```

The notebook asks for the Anthropic key with `getpass` and then runs the same production Python code.

Each run creates four files:

- `outputs/YYYY-MM-DD_daily_post.md`
- `outputs/YYYY-MM-DD_visual_brief.md`
- `outputs/YYYY-MM-DD_sources.md`
- `outputs/YYYY-MM-DD_reasoning_log.md`

## Scheduler

GitHub Actions runs the project daily at 8:00 AM Central Time during standard time.

The workflow uses UTC cron:

```yaml
cron: "0 14 * * *"
```

Important DST note: GitHub Actions cron is UTC-only. `0 14 * * *` equals 8:00 AM Central Standard Time and 9:00 AM Central Daylight Time. For exact 8:00 AM local delivery year-round, adjust the cron seasonally or add a second workflow with date-aware gating.

The workflow also supports manual runs with `workflow_dispatch`.

## Folder Structure

```text
daily-ai-radar-linkedin-agent/
  config/
  src/
  agents/
  tools/
  utils/
  data/
  outputs/
  .github/workflows/
```

## Memory System

The project creates starter memory files if they do not exist:

- `data/past_posts.csv`
- `data/post_performance.csv`
- `data/positioning_rules.md`
- `data/ai_radar_themes.md`

Use `past_posts.csv` to avoid repetitive topics and angles. Use `post_performance.csv` to record what attracts recruiters, executives, profile visits, connection requests, and speaking or consulting inbound.

## Improving Future Recommendations

After publishing, add performance data to `data/post_performance.csv`.

Useful notes include:

- Which posts attracted recruiters
- Which posts created executive comments
- Which topics drove profile visits
- Which angles felt differentiated
- Which visuals were easiest to reuse in Canva

The more specific the notes, the better the system can optimize future recommendations.

## Example Output Shape

`daily_post.md` includes:

- Selected Topic
- Selected Angle
- Why Today
- Confidence Score
- Final LinkedIn Post

`visual_brief.md` includes:

- Hero title
- Layout recommendation
- 3-5 visual blocks
- Canva instructions
- Yellow/black/white AI Radar branding
- Carousel vs single-image recommendation

`sources.md` includes source URLs, summaries, and credibility notes.

`reasoning_log.md` includes top 10 signals, scoring table, selection reasoning, and QC revisions.
