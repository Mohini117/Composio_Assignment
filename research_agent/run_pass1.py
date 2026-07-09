"""
Entrypoint for pass 1.

Usage:
    python run_pass1.py --test      # runs only the first 5 apps, writes to results_v1_test.json
    python run_pass1.py             # runs all 100, writes to results_v1.json

ALWAYS run --test first. Check results_v1_test.json by hand before running the full batch.
This is not optional — an unvalidated prompt burns your Groq rate limit and your time budget
on 100 apps of garbage.
"""

import sys
import json
import agent
from apps import APPS

TEST_MODE = "--test" in sys.argv

if TEST_MODE:
    agent.RESULTS_PATH = "results_v1_test.json"
    agent.LOG_PATH = "run_log_pass1_test.csv"
    apps_to_run = APPS[:5]
    print(f"[TEST MODE] Running on {len(apps_to_run)} apps: {[a['name'] for a in apps_to_run]}")
    print(f"[TEST MODE] Writing to {agent.RESULTS_PATH}")
else:
    apps_to_run = APPS
    print(f"[FULL RUN] Running on all {len(apps_to_run)} apps")
    print(f"[FULL RUN] Writing to {agent.RESULTS_PATH}")
    confirm = input("Type 'yes' to proceed with the full 100-app run: ")
    if confirm.strip().lower() != "yes":
        print("Aborted.")
        sys.exit(0)

# monkey-patch the APPS list agent.run() iterates over
agent.APPS = apps_to_run
agent.run()

# quick post-run summary
with open(agent.RESULTS_PATH) as f:
    results = json.load(f)

succeeded = {k: v for k, v in results.items() if v is not None}
failed = [k for k, v in results.items() if v is None]

print(f"\n=== SUMMARY ===")
print(f"Succeeded: {len(succeeded)}/{len(apps_to_run)}")
if failed:
    print(f"Failed: {failed}")

if succeeded:
    confidences = [v["confidence"] for v in succeeded.values()]
    print(f"Confidence breakdown: high={confidences.count('high')}, "
          f"medium={confidences.count('medium')}, low={confidences.count('low')}")
    verdicts = [v["verdict"] for v in succeeded.values()]
    print(f"Verdict breakdown: buildable={verdicts.count('buildable')}, "
          f"blocked={verdicts.count('blocked')}, partial={verdicts.count('partial')}")

if TEST_MODE:
    print(f"\n>>> Now open {agent.RESULTS_PATH} and manually check these 5 against real docs.")
    print(">>> If they look wrong, fix the prompt in agent.py's SYSTEM_PROMPT before running full.")