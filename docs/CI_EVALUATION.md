# CI Evaluation

## What runs on every PR

The CI layer is intentionally deterministic and free of external model/API dependencies until provider policy is versioned.

1. Validate every `golden/**/*.yaml` case.
2. Reject malformed expected/dependency/unknown assertion structures.
3. Run deterministic scoring tests for required concepts, forbidden concepts, and abstention behavior.
4. Run all pytest regression tests.
5. Execute the three-strategy matrix contract (`plain`, `structured`, `decomposion`) through deterministic fixture adapters.
6. Publish a Markdown evaluation table to the GitHub Actions step summary.

The workflow is `.github/workflows/eval.yml`.

## Baseline matrix architecture

All strategies implement the same interface:

- input: case id, supplied context, change request;
- output: normalized concepts, explicit abstentions, metadata.

The matrix runner scores each strategy against exactly the same Golden Case assertions. This prevents each baseline from quietly using a different metric or data shape.

Current strategies are deterministic fixtures. They validate the runner, scorers, aggregation, report generation, and CI wiring without pretending to measure model quality.

When model-backed evaluation is enabled, replace/add adapters while preserving the contract:

1. `plain` — a strong direct analysis prompt with no Decomposion-specific reasoning stages;
2. `structured` — a strong structured prompt that explicitly asks for outcomes, impacts, uncertainty, and dependencies;
3. `decomposion` — the actual staged reasoning pipeline.

## Why live LLM evaluation is not enabled by default

A model-backed gate is useful only after the following are explicit and versioned:

- provider and exact model ID;
- prompt version for each strategy;
- model parameters and repeat policy;
- secrets and budget ceiling;
- retry/error policy;
- raw-output retention for audit;
- variance policy and release thresholds;
- provider failure behavior;
- cost and latency measurement.

Until then, a live model-backed PR gate would look authoritative while being neither reproducible nor cost-controlled. The workflow keeps a disabled placeholder rather than silently calling a provider.

## Metrics

Compare at minimum:

- must-detect recall;
- forbidden/noise rate;
- abstention accuracy;
- dependency correctness;
- invariant violations;
- latency;
- model cost.

Future comparison reports should also include per-case regressions so an aggregate gain cannot hide a critical miss.

## Regression policy

The product thesis is comparative, not absolute. Decomposion should not be considered justified merely because it obtains a high standalone score.

Once real model adapters exist, PR CI should fail or warn on policy-defined regressions such as:

- critical must-detect recall falling materially below the frozen baseline;
- forbidden/noise rate materially increasing;
- abstention accuracy materially decreasing;
- new invariant violations or dependency cycles;
- Decomposion failing to beat the strongest reasonable baseline by the agreed margin on the targeted wedge.

Thresholds must be derived from measured variance rather than invented in advance.

## Recommended cadence

- PR: deterministic checks plus 5–10 model smoke cases once enabled.
- Nightly/manual: full development and adversarial set with repeated runs where variance matters.
- Release candidate: blind/held-out set with frozen prompts/model configuration.

## Initial release gates

Deterministic gates:

- zero malformed golden cases;
- zero graph invariant violations once graph implementation exists;
- zero dependency cycles in accepted execution graphs;
- all regression tests pass;
- baseline matrix/report pipeline completes successfully.

Model-backed thresholds should be derived from baseline runs rather than invented before measurements exist.
