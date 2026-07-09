"""
Pass 1 research agent.
For each app: web search -> fetch top page(s) -> Groq extraction -> validate -> checkpoint.

Design notes (read before running):
- Search: DuckDuckGo (ddgs package) — no API key needed, free.
- Fetch: trafilatura for clean text extraction (strips nav/ads/boilerplate).
- Extraction: Groq llama-3.1-8b-instant, forced JSON output, validated against schema.AppRecord.
- Checkpointing: results written to results_v1.json after EVERY app (crash-safe).
- Retries: malformed JSON -> 1 retry with the validation error appended to the prompt.
- Composio is NOT used in this pass by design (see chat discussion) — it drives pass 2's
  grounding/verification step instead, where its search+fetch tools add the most value.

Run: python run_pass1.py
"""

import os
import json
import time
import re
from urllib.parse import urlparse
from datetime import datetime, timezone
from dotenv import load_dotenv
from groq import Groq
from ddgs import DDGS
import trafilatura
from pydantic import ValidationError
load_dotenv()  # load GROQ_API_KEY from .env
from schema import AppRecord
from apps import APPS

GROQ_MODEL = "llama-3.1-8b-instant"
RESULTS_PATH = "results_v1.json"
LOG_PATH = "run_log_pass1.csv"
SLEEP_BETWEEN_APPS = 2.0  # seconds, be polite to search + rate limits
MAX_RETRIES = 1

client = Groq(api_key=os.environ["GROQ_API_KEY"])


def extract_domain(hint: str) -> str | None:
    """Pull a bare domain out of a hint string, or None if the hint isn't a URL/domain
    (e.g. 'paygent (NMI-powered)' has no usable domain)."""
    candidate = hint.strip()
    if not candidate.startswith("http"):
        candidate = f"https://{candidate}"
    try:
        netloc = urlparse(candidate).netloc.lower()
        netloc = netloc.replace("www.", "")
        # bail out if it clearly isn't a real domain (contains spaces, parens, etc in original hint)
        if " " in hint or "(" in hint:
            return None
        return netloc.split("/")[0] if netloc else None
    except Exception:
        return None


def domain_actually_matches(domain: str, candidate_url: str) -> bool:
    """Proper boundary-aware domain match. 'salesforce.com' must NOT match
    'sainisalesforce.com' (the bug caught in testing) — only exact netloc match
    or a genuine subdomain (e.g. 'developers.salesforce.com') counts."""
    try:
        candidate_netloc = urlparse(candidate_url).netloc.lower().replace("www.", "")
    except Exception:
        return False
    return candidate_netloc == domain or candidate_netloc.endswith("." + domain)


SYSTEM_PROMPT = """You are a precise technical research assistant. You will be given
the name of a software app/API and raw text scraped from its official documentation
or website. Extract ONLY facts that are directly supported by the provided text.

Output STRICT JSON matching this exact shape (no markdown fences, no commentary):

{
  "app": "<name as given>",
  "category": "<category as given>",
  "one_liner": "<what it does, <=200 chars>",
  "auth_methods": ["OAuth2" | "API key" | "Basic" | "Token" | "None" | "Other"],
  "auth_note": "<detail or null>",
  "self_serve": "self-serve" | "gated" | "partial",
  "gate_reason": "<required if not self-serve, else null>",
  "api_surface": {
    "type": "REST" | "GraphQL" | "REST+GraphQL" | "SDK-only" | "none found",
    "breadth": "broad" | "moderate" | "narrow" | "unknown",
    "mcp_exists": true | false,
    "mcp_note": "<detail or null>"
  },
  "verdict": "buildable" | "blocked" | "partial",
  "blocker": "<required if not buildable, else null>",
  "evidence": [{"url": "<source url>", "snippet": "<short supporting quote/paraphrase from the text>"}],
  "confidence": "high" | "medium" | "low"
}

Rules:
- confidence must be "high" ONLY if the page text explicitly and unambiguously states the fact.
- If the page text implies something but doesn't state it directly, confidence must be "medium"
  and the relevant note/reason field must say what was inferred vs. stated.
- If the page text does not address something at all, confidence must be "low" — make your best
  reasonable inference for the field values, but do not phrase gate_reason/blocker/auth_note as if
  they were confirmed facts. Phrases like "not included in the provided text" mean confidence is
  LOW, never "high" — do not contradict your own confidence label.
- Do not fabricate specific procedural details (e.g. "provided by customer success team",
  "requires admin approval") unless the page text actually says that. If unsure, describe the
  gate/blocker in general terms and mark confidence low/medium.
- evidence must contain at least one entry with the real source URL you were given.
- If SOURCE DOMAIN NOTE below says the page may not be the official source for this app, treat
  everything with extra skepticism, mention the mismatch risk in one evidence snippet, and cap
  confidence at "medium" even if the page text looks confident.
"""


def log(row: str):
    with open(LOG_PATH, "a") as f:
        f.write(row + "\n")


def search_and_fetch(app_name: str, hint: str) -> tuple[str, str, bool]:
    """Search for docs, fetch best result. Returns (clean_text, source_url, domain_matched)."""
    domain = extract_domain(hint)
    query = f"{app_name} {domain} API documentation authentication" if domain else f"{app_name} API documentation authentication"
    text, url, domain_matched = "", hint if hint.startswith("http") else f"https://{hint}", False

    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=5))

        # Prefer results whose URL actually matches our known domain (boundary-aware —
        # this is the fix for 'sainisalesforce.com' falsely matching 'salesforce.com').
        ordered = results
        if domain:
            domain_hits = [r for r in results if domain_actually_matches(domain, r.get("href") or r.get("url") or "")]
            other_hits = [r for r in results if r not in domain_hits]
            ordered = domain_hits + other_hits

        for r in ordered:
            candidate_url = r.get("href") or r.get("url")
            if not candidate_url:
                continue
            downloaded = trafilatura.fetch_url(candidate_url)
            if downloaded:
                extracted = trafilatura.extract(downloaded)
                if extracted and len(extracted) > 200:
                    text, url = extracted, candidate_url
                    domain_matched = bool(domain and domain_actually_matches(domain, candidate_url))
                    break
    except Exception as e:
        log(f"{app_name},search_error,{e}")

    # fallback: try the hint URL directly if search yielded nothing
    if not text:
        try:
            fallback_url = hint if hint.startswith("http") else f"https://{hint}"
            downloaded = trafilatura.fetch_url(fallback_url)
            if downloaded:
                text = trafilatura.extract(downloaded) or ""
                url = fallback_url
                domain_matched = True  # fallback IS the known domain by definition
        except Exception as e:
            log(f"{app_name},fallback_fetch_error,{e}")

    if not domain_matched:
        log(f"{app_name},WARNING_domain_mismatch,source={url}")

    return text[:6000], url, domain_matched  # cap text length for context budget


def extract_record(app_name: str, category: str, page_text: str, source_url: str,
                    domain_matched: bool, retry_note: str = "") -> dict:
    domain_note = (
        "SOURCE DOMAIN NOTE: This page's domain matches the app's known official domain."
        if domain_matched else
        "SOURCE DOMAIN NOTE: This page's domain does NOT clearly match the app's known official "
        "domain — this may be a different product with a similar name, or a third-party source. "
        "Treat with extra skepticism per the rules above."
    )

    user_content = f"""App: {app_name}
Category: {category}
Source URL: {source_url}
{domain_note}

--- PAGE TEXT ---
{page_text if page_text else "(no page text could be retrieved — infer conservatively, set confidence low)"}
--- END PAGE TEXT ---
{retry_note}"""

    resp = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_content},
        ],
        temperature=0.1,
        response_format={"type": "json_object"},
    )
    raw = resp.choices[0].message.content
    return json.loads(raw)


# phrases from our own prompt — if these show up in "evidence" snippets, the model is
# hallucinating by echoing instructions back as if they were page content
PROMPT_LEAK_MARKERS = [
    "confidence is medium", "confidence is high", "confidence is low",
    "domain note", "page text explicitly", "does not explicitly state",
    "source domain note", "treat with extra skepticism",
]


def strip_leaked_evidence(record: dict, app_name: str) -> dict:
    """Remove any evidence entries that look like leaked prompt text rather than
    real page content, and log it so it shows up in the verification story."""
    clean_evidence = []
    for e in record.get("evidence", []):
        snippet_lower = e.get("snippet", "").lower()
        if any(marker in snippet_lower for marker in PROMPT_LEAK_MARKERS):
            log(f"{app_name},PROMPT_LEAK_DETECTED,{e.get('snippet', '')[:100]}")
            continue
        clean_evidence.append(e)
    record["evidence"] = clean_evidence
    return record


AUTH_METHOD_ALIASES = {
    "bearer": "Token", "bearer token": "Token", "access token": "Token",
    "sso": "OAuth2", "sso / social login": "OAuth2", "social login": "OAuth2",
    "native proxy protocol": "Other", "proxy protocol": "Other",
    "signature": "Other", "hmac": "Other", "custom": "Other",
}


def normalize_auth_methods(raw_methods, app_name: str) -> list[str]:
    """Map non-standard auth strings the model invents onto our fixed enum,
    instead of hoping a retry makes it comply (it usually repeats the same
    'reasonable' non-standard value — that's what happened with Bright Data,
    Clay, and PitchBook in testing)."""
    valid = {"OAuth2", "API key", "Basic", "Token", "None", "Other"}
    if isinstance(raw_methods, str):
        # the Mermaid CLI failure: model returned a bare string instead of a list
        log(f"{app_name},AUTH_METHODS_WAS_STRING_NOT_LIST,{raw_methods!r}")
        raw_methods = [raw_methods]
    normalized = []
    for m in raw_methods or []:
        if m in valid:
            normalized.append(m)
        else:
            mapped = AUTH_METHOD_ALIASES.get(str(m).strip().lower(), "Other")
            log(f"{app_name},AUTH_METHOD_NORMALIZED,{m!r}->{mapped}")
            normalized.append(mapped)
    # dedupe, preserve order
    seen = set()
    result = [m for m in normalized if not (m in seen or seen.add(m))]
    return result or ["Other"]  # never return an empty list — schema requires at least handling


def backfill_gate_reason(raw: dict, app_name: str) -> dict:
    """If the model says gated/partial but forgot gate_reason (the BigCommerce
    failure), backfill a placeholder that flags it for manual review instead of
    failing the whole record."""
    if raw.get("self_serve") in ("gated", "partial") and not raw.get("gate_reason"):
        raw["gate_reason"] = "(agent flagged as gated/partial but did not specify why — needs manual check)"
        raw["confidence"] = "low"
        log(f"{app_name},GATE_REASON_BACKFILLED")
    return raw


def process_app_dict(app: dict) -> dict | None:
    return process_app(app["name"], app["hint"], app["category"])


def process_app(app_name: str, hint: str, category: str) -> dict | None:
    page_text, source_url, domain_matched = search_and_fetch(app_name, hint)

    retry_note = ""
    for attempt in range(MAX_RETRIES + 1):
        try:
            raw = extract_record(app_name, category, page_text, source_url, domain_matched, retry_note)
            raw["fetched_at"] = datetime.now(timezone.utc).isoformat()
            raw["model_used"] = GROQ_MODEL
            raw["pass_number"] = 1
            raw["domain_matched"] = domain_matched
            raw["auth_methods"] = normalize_auth_methods(raw.get("auth_methods"), app_name)
            raw = backfill_gate_reason(raw, app_name)
            raw = strip_leaked_evidence(raw, app_name)
            if not raw.get("evidence"):
                # stripping emptied it — fall back to a low-confidence placeholder rather
                # than fail validation; this app becomes a clear manual-check candidate
                raw["evidence"] = [{"url": source_url, "snippet": "(evidence stripped — model echoed prompt text instead of page content, needs manual check)"}]
                raw["confidence"] = "low"
                log(f"{app_name},EVIDENCE_EMPTIED_AFTER_STRIP,forced_low_confidence")
            record = AppRecord(**raw)
            log(f"{app_name},success,attempt_{attempt+1},domain_matched={domain_matched}")
            return record.model_dump()
        except (ValidationError, json.JSONDecodeError) as e:
            retry_note = f"\nYour previous output was invalid: {str(e)[:500]}. Fix it and output valid JSON only."
            log(f"{app_name},validation_error,attempt_{attempt+1},{str(e)[:200]}")
            continue
    log(f"{app_name},FAILED,all_retries_exhausted")
    return None


def load_existing() -> dict:
    if os.path.exists(RESULTS_PATH):
        with open(RESULTS_PATH) as f:
            return json.load(f)
    return {}


def save_results(results: dict):
    with open(RESULTS_PATH, "w") as f:
        json.dump(results, f, indent=2)


def run():
    results = load_existing()
    log(f"--- run started {datetime.now(timezone.utc).isoformat()} ---")

    for i, app in enumerate(APPS, 1):
        app_name = app["name"]
        if app_name in results and results[app_name] is not None:
            print(f"[{i}/{len(APPS)}] {app_name}: already done, skipping")
            continue

        print(f"[{i}/{len(APPS)}] {app_name}: researching...")
        record = process_app_dict(app)
        results[app_name] = record
        save_results(results)  # checkpoint every single app

        if record is None:
            print(f"  -> FAILED after retries")
        else:
            print(f"  -> {record['verdict']} / {record['self_serve']} / confidence={record['confidence']}")

        time.sleep(SLEEP_BETWEEN_APPS)

    failed = [k for k, v in results.items() if v is None]
    print(f"\nDone. {100 - len(failed)}/100 succeeded. Failed: {failed}")


if __name__ == "__main__":
    run()