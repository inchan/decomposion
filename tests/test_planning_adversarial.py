"""Frozen counterexamples for scoring mechanics, not live LLM quality tests.

Run as pytest, or directly to retain expected/observed JSON for a pinned revision.
The truth table is specified independently of evaluate(), before applying fixes.
"""
from copy import deepcopy
from itertools import product
import json

import pytest

from planning_eval.core import digest, evaluate, review_template
from planning_eval.selftest import fixture


VERDICTS = ('met', 'missing', 'contradicted', 'unresolved')
DEPENDENCY_CODES = {'BAD_DEPENDENCY', 'MISSING_DEPENDENCY'}


def expectation(met=0, pending=0, codes=(), valid=True):
    return {'dependency': {'met': met, 'total': 1, 'pending': pending},
            'codes': sorted(codes), 'structurally_valid': valid}


def scenarios():
    rows = []
    for before, after, topology in product(VERDICTS, VERDICTS, ('forward', 'reverse', 'absent')):
        case, plan, review = fixture()
        if topology == 'reverse':
            plan['edges'] = [{'from': 't', 'to': 'd', 'relation': 'precedes'}]
        elif topology == 'absent':
            plan['edges'] = []
        review['plan_sha256'] = digest(plan)
        for row, verdict in zip(review['judgments'], (before, after)):
            row['verdict'] = verdict
            if verdict in {'missing', 'unresolved'}:
                row['support'] = []
        # A known failure cannot become pending because the other label is unknown.
        if {before, after} & {'missing', 'contradicted'}:
            expected = expectation(codes=('MISSING_DEPENDENCY',))
        elif 'unresolved' in (before, after):
            expected = expectation(pending=1)
        elif topology == 'forward':
            expected = expectation(met=1)
        else:
            expected = expectation(codes=('BAD_DEPENDENCY' if topology == 'reverse' else 'MISSING_DEPENDENCY',))
        rows.append((f'verdicts/{before}/{after}/{topology}', case, plan, review, expected))

    for topology in ('ghost_bridge', 'cycle', 'transitive', 'influence_backlink'):
        case, plan, review = fixture()
        if topology in {'ghost_bridge', 'transitive'}:
            middle = 'ghost' if topology == 'ghost_bridge' else 'middle'
            plan['edges'] = [{'from': 'd', 'to': middle, 'relation': 'precedes'},
                             {'from': middle, 'to': 't', 'relation': 'precedes'}]
            if topology == 'transitive':
                plan['nodes'].append({'id': middle, 'kind': 'task', 'state': 'proposed',
                                      'text': 'Prepare the interface.', 'evidence': ['S']})
        else:
            plan['edges'].append({'from': 't', 'to': 'd',
                                  'relation': 'precedes' if topology == 'cycle' else 'affects'})
        review['plan_sha256'] = digest(plan)
        if topology == 'ghost_bridge':
            expected = expectation(codes=('MISSING_DEPENDENCY',), valid=False)
        elif topology == 'cycle':
            expected = expectation(codes=('BAD_DEPENDENCY',), valid=False)
        else:
            expected = expectation(met=1)
        rows.append((f'topology/{topology}', case, plan, review, expected))

    # Review findings require a usable identity even when every obligation is unresolved.
    identities = [('none', None), ('empty', ''), ('whitespace', ' \t'),
                  ('sentinel', 'UNASSIGNED'), ('padded_sentinel', ' UNASSIGNED '),
                  ('number', 7), ('list', ['reviewer'])]
    for mode, (label, identity) in product(('judgments', 'issues_only'), identities):
        case, plan, review = fixture()
        if mode == 'issues_only':
            review = review_template(case, plan)
            review['plan_issues'] = [{'code': 'UNDER_DECOMPOSITION', 'severity': 'major',
                                     'nodes': ['t'], 'reason': 'Controlled issue label, not a real semantic judgment.'}]
        review.update(reviewer_kind='fixture', reviewer=identity)
        rows.append((f'identity/{mode}/{label}', case, plan, review, {'error': 'ValueError'}))

    case, plan, review = fixture()
    review = review_template(case, plan)
    rows.append(('control/unassigned_template', case, plan, review, expectation(pending=1)))
    case, plan, review = fixture()
    review = review_template(case, plan)
    review.update(reviewer_kind='fixture', reviewer='test-reviewer')
    review['plan_issues'] = [{'code': 'UNDER_DECOMPOSITION', 'severity': 'major',
                             'nodes': ['t'], 'reason': 'Controlled issue label.'}]
    rows.append(('control/assigned_issues_only', case, plan, review, expectation(pending=1)))
    return rows


def observe(case, plan, review):
    try:
        result = evaluate(deepcopy(case), deepcopy(plan), deepcopy(review))
    except (ValueError, TypeError) as exc:
        return {'error': type(exc).__name__}
    return {'dependency': result['metrics']['dependency_coverage'],
            'codes': sorted({f['code'] for f in result['findings']} & DEPENDENCY_CODES),
            'structurally_valid': result['structurally_valid']}


@pytest.mark.parametrize('name,case,plan,review,expected', scenarios(), ids=[r[0] for r in scenarios()])
def test_scoring_counterexamples(name, case, plan, review, expected):
    assert observe(case, plan, review) == expected, name


if __name__ == '__main__':
    import argparse
    import hashlib
    from pathlib import Path
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--revision', required=True, help='Git revision or explicitly labeled local candidate')
    args = parser.parse_args()
    inputs = scenarios()
    results = [{'name': name, 'expected': expected, 'observed': observe(case, plan, review)}
               for name, case, plan, review, expected in inputs]
    for result in results:
        result['passed'] = result['expected'] == result['observed']
    root = Path(__file__).resolve().parents[1]
    receipt = {'kind': 'deterministic_adversarial_experiment', 'revision': args.revision,
               'model_calls': 0, 'model_quality_evaluated': False,
               'scenario_sha256': digest(inputs),
               'files_sha256': {p: hashlib.sha256((root / p).read_bytes()).hexdigest() for p in
                                ('planning_eval/core.py', 'planning_eval/selftest.py', 'tests/test_planning_adversarial.py')},
               'total': len(results), 'passed': sum(r['passed'] for r in results), 'results': results}
    with args.out.open('x', encoding='utf-8') as stream:
        json.dump(receipt, stream, ensure_ascii=False, indent=2)
        stream.write('\n')
    print(f"{receipt['passed']}/{receipt['total']} passed; {args.out}")
    raise SystemExit(0 if all(r['passed'] for r in results) else 1)
