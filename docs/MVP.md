# MVP Implementation Plan

## Goal

Validate one thesis before expanding scope:

> Given existing software context and a proposed change, can Decomposion reveal meaningful affected areas, hidden concerns, dependencies, and decisions better than a strong plain-LLM baseline, while controlling hallucination and noise?

The MVP must be optimized for falsifiability. We should be able to prove that the reasoning architecture adds value beyond a good prompt.

## Phase 0 — Evaluation before architecture lock-in

Build a small evaluation harness before hardening the graph model.

Start with 20 strong software-change cases split into:

- development set — visible to prompt/engine authors;
- blind test set — authored or reviewed independently;
- adversarial set — ambiguous, underspecified, misleading, and no-impact cases.

Every case must be run against at least:

1. a strong plain-LLM prompt baseline;
2. Decomposion minimal pipeline;
3. later engine revisions.

Track correctness, useful surprise, actionability, abstention quality, and noise.

Exit criteria:

- repeatable baseline exists;
- failure taxonomy exists;
- blind/adversarial cases exist;
- we can measure whether Decomposion materially beats a plain-LLM prompt.

## Phase 1 — Minimal reasoning IR

Do not freeze the full canonical schema yet.

Start only with concepts repeatedly required by the first evaluation cases:

- entity/system fact;
- outcome;
- decision;
- risk;
- task;
- evidence;
- hard dependency.

Add node/edge kinds only when repeated failures demonstrate a need.

The IR must support epistemic state:

- observed;
- inferred;
- proposed;
- unknown;
- contradicted;
- human_confirmed.

Exit criteria:

- evaluation cases can round-trip through the IR without blocking useful analysis;
- unknown and contradictory evidence can be represented explicitly;
- schema changes remain cheap.

## Phase 2 — Independently evaluable reasoning passes

Implement passes as structured graph-delta producers:

1. Context Mapper
2. Goal normalizer
3. Outcome Decomposer
4. Multi-lens Impact Scanner
5. Gap Critic
6. Dependency derivation
7. Task synthesis
8. Granularity Critic

Each pass must be scored separately where practical.

Critical behavior:

- the engine may abstain;
- missing evidence must create an `unknown` or information requirement instead of fabricated certainty;
- inferred high-impact additions require rationale and provenance;
- numerical confidence is treated as an uncalibrated model signal until calibration is demonstrated.

Exit criteria:

- stage outputs can be evaluated independently;
- meaningful failure classes are attributable to a stage;
- engine can say `insufficient evidence` without inventing structure.

## Phase 3 — Schema hardening and deterministic semantics

Only after 20–50 evaluation cases, promote stable concepts into the canonical graph.

Define formal execution semantics for dependency edges:

- whether they block readiness;
- whether they are hard, soft, or advisory;
- their resolution condition;
- how invalidation reopens downstream work.

Deterministic code should own:

- schema validation;
- cycle detection;
- readiness calculation;
- topological ordering;
- orphan detection;
- duplicate semantic-node checks;
- revision creation;
- human-override preservation;
- stale-evidence invalidation.

Exit criteria:

- dependency semantics are testable;
- graph invariants are deterministic;
- schema changes are justified by repeated evidence, not taste.

## Phase 4 — Graph + Chat UI

First UI should support:

- Current System Map;
- Change Graph;
- Outcome view;
- Domain view;
- Dependency view;
- Risk view;
- click node for evidence/rationale;
- explicit observed/inferred/unknown/contradicted state;
- accept/reject/edit inferred nodes;
- natural-language graph operations such as `look again from a security perspective`.

Do not promise a true timeline until duration/resource semantics exist.

## Phase 5 — MCP integration

Expose the reasoning layer to Claude Code/Codex after revision and concurrency semantics are defined.

Target flow:

- agent requests analysis before implementation;
- receives a project/change/revision handle;
- reports architecture discoveries;
- requests impact review before material design deviations;
- completes tasks against an expected graph revision;
- handles revision conflicts explicitly;
- requests final validation before declaring completion.

Long-running reasoning must support asynchronous task lifecycle rather than assuming every analysis fits one synchronous tool call.

## Phase 6 — Evidence connectors

Add in this order unless evaluation disproves the priority:

1. local/project documents;
2. Git repository evidence;
3. GitHub metadata/PR evidence;
4. Linear/Jira;
5. broader document systems.

Every evidence reference should be version-addressable where possible: commit SHA, blob SHA, document version, immutable content hash, or equivalent.

## Explicitly defer

- direct shell execution;
- autonomous coding-agent orchestration;
- automatic deployment;
- resource scheduling;
- generalized workflow builder;
- full PM replacement;
- many-agent routing;
- full Gantt planning.

## Product success signal

Do not optimize for surprise alone.

A useful discovery should score high on:

- correctness;
- actionability;
- non-obviousness;
- evidence quality;
- low false-positive cost.

The strongest early product signal is:

> The system repeatedly surfaces correct, actionable impacts or missing decisions that a strong plain-LLM baseline and a competent reviewer are likely to miss, without flooding the user with speculative noise.
