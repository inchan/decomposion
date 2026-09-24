"""Settings/packaging checks, not evidence of achieved decomposition or agent efficiency."""
from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / 'skills/decomposion'
spec = importlib.util.spec_from_file_location('granularity_reviewer', SKILL / 'scripts/review.py')
reviewer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(reviewer)


@pytest.mark.parametrize('level', range(1, 6))
def test_requested_level_roundtrip_is_not_a_quality_grade(tmp_path, level):
    plan = deepcopy(reviewer.EXAMPLE)
    # Synthetic metadata only; this test does NOT claim identical tasks meet each level.
    plan['granularity'] = level
    original = deepcopy(plan)
    out = tmp_path / 'review'
    result = reviewer.export(plan, tmp_path, out, expected_granularity=level)
    assert plan == original
    assert json.loads((out / 'plan.json').read_text()) == original
    assert result['granularity'] == level
    assert result['granularity_quality'] == result['semantic_quality'] == 'not_evaluated'
    assert result['model_calls'] == 0
    assert f'{level} / {reviewer.GRANULARITY_LEVELS[level]}' in (out / 'review.md').read_text()


@pytest.mark.parametrize('bad', [0, 6, -1, True, False, None, '3', 3.0, [], {}])
def test_invalid_level_rejected_before_output(tmp_path, bad):
    plan = dict(reviewer.EXAMPLE, granularity=bad)
    with pytest.raises(ValueError, match='granularity'):
        reviewer.export(plan, tmp_path, tmp_path / 'out')
    assert not (tmp_path / 'out').exists()


def test_legacy_is_not_silently_relabeled_with_default(tmp_path):
    plan = deepcopy(reviewer.EXAMPLE)
    del plan['granularity']
    del plan['granularity_note']
    result = reviewer.export(plan, tmp_path, tmp_path / 'legacy')
    assert result['granularity'] is None
    assert 'granularity' not in json.loads((tmp_path / 'legacy/plan.json').read_text())
    assert 'unspecified (legacy plan)' in (tmp_path / 'legacy/review.md').read_text()
    with pytest.raises(ValueError, match='missing or differs'):
        reviewer.export(plan, tmp_path, tmp_path / 'mislabeled', expected_granularity=3)
    assert not (tmp_path / 'mislabeled').exists()


@pytest.mark.parametrize('expected', [1, 5, 0, True, 3.0, '3'])
def test_mismatched_or_invalid_expected_level_rejected(tmp_path, expected):
    with pytest.raises(ValueError, match='granularity'):
        reviewer.export(deepcopy(reviewer.EXAMPLE), tmp_path, tmp_path / 'out', expected_granularity=expected)
    assert not (tmp_path / 'out').exists()


def test_overview_and_empty_graph_are_not_confused(tmp_path):
    plan = deepcopy(reviewer.EXAMPLE)
    plan.update(granularity=1, nodes=[plan['nodes'][0]], edges=[])
    result = reviewer.export(plan, tmp_path, tmp_path / 'overview')
    assert result['structurally_valid']
    assert [w['code'] for w in result['review_warnings']] == ['OVERVIEW_ONLY']
    plan['nodes'] = []
    result = reviewer.export(plan, tmp_path, tmp_path / 'empty')
    assert not result['structurally_valid']
    assert 'EMPTY_PLAN' in {f['code'] for f in result['findings']}


def test_stop_rationale_is_escaped(tmp_path):
    plan = dict(reviewer.EXAMPLE, granularity_note='<script>alert(1)</script> ` | [x]')
    reviewer.export(plan, tmp_path, tmp_path / 'out')
    assert '<script>' not in (tmp_path / 'out/review.md').read_text()
    plan['granularity_note'] = '  '
    with pytest.raises(ValueError, match='granularity_note'):
        reviewer.export(plan, tmp_path, tmp_path / 'bad-note')
    assert not (tmp_path / 'bad-note').exists()


def test_cli_enforces_setting_without_redecomposing(tmp_path):
    plan = tmp_path / 'plan.json'
    plan.write_text(json.dumps(reviewer.EXAMPLE))
    command = [sys.executable, '-I', str(SKILL / 'scripts/review.py'), '--project', str(tmp_path), '--plan', str(plan)]
    result = subprocess.run(command + ['--out', str(tmp_path / 'ok'), '--granularity', '3'], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    for value in ('1', '0', '5', 'x'):
        out = tmp_path / ('bad-' + value)
        result = subprocess.run(command + ['--out', str(out), '--granularity', value], capture_output=True, text=True)
        assert result.returncode == 2
        assert not out.exists()
    repeated = subprocess.run(command + ['--out', str(tmp_path / 'repeated'), '--granularity', '3', '--granularity', '3'], capture_output=True)
    assert repeated.returncode == 2
    assert not (tmp_path / 'repeated').exists()
    example = subprocess.run([sys.executable, '-I', str(SKILL / 'scripts/review.py'), '--example', '--granularity', '5'], capture_output=True)
    assert example.returncode == 2  # no relabeling the task example as an atomic plan


def test_skill_only_distribution_is_self_contained_and_validator_cannot_drift(tmp_path):
    # skills CLI distributes this directory, not planning_eval/ or the custom installer.
    assert (SKILL / 'scripts/_core.py').read_bytes() == (ROOT / 'planning_eval/core.py').read_bytes()
    destination = tmp_path / 'project/.agents/skills/decomposion'
    shutil.copytree(SKILL, destination)
    helper = destination / 'scripts/review.py'
    example = subprocess.run([sys.executable, '-I', str(helper), '--example'], cwd=tmp_path, capture_output=True, text=True)
    assert example.returncode == 0, example.stderr
    plan = tmp_path / 'example.json'
    plan.write_text(example.stdout)
    run = subprocess.run([sys.executable, '-I', str(helper), '--project', str(tmp_path), '--plan', str(plan),
                          '--out', str(tmp_path / 'delivery'), '--granularity', '3'],
                         cwd=tmp_path, capture_output=True, text=True)
    assert run.returncode == 0, run.stderr
    assert json.loads(run.stdout)['granularity'] == 3


def test_cloud_proxy_includes_the_granularity_instructions():
    skill = (SKILL / 'SKILL.md').read_text()
    # Match the existing cloud runner's extraction boundary.
    procedure = skill.split('## Planning procedure\n', 1)[1].split('## Plan contract', 1)[0]
    assert '--granularity N' in procedure
    for level in reviewer.GRANULARITY_LEVELS:
        assert f'| {level} |' in procedure
