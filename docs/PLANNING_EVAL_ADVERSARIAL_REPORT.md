# Planning Eval: counterexample experiment (2026-09-17)

## Scope and result

This is an executed **deterministic scoring experiment**, not a live model comparison.
No model endpoint/credentials or coding-agent executable was available in the authoring
runtime; model calls: **0**. No model quality, semantic judge reliability or product
superiority is claimed. Remote execution requires an authorized connection.

Baseline: `7846f3dd8bfa0ed6a1fddfd6ecd992c6dcf705fb` (merged PR #6).
The retrieved `core.py`, `selftest.py`, and original core test module were checked
against their Git blob hashes before local execution. Only the scoring core is changed.

The 68 counterexamples and expected results were frozen **before** patching the scorer.
They combine synthetic review verdicts, graph mutations and reviewer metadata; they
are not 68 independent real-world planning tasks. The oracle specifies accounting
semantics, not natural-language correctness. Both runs used identical scenarios:

`f3133b9a85c4d37a4937257e47d1b75d0450e1eb4270eb8cd9f24904ca763be5`

| Test family | Cases | Baseline pass | Patched pass |
|---|---:|---:|---:|
| 4 x 4 endpoint verdicts x 3 graph directions | 48 | 36 | 48 |
| Dangling bridge / cycle / valid transitive / influence backlink | 4 | 2 | 4 |
| Invalid reviewer identities in judgments and issues-only reviews | 14 | 3 | 14 |
| Valid pending-template and assigned-issues controls | 2 | 2 | 2 |
| Total | 68 | 43 | 68 |

**25 failing variants correspond to four defect types, not 25 independent bugs.**
This is a targeted regression set, not an unbiased accuracy estimate or proof of
complete evaluator correctness. Existing core regression tests also passed locally:
38 existing + 68 new = 106 pytest cases; the 10 legacy self-checks remained passing.
Full repository, packaging and real-source integration results belong to the PR CI.

## Findings and minimal corrections

1. **Known failure hidden by pending review (12 variants).** A `missing` or
   `contradicted` prerequisite combined with an `unresolved` endpoint was reported
   as pending, with no dependency failure. A known unsatisfied endpoint now yields
   `MISSING_DEPENDENCY`; remaining obligation judgments may still be pending.
2. **Absent-node bridge earned credit (1 variant).** `d -> ghost -> t` was already
   structurally INVALID, yet earned dependency credit. Only edges between existing,
   distinct candidate nodes now participate in precedence reachability.
3. **Contradictory precedence earned credit (1 variant).** `d -> t -> d` was already
   flagged HARD_CYCLE, yet fulfilled the prerequisite. Reverse reachability now
   prevents credit even when forward reachability also exists. Legitimate indirect
   paths still count, and an `affects` backlink does not become precedence.
4. **Unusable reviewer identity accepted (11 variants).** Whitespace, numeric or
   sentinel identities could support verdicts; issues-only reviews bypassed identity
   validation; a list identity raised TypeError. Both paths now require a nonblank
   string other than stripped `UNASSIGNED` and reject invalid identities with ValueError.

## Reproduction

On the patched checkout:

```bash
python -m pytest tests/test_planning_eval.py tests/test_planning_adversarial.py
PYTHONPATH=. python tests/test_planning_adversarial.py \
  --out /tmp/adversarial-after.json --revision "$(git rev-parse HEAD)"
```

To reproduce the before/after result without modifying an existing experiment:

```bash
ROOT="$PWD"
BEFORE="$(mktemp -d)"
git archive 7846f3dd8bfa0ed6a1fddfd6ecd992c6dcf705fb | tar -x -C "$BEFORE"
cp tests/test_planning_adversarial.py "$BEFORE/tests/"
(cd "$BEFORE" && PYTHONPATH=. python tests/test_planning_adversarial.py \
  --out before.json --revision 7846f3dd8bfa0ed6a1fddfd6ecd992c6dcf705fb)
# Expected nonzero exit on baseline: 43/68 pass. Output remains in $BEFORE/before.json.
```

The JSON receipts contain all scenario names, expected/observed results, the scenario
hash and source hashes. They refuse overwrite. No provider calls or new dependencies
are introduced. The new pytest file is picked up by the existing CI automatically.

## Self-review / next gate

Keep this change to one core patch, one substantive regression module and this report.
Do not add an execution framework, service, UI, database or automatic model retries.
Do not change the reference cases or baseline prompts to make scores look better.
Old runs must retain their original evaluator; the existing source fingerprint refuses
to silently re-score them under changed code. This report does not rewrite any old run.

The actual next quality experiment remains 3 cases x 4 strategies x 1 repeat, with a
maximum of 21 planner requests, followed by at most 12 explicitly requested judge
requests. It is **not run** by these tests. Stop on the first failure, preserve outputs,
and do not label an uncalibrated review as ground truth. The current chat already saw
reference material, so generating purported blind baseline answers in this same
conversation would not substitute for isolated model calls.
