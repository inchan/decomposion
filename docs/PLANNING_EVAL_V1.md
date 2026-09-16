# Planning Eval v1

Planning Eval v1 answers one question: **does a generated plan cover the important work and reasoning without inventing facts, and does it expose the dependencies and uncertainty a reviewer needs?**

It does not evaluate visual UX, execution, coding quality, latency, cost, or agent autonomy.

## What v1 measures

- **Coverage**: required outcomes, tasks, decisions, risks, and impacts are present.
- **Correctness**: claims are compatible with supplied evidence.
- **Dependency**: required ordering/decision relationships are present and not reversed.
- **Uncertainty**: unknown facts stay unknown; silence is not abstention.
- **Granularity**: only review-critical grouping/splitting constraints are judged. Exact task counts are never canonical.

## Severity

- `critical`: omission/error can invalidate the plan or cause serious security, data, or correctness failure.
- `major`: materially reduces completeness or executability.
- `minor`: useful improvement with limited effect on core validity.

Critical misses are reported separately in v1. They do not become a hard pass/fail gate until baseline data justifies a threshold.

## Reference model

A reference case is a **constraint graph, not a canonical task list**. It contains only obligations that matter to review:

```yaml
nodes:
  - id: permission_policy
    kind: decision
    concept: permission policy
    severity: critical
    aliases: []
  - id: retrieval_authorization
    kind: task
    concept: retrieval authorization
    severity: critical
    aliases: [authorize retrieval against document permissions]
edges:
  - from: permission_policy
    to: retrieval_authorization
    relation: requires_decision
    severity: critical
unknowns:
  - concept: cache existence
    severity: major
```

Candidate plans may group or split work differently if the required obligation remains explicit enough to review.

## Error taxonomy

Keep the first version small:

- `MISS_CRITICAL`, `MISS_MAJOR`, `MISS_MINOR`
- `MISSING_DECISION`, `MISSING_RISK`
- `FALSE_CERTAINTY`
- `BAD_DEPENDENCY`, `MISSING_DEPENDENCY`
- `UNDER_DECOMPOSITION`, `OVER_DECOMPOSITION` (human/semantic review only in v1)

Do not add a new error code until a real reference case requires it.

## Evaluation layers

1. **Deterministic**: schema/invariant checks and controlled exact/alias self-tests.
2. **Semantic**: future versioned matcher for paraphrases; it must be allowed to abstain.
3. **Human**: ambiguous equivalence, granularity, contested dependencies, and novel findings.

Novel findings are neither rewarded nor penalized until adjudicated.

## Scorecard

Report dimensions separately; no composite score in v1:

- critical / major / minor coverage
- decision and risk recall
- required dependency recall and bad dependency count
- false-certainty count
- unresolved novel findings

## Baselines

Freeze the same context/model for:

- `plain`: direct planning request
- `strong_one_shot`: one carefully structured prompt
- `decomposion`: staged method under test

## Versioning

An eval version freezes dataset inputs, reference constraints, scoring semantics, semantic-judge configuration (when introduced), and baseline prompts. Changing one creates a new eval version.

## Step 1 gate

Before Step 2, controlled tests must prove at least:

- critical omission is detected;
- explicit alias is accepted;
- unknown promoted to fact is detected;
- silence does not count as abstention;
- reversed required dependency is detected;
- novel findings are left unadjudicated.

## Anti-overengineering rule

**No new module, schema field, metric, document, or abstraction unless a concrete reference case or evaluator failure requires it.** At every step review, ask what can be deleted or merged before asking what can be added.

Defaults for Step 2: critical coverage must be explicit; granularity uses only `must-separate` style constraints when needed; critical misses remain separately visible; novel findings require adjudication; the first three cases are development cases and do not prove generalization.
