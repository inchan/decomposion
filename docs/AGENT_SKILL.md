# Decomposion Skill — local subscription agent, cloud verification

## Product boundary

Decomposion is a **planning and visual-review skill**, not an agent orchestrator.
Your existing Codex/Claude Code session reads the repository and reasons using its
normal account/model. The skill does not copy login tokens, call paid APIs, install
models, start a daemon, or change application code. Your host's usual usage limits,
permissions and data handling still apply. No Remote Desktop Commander is needed.

We choose a shared Skill over an MCP server or automatic hooks for this iteration:
it is enough to provide the procedure plus deterministic checks, without an extra
service or hidden model billing. This does not claim multi-agent or MCP support.

## Recommended install: skills CLI

The repository uses the standard `skills/decomposion/SKILL.md` layout, so the open Agent Skills CLI can discover and install it directly from GitHub. The CLI supports both Codex and Claude Code.

```bash
# Optional: verify discovery first
npx skills add inchan/decomposion --list

# Install into the current project
npx skills add inchan/decomposion --skill decomposion -a codex -y
npx skills add inchan/decomposion --skill decomposion -a claude-code -y
```

Use the default project scope for the first human test. This keeps the experiment isolated to one repository. Start a fresh agent session after installation. `npx skills list` can be used to confirm the installed skill. The CLI also supports update/remove and global installs, but those are not required for the first test.

## Fallback install (Git and Python 3.11+, no package installation)

If Node/npx is unavailable, clone this repository at the revision you wish to test. From its root:

```bash
# Replace /absolute/path/to/project with the repository you plan to inspect.
python3 scripts/install_skill.py --agent codex --project /absolute/path/to/project
# Or for Claude Code:
python3 scripts/install_skill.py --agent claude --project /absolute/path/to/project
```

The installer copies the same skill into `.agents/skills/decomposion/` for Codex or
`.claude/skills/decomposion/` for Claude Code. Only that skill directory is created.
It never edits AGENTS.md, CLAUDE.md, global settings, hooks, credentials or existing
skills. Repeating the same installation is a no-op. A different/modified existing
skill is rejected rather than overwritten.

Start a fresh session in the target repository. Invoke explicitly:

```text
Codex:
$decomposion 문서 공유와 권한 회수를 추가하려고 합니다. 구현하지 말고 계획과 리뷰용 다이어그램을 만들어주세요.

Claude Code:
/decomposion 문서 공유와 권한 회수를 추가하려고 합니다. 구현하지 말고 계획과 리뷰용 다이어그램을 만들어주세요.
```

The host may request permission to create planning artifacts or run the bundled
Python helper. Do not disable its safety checks. The skill does not force a number
of model calls or guarantee the host will follow every instruction.

## 분해 강도 조절: `--granularity 1..5`

**Skill 0.2.0부터** 호출 문장에 분해 강도를 지정할 수 있습니다. 기본값은 3입니다.
설치 명령이나 Claude/Codex 실행파일의 옵션이 아니라 **스킬에 전달하는 요청**입니다.
`--granularity=N`도 허용하며 1–5 밖의 값이나 중복 지정은 사용하지 않습니다.

| 값 | 목적 | 문서 공유 기능의 분해 예시 (실험 결과 아님) |
|---|---|---|
| 1 | 러프한 개요 | 안전한 공유 / 공유 회수 / 감사 가능이라는 큰 목표 |
| 2 | 산출물 묶음 | 공유 정책, 공유·회수 기능, 접근 차단 검증 묶음 |
| 3 | 작업 단위 · 기본값 | 권한 검사 구현, 회수 처리, 검색 접근 검증을 각각 입력·산출물·완료 조건으로 정의 |
| 4 | 세부 단계 | 권한 평가, 각 접근 경로 연결, 실패 처리, 통합 검증으로 세분화 |
| 5 | 극세분화 | 대상 하나의 권한 변경, 그 결과 한 가지의 확인, 실패 경로 하나의 검증까지 |

```text
/decomposion --granularity 1 문서 공유 기능을 러프하게 분해해주세요. 구현은 하지 마세요.
/decomposion --granularity 3 문서 공유 기능을 작업 단위로 분해해주세요. 구현은 하지 마세요.
/decomposion --granularity 5 같은 범위에서 가능한 최소 검증 단위까지 쪼개주세요. 구현은 하지 마세요.
```

Codex에서는 `/decomposion` 대신 `$decomposion`을 사용합니다.
높은 값은 **분해 강도**이지 점수, 트리의 정확한 깊이, 화면 확대 정도 또는 에이전트 수가 아닙니다.
5가 3보다 빠르다는 보장은 없습니다. 인계·공유 맥락·수정 충돌·통합 비용은 별도로 검토합니다.
목표와 범위는 유지하며, 위험·결정·불확실성을 낮은 수준이라는 이유로 숨기지 않습니다.
빈 프로젝트에서 세밀한 구현 근거가 부족하면 조사할 작업과 그 한계를 남기고,
존재하지 않는 파일이나 인프라를 만들어내지 않습니다. 같은 수준이어도 가지마다 깊이는 다를 수 있습니다.

새 계획에는 `granularity`와 분해를 멈춘 이유인 `granularity_note`를 기록합니다.
에이전트는 선택한 값으로 계획을 만든 뒤, 같은 값으로 검증기를 호출합니다.

```bash
python3 "<skill-directory>/scripts/review.py" \
  --project "<project-root>" --plan "<plan.json>" --out "<new-review-directory>" \
  --granularity 3
```

이 helper 옵션은 **이미 만든 계획의 설정값이 맞는지 검사**할 뿐 작업을 새로 분해하지 않습니다.
설정값 불일치·잘못된 값은 출력 전 거부합니다. `checks.json`과 `review.md`에도 요청 수준을 표시하지만
실제 분해 품질은 `not_evaluated`로 남깁니다. 기존 계획에 필드가 없으면 옵션 없이 그대로 읽으며,
그 계획을 임의로 3단계라고 기록하지 않습니다. 수준 변경은 단순 재표기가 아니라 별도 수정안입니다.

1단계에서는 작업이 없는 개요도 허용하되 `OVERVIEW_ONLY`로 실행계획이 아님을 표시합니다.
아무 노드도 없는 계획은 모든 수준에서 오류입니다. 2–5단계의 작업 누락은 기존처럼 경고합니다.
이 버전은 수준별 의미 품질이나 병렬 수행 최적값을 측정한 버전이 아닙니다.

## Output

The agent saves a plan, invokes `scripts/review.py` inside the installed skill,
and returns `plan.json`, `checks.json` and `review.md` in a **new output directory**.
The review contains decision/risk/unknown items first, a Mermaid prerequisite graph,
a domain-sorted table, and a relationship table for non-Mermaid viewers.
It is a basic review artifact, not the future interactive graph product or proof
of faster human review.

The helper reuses `planning_eval/core.py` as a byte-identical bundled `scripts/_core.py`,
so a skills-CLI directory-only installation also works without the controller repo.
CI rejects drift between the canonical validator and its distribution copy; refresh
the latter with `cp planning_eval/core.py skills/decomposion/scripts/_core.py` after core changes.
It checks graph structure, evidence IDs, relative source paths, real line ranges
and optional source hashes. It does not judge semantic entailment or plan quality.
A graph can be structurally valid and still be a bad plan. The agent must self-review
its content and clearly label unresolved decisions. Model text is never executed.

## Versioning and removal

Skill metadata records version **0.2.0** (separate from the evaluation Python package).
The fallback Python installer also writes `INSTALL.json` with file SHA-256 hashes,
including the bundled validator. The skills CLI manages its own installation metadata. Pin the repository commit for exact reproduction.
No silent updates. To update, preserve/rename the installed `decomposion` directory
outside the host's skill-discovery folder, then run the installer from the desired
revision. To uninstall, remove only that installed skill directory. Keep experiment
outputs separate; old outputs must not be relabeled with a new version.

## Cloud pilot and limits

The `Cloud skill experiment` workflow executes a fixed public Qwen2.5-Coder-1.5B
Q4_K_M model with llama.cpp on a GitHub-hosted CPU. It requires no model/API secret
or connection to the user's machine. It makes six inference calls: three existing
Open WebUI evidence packets, each with plain instructions versus the Skill's planning
procedure. Same model, input evidence, temperature, seed and per-call output budget.
Raw prompts, provider responses, source/model pins and structural findings are saved
as Actions artifacts, including failures. No response repair or inference retries.

This is an **instruction-only cloud proxy**. It does not authenticate into Codex or
Claude, test skill discovery inside those apps, or establish subscription-model
quality. Both hosts' installer/helper paths are exercised separately by tests.
The small CPU model is a smoke-test instrument, not a recommended planning model.
Semantic grades and product superiority remain unmeasured; no winner is declared
from JSON validity or three cases. The existing baseline harness remains unchanged.

The workflow runs for same-repository PRs changing these integration files, or by
manual dispatch after merge. It has read-only repository permissions, no secrets,
no scheduled cadence, a 30-minute job cap and 14-day artifact retention. CPU minutes
and downloads are real resource use; it does not promise unlimited free compute.

## Primary format references checked during implementation

- Codex skills: https://developers.openai.com/codex/skills
- Claude Code skills: https://code.claude.com/docs/en/skills
- Model: https://huggingface.co/Qwen/Qwen2.5-Coder-1.5B-Instruct-GGUF
- Runtime release: https://github.com/ggml-org/llama.cpp/releases/tag/b10964
