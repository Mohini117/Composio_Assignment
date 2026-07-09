# Composio Research Agent

An agent-assisted research pipeline built for the Composio AI Product Ops Intern take-home assignment.
The pipeline evaluates 100 SaaS applications and produces a structured research output plus a polished HTML case study.

## Overview

This project automates research across a fixed app list and extracts:

- Category
- One-line description
- Authentication methods
- Self-serve vs gated onboarding
- API surface (REST / GraphQL / SDK / MCP)
- Buildability verdict
- Evidence links
- Confidence score

The pipeline also aggregates the results to surface patterns and verification insights.

## Features

- Automated documentation discovery and extraction
- LLM-assisted structured data extraction
- JSON schema validation and retry logic
- Evidence capture with source URLs
- Confidence scoring and manual-review flags
- Pattern analysis across the SaaS app set
- Interactive HTML case study generation

## Research Workflow

1. Load the 100 app list from `apps.py`
2. Search official docs and fetch relevant pages
3. Extract structured fields using the agent pipeline
4. Validate each record against `schema.py`
5. Retry weak or malformed outputs
6. Flag ambiguous apps for manual review
7. Generate the HTML report in `case_study.html`

## What the agent extracts

Each app record can include:

- Category
- Description
- Authentication method(s)
- Self-serve or gated status
- API surface details
- MCP-related support signal
- Buildability verdict
- Evidence URLs
- Confidence level

## Verification strategy

The workflow prioritizes accuracy over guesswork:

1. Official documentation search
2. LLM extraction
3. JSON schema validation
4. Retry weak outputs
5. Confidence scoring
6. Human review for ambiguous cases

Ambiguous or low-confidence apps are intentionally surfaced rather than automatically over-labeled.

## Pattern analysis

The pipeline aggregates results to identify:

- Dominant authentication methods
- Self-serve vs gated ratios
- API surface distribution
- MCP adoption signals
- Categories with the easiest integrations
- Categories requiring partner or enterprise workflows

## Repository structure

```
.
├── .gitignore
├── research_agent/
│   ├── agent.py
│   ├── apps.py
│   ├── case_study.html
│   ├── generate_case_study.py
│   ├── README.md
│   ├── requirements.txt
│   ├── results_v1.json
│   ├── run_pass1.py
│   ├── schema.py
│   ├── verification.py
│   └── tests/
│       └── test_report.py
```

## Installation

```bash
cd research_agent
pip install -r requirements.txt
```

## Run

```bash
python run_pass1.py --test
python generate_case_study.py
```

## Output

The pipeline generates:

- `results_v1.json` — structured research output
- `case_study.html` — interactive HTML case study

Open `case_study.html` in a browser to review the final report.

## Human-in-the-loop

Some applications are intentionally marked for manual follow-up when:

- Documentation is ambiguous or incomplete
- Access appears partner-gated or enterprise-only
- Authentication requires a paid account or special approval
- The confidence score is low

## Limitations

- Docs can change over time.
- Some enterprise APIs require authenticated access.
- MCP support evolves rapidly.
- A sample of apps may receive manual verification rather than full coverage.

## Future improvements

- Browser automation for deeper verification
- Multi-agent result validation
- Automatic docs drift detection
- Continuous monitoring of API surface changes
- Direct MCP discovery and validation

## Technologies used

- Python
- JSON schema validation
- LLM-assisted extraction
- HTML/CSS report generation
- HTTP fetching and HTML parsing

## Assignment deliverables

- ✅ AI research agent
- ✅ Automated SaaS documentation analysis
- ✅ Pattern discovery and verification workflow
- ✅ Human review loop
- ✅ Interactive HTML case study
- ✅ Reproducible source code
