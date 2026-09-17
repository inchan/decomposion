"""Six real, bounded CPU model calls. A skill-instruction proxy, not a subscription-host benchmark."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import random
import time

from planning_eval.core import digest, evaluate
from planning_eval.experiment import complete, load_packet, parse_object, response_text


def experiment(packet_path: Path, skill_path: Path, out: Path) -> dict:
    packet = load_packet(packet_path)
    items = packet['payload']['items']
    if {i['case']['id'] for i in items} != {'P01', 'P02', 'P10'}:
        raise ValueError('this bounded pilot is restricted to P01, P02 and P10')
    skill = skill_path.read_text(encoding='utf-8')
    procedure = skill.split('## Planning procedure\n', 1)[1].split('## Plan contract', 1)[0]
    arms = {'plain': 'Analyze this change and propose a reviewable plan.', 'skill': procedure}
    config = {'endpoint': 'http://127.0.0.1:8080/v1/chat/completions', 'model': 'qwen-coder-smoke',
              'request_options': {'temperature': 0, 'seed': 17, 'max_tokens': 2048},
              'timeout_seconds': 600, 'environment': 'github-hosted-cpu'}
    out.mkdir(parents=True, exist_ok=False)
    queue = [(i, a) for i in range(len(items)) for a in arms]
    random.Random(17).shuffle(queue)
    receipt = {'kind': 'live_cloud_instruction_proxy', 'model': 'Qwen2.5-Coder-1.5B-Instruct Q4_K_M',
               'config': config, 'git_sha': os.environ.get('GITHUB_SHA', 'unknown'),
               'run_id': os.environ.get('GITHUB_RUN_ID', 'unknown'),
               'packet_sha256': packet['sha256'], 'skill_sha256': hashlib.sha256(skill.encode()).hexdigest(),
               'python': platform.python_version(), 'platform': platform.platform(),
               'subscription_host_executed': False, 'semantic_quality_evaluated': False,
               'grammar_constrained': False, 'retries': 0, 'queue': queue, 'trials': []}
    for idx, (i, arm) in enumerate(queue, 1):
        item = items[i]
        directory = out / f'{idx:02d}-{item["case"]["id"]}-{arm}'
        directory.mkdir()
        prompt = (packet['payload']['common'] + '\n' + arms[arm] + '\nINPUT DATA:\n' +
                  json.dumps(item['input'], ensure_ascii=False) + '\n' + packet['payload']['output_contract'] +
                  '\nKeep the complete JSON within 2048 output tokens. Do not request tools.')
        (directory / 'prompt.txt').write_text(prompt, encoding='utf-8')
        row = {'case': item['case']['id'], 'arm': arm, 'json_valid': False, 'structure_valid': False}
        start = time.monotonic()
        try:
            response = complete(config, prompt)
            (directory / 'response.json').write_text(json.dumps(response, ensure_ascii=False, indent=2), encoding='utf-8')
            row['finish_reason'] = response.get('choices', [{}])[0].get('finish_reason')
            row['usage'] = response.get('usage')
            answer = response_text(response)
            (directory / 'answer.txt').write_text(answer, encoding='utf-8')
            plan = parse_object(answer)
            row['json_valid'] = True
            (directory / 'plan.json').write_text(json.dumps(plan, ensure_ascii=False, indent=2), encoding='utf-8')
            score = evaluate(item['case'], plan)
            row.update(structure_valid=score['structurally_valid'], findings=score['findings'],
                       nodes=len(plan['nodes']), edges=len(plan['edges']), review_status=score['review_status'])
        except (ValueError, TypeError, KeyError) as exc:
            # Schema/parse failures are experiment observations, not repaired or retried.
            row['error'] = f'{type(exc).__name__}: {exc}'
        finally:
            row['seconds'] = time.monotonic() - start
            row['artifacts_sha256'] = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in directory.iterdir() if p.is_file()}
            receipt['trials'].append(row)
            (out / 'receipt.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2), encoding='utf-8')
            print(json.dumps(row, ensure_ascii=False), flush=True)
    receipt['actual_model_calls'] = len(queue)
    receipt['arms'] = {a: {'trials': len([r for r in receipt['trials'] if r['arm'] == a]),
                           'json_valid': sum(r['json_valid'] for r in receipt['trials'] if r['arm'] == a),
                           'structure_valid': sum(r['structure_valid'] for r in receipt['trials'] if r['arm'] == a)} for a in arms}
    (out / 'receipt.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2), encoding='utf-8')
    return receipt


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--packet', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--skill', type=Path, default=Path('skills/decomposion/SKILL.md'))
    args = parser.parse_args()
    print(json.dumps(experiment(args.packet, args.skill, args.out), ensure_ascii=False, indent=2))
