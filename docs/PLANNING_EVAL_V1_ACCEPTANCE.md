# Planning Eval v1 — Step 1 acceptance

Step 1 is complete only when:

- the planning-quality boundary is explicit and visual-review UX is excluded;
- severity, error taxonomy, reference/candidate models and dependency semantics are represented in code;
- reference graph structural invariants have deterministic tests;
- controlled critical omission, uncertainty, dependency, novelty and alias mutations behave as documented;
- semantic matching has an auditable match/no-match/abstain contract;
- ambiguous granularity cannot be silently decided by the deterministic evaluator;
- the scorecard remains multidimensional with no composite score;
- eval release inputs and baseline protocols are versioned/fingerprintable;
- the module is included in the built wheel and `planning-eval selftest` succeeds from the installed package;
- existing repository CI remains green.

Step 1 does **not** claim that the evaluator can yet grade arbitrary real plans. That requires Step 2 reference cases and later semantic-judge calibration.