# Composio AI Product Research Agent

A research workflow for evaluating whether 100 SaaS applications can be turned into agent-callable toolkits.
This repo was created for the Composio AI Product Ops Intern take-home assignment.

## What this project does

The pipeline automates research across a curated list of SaaS apps and produces:

- Structured output for every app
- Authentication and self-serve / gated analysis
- API surface classification (REST / GraphQL / SDK / MCP)
- Buildability verdicts with evidence links
- Confidence scoring and manual-review flags
- A single interactive HTML case study report

## Why it matters

Instead of manually inspecting each product, this workflow:

- finds official documentation pages,
- extracts standardized signals with an LLM-assisted pipeline,
- validates results with JSON schema rules,
- surfaces uncertain apps for human review,
- then summarizes ecosystem patterns in an easy-to-read report.

## Quick start

```bash
cd research_agent
pip install -r requirements.txt
python run_pass1.py --test
python generate_case_study.py
```

Then open `case_study.html` in your browser.

## Repository layout

```text
research_agent/
├── agent.py               # core research pipeline and extraction logic
├── apps.py                # 100-app list and categories
├── case_study.html        # generated interactive report
├── generate_case_study.py # report builder
├── README.md              # this file
├── requirements.txt       # Python dependencies
├── results_v1.json        # structured research output
├── run_pass1.py           # entry point for the research workflow
├── schema.py              # pydantic schema and validation rules
├── verification.py        # quality checks and review flags
└── tests/
    └── test_report.py     # basic report generation test
```

## How it works

1. Load the app list from `apps.py`
2. Search official documentation for each app
3. Fetch the most relevant page(s)
4. Extract structured fields with the agent pipeline
5. Validate output against `schema.py`
6. Retry weak or invalid extractions
7. Flag ambiguous apps for manual review
8. Build the final HTML case study

## Key outputs

- `results_v1.json` — extracted research records
- `case_study.html` — polished interactive case study

## Important considerations

- The process is intentionally conservative: uncertain apps are flagged rather than overclaimed.
- Source evidence URLs are captured for every extracted record.
- Some enterprise or gated products may need manual follow-up.
- MCP support is evolving, so that signal is treated as experimental.

## Notes for reviewers

- `run_pass1.py --test` runs a test pass for the pipeline.
- `generate_case_study.py` converts the JSON output into the HTML report.
- `results_v1.json` is the structured dataset used by the report.
- `case_study.html` is the primary deliverable for review.

## Future improvements

- Add browser automation to verify docs and authentication flows
- Improve multi-agent validation for uncertain cases
- Add continuous monitoring for docs drift
- Add richer MCP discovery and verification

## Technologies

- Python
- Pydantic / JSON schema validation
- HTML report generation
- LLM-assisted information extraction
- Requests / HTML parsing

## Contact

If you want to extend this work, start by examining `agent.py`, `schema.py`, and `generate_case_study.py`.
