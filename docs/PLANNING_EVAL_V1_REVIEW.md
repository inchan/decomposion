# Step 1 Review — Planning Eval v1

This document is intentionally a checkpoint. Step 2 Golden authoring should not start until these choices are reviewed.

## What Step 1 establishes

- Planning quality and visual-review quality are separate evaluations.
- A reference plan is a constraint graph, not a canonical task list.
- Severity is explicit and independent of model confidence.
- Deterministic, semantic, and human judgment have different responsibilities.
- Novel findings are held for adjudication rather than automatically penalized.
- Silence is not uncertainty/abstention.
- Baseline prompts and scoring semantics are versioned with the dataset.
- The first scorecard is multidimensional, not a single leaderboard number.

## What Step 1 deliberately does not solve

1. Semantic equivalence is not implemented. The deterministic matcher only recognizes exact concepts and explicitly authored aliases.
2. Granularity quality cannot generally be inferred deterministically. `UNDER_DECOMPOSITION` and `OVER_DECOMPOSITION` require authored constraints and semantic/human adjudication in the next iteration.
3. Novel valid findings need an adjudication workflow before precision can be honestly reported.
4. No LLM judge has been selected or trusted. Judge reliability must be measured against human labels.
5. No 10-case Golden Set exists yet. Existing Open WebUI prompts are experiment prompts, not validated reference plans.
6. No overall score or pass threshold is defined; doing so before observed distributions would create false precision.

## Questions that must be answered before or during Step 2

1. Should a critical reference obligation be allowed to be satisfied only implicitly, or must the candidate state it explicitly enough for a reviewer to see it?
2. For granularity, should the reference encode `must_separate` / `may_group` concept sets, or should granularity remain a human-only judgment in Eval v1?
3. Should security/data-loss critical misses be a hard failure regardless of otherwise high coverage?
4. How should a novel, evidence-backed finding affect scoring before a human adjudicates it: neutral (current proposal) or provisional positive credit?
5. Who authors and who independently reviews the first three reference cases to reduce self-confirmation bias?

## Proposed Step 2 acceptance gate

Author only three deep reference cases first. For each, require:

- repository evidence for factual context;
- explicit critical/major/minor obligations;
- required unknowns and decisions;
- required dependency constraints;
- at least two acceptable alternative decompositions;
- controlled bad plans that trigger expected error classes;
- independent review notes for contested assertions.

Only after those three cases can be represented without bending the schema should the set expand to ten.