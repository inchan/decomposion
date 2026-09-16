# Planning Eval v1

## Purpose

Planning Eval v1 measures the quality of a plan produced from a fixed project context and change request. It does not evaluate visual presentation, execution, coding quality, or agent autonomy.

The primary question is: **does the plan cover the important work and reasoning, avoid unsupported claims, and express useful dependencies and uncertainty?**

## Frozen evaluation axes

1. **Coverage** — important outcomes, work, decisions, risks, and impacts are present.
2. **Correctness** — assertions and proposed work are compatible with supplied evidence.
3. **Impact** — materially affected domains/components/actors/data paths are identified.
4. **Dependency** — required ordering/decision/information relationships are represented correctly.
5. **Granularity** — plan units are neither unusably broad nor pointlessly fragmented.
6. **Decision** — unresolved human/product/architecture decisions are separated from implementation work.
7. **Risk** — material failure, security, compatibility, migration, and operational concerns are surfaced.
8. **Uncertainty** — unknown or contradictory facts are not promoted to certainty.
9. **Traceability** — important plan items can be traced to an outcome, impact, decision, risk, or evidence source.

No single aggregate score is normative in v1. Report the axes and severe errors separately.

## Severity

- **critical** — omission/error can invalidate the plan, create a serious safety/security/data/correctness failure, or make downstream work materially wrong.
- **major** — materially reduces completeness or executability but does not invalidate the whole plan.
- **minor** — useful quality improvement with limited effect on the plan's core validity.

Severity belongs to the reference assertion, not to wording or model confidence.

## Error taxonomy

- `MISS_CRITICAL`, `MISS_MAJOR`, `MISS_MINOR`
- `FALSE_IMPACT` — claims a material impact unsupported by context or reference policy.
- `UNSUPPORTED_CLAIM` — presents an unestablished architecture/system fact as fact.
- `FALSE_CERTAINTY` — fails to preserve a required unknown/contradiction.
- `BAD_DEPENDENCY` — asserts a dependency that is materially wrong.
- `MISSING_DEPENDENCY` — misses a required dependency.
- `UNDER_DECOMPOSITION` — a plan unit is too broad to review or reason about at the required level.
- `OVER_DECOMPOSITION` — fragmentation adds noise without useful planning information.
- `MISSING_DECISION`, `MISSING_RISK`
- `DUPLICATE_PLAN_ITEM`
- `UNTRACEABLE_PLAN_ITEM`

## Reference Plan Graph

A reference case is a **constraint graph, not a single canonical task list**. Alternative decompositions may be valid.

Minimum node fields:

```yaml
id: retrieval_authorization
kind: task            # outcome | task | decision | risk | unknown | deliverable
concept: retrieval authorization
severity: critical    # critical | major | minor
required: true
acceptable_aliases:
  - authorize retrieval against document permissions
```

Minimum edge fields:

```yaml
from: permission_policy
to: retrieval_authorization
relation: requires_decision
severity: critical
required: true
```

Unknown constraints:

```yaml
- concept: cache existence
  expected_state: unknown
  severity: major
```

A candidate is not penalized merely because it groups/splits tasks differently. Evaluation should match semantic obligations and required relationships rather than exact node counts.

## Three evaluation layers

### Layer 1 — deterministic

Code must own checks that do not require judgment: schema validity, duplicate IDs, dangling edges, forbidden cycles for hard execution dependencies, missing required fields, and structural traceability when explicit links exist.

### Layer 2 — semantic

Semantic matching determines whether candidate language satisfies a reference obligation despite wording differences. This layer must return match evidence and may abstain. An LLM judge, if used, is a fallible judge and must be versioned and audited against human labels.

### Layer 3 — human/expert

Humans adjudicate ambiguous equivalence, granularity, contested dependencies, severity, and novel valid findings not represented in the reference. Blind-set quality claims require human adjudication until judge reliability is demonstrated.

## Matching principles

- Match concepts, not strings.
- Allow one candidate node to satisfy multiple tightly coupled reference obligations only when its content explicitly covers them.
- Allow multiple candidate nodes to satisfy one reference obligation without awarding extra credit.
- Novel findings are not automatically false positives; they enter an `unadjudicated_novel` bucket until evidence/human review.
- Unsupported claims and explicit uncertainty are different outcomes.
- Silence is not abstention.
- A candidate cannot receive uncertainty credit if it simultaneously asserts the same fact as established.

## Scorecard

Report at minimum:

- critical coverage
- major coverage
- minor coverage
- decision recall
- risk recall
- impact coverage
- required dependency recall
- bad dependency count
- unsupported claim count
- uncertainty/abstention accuracy
- under/over-decomposition findings
- untraceable item count
- unadjudicated novel findings

Do not collapse these into a single leaderboard score in v1.

## Eval versioning

An evaluation release freezes together:

1. dataset inputs;
2. reference graphs/assertions;
3. scoring semantics;
4. semantic-judge configuration, if any;
5. baseline prompts/protocols.

Changing a frozen item creates a new eval version. Historical results retain their original eval version.

## Baselines

Every quality claim compares the same model/context against at least:

- `plain` — direct planning request;
- `strong_one_shot` — one carefully structured prompt;
- `decomposion` — staged planning method under test.

Additional published planning/decomposition methods may be added as baselines, but must not receive extra context unavailable to the other strategies.

## Self-test requirement

Before creating a large Golden Set, the evaluator must prove that it distinguishes controlled mutations of a small reference plan:

- remove a critical obligation -> critical miss;
- convert an unknown into a fact -> false certainty/unsupported claim;
- reverse a required dependency -> bad/missing dependency;
- collapse a deliberately review-critical unit -> under-decomposition;
- split a trivial unit into redundant fragments -> over-decomposition;
- preserve an equivalent paraphrase -> no miss.

If these tests cannot be expressed and pass reliably, the evaluator is not ready for Step 2 Golden authoring.

## Explicit non-goals

Planning Eval v1 does not measure graph aesthetics, human review time, coding success, execution success, token cost, latency, or business value. Those require separate evaluations.