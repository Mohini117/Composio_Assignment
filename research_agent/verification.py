from __future__ import annotations

from collections import Counter
from typing import Any


def select_verification_sample(records: list[dict[str, Any]], sample_size: int = 15) -> list[dict[str, Any]]:
    """Select a small but diverse sample for a stronger verification pass.

    Priority goes to low-confidence rows and rows with partial/gated outcomes so the
    review process targets the most error-prone cases first.
    """
    if not records:
        return []

    low_confidence = [r for r in records if r.get('confidence') != 'high']
    gated_or_partial = [r for r in records if r.get('self_serve') != 'self-serve']
    high_confidence = [r for r in records if r.get('confidence') == 'high']

    ordered = []
    ordered.extend(low_confidence)
    ordered.extend(gated_or_partial)
    ordered.extend(high_confidence)

    seen = set()
    sample = []
    for record in ordered:
        app_name = record.get('app')
        if app_name in seen:
            continue
        seen.add(app_name)
        sample.append(record)
        if len(sample) >= sample_size:
            break

    # If the priority list is too short, fill with the remaining records.
    if len(sample) < sample_size:
        for record in records:
            app_name = record.get('app')
            if app_name in seen:
                continue
            sample.append(record)
            seen.add(app_name)
            if len(sample) >= sample_size:
                break

    return sample


def summarize_verification(results: dict[str, Any], sample_size: int = 15) -> dict[str, Any]:
    records = [r for r in results.values() if isinstance(r, dict)]
    sample = select_verification_sample(records, sample_size=sample_size)

    review_items = []
    for record in sample:
        issues = []
        if record.get('confidence') != 'high':
            issues.append('low-confidence extraction')
        if not record.get('evidence'):
            issues.append('missing evidence')
        if record.get('domain_matched') is False:
            issues.append('domain mismatch')
        if record.get('self_serve') != 'self-serve' and not record.get('gate_reason'):
            issues.append('missing gate reason')
        if record.get('verdict') != 'buildable' and not record.get('blocker'):
            issues.append('missing blocker')

        review_items.append({
            'app': record.get('app'),
            'initial_confidence': record.get('confidence'),
            'self_serve': record.get('self_serve'),
            'verdict': record.get('verdict'),
            'needs_manual_review': bool(issues),
            'issues': issues,
        })

    confidence_counts = Counter(r.get('confidence') for r in records)
    domain_match_count = sum(1 for r in records if r.get('domain_matched') is True)
    evidence_count = sum(1 for r in records if r.get('evidence'))

    # Heuristic trust score: this is a quality signal, not a claim of true factual accuracy.
    quality_score = round(
        100 * (
            0.5 * (confidence_counts.get('high', 0) / max(1, len(records)))
            + 0.3 * (domain_match_count / max(1, len(records)))
            + 0.2 * (evidence_count / max(1, len(records)))
        ),
        1,
    )

    return {
        'sample_size': len(review_items),
        'sample_apps': review_items,
        'manual_review_count': sum(1 for item in review_items if item['needs_manual_review']),
        'confidence_counts': dict(confidence_counts),
        'domain_match_count': domain_match_count,
        'evidence_count': evidence_count,
        'quality_score': quality_score,
    }
