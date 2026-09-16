# Planning Eval v1 — Review Gate

This is the only review gate for Step 1.

Proceed to Step 2 only when:

- required planning obligations can be represented as reference constraints rather than one canonical task list;
- critical, major, and minor omissions remain distinguishable;
- unknown facts must be stated explicitly; silence is not abstention;
- required dependency omissions/reversals are detectable in controlled tests;
- novel candidate findings remain unadjudicated rather than automatic false positives;
- semantic equivalence is explicitly deferred to a versioned semantic/human judge;
- v1 has no composite score and does not evaluate visual UX.

## Defaults carried into Step 2

- Critical coverage must be explicit enough for a reviewer to identify it.
- Granularity is constrained only where grouping would hide a review-critical obligation; exact task counts are never canonical.
- A critical miss is reported separately; hard pass/fail thresholds wait for baseline data.
- Novel findings require evidence/human adjudication before credit or penalty.
- The first three reference cases are development cases, not evidence of generalization; later blind cases require independent review.

## Anti-overengineering rule

Do not add a new module, schema field, metric, document, or abstraction unless a concrete reference case or evaluator failure requires it. Prefer deleting unused structure to predicting future needs.
