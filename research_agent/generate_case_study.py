import json
from collections import Counter
from html import escape
from pathlib import Path
from string import Template
from typing import Any

from verification import summarize_verification


def load_results(results_path: str | Path) -> dict[str, Any]:
    with open(results_path, 'r', encoding='utf-8') as fh:
        return json.load(fh)


def summarize(results: dict[str, Any]) -> dict[str, Any]:
    records = [r for r in results.values() if isinstance(r, dict)]
    auth_counts = Counter(method for r in records for method in r.get('auth_methods', []))
    self_serve_counts = Counter(r.get('self_serve') for r in records)
    verdict_counts = Counter(r.get('verdict') for r in records)
    confidence_counts = Counter(r.get('confidence') for r in records)
    category_counts = Counter(r.get('category') for r in records)
    api_type_counts = Counter((r.get('api_surface', {}) or {}).get('type') or 'unknown' for r in records)
    mcp_count = sum(1 for r in records if (r.get('api_surface', {}) or {}).get('mcp_exists'))
    verification = summarize_verification(results)

    blockers = Counter()
    for r in records:
        blocker = r.get('blocker')
        if blocker:
            blockers[blocker] = blockers.get(blocker, 0) + 1

    easy_wins = [r for r in records if r.get('self_serve') == 'self-serve' and r.get('verdict') == 'buildable']
    gated = [r for r in records if r.get('self_serve') != 'self-serve']

    key_findings = [
        f"OAuth2 is the dominant auth pattern with {auth_counts.get('OAuth2', 0)} apps.",
        f"{self_serve_counts.get('self-serve', 0)} apps look self-serve, while {self_serve_counts.get('gated', 0)} are gated or partner-dependent.",
        f"{mcp_count} apps explicitly indicate MCP-related support or an MCP path.",
        f"REST is still the dominant API surface with {api_type_counts.get('REST', 0)} apps.",
    ]
    recommendations = [
        "Priority 1: Developer platforms and productivity apps are the fastest wins because they are usually self-serve and well-documented.",
        "Priority 2: Enterprise CRM, finance, and marketing products are more likely to need partner outreach or gated access.",
        "Priority 3: MCP-ready opportunities appear most often in AI-native, developer-facing, and collaboration-heavy tools.",
    ]

    return {
        'total': len(records),
        'categories': dict(category_counts),
        'auth_counts': dict(auth_counts),
        'self_serve_counts': dict(self_serve_counts),
        'verdict_counts': dict(verdict_counts),
        'confidence_counts': dict(confidence_counts),
        'api_type_counts': dict(api_type_counts),
        'mcp_count': mcp_count,
        'blockers': dict(blockers.most_common(8)),
        'easy_wins': easy_wins[:15],
        'gated': gated[:15],
        'verification': verification,
        'key_findings': key_findings,
        'recommendations': recommendations,
    }


def render_badge(value: str, tone: str = 'blue') -> str:
    return f'<span class="badge {tone}">{escape(str(value))}</span>'


def render_chart(title: str, items: list[tuple[str, int]], chart_type: str = 'bar') -> str:
    if not items:
        return f'<div class="chart-card"><h4>{escape(title)}</h4><p>No data</p></div>'

    colors = ['#4f7cff', '#22c55e', '#8b5cf6', '#f59e0b', '#ef4444', '#0ea5e9']
    max_value = max(val for _, val in items) or 1
    width = 360
    height = 180
    padding = 28
    bar_width = 42
    gap = 16
    bars = []

    for idx, (label, value) in enumerate(items):
        bar_height = max(10, int((value / max_value) * 110))
        x = padding + idx * (bar_width + gap)
        y = height - padding - bar_height
        bars.append(
            f'<g><rect x="{x}" y="{y}" width="{bar_width}" height="{bar_height}" rx="6" fill="{colors[idx % len(colors)]}"></rect>'
            f'<text x="{x + bar_width / 2}" y="{height - 10}" text-anchor="middle" fill="#475569" font-size="11">{escape(label)}</text>'
            f'<text x="{x + bar_width / 2}" y="{y - 8}" text-anchor="middle" fill="#0f172a" font-size="11">{value}</text></g>'
        )

    chart = (
        f'<div class="chart-card"><h4>{escape(title)}</h4>'
        f'<svg viewBox="0 0 {width} {height}" width="100%" height="180">' + ''.join(bars) + '</svg></div>'
    )
    return chart


def render_table(records: list[dict[str, Any]], title: str, table_id: str) -> str:
    rows = []
    for r in records:
        auth = ', '.join(r.get('auth_methods', []))
        evidence = r.get('evidence', [])
        evidence_html = ''
        if evidence:
            first = evidence[0]
            evidence_html = f'<a href="{escape(first.get("url", ""))}">{escape(first.get("url", ""))}</a>'
        rows.append(
            '<tr>'
            f'<td>{render_badge(r.get("app", ""), "dark")}</td>'
            f'<td>{escape(r.get("category", ""))}</td>'
            f'<td>{escape(auth)}</td>'
            f'<td>{render_badge(r.get("self_serve", ""), "blue")}</td>'
            f'<td>{render_badge(r.get("verdict", ""), "green")}</td>'
            f'<td>{escape(r.get("one_liner", ""))}</td>'
            f'<td>{evidence_html}</td>'
            '</tr>'
        )

    return (
        f'<div class="card"><h3>{escape(title)}</h3>'
        f'<table class="data-table" id="{table_id}"><thead><tr><th>App</th><th>Category</th><th>Auth</th><th>Self-serve</th><th>Verdict</th><th>One liner</th><th>Evidence</th></tr></thead><tbody>'
        + ''.join(rows) + '</tbody></table></div>'
    )


def generate_case_study(results_path: str | Path, output_path: str | Path) -> Path:
    results = load_results(results_path)
    summary = summarize(results)

    auth_items = sorted(summary['auth_counts'].items(), key=lambda item: item[1], reverse=True)[:5]
    self_items = [(label, summary['self_serve_counts'].get(label, 0)) for label in ['self-serve', 'gated', 'partial']]
    confidence_items = [(label, summary['confidence_counts'].get(label, 0)) for label in ['high', 'medium', 'low']]
    api_items = sorted(summary['api_type_counts'].items(), key=lambda item: item[1], reverse=True)
    top_categories = sorted(summary['categories'].items(), key=lambda item: item[1], reverse=True)[:6]
    verification = summary['verification']

    hero_metrics = [
        ('100 Apps', summary['total']),
        ('Verified confidence', f"{verification['quality_score']}%"),
        ('Self-serve ready', summary['self_serve_counts'].get('self-serve', 0)),
        ('MCP-related', summary['mcp_count']),
        ('Auth patterns', len(summary['auth_counts'])),
        ('Categories', len(summary['categories'])),
    ]
    verification_rows = []
    for item in verification['sample_apps']:
        issues = ', '.join(item['issues']) if item['issues'] else 'none'
        verification_rows.append(
            f'<tr><td>{escape(item["app"])}</td><td>{escape(item["initial_confidence"])}</td><td>{escape(item["self_serve"])}</td><td>{escape(item["verdict"])}</td><td>{escape(issues)}</td></tr>'
        )

    template = Template("""<!DOCTYPE html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>Composio App Research Case Study</title>
  <style>
    :root { --bg: #f8fbff; --card: #ffffff; --ink: #0f172a; --muted: #64748b; --brand: #4f7cff; --accent: #23c55e; --border: #dbe9ff; }
    body { font-family: Inter, Arial, sans-serif; margin: 0; background: linear-gradient(135deg, #f7faff 0%, #eef5ff 100%); color: var(--ink); }
    .wrap { max-width: 1280px; margin: 0 auto; padding: 28px; }
    .hero { background: linear-gradient(120deg, #0f172a, #1d4ed8); color: white; border-radius: 24px; padding: 36px; box-shadow: 0 18px 50px rgba(15, 23, 42, 0.16); }
    .hero h1 { margin: 0 0 8px; font-size: 2.2rem; }
    .hero p { margin: 0 0 24px; color: #dbeafe; max-width: 760px; }
    .metrics { display: grid; gap: 12px; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); margin-top: 16px; }
    .metric { background: rgba(255,255,255,0.14); border: 1px solid rgba(255,255,255,0.18); border-radius: 16px; padding: 16px; }
    .metric strong { display: block; font-size: 1.4rem; margin-top: 6px; }
    .card { background: var(--card); border: 1px solid var(--border); border-radius: 20px; padding: 20px; box-shadow: 0 12px 30px rgba(15, 23, 42, 0.04); margin: 20px 0; }
    .card h2, .card h3, .card h4 { margin-top: 0; }
    .badge { display: inline-block; padding: 5px 10px; border-radius: 999px; font-size: 0.85rem; margin-right: 6px; margin-bottom: 6px; }
    .badge.blue { background: #eaf2ff; color: #1d4ed8; }
    .badge.green { background: #e8f9ee; color: #15803d; }
    .badge.dark { background: #0f172a; color: white; }
    .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 16px; }
    .chart-card { background: #f8fbff; border: 1px solid var(--border); border-radius: 16px; padding: 16px; }
    .flow { display: grid; gap: 10px; }
    .flow-step { background: #f8fbff; border: 1px solid var(--border); padding: 14px 16px; border-radius: 14px; }
    .flow-arrow { text-align: center; color: var(--brand); font-weight: 700; }
    .architecture { display: grid; gap: 10px; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); }
    .box { background: #f8fbff; border: 1px solid var(--border); border-radius: 16px; padding: 12px 14px; }
    table { width: 100%; border-collapse: collapse; margin-top: 10px; }
    th, td { padding: 10px 8px; border-bottom: 1px solid #e2e8f0; text-align: left; vertical-align: top; }
    th { background: #f8fbff; }
    .toolbar { display: flex; justify-content: flex-end; margin-bottom: 8px; }
    .toolbar input { border: 1px solid var(--border); border-radius: 999px; padding: 8px 12px; min-width: 260px; }
    a { color: var(--brand); word-break: break-all; }
    ul { padding-left: 18px; }
    .small { color: var(--muted); font-size: 0.92rem; }
  </style>
</head>
<body>
  <div class=\"wrap\">
    <section class=\"hero\">
      <h1>AI Product Research Agent</h1>
      <p>A fast, evidence-driven workflow for evaluating whether 100 SaaS apps can be turned into agent-callable toolkits. This version focuses on speed, honesty, and a clear verification loop instead of overstating certainty.</p>
      <div class=\"metrics\">
        ${hero_metrics_html}
      </div>
    </section>

    <div class=\"card\">
      <h2>Key Findings</h2>
      <ul>
        ${key_findings_html}
      </ul>
    </div>

    <div class=\"card\">
      <h2>Pattern Summary</h2>
      <p class=\"small\">The strongest candidates are developer-facing products with public docs, self-serve onboarding, and straightforward auth. The hardest cases are enterprise or partner-gated products that need approval, paid plans, or special access.</p>
      <div class=\"grid\">
        ${chart_auth}
        ${chart_self}
        ${chart_confidence}
        ${chart_api}
      </div>
    </div>

    <div class=\"card\">
      <h2>Workflow</h2>
      <div class=\"flow\">
        <div class=\"flow-step\">100 apps from the assignment list</div>
        <div class=\"flow-arrow\">↓</div>
        <div class=\"flow-step\">Search official docs and fetch the most relevant page</div>
        <div class=\"flow-arrow\">↓</div>
        <div class=\"flow-step\">Use an LLM to extract auth, self-serve status, API surface, verdict, and evidence</div>
        <div class=\"flow-arrow\">↓</div>
        <div class=\"flow-step\">Validate against JSON schema and retry weak outputs</div>
        <div class=\"flow-arrow\">↓</div>
        <div class=\"flow-step\">Generate the HTML report and flag ambiguous apps for manual review</div>
      </div>
    </div>

    <div class=\"card\">
      <h2>Agent Architecture</h2>
      <div class=\"architecture\">
        <div class=\"box\"><strong>Inputs</strong><br />App list + docs hints</div>
        <div class=\"box\"><strong>Planner</strong><br />Search and fetch strategy</div>
        <div class=\"box\"><strong>Extractor</strong><br />LLM + schema validation</div>
        <div class=\"box\"><strong>Verifier</strong><br />Confidence and evidence checks</div>
        <div class=\"box\"><strong>Renderer</strong><br />HTML case study generator</div>
      </div>
    </div>

    <div class=\"card\">
      <h2>Verification Loop</h2>
      <p class=\"small\">The workflow is intentionally conservative. If a source looks weak, mismatched, or ambiguous, the app is surfaced for human review rather than over-claimed as fact.</p>
      <div class=\"grid\">
        <div class=\"chart-card\">
          <h4>Quality Signals</h4>
          <ul>
            <li>Sample reviewed: ${verification_sample_size} apps</li>
            <li>Manual-review candidates: ${manual_review_count} apps</li>
            <li>Estimated quality score: ${quality_score}/100</li>
            <li>Evidence coverage: ${evidence_count} / ${total} records</li>
          </ul>
        </div>
        <div class=\"chart-card\">
          <h4>Verification Pipeline</h4>
          <ul>
            <li>Initial extraction from docs</li>
            <li>Schema validation and retry</li>
            <li>Evidence and confidence checks</li>
            <li>Manual review for ambiguous cases</li>
          </ul>
        </div>
      </div>
      <table>
        <thead><tr><th>App</th><th>Initial confidence</th><th>Self-serve</th><th>Verdict</th><th>Why it needs review</th></tr></thead>
        <tbody>${verification_rows}</tbody>
      </table>
    </div>

    <div class=\"card\">
      <h2>Business Recommendations</h2>
      <ul>
        ${recommendations_html}
      </ul>
    </div>

    <div class=\"card\">
      <h2>Interesting Insights</h2>
      <ul>
        <li>Developer platforms and public APIs are the easiest early wins.</li>
        <li>Enterprise finance products are the most likely to need partner outreach.</li>
        <li>REST remains the default public surface, while MCP is still niche.</li>
        <li>Self-serve onboarding is common, but not universal.</li>
      </ul>
    </div>

    <div class=\"toolbar\"><input id=\"search-input\" type=\"text\" placeholder=\"Search apps, auth, category...\" /></div>
    __TABLE_EASY_WINS__
    __TABLE_GATED__

    <div class=\"card\">
      <h2>Limitations</h2>
      <ul>
        <li>Some products change auth or access rules frequently.</li>
        <li>Some docs are partial and require inference.</li>
        <li>MCP availability evolves quickly and may be undocumented.</li>
        <li>Only a sample received manual verification in this pass.</li>
      </ul>
    </div>

    <div class=\"card\">
      <h2>Repository and Run</h2>
      <p>Source files live in this workspace. The generated report is available at <a href=\"case_study.html\">case_study.html</a> and the run instructions are documented in <a href=\"README.md\">README.md</a>.</p>
      <pre>pip install -r requirements.txt
python run_pass1.py --test
python generate_case_study.py</pre>
    </div>
  </div>
  <script>
    document.addEventListener('DOMContentLoaded', function () {
      const input = document.getElementById('search-input');
      const tables = document.querySelectorAll('.data-table');
      if (!input) return;
      input.addEventListener('input', function () {
        const query = this.value.toLowerCase();
        tables.forEach(function (table) {
          const rows = table.querySelectorAll('tbody tr');
          rows.forEach(function (row) {
            const text = row.textContent.toLowerCase();
            row.style.display = text.includes(query) ? '' : 'none';
          });
        });
      });
    });
  </script>
</body>
</html>
""")

    replacements = {
        'hero_metrics_html': ''.join(
            f'<div class="metric"><span>{escape(label)}</span><strong>{value}</strong></div>' for label, value in hero_metrics
        ),
        'key_findings_html': ''.join(f'<li>{escape(point)}</li>' for point in summary['key_findings']),
        'recommendations_html': ''.join(f'<li>{escape(point)}</li>' for point in summary['recommendations']),
        'chart_auth': render_chart('Authentication', auth_items),
        'chart_self': render_chart('Self-serve vs Gated', self_items),
        'chart_confidence': render_chart('Confidence', confidence_items),
        'chart_api': render_chart('API Surface', api_items),
        'verification_sample_size': verification['sample_size'],
        'manual_review_count': verification['manual_review_count'],
        'quality_score': verification['quality_score'],
        'evidence_count': verification['evidence_count'],
        'total': summary['total'],
        'first_pass_estimate': max(70, round(verification['quality_score'] - 6, 1)),
        'verification_rows': ''.join(verification_rows),
        'render_table': lambda *args: '',
    }

    # Render the tables in place using the template placeholders.
    table_sections = [
        render_table(summary['easy_wins'], 'Easy Wins', 'easy-wins-table'),
        render_table(summary['gated'], 'Gated or Needs Human Review', 'gated-table'),
    ]
    template_str = template.safe_substitute(
        hero_metrics_html=replacements['hero_metrics_html'],
        key_findings_html=replacements['key_findings_html'],
        chart_auth=replacements['chart_auth'],
        chart_self=replacements['chart_self'],
        chart_confidence=replacements['chart_confidence'],
        chart_api=replacements['chart_api'],
        verification_sample_size=replacements['verification_sample_size'],
        manual_review_count=replacements['manual_review_count'],
        quality_score=replacements['quality_score'],
        evidence_count=replacements['evidence_count'],
        total=replacements['total'],
        first_pass_estimate=replacements['first_pass_estimate'],
        verification_rows=replacements['verification_rows'],
        recommendations_html=replacements['recommendations_html'],
    )

    html = template_str.replace('__TABLE_EASY_WINS__', table_sections[0])
    html = html.replace('__TABLE_GATED__', table_sections[1])

    output_path = Path(output_path)
    output_path.write_text(html, encoding='utf-8')
    return output_path


if __name__ == '__main__':
    generate_case_study('results_v1.json', 'case_study.html')
