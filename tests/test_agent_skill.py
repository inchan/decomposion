"""Portable installation and offline delivery tests, not claims of host/model accuracy."""
from copy import deepcopy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]


def module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


installer = module(ROOT / 'scripts/install_skill.py', 'skill_installer')
reviewer = module(ROOT / 'skills/decomposion/scripts/review.py', 'skill_reviewer')


@pytest.mark.parametrize('agent,folder', [('codex', '.agents'), ('claude', '.claude')])
def test_installed_helper_works_outside_controller_without_pip_or_keys(tmp_path, agent, folder):
    project = tmp_path / 'project with spaces'
    project.mkdir()
    first = installer.install(project, agent)
    assert first['status'] == 'installed'
    assert installer.install(project, agent)['status'] == 'unchanged'
    dest = project / folder / 'skills/decomposion'
    receipt = json.loads((dest / 'INSTALL.json').read_text())
    for name, expected in receipt['files_sha256'].items():
        assert hashlib.sha256((dest / name).read_bytes()).hexdigest() == expected
    assert (dest / 'scripts/_core.py').read_bytes() == (ROOT / 'planning_eval/core.py').read_bytes()
    env = {k: v for k, v in os.environ.items() if k not in {'PYTHONPATH', 'OPENAI_API_KEY', 'ANTHROPIC_API_KEY'}}
    helper = dest / 'scripts/review.py'
    example = subprocess.run([sys.executable, '-I', str(helper), '--example'], cwd=tmp_path, env=env, capture_output=True, text=True, check=True)
    plan = tmp_path / 'plan.json'
    plan.write_text(example.stdout)
    output = tmp_path / 'review'
    run = subprocess.run([sys.executable, '-I', str(helper), '--project', str(project), '--plan', str(plan), '--out', str(output)], cwd=tmp_path, env=env, capture_output=True, text=True)
    assert run.returncode == 0, run.stderr
    assert json.loads(run.stdout)['model_calls'] == 0
    assert '```mermaid' in (output / 'review.md').read_text()
    assert json.loads((output / 'checks.json').read_text())['semantic_quality'] == 'not_evaluated'
    again = subprocess.run([sys.executable, '-I', str(helper), '--project', str(project), '--plan', str(plan), '--out', str(output)], cwd=tmp_path, capture_output=True)
    assert again.returncode == 2
    assert installer.install(project, agent)['status'] == 'unchanged'


@pytest.mark.parametrize('change', ['edit', 'extra', 'symlink'])
def test_install_never_overwrites_user_customizations(tmp_path, change):
    dest = Path(installer.install(tmp_path, 'codex')['path'])
    if change == 'edit':
        (dest / 'SKILL.md').write_text('my custom skill')
    if change == 'extra':
        (dest / 'notes.txt').write_text('my notes')
    if change == 'symlink':
        (dest / 'linked').symlink_to(dest / 'SKILL.md')
    with pytest.raises(ValueError, match='existing skill differs'):
        installer.install(tmp_path, 'codex')


def test_install_rejects_symlinked_agent_directory(tmp_path):
    target = tmp_path / 'elsewhere'
    target.mkdir()
    (tmp_path / '.agents').symlink_to(target, target_is_directory=True)
    with pytest.raises(ValueError, match='symlink'):
        installer.install(tmp_path, 'codex')
    assert not list(target.iterdir())


@pytest.mark.parametrize('mutation', ['escape', 'absolute', 'symlink', 'missing', 'bad_range', 'wrong_hash', 'reserved'])
def test_bad_source_provenance_is_rejected_without_outputs(tmp_path, mutation):
    project = tmp_path / 'project'
    project.mkdir()
    source = project / 'code.py'
    source.write_text('first\nsecond\n')
    plan = deepcopy(reviewer.EXAMPLE)
    ref = {'id': 'S', 'path': 'code.py', 'start': 1, 'end': 2}
    plan['sources'] = [ref]
    if mutation == 'escape': ref['path'] = '../secret'
    if mutation == 'absolute': ref['path'] = str(source)
    if mutation == 'symlink':
        (project / 'link.py').symlink_to(source)
        ref['path'] = 'link.py'
    if mutation == 'missing': ref['path'] = 'missing.py'
    if mutation == 'bad_range': ref['end'] = 3
    if mutation == 'wrong_hash': ref['sha256'] = 'a' * 64
    if mutation == 'reserved': ref['id'] = 'request'
    with pytest.raises(ValueError):
        reviewer.export(plan, project, tmp_path / 'out')
    assert not (tmp_path / 'out').exists()


def test_valid_source_is_fingerprinted_but_not_called_semantically_correct(tmp_path):
    source = tmp_path / 'app.py'
    source.write_text('allow = True\n')
    plan = deepcopy(reviewer.EXAMPLE)
    plan['sources'] = [{'id': 'S', 'path': 'app.py', 'start': 1, 'end': 1}]
    plan['nodes'][2]['evidence'] = ['S']
    receipt = reviewer.export(plan, tmp_path, tmp_path / 'out')
    assert receipt['sources'][0]['sha256'] == hashlib.sha256(source.read_bytes()).hexdigest()
    assert receipt['structurally_valid']
    assert receipt['semantic_quality'] == 'not_evaluated'


@pytest.mark.parametrize('mutation,code', [('cycle','HARD_CYCLE'), ('dangling','INVALID_EDGE'), ('evidence','UNKNOWN_EVIDENCE_ID'), ('untraceable','UNTRACEABLE_PLAN_ITEM')])
def test_structural_defects_visible_in_visual_review(tmp_path, mutation, code):
    plan = deepcopy(reviewer.EXAMPLE)
    if mutation == 'cycle': plan['edges'].append({'from':'check','to':'policy','relation':'precedes'})
    if mutation == 'dangling': plan['edges'][0]['to'] = 'missing'
    if mutation == 'evidence': plan['nodes'][0]['evidence'] = ['NO_SOURCE']
    if mutation == 'untraceable': plan['nodes'][2].update(evidence=[], traces_to=[])
    result = reviewer.export(plan, tmp_path, tmp_path / 'out')
    assert not result['structurally_valid']
    assert code in {f['code'] for f in result['findings']}
    assert 'INVALID' in (tmp_path / 'out/review.md').read_text()


def test_generated_markdown_does_not_execute_or_inject_model_text(tmp_path):
    plan = deepcopy(reviewer.EXAMPLE)
    plan['nodes'][0]['text'] = '<script>alert(1)</script> ```\nclick x "javascript:x" | [link](x)'
    reviewer.export(plan, tmp_path, tmp_path / 'out')
    output = (tmp_path / 'out/review.md').read_text()
    diagram = output.split('```mermaid')[1].split('```')[0]
    assert '<script>' not in output
    assert '\nclick ' not in diagram and '<script>' not in diagram
    assert output.count('```') == 2
    assert '&#124;' in output


def test_output_symlink_is_rejected(tmp_path):
    actual = tmp_path / 'actual'
    actual.mkdir()
    link = tmp_path / 'link'
    link.symlink_to(actual, target_is_directory=True)
    with pytest.raises(ValueError, match='symlink'):
        reviewer.export(deepcopy(reviewer.EXAMPLE), tmp_path, link / 'report')
    assert not list(actual.iterdir())


def test_skill_contract_is_shared_and_has_no_host_specific_shell_interpolation():
    skill = (ROOT / 'skills/decomposion/SKILL.md').read_text()
    assert 'name: decomposion' in skill and 'description:' in skill
    assert f'version: "{installer.VERSION}"' in skill
    assert '$ARGUMENTS' not in skill and '!`' not in skill
    assert 'does not call an LLM' not in skill or 'API key' in skill
