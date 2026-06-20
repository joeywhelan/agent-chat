# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This repo contains the specification (`assets/plan.md`) and deliverables for a hands-on notebook walkthrough demonstrating:
1. **Elastic Agent Builder** — natural language → ES|QL query generation via the Kibana GUI
2. **Official Elastic Agent Skills** — `elasticsearch-esql` and the full `elastic/agent-skills` collection inside Claude Code

The primary deliverable is a runnable Jupyter/Markdown notebook targeted at Elastic practitioners.

## Deliverable Structure

The notebook has four sections; division of labor is documented in `assets/plan.md` under **Sequencing & Dependencies**:

| Section | Owner | Status |
|---------|-------|--------|
| Section 0 — Prerequisites & Setup | User (Terraform provisioning) + Claude (Python cells) | — |
| Section 1 — Agent Chat walkthrough + synthetic data | Claude | Depends on Section 0 |
| Section 2 — Claude Code + Elastic Agent Skills (elasticsearch-esql, full-text, aggregation) | Claude | Depends on Section 0 |
| Section 3 — Terraform teardown | User | Depends on Section 0 |

## Environment & Dependencies

Required environment variables (written to `.env` by Terraform in Section 0):
```
ELASTICSEARCH_URL=https://your-project.es.us-east-1.aws.elastic.cloud
ELASTICSEARCH_USERNAME=elastic
ELASTICSEARCH_PASSWORD=your-generated-password
```

Python dependencies for the notebook: `elasticsearch-py`, `requests`, `python-dotenv`, `faker`

## Notebook Conventions

- Each section opens with `## Overview` and closes with `## Key Takeaways` markdown cells
- Screenshot placeholders use the format `[SCREENSHOT: description]`
- Terminal commands are shown as non-runnable bash code blocks (not notebook cells)
- No hardcoded credentials — all via env vars

## Key Reference Links

- `assets/plan.md` — the authoritative spec for all notebook content
- Elastic Agent Builder docs: https://www.elastic.co/docs/explore-analyze/ai-features/elastic-agent-builder
- Official Agent Skills repo: https://github.com/elastic/agent-skills
- `elasticsearch-esql` SKILL.md: https://github.com/elastic/agent-skills/blob/main/skills/elasticsearch/elasticsearch-esql/SKILL.md

# Skills
@.claude/skills
