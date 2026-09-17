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

## Output

The agent saves a plan, invokes `scripts/review.py` inside the installed skill,
and returns `plan.json`, `checks.json` and `review.md` in a **new output directory**.
The review contains decision/risk/unknown items first, a Mermaid prerequisite graph,
a domain-sorted table, and a relationship table for non-Mermaid viewers.
It is a basic review artifact, not the future interactive graph product or proof
of faster human review.

The helper reuses the current `planning_eval/core.py`, bundled by the installer.
It checks graph structure, evidence IDs, relative source paths, real line ranges
and optional source hashes. It does not judge semantic entailment or plan quality.
A graph can be structurally valid and still be a bad plan. The agent must self-review
its content and clearly label unresolved decisions. Model text is never executed.

## Versioning and removal

`INSTALL.json` records skill version 0.1.0 and SHA-256 for each installed file,
including the bundled validator. Pin the repository commit for exact reproduction.
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
