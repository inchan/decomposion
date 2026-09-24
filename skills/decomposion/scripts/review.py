"""Offline plan validation and review export; the subscription agent does the reasoning."""
from __future__ import annotations

import argparse
import hashlib
import html
import importlib.util
import json
from pathlib import Path, PurePosixPath
import sys

sys.dont_write_bytecode = True
# Installer bundles the repository's existing validator, not a second implementation.
CORE = Path(__file__).with_name('_core.py')
if not CORE.is_file():
    CORE = Path(__file__).resolve().parents[3] / 'planning_eval' / 'core.py'
spec = importlib.util.spec_from_file_location('decomposion_core', CORE)
core = importlib.util.module_from_spec(spec)
spec.loader.exec_module(core)

GRANULARITY_LEVELS = {1: 'rough', 2: 'coarse', 3: 'normal', 4: 'fine', 5: 'micro'}

EXAMPLE = {
    'granularity': 3,
    'granularity_note': 'One policy decision and one independently verifiable retrieval change; no implementation stack is assumed.',
    'axis': 'Outcome, cross-checked against permissions and failure recovery.',
    'sources': [],
    'nodes': [
        {'id': 'goal', 'kind': 'outcome', 'state': 'proposed', 'text': 'Only authorized readers receive shared content.', 'evidence': ['request'], 'traces_to': [], 'domain': 'document'},
        {'id': 'policy', 'kind': 'decision', 'state': 'unknown', 'text': 'Decide which recipients and existing chats a revocation affects.', 'evidence': ['request'], 'traces_to': ['goal'], 'domain': 'permission'},
        {'id': 'check', 'kind': 'task', 'state': 'proposed', 'text': 'Enforce the chosen policy on retrieval. Accept when allowed and revoked-recipient tests agree with it.', 'evidence': ['request'], 'traces_to': ['goal', 'policy'], 'domain': 'retrieval'},
    ],
    'edges': [{'from': 'policy', 'to': 'check', 'relation': 'precedes'}],
}


def safe(value) -> str:
    """Escape Markdown/HTML control text. Mermaid uses generated IDs, never user syntax."""
    value = ' '.join(str(value).split())
    value = html.escape(value, quote=True)
    for c in ('|', '`', '[', ']', '*', '_', '\\'):
        value = value.replace(c, f'&#{ord(c)};')
    return value


def parse_level(value: str) -> int:
    """Normalize CLI names/numbers; stored plan metadata remains a strict integer."""
    for level, name in GRANULARITY_LEVELS.items():
        if value.lower() in (str(level), name):
            return level
    raise argparse.ArgumentTypeError('level must be 1..5 or rough/coarse/normal/fine/micro')


def granularity(plan: dict, expected: int | None = None) -> int | None:
    """Validate requested metadata only; never infer actual work size from a graph."""
    level = plan.get('granularity')
    if 'granularity' in plan and (type(level) is not int or level not in GRANULARITY_LEVELS):
        raise ValueError('granularity must be an integer from 1 to 5')
    if expected is not None:
        if type(expected) is not int or expected not in GRANULARITY_LEVELS:
            raise ValueError('expected granularity must be an integer from 1 to 5')
        if level != expected:
            raise ValueError('plan granularity is missing or differs from the requested level; re-plan, do not relabel')
    if 'granularity_note' in plan:
        core.text(plan['granularity_note'], 'granularity_note')
    return level


def inspect(plan: dict, project: Path) -> tuple[list[dict], list[dict]]:
    granularity(plan)
    findings = core.validate_plan(plan)
    sources = core.index(plan.get('sources', []), 'sources')
    if 'request' in sources:
        raise ValueError('request is a reserved evidence ID')
    snapshots = []
    for source in sources.values():
        rel = core.text(source.get('path'), 'source.path')
        parts = PurePosixPath(rel)
        if parts.is_absolute() or '..' in parts.parts or '.git' in parts.parts or '\\' in rel or ':' in rel:
            raise ValueError('source path must stay inside the project')
        path = project / rel
        if not path.resolve().is_relative_to(project) or any(p.is_symlink() for p in (path, *path.parents) if p != project.parent):
            raise ValueError('symlink evidence is not supported')
        if not path.is_file() or path.stat().st_size > 2_000_000:
            raise ValueError('source is missing, not regular, or too large')
        data = path.read_bytes()
        lines = data.decode('utf-8').splitlines()
        start, end = source.get('start'), source.get('end')
        if type(start) is not int or type(end) is not int or not 1 <= start <= end <= len(lines):
            raise ValueError('source line range is outside the file')
        sha = hashlib.sha256(data).hexdigest()
        if 'sha256' in source and source['sha256'] != sha:
            raise ValueError('source hash changed')
        snapshots.append({'id': source['id'], 'path': rel, 'start': start, 'end': end, 'sha256': sha})
    for node in plan['nodes']:
        for evidence in node.get('evidence', []):
            if evidence not in sources and evidence != 'request':
                findings.append({'code': 'UNKNOWN_EVIDENCE_ID', 'node': node['id'], 'evidence': evidence})
        if 'domain' in node:
            core.text(node['domain'], 'node.domain')
    return findings, snapshots


def review_warnings(plan: dict) -> list[dict]:
    # Delivery diagnostic, not a semantic score or a demand for arbitrary task counts.
    if plan.get('granularity') == 1:
        return [{'code': 'OVERVIEW_ONLY', 'detail': 'Level 1 intentionally shows the big picture, not an execution-ready task breakdown.'}]
    if not any(n['kind'] == 'task' for n in plan['nodes']):
        return [{'code': 'NO_TASKS', 'detail': 'No task nodes were supplied. Review whether this is only a requirements outline rather than a decomposed work plan.'}]
    return []


def markdown(plan: dict, findings: list[dict], warnings: list[dict]) -> str:
    nodes = plan['nodes']
    level = granularity(plan)
    level_text = f'{level} / {GRANULARITY_LEVELS[level]}' if level is not None else 'unspecified (legacy plan)'
    lines = ['# Decomposion plan review', '',
             f"Structural checks: {'INVALID' if findings else 'valid'}. Semantic quality: **not evaluated**.",
             '', 'Primary axis: ' + safe(plan.get('axis', 'Not specified')),
             '', 'Requested granularity: **' + level_text + '**. Actual granularity: **not evaluated**.',
             'Stopping rationale: ' + safe(plan.get('granularity_note', 'Not supplied')), '', '## Review first', '']
    for node in nodes:
        if node['kind'] in {'decision', 'risk', 'unknown'}:
            lines.append(f"- **{safe(node['id'])} · {node['kind']}**: {safe(node['text'])}")
    if not any(n['kind'] in {'decision', 'risk', 'unknown'} for n in nodes):
        lines.append('No review items were supplied; this is not evidence that no issues exist.')
    if warnings:
        lines += ['', '## Delivery cautions (not semantic grades)', '']
        lines += ['- **' + safe(w['code']) + '**: ' + safe(w['detail']) for w in warnings]
    if findings:
        lines += ['', '## Structural findings', '']
        lines += ['- ' + safe(json.dumps(f, ensure_ascii=False, sort_keys=True)) for f in findings]
    lines += ['', '## Dependency view', '', 'Only acceptance prerequisites are drawn. Other relationships are listed below.', '', '```mermaid', 'flowchart TD']
    ids = {n['id']: f'n{i}' for i, n in enumerate(nodes)}
    for n in nodes:
        # Whitelist label characters; full text remains in the escaped table.
        label = ''.join(c if c.isalnum() or c in ' .,:/()-' else ' ' for c in n['text'])
        label = ' '.join(label.split())[:64]
        lines.append(f'  {ids[n["id"]]}["{ids[n["id"]]} · {n["kind"]}: {label}"]')
    for e in plan['edges']:
        if e['relation'] == 'precedes' and e['from'] in ids and e['to'] in ids:
            lines.append(f"  {ids[e['from']]} --> {ids[e['to']]}")
    lines += ['```', '', '## Plan by domain', '', '| Diagram | ID | Domain | Kind / State | Plan / acceptance | Evidence |', '|---|---|---|---|---|---|']
    for n in sorted(nodes, key=lambda n: (n.get('domain', ''), n['id'])):
        lines.append('| ' + ' | '.join(safe(v) for v in (ids[n['id']], n['id'], n.get('domain', 'unspecified'), n['kind'] + ' / ' + n['state'], n['text'], ', '.join(n.get('evidence', [])))) + ' |')
    lines += ['', '## Relationships (text fallback)', '', '| From | Relation | To |', '|---|---|---|']
    lines += ['| ' + ' | '.join(safe(e[k]) for k in ('from', 'relation', 'to')) + ' |' for e in plan['edges']]
    lines += ['', '## Evidence index', '', '| Source ID | File | Lines |', '|---|---|---|',
              '| request | Explicit change request (not an architecture source) | N/A |']
    lines += ['| ' + ' | '.join(safe(v) for v in (s['id'], s['path'], f"{s['start']}-{s['end']}")) + ' |'
              for s in plan.get('sources', [])]
    lines += ['', 'Evidence paths/ranges are checked for existence; semantic entailment, completeness and business decisions remain review judgments.', '']
    return '\n'.join(lines)


def export(plan: dict, project: Path, out: Path, expected_granularity: int | None = None) -> dict:
    level = granularity(plan, expected_granularity)
    project = project.resolve(strict=True)
    if not project.is_dir():
        raise ValueError('project must be a directory')
    findings, sources = inspect(plan, project)
    # Check ancestors too: output must not be silently redirected through a symlink.
    if any(p.is_symlink() for p in (out, *out.parents)):
        raise ValueError('symlink output is not supported')
    out.mkdir(parents=True, exist_ok=False, mode=0o700)
    warnings = review_warnings(plan)
    receipt = {'schema_version': 1, 'plan_sha256': core.digest(plan),
               'validator_sha256': hashlib.sha256(CORE.read_bytes()).hexdigest(),
               'helper_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
               'skill_sha256': hashlib.sha256((Path(__file__).resolve().parents[1] / 'SKILL.md').read_bytes()).hexdigest(),
               'structurally_valid': not findings, 'semantic_quality': 'not_evaluated',
               'granularity': level, 'granularity_quality': 'not_evaluated',
               'sources': sources, 'findings': findings, 'review_warnings': warnings, 'model_calls': 0}
    for name, value in (('plan.json', plan), ('checks.json', receipt)):
        (out / name).write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n', encoding='utf-8')
    (out / 'review.md').write_text(markdown(plan, findings, warnings), encoding='utf-8')
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    parser.add_argument('--example', action='store_true')
    parser.add_argument('--project', type=Path)
    parser.add_argument('--plan', type=Path)
    parser.add_argument('--out', type=Path)
    parser.add_argument('--level', '-l', '--granularity', dest='granularity',
                        type=parse_level, action='append', metavar='LEVEL',
                        help='1..5 or rough/coarse/normal/fine/micro; checks --plan, does not split tasks')
    args = parser.parse_args()
    if args.granularity is not None and len(args.granularity) != 1:
        parser.error('--level / -l / --granularity may be supplied only once')
    args.granularity = args.granularity[0] if args.granularity else None
    if args.example:
        if args.granularity is not None:
            parser.error('--level checks --plan; cannot be used with --example')
        print(json.dumps(EXAMPLE, ensure_ascii=False, indent=2))
        return 0
    if not all((args.project, args.plan, args.out)):
        parser.error('--project, --plan and --out are required')
    try:
        if args.plan.stat().st_size > 512_000:
            raise ValueError('plan exceeds 512 KB limit')
        result = export(core.load_json(args.plan), args.project, args.out, args.granularity)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if result['structurally_valid'] else 2
    except (OSError, ValueError, TypeError, KeyError) as exc:
        print(f'Plan review failed: {exc}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
