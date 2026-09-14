# CI Evaluation

## What runs on every PR

The first CI layer is intentionally deterministic and free of model/API dependencies.

1. Validate every `golden/**/*.yaml` case.
2. Reject malformed expected/dependency/unknown assertion structures.
3. Run deterministic scoring tests for required concepts, forbidden concepts, and abstention behavior.
4. Run all pytest regression tests.

The workflow is `.github/workflows/eval.yml`.

## Why LLM evaluation is not enabled by default

A model-backed gate is useful only after the following are explicit and versioned:

- provider and model ID;
- model parameters and repeat policy;
- secrets and budget ceiling;
- prompt/baseline version;
- retry/error policy;
- stored raw outputs for audit;
- variance policy and release thresholds.

Until then, a model-backed PR gate would look authoritative while being neither reproducible nor cost-controlled. The workflow contains a disabled placeholder rather than silently calling a provider.

## Planned model-backed matrix

For the same held-out cases run:

- plain LLM baseline;
- structured-prompt baseline;
- Decomposion pipeline.

Compare at minimum:

- must-detect recall;
- forbidden/noise rate;
- abstention accuracy;
- dependency correctness;
- invariant violations;
- latency and model cost.

Do not ship additional architecture solely because Decomposion scores highly in isolation. The product thesis requires a material and repeatable advantage over the strongest reasonable baseline.

## Recommended cadence

- PR: deterministic checks + 5–10 model smoke cases once enabled.
- Nightly/manual: full development and adversarial set.
- Release candidate: blind/held-out set with frozen prompts/model configuration.

## Initial release gates

Deterministic gates:

- zero malformed golden cases;
- zero graph invariant violations once graph implementation exists;
- zero dependency cycles in accepted execution graphs;
- all regression tests pass.

Model-backed thresholds should be derived from baseline runs rather than invented before measurements exist.
