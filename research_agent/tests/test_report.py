import json
from pathlib import Path

from generate_case_study import generate_case_study


def test_generate_case_study_creates_html(tmp_path):
    results_path = Path('results_v1.json')
    output_path = tmp_path / 'case_study.html'

    generate_case_study(results_path, output_path)

    assert output_path.exists()
    html = output_path.read_text(encoding='utf-8')
    assert 'Composio App Research Case Study' in html
    assert 'Pattern Summary' in html
    assert 'Verification' in html
