# CI evaluation and environment verification

## Implemented jobs

`.github/workflows/eval.yml` runs on PRs, master pushes and manual dispatch.
It uses read-only repository permissions, pinned action commits, timeouts and
cancellation of superseded runs. There are no provider secrets or paid model calls.

`deterministic` (Linux, Python 3.11 and 3.13):

1. Install the actual editable package from `pyproject.toml`; run `pip check`.
2. Check the installed CLI and runtime diagnostics.
3. Validate both existing golden cases and the ten-prompt Open WebUI experiment manifest.
4. Run unit/regression tests and local-Git workspace integration tests.
5. Run the fixture baseline matrix; label its report **FIXTURE ONLY**.
6. Build a wheel, install it into a separate venv and import it from outside the source tree.
7. Retain JUnit diagnostics and fixture reports, including on failures.

`real-target-setup` (Linux, Python 3.11):

1. Execute the documented bootstrap script.
2. Fetch the real Open WebUI repository at the manifest's fixed commit.
3. Freeze a nine-session smoke queue and prepare one independent run checkout.
4. Confirm preparation/status without starting a model or the target application.

Network failure in the real-target job is reported as failure, not as a model
quality regression. Inspect logs before rerunning. Mergeability is not CI success.
Dev Container configuration is provided, but this workflow does not launch Codespaces.

## What is NOT measured

The fixture matrix does not compare real Plain/Structured/Decomposion model outputs.
The ten experiment prompts have no independently validated gold answers yet.
The current concept-ID scorer is not a semantic judge or a full dependency/graph validator.
Do not infer recall improvements, model costs, latency or correctness from green CI.

## Scoring correction in 0.2.0.dev0

Previously the expected abstention labels were passed in place of actual model
abstentions, and absence from produced concepts earned credit. An empty output could
therefore receive full abstention credit. The scorer now requires both:

- `expected_abstentions`: rubric labels;
- `abstained`: explicit output labels, supplied from `EvalOutput.abstentions`.

An asserted concept cannot simultaneously earn abstention credit. Nested
`must_not_invent` assertions now participate in forbidden scoring. Strategy inputs
are deep-copied; gold labels are not included. Empty matrices and duplicate case or
strategy identifiers fail instead of yielding an apparently valid report.

The forbidden metric is a hit fraction over known forbidden labels, not general
precision. Undefined metrics retain legacy neutral values; inspect support counts.
Old and new abstention reports are not comparable without rescoring old outputs.

## Improvement protocol

Reproduce a failure as a deterministic test before changing the implementation.
Preserve old artifacts; freeze new protocol/source versions in a new workspace.
Use `decomposion lab audit` to recheck record integrity. This does not evaluate the
truth of answers or protect against an adversary rewriting every stored hash.

Live model experiments are operator-run as documented in [LOCAL_LAB.md](LOCAL_LAB.md).
Keep model identity, settings and context fixed, record extra compute for multi-pass
runs, review evidence independently, and keep real held-out labels outside agent access.
No automatic nightly model workload is registered by this repository.
