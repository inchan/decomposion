from copy import deepcopy
import json

import pytest

from planning_eval.core import (digest, evaluate, has_cycle, load_json, reachable,
                                review_template, validate_case, validate_plan)
from planning_eval.selftest import fixture, selftest


def test_selftest_is_an_executable_contract():
    assert all(row['passed'] for row in selftest())


def test_no_labels_means_pending_not_success_or_zero_accuracy():
    case, plan, _ = fixture()
    score = evaluate(case, plan)
    assert score['review_status'] == 'pending'
    assert score['metrics']['critical_coverage'] == dict(met=0,total=2,pending=2,lower_bound=0.0,upper_bound=1.0)
    assert score['metrics']['minor_coverage']['lower_bound'] is None
    assert not score['quality_claim_allowed']


@pytest.mark.parametrize('mutation', ['duplicate_node','bad_kind','bad_state','empty_text','nonobject_node','duplicate_json'])
def test_malformed_plans_are_not_silently_scored(mutation,tmp_path):
    _, plan, _ = fixture()
    if mutation == 'duplicate_node': plan['nodes'].append(deepcopy(plan['nodes'][0]))
    if mutation == 'bad_kind': plan['nodes'][0]['kind'] = 'anything'
    if mutation == 'bad_state': plan['nodes'][0]['state'] = 'certain'
    if mutation == 'empty_text': plan['nodes'][0]['text'] = ' '
    if mutation == 'nonobject_node': plan['nodes'].append('bad')
    if mutation == 'duplicate_json':
        p=tmp_path/'duplicate.json'; p.write_text('{"nodes":[],"nodes":[],"edges":[]}')
        with pytest.raises(ValueError): load_json(p)
    else:
        with pytest.raises(ValueError): validate_plan(plan)


@pytest.mark.parametrize('mutation,code', [('dangling','INVALID_EDGE'),('self_edge','INVALID_EDGE'),('cycle','HARD_CYCLE'),('duplicate_edge','DUPLICATE_EDGE'),('trace','INVALID_TRACE'),('untraceable','UNTRACEABLE_PLAN_ITEM')])
def test_structural_mutations(mutation,code):
    _,plan,_=fixture()
    if mutation=='dangling': plan['edges'][0]['to']='missing'
    if mutation=='self_edge': plan['edges'][0]['to']='d'
    if mutation=='cycle': plan['edges'].append(dict(plan['edges'][0],**{'from':'t','to':'d'}))
    if mutation=='duplicate_edge': plan['edges'].append(deepcopy(plan['edges'][0]))
    if mutation=='trace': plan['nodes'][1]['traces_to']=['missing']
    if mutation=='untraceable': plan['nodes'][1].update(evidence=[],traces_to=[])
    assert code in {f['code'] for f in validate_plan(plan)}


def test_only_hard_precedence_is_used_for_cycles():
    _,plan,_=fixture()
    plan['edges'].append({'from':'t','to':'d','relation':'affects'})
    assert not validate_plan(plan)


def test_transitive_precedence_not_direct_edge_only():
    case,plan,review=fixture()
    plan['nodes'].append({'id':'middle','kind':'task','state':'proposed','text':'Prepare interface.','evidence':['S']})
    plan['edges']=[{'from':'d','to':'middle','relation':'precedes'},{'from':'middle','to':'t','relation':'precedes'}]
    review['plan_sha256']=digest(plan)
    score=evaluate(case,plan,review)
    assert score['metrics']['dependency_coverage']['met']==1
    assert 'middle' in score['unadjudicated_nodes']
    assert not score['findings']


@pytest.mark.parametrize('mutation', ['hash','reviewer','quote','kind','state','missing_row','extra_row','missing_reason'])
def test_invalid_review_cannot_inflate_scores(mutation):
    case,plan,review=fixture()
    if mutation=='hash': review['plan_sha256']='other'
    if mutation=='reviewer': review['reviewer_kind']='unassigned'
    if mutation=='quote': review['judgments'][0]['support'][0]['quote']='not in plan'
    if mutation=='kind': plan['nodes'][0]['kind']='task'; review['plan_sha256']=digest(plan)
    if mutation=='state': plan['nodes'][2]['state']='observed'; review['plan_sha256']=digest(plan)
    if mutation=='missing_row': review['judgments'].pop()
    if mutation=='extra_row': review['judgments'].append(deepcopy(review['judgments'][0]))
    if mutation=='missing_reason': review['judgments'][0]['reason']=''
    with pytest.raises(ValueError): evaluate(case,plan,review)


def test_silence_and_false_certainty_are_different_labels():
    case,plan,review=fixture()
    review['judgments'][2].update(verdict='missing',support=[],reason='No uncertainty was stated in this controlled fixture.')
    score=evaluate(case,plan,review)
    assert 'MISS_MAJOR' in {f['code'] for f in score['findings']}
    assert 'FALSE_CERTAINTY' not in {f['code'] for f in score['findings']}


def test_unlisted_findings_are_neutral_and_metrics_are_not_a_composite():
    case,plan,review=fixture()
    plan['nodes'].append({'id':'novel','kind':'risk','state':'inferred','text':'Novel concern.','evidence':['S']})
    review['plan_sha256']=digest(plan)
    result=evaluate(case,plan,review)
    assert result['unadjudicated_nodes']==['novel']
    assert not result['findings']
    assert 'score' not in result and 'accuracy' not in result


def test_unlisted_evidence_link_is_mechanically_invalid_not_semantic_judgment():
    case,plan,_=fixture()
    plan['nodes'][0]['evidence']=['invented-source']
    score=evaluate(case,plan)
    assert not score['structurally_valid']
    assert 'UNKNOWN_EVIDENCE_ID' in {f['code'] for f in score['findings']}
    assert 'semantic_evidence_support' in score['not_measured']


@pytest.mark.parametrize('mutation',['bad_pin','bad_range','path_escape','source_basis','severity','duplicate_obligation','ref_cycle','boolean_version'])
def test_invalid_references_rejected(mutation):
    case,_,_=fixture()
    if mutation=='bad_pin': case['target']['commit']='main'
    if mutation=='bad_range': case['sources'][0]['start']=0
    if mutation=='path_escape': case['sources'][0]['path']='../secret'
    if mutation=='source_basis': case['obligations'][0]['basis']=['not-supplied']
    if mutation=='severity': case['obligations'][0]['severity']='blocker'
    if mutation=='duplicate_obligation': case['obligations'].append(deepcopy(case['obligations'][0]))
    if mutation=='ref_cycle': case['dependencies'].append(dict(case['dependencies'][0],before='auth',after='policy'))
    if mutation=='boolean_version': case['schema_version']=True
    with pytest.raises(ValueError): validate_case(case)


def test_review_handles_arbitrary_paraphrase_without_keyword_or_id_matching():
    case,plan,review=fixture()
    plan['nodes'][1]['text']='Check the recipient can see this content before handing it to generation.'
    review['plan_sha256']=digest(plan)
    review['judgments'][1]['support'][0]['quote']=plan['nodes'][1]['text']
    assert evaluate(case,plan,review)['metrics']['critical_coverage']['met']==2
    # This verifies accepted external labels are counted, NOT that an automatic semantic judge is accurate.


def test_missing_matched_endpoint_cannot_hide_missing_dependency():
    case,plan,review=fixture()
    review['judgments'][0].update(verdict='missing',support=[],reason='Controlled omission.')
    result=evaluate(case,plan,review)
    assert result['metrics']['dependency_coverage']=={'met':0,'total':1,'pending':0}
    assert 'MISSING_DEPENDENCY' in {f['code'] for f in result['findings']}


def test_empty_plan_is_structurally_invalid():
    from planning_eval.core import validate_plan
    assert {"code": "EMPTY_PLAN"} in validate_plan({"nodes": [], "edges": []})
