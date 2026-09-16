from copy import deepcopy
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
import json
import subprocess
import threading

import pytest

from planning_eval.cli import main
from planning_eval.core import digest, load_json
from planning_eval.experiment import (cases, complete, judge, load_packet, parse_object,
    prepare, report, response_text, run, validate_config)
from planning_eval.selftest import fixture


def config():
    return {'endpoint':'http://127.0.0.1:8000/v1/chat/completions','model':'fixture-not-a-model',
            'key_env':None,'request_options':{'max_tokens':256},'timeout_seconds':5,'environment':'local-fixture'}


@pytest.fixture
def packet(tmp_path):
    repo=tmp_path/'target'; repo.mkdir()
    subprocess.run(['git','init','--object-format=sha1',str(repo)],check=True,capture_output=True)
    (repo/'app.py').write_text('# fixture\n')
    subprocess.run(['git','-C',str(repo),'add','app.py'],check=True)
    subprocess.run(['git','-C',str(repo),'-c','user.name=Fixture','-c','user.email=fixture@example.invalid','commit','-m','fixture'],check=True,capture_output=True)
    def git(*args): return subprocess.check_output(['git','-C',str(repo),*args]).decode().strip()
    case,_,_=fixture(); case['target']['commit']=git('rev-parse','HEAD'); case['sources'][0]['blob']=git('rev-parse','HEAD:app.py')
    suite=[dict(deepcopy(case),id=f'fixture-{i}') for i in range(3)]
    path=tmp_path/'packet.json'; prepare(repo,path,suite)
    return repo,path,suite


def response(plan=None):
    if plan is None: _,plan,_=fixture()
    return {'model':'fixture-not-a-model','choices':[{'finish_reason':'stop','message':{'content':json.dumps(plan)}}],
            'usage':{'prompt_tokens':1,'completion_tokens':1,'total_tokens':2}}


def test_real_cases_and_cli_contract():
    suite=cases()
    assert len(suite)==3 and sum(len(c['obligations']) for c in suite)==36
    assert main(['check'])==0 and main(['selftest'])==0


def test_packet_has_source_evidence_not_gold_in_model_input(packet):
    _,path,_=packet
    data=load_packet(path)
    for item in data['payload']['items']:
        assert set(item['input'])=={'sources','change'}
        assert 'obligations' not in json.dumps(item['input'])
        assert item['input']['sources'][0]['text']=='# fixture'


def test_frozen_packet_reproducible_and_tampering_rejected(packet,tmp_path):
    repo,path,suite=packet
    other=tmp_path/'other.json'; prepare(repo,other,suite)
    assert load_packet(path)['sha256']==load_packet(other)['sha256']
    data=load_json(other); data['payload']['common']='different'; other.write_text(json.dumps(data))
    with pytest.raises(ValueError): load_packet(other)


@pytest.mark.parametrize('mutation',['dirty','wrong_blob','anchor','range'])
def test_source_integrity_and_no_overwriting(packet,tmp_path,mutation):
    repo,_,suite=packet
    if mutation=='dirty': (repo/'untracked.txt').write_text('preserve me')
    if mutation=='wrong_blob': suite[0]['sources'][0]['blob']='1'*40
    if mutation=='anchor': suite[0]['sources'][0]['anchor']='absent'
    if mutation=='range': suite[0]['sources'][0]['end']=20
    with pytest.raises(ValueError): prepare(repo,tmp_path/'fail.json',suite)
    assert (repo/'app.py').read_text()=='# fixture\n'


def test_dry_run_never_calls_provider_or_creates_results(packet,tmp_path):
    _,path,_=packet; output=tmp_path/'dry'
    def forbidden(*args): raise AssertionError('must not call')
    preview=run(path,config(),output,caller=forbidden)
    assert preview['planned_calls']==21 and preview['plans']==12
    assert not output.exists()
    with pytest.raises(ValueError): run(path,config(),output,max_calls=20,execute=True,caller=forbidden)


def test_full_pipeline_keeps_prior_artifacts_and_never_leaks_gold(packet,tmp_path):
    _,path,_=packet; output=tmp_path/'experiment'; prompts=[]
    def caller(cfg,prompt):
        assert '"obligations":' not in prompt and '"acceptance":' not in prompt
        assert '"author_review":' not in prompt
        prompts.append(prompt); return response()
    summary=run(path,config(),output,execute=True,caller=caller)
    assert summary['actual_calls']==21 and summary['recorded_plans']==12
    assert summary['provider']=='fixture' and not summary['quality_evaluated']
    assert sum('PRIOR WORK PRODUCTS' in p for p in prompts)==9
    text=report(output)
    assert 'unassigned:pending' in text and 'fixture' in text
    with pytest.raises(ValueError): run(path,config(),output,execute=True,caller=caller)
    trial=next(output.glob('trial-*'))
    (trial/'plan.json').write_text('{}')
    with pytest.raises(ValueError): report(output)


@pytest.mark.parametrize('failure',['truncated','bad_json','blank','timeout'])
def test_failures_are_retained_and_stop_spend(packet,tmp_path,failure):
    _,path,_=packet
    def caller(*args):
        result=response()
        if failure=='truncated': result['choices'][0]['finish_reason']='length'
        if failure=='bad_json': result['choices'][0]['message']['content']='not JSON'
        if failure=='blank': result['choices'][0]['message']['content']=' '
        if failure=='timeout': raise TimeoutError()
        return result
    out=tmp_path/failure
    result=run(path,config(),out,strategies=['plain'],execute=True,caller=caller)
    assert result['actual_calls']==1 and result['failed_plans']==1 and result['not_started_plans']==2
    assert (out/'trial-001'/'stage-1.input.txt').exists()
    assert 'FAILED' in report(out)


@pytest.mark.parametrize('change',[{'endpoint':'http://example.com/v1/chat/completions'},
 {'endpoint':'https://key:secret@example.com/v1/chat/completions'},
 {'api_key':'do-not-save'}, {'request_options':{}},
 {'request_options':{'max_tokens':1,'max_completion_tokens':1}},
 {'request_options':{'max_tokens':1,'tools':[]}}, {'timeout_seconds':0}])
def test_safe_config_boundaries(change):
    cfg=config(); cfg.update(change)
    with pytest.raises(ValueError): validate_config(cfg)


def test_optional_judge_labels_remain_uncalibrated_and_untrusted(packet,tmp_path):
    _,path,_=packet; root=tmp_path/'judged'
    run(path,config(),root,strategies=['plain'],execute=True,caller=lambda *_:response())
    def judge_caller(cfg,prompt):
        payload=json.loads(prompt.split('\n',1)[1]); review=payload['review_template']
        for row,node in zip(review['judgments'],payload['candidate']['nodes']):
            row.update(verdict='met',support=[{'node':node['id'],'quote':node['text']}],reason='Controlled label.')
        return response(review)
    assert not judge(root,config(),3,caller=judge_caller)['executed']
    result=judge(root,config(),3,execute=True,caller=judge_caller)
    assert not result['judge_calibrated'] and not result['quality_claim_allowed']
    assert 'llm:complete' in report(root)
    with pytest.raises(ValueError): judge(root,config(),3,execute=True,caller=judge_caller)


def test_actual_http_client_with_local_mock_not_a_model(monkeypatch):
    received=[]
    class Handler(BaseHTTPRequestHandler):
        def log_message(self,*args): pass
        def do_POST(self):
            received.append(json.loads(self.rfile.read(int(self.headers['Content-Length']))))
            content=json.dumps(response()).encode()
            self.send_response(200); self.send_header('Content-Type','application/json'); self.end_headers(); self.wfile.write(content)
    server=HTTPServer(('127.0.0.1',0),Handler)
    thread=threading.Thread(target=server.serve_forever,daemon=True); thread.start()
    try:
        cfg=config();cfg['endpoint']=f'http://127.0.0.1:{server.server_port}/v1/chat/completions'
        assert response_text(complete(cfg,'fixture request'))
        assert received[0]['messages']==[{'role':'user','content':'fixture request'}]
        assert received[0]['max_tokens']==256
    finally:
        server.shutdown();server.server_close();thread.join()


@pytest.mark.parametrize('bad',['{"a":1,"a":2}','{"a": NaN}', '[]','prefix {"nodes":[]}'])
def test_output_is_not_silently_repaired(bad):
    with pytest.raises(ValueError): parse_object(bad)


def test_report_refuses_changed_evaluator_fingerprint(packet, tmp_path, monkeypatch):
    _, path, _ = packet
    output = tmp_path / "frozen"
    run(path, config(), output, strategies=["plain"], execute=True, caller=lambda *_: response())
    monkeypatch.setattr("planning_eval.experiment.source_fingerprint", lambda: "changed")
    with pytest.raises(ValueError):
        report(output)
