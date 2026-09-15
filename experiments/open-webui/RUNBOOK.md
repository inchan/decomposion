# Open WebUI local experiment runbook

## Why this target

The experiment uses `open-webui/open-webui` because it is a large, active application with chat, files/knowledge, retrieval, users, permissions and administrative concerns. That makes cross-cutting change prompts difficult enough to expose differences between a one-shot answer and a structured reasoning pipeline.

The target is pinned to commit `0a7c15832fb30b1903753e83f81dc7d27e5b0944`. Do not test against moving `main`, otherwise results across days are not comparable.

## 1. Prepare Decomposion

From a clone of this repository:

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -e '.[dev]'
python -m pytest
bash scripts/setup_open_webui_experiment.sh
```

The bootstrap creates `.experiment-workspace/open-webui` and checks out the pinned target commit in detached-HEAD mode. It also creates isolated result directories.

## 2. Experimental controls

Use the same coding-agent product, model, thinking level and repository commit for all three strategies. Start a fresh session for every run. Disable or avoid persistent project memory that could reveal previous answers. Do not let one strategy read another strategy's output. Do not edit the target repository during this planning experiment.

Run 10 prompts x 3 strategies x 3 repeats = 90 sessions for the full experiment. Start with P01, P02 and P10 x 3 strategies x 1 repeat (9 sessions) as a smoke experiment before paying the full cost.

Record for every run: agent product/version, model, thinking level, prompt ID, strategy, start/end timestamps, target commit, raw answer and any tool/repository exploration notes available from the agent.

## 3. Strategy instructions

### A — plain

Give only the repository and the prompt's `change` text, plus:

> Inspect this repository and analyze the requested change. Identify impact, decisions, risks, implementation work and dependencies. Do not implement anything. Distinguish repository facts from assumptions.

Do not mention Decomposion, lenses or the expected answer.

### B — structured

Use the same change text, plus one strong one-shot instruction:

> Inspect the repository. Do not jump directly to tasks. In one response analyze: desired outcomes; affected domains/components; actors; data lifecycle; authorization/security; failure/recovery; migration/backward compatibility; operations; external systems; missing decisions; risks; dependencies; and unknowns. Cite repository evidence where possible and do not assert unsupported architecture. Then propose implementation work. Do not implement anything.

### C — decomposion

Use the Decomposion reasoning sequence, preferably through the local pipeline once implemented. Until a model adapter exists, run the passes explicitly in the agent session without showing it the golden expectations:

1. map repository-backed current context;
2. normalize goal/scope;
3. derive outcomes before tasks;
4. run multi-lens impact scan;
5. run a separate gap/omission critic;
6. identify unknown/contradicted claims;
7. derive typed dependencies and decisions;
8. synthesize tasks only after impact analysis;
9. critique granularity;
10. produce a final evidence-backed graph/list.

The important experimental distinction is multi-pass critique and intermediate state, not prettier formatting.

## 4. Saving output

For each session save the unedited final response to:

```text
.experiment-workspace/results/<strategy>/<prompt-id>/run-<n>/answer.md
```

Create `metadata.json` beside it. Example:

```json
{
  "experiment": "open-webui-change-impact-v1",
  "strategy": "structured",
  "prompt_id": "P01",
  "run": 1,
  "target_commit": "0a7c15832fb30b1903753e83f81dc7d27e5b0944",
  "agent": "codex-or-claude-code",
  "agent_version": "record-exact-version",
  "model": "record-exact-model",
  "thinking": "record-setting",
  "started_at": "ISO-8601",
  "ended_at": "ISO-8601"
}
```

Do not hand-edit answers before scoring.

## 5. Avoid contaminating the experiment

The person writing the strategy prompts should not tune strategy C after looking at blind-case answers. Golden expectations should be authored separately from model outputs where practical. Keep at least two prompts held out from prompt tuning. P10 is intentionally underspecified and should heavily penalize invented infrastructure.

## 6. Local vs cloud

Both are valid. The experiment does not require Open WebUI to run as an application; the coding agent only needs the repository checkout for static inspection. Therefore a normal Linux/macOS development machine, GitHub Codespaces, a disposable VM, or another cloud development environment can run it.

For cloud runs, pin the same target commit, persist only the result directory, use secrets through the cloud provider's secret store, and destroy the workspace after the experiment if desired. Do not put provider API keys in this repository or in result metadata.

Cloud and local results should not be mixed into one latency benchmark because hardware/network/tooling differ. Reasoning-quality scores can still be compared if model/agent/repository controls are identical.

## 7. Recommended first execution

Do not start with all 90 sessions. Run this 9-session smoke matrix first:

| Prompt | Plain | Structured | Decomposion |
|---|---|---|---|
| P01 document sharing/revocation | 1 | 1 | 1 |
| P02 account deletion/ownership | 1 | 1 | 1 |
| P10 underspecified audit mode | 1 | 1 | 1 |

Review whether the outputs are sufficiently different and whether repository evidence can be scored reliably. Only then run repeats and the remaining seven prompts.
