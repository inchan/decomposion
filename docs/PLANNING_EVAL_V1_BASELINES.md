# Planning Eval v1 baseline protocols

Baseline definitions are frozen with an Eval release. Exact prompts will be stored with each released dataset; this document defines the protocol boundary.

## plain

One model call/session. Provide the same repository/context and change request available to all strategies. Ask for a plan including impacts, decisions, risks, work, dependencies, and uncertainty. Do not expose Decomposion stages, reference assertions, or judge rubric.

## strong_one_shot

One model call/session. Provide the same context and explicitly request a structured analysis of outcomes, affected domains/components, actors, data lifecycle, authorization/security, failure/recovery, migration/backward compatibility, operations/external systems, decisions, risks, dependencies, and unknowns before implementation work. Do not expose reference assertions.

## decomposion

Use the staged method under test. Intermediate artifacts may be passed only within that run. It receives no additional repository facts or reference assertions unavailable to the baselines.

## Fairness controls

- same underlying model and model configuration when testing reasoning architecture;
- same target repository commit/context snapshot;
- fresh run/session and no cross-strategy answer memory;
- identical evidence-access permissions;
- raw output retained;
- model, agent, prompt/protocol, eval and source versions recorded;
- no post-hoc prompt tuning on blind cases.
