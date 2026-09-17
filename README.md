# decomposion

Decomposion is a **planning and visual-review skill** for complex software changes. It helps a coding agent inspect the current repository, decompose the requested change, expose decisions/risks/unknowns, and produce an evidence-backed dependency view **before implementation**.

It is intentionally not an autonomous executor or project manager.

## Try it with your subscription coding agent

The public skill lives at `skills/decomposion/SKILL.md` and follows the standard Agent Skills layout. The `skills` CLI can discover skills from a public GitHub repository and install a selected skill for supported agents. citeturn0search3

From the project where you want to use Decomposion:

```bash
# Inspect what the repository publishes
npx skills add inchan/decomposion --list

# Codex
npx skills add inchan/decomposion --skill decomposion -a codex -y

# Claude Code
npx skills add inchan/decomposion --skill decomposion -a claude-code -y
```

Then start a **fresh** Codex or Claude Code session in that project and explicitly invoke the installed skill:

```text
Codex:
$decomposion 문서 공유 기능을 추가하려고 합니다. 구현하지 말고 계획과 리뷰를 만들어주세요.

Claude Code:
/decomposion 문서 공유 기능을 추가하려고 합니다. 구현하지 말고 계획과 리뷰를 만들어주세요.
```

The skill uses the model/account already provided by your coding-agent subscription. Decomposion does not ask you to copy an OpenAI/Anthropic API key or login token.

For a team/project install, keep the default project scope. If you intentionally want the skill available across projects, the `skills` CLI also supports `-g`; review the destination before choosing global scope. The CLI's default install can use symlinks; add `--copy` when you explicitly want independent copied files. citeturn0search3

### Alternative installer

If you do not have Node/npx, this repository also includes a conservative Python installer:

```bash
python3 scripts/install_skill.py --agent codex --project /absolute/path/to/project
python3 scripts/install_skill.py --agent claude --project /absolute/path/to/project
```

It requires Python 3.11+, creates only the project-local skill directory, records checksums, and refuses to overwrite a modified installation.

See [docs/AGENT_SKILL.md](docs/AGENT_SKILL.md) for output files, removal/update notes, limitations, and the cloud verification record.

## What you should expect

The agent should return planning artifacts rather than implementation:

- `plan.json` — typed outcomes/tasks/decisions/risks/unknowns and relationships;
- `checks.json` — deterministic structural/evidence checks;
- `review.md` — review-first Markdown with Mermaid dependency graph, domain grouping, and unresolved decisions.

Structural validity is **not** a semantic quality score. The first public cloud pilot validated installation, real-model failure capture, and the deterministic review path; it did not establish that Decomposion improves planning quality.

## Development / evaluation

The repository also contains the evaluation lab used to test planning behavior:

```bash
python3 scripts/bootstrap_lab.py
. .venv/bin/activate
decomposion doctor
python -m pytest
```

See [docs/LOCAL_LAB.md](docs/LOCAL_LAB.md) and [docs/PLANNING_EVAL_V1.md](docs/PLANNING_EVAL_V1.md).

## Product boundary

Decomposion currently focuses on:

`Request -> repository evidence -> outcomes -> decomposition -> impact cross-check -> critique -> dependencies -> tasks -> visual review`

Direct shell execution of the proposed work, autonomous orchestration, deployment, Jira/Linear replacement, and automatic code changes are outside the current product core.

## Repository map

- [skills/decomposion/SKILL.md](skills/decomposion/SKILL.md) — installable agent skill
- [docs/AGENT_SKILL.md](docs/AGENT_SKILL.md) — human installation/use guide
- [docs/PRODUCT.md](docs/PRODUCT.md) — positioning and product principles
- [docs/EVALUATION.md](docs/EVALUATION.md) — evaluation strategy
- [docs/GRAPH_SCHEMA.md](docs/GRAPH_SCHEMA.md) — working graph/IR concepts
- [docs/LOCAL_LAB.md](docs/LOCAL_LAB.md) — reproducible experiment lab

## Development standard

Prefer a smaller mechanism that can be tested over a larger architecture that merely looks complete. Reasoning changes should be evaluated against development, blind, and adversarial cases. Prefer explicit provenance over unsupported certainty and `unknown` over fabricated confidence.
