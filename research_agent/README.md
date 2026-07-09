# Composio Research Agent

This workspace contains a lightweight research pipeline for the 100-app case study assignment.

## What it does
- Reads the app list from apps.py.
- Searches docs pages, extracts auth / self-serve / API surface details, and validates them.
- Writes structured research records to results_v1.json.
- Generates a self-explanatory HTML case study at case_study.html.

## Run it
1. Install dependencies:
   pip install -r requirements.txt
2. Run the research pass:
   python run_pass1.py --test
3. Generate the case study:
   python generate_case_study.py

## Notes
- The first test pass should be reviewed manually before running the full batch.
- The generated HTML page is intended to be the deliverable for reviewers.
