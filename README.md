# AI Product Research Agent

An agent-assisted research pipeline that analyzes SaaS applications and determines whether they can be turned into agent-callable toolkits.

This project was built as a take-home assignment for the **Composio AI Product Ops Intern** role.

---

## Overview

The goal is to automate research across a list of **100 SaaS applications** instead of manually inspecting documentation.

For each application, the agent identifies:

- Category
- One-line description
- Authentication method(s)
- Self-serve vs gated onboarding
- API surface (REST / GraphQL / SDK / MCP)
- Buildability verdict
- Evidence links
- Confidence score

The pipeline then aggregates the results to discover ecosystem-wide patterns and generates a single HTML case study.

---

## Features

- Automated documentation research
- Structured information extraction using an LLM
- JSON schema validation
- Evidence collection
- Confidence scoring
- Manual review identification
- Pattern analysis
- Interactive HTML report generation

---

## Research Workflow

```
100 Apps
      │
      ▼
Search Official Documentation
      │
      ▼
Retrieve Relevant Pages
      │
      ▼
LLM Information Extraction
      │
      ▼
Schema Validation
      │
      ▼
Evidence & Confidence Checks
      │
      ▼
Flag Ambiguous Apps
      │
      ▼
Pattern Analysis
      │
      ▼
Generate HTML Case Study
```

---

## What the Agent Extracts

For every application the agent collects:

- Category
- Description
- Authentication method
- Self-serve / Gated status
- API surface
- Existing MCP support
- Buildability verdict
- Supporting evidence
- Confidence level

---

## Verification Strategy

Accuracy was prioritized over speed.

The verification workflow consists of:

1. Official documentation search
2. LLM extraction
3. JSON schema validation
4. Retry when extraction is weak
5. Confidence scoring
6. Manual review for ambiguous cases

Rather than forcing uncertain answers, the pipeline flags applications that require human verification.

---

## Pattern Analysis

After collecting all applications, the project identifies ecosystem-level patterns such as:

- Dominant authentication methods
- Self-serve vs gated products
- API surface distribution
- MCP adoption
- Categories with the easiest integrations
- Categories requiring partnerships

The goal is to provide actionable insights rather than only a spreadsheet of results.

---

## Project Structure

```
.
├── README.md
├── requirements.txt
├── run_pass1.py
├── generate_case_study.py
├── case_study.html
├── data/
│   └── apps.json
├── outputs/
│   ├── results.json
│   └── summary.json
└── prompts/
```

*(Adjust the structure if your repository differs.)*

---

## Installation

Clone the repository

```bash
git clone <repository-url>
cd <repository-name>
```

Install dependencies

```bash
pip install -r requirements.txt
```

---

## Run

Run the research pipeline

```bash
python run_pass1.py --test
```

Generate the HTML case study

```bash
python generate_case_study.py
```

---

## Output

The pipeline generates:

- Structured JSON results
- Pattern summary
- Verification statistics
- Interactive HTML report

Open

```
case_study.html
```

in your browser to view the final case study.

---

## Human-in-the-Loop

Some applications cannot be confidently classified automatically.

These typically include:

- Enterprise-only APIs
- Partner-gated platforms
- Ambiguous documentation
- Authentication requiring paid accounts

These applications are intentionally flagged for manual review instead of being automatically labeled.

---

## Limitations

- Some documentation changes over time.
- Enterprise APIs may require authenticated access.
- MCP support is evolving rapidly.
- Verification was performed on a representative sample rather than every application.

---

## Future Improvements

- Browser automation for deeper verification
- Multi-agent verification pipeline
- Automatic documentation change detection
- Continuous monitoring of API updates
- Direct MCP capability discovery

---

## Technologies Used

- Python
- Large Language Models (LLMs)
- HTML/CSS
- JSON Schema Validation
- Requests
- BeautifulSoup (or equivalent HTML parsing)
- Async processing where applicable

---

## Assignment Deliverables

- ✅ AI research agent
- ✅ Automated SaaS documentation analysis
- ✅ Pattern discovery
- ✅ Verification workflow
- ✅ Human review loop
- ✅ Interactive HTML case study
- ✅ Source code with reproducible pipeline

---

## License

This project was created solely for the Composio AI Product Ops Intern take-home assignment.
