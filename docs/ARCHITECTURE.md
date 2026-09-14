# Architecture

## Overview

Decomposion is a reasoning layer between human intent and execution agents.

The architecture is intentionally evaluation-driven: the product must first demonstrate that its structured reasoning outperforms a strong plain-LLM baseline before the graph ontology and agent protocol are treated as stable platform contracts.

```text
Human / PM / Engineer
        |
        v
Change request + current context
        |
        v
+-----------------------------+
| Project Reasoning Engine    |
|-----------------------------|
| Context Mapper              |
| Outcome Decomposer          |
| Impact Scanner              |
| Gap Critic                  |
| Dependency Reasoner         |
| Granularity Critic          |
+-----------------------------+
        |
        v
Minimal Reasoning IR
        |
        +--> deterministic validators
        +--> human graph/chat projection
        +--> Claude Code / Codex via MCP
```

## Design principle: reason first, harden later

The first implementation should use a minimal IR and evaluation harness. Stable graph kinds and edge semantics are promoted only after repeated cases show they are necessary.

This avoids encoding one attractive decomposition theory into the product before it has been tested against blind and adversarial examples.

## Pipeline

### Stage 0 — Context ingestion

Build an evidence-backed current-system model from documents and, later, repositories and project systems.

Each assertion must retain provenance and freshness information.

Possible epistemic states:

- observed
- inferred
- proposed
- unknown
- contradicted
- human_confirmed

Missing evidence is not permission to invent a fact.

### Stage 1 — Goal normalization

Convert the raw request into a bounded change statement:

- intent
- scope
- explicit exclusions
- constraints
- success criteria
- known unknowns

### Stage 2 — Outcome decomposition

Generate states that must become true when the change is complete. Do not generate implementation steps yet.

### Stage 3 — Multi-lens impact scan

Run the proposed change against configurable lenses such as:

- Capability
- Domain/component
- Actor
- Data
- Lifecycle
- Permission/security
- Failure/recovery
- Backward compatibility/migration
- Operations/observability
- External systems

Each candidate impact should include:

- source outcome
- affected entity
- impact type
- rationale
- evidence references
- epistemic state
- optional raw confidence signal for evaluation only

### Stage 4 — Gap critic

A separate reasoning pass challenges the graph rather than merely adding more nodes.

It should ask both omission and restraint questions:

- What important actor/lifecycle/data path is absent?
- What existing evidence contradicts this interpretation?
- What cannot be determined from the available context?
- Which proposed impacts are speculative or irrelevant?
- What happens to existing data and historical state?
- What happens on partial failure or revocation?
- Are decisions being disguised as tasks?

### Stage 5 — Dependency derivation

Derive typed dependencies only when their semantics are explicit.

Every execution dependency must define whether it is blocking, its strength, resolution condition, and invalidation behavior.

Potential parallelism is derived from the absence of blocking dependencies plus explicit concurrency constraints. It should not be stored as a universal pairwise relationship.

### Stage 6 — Task synthesis

Only now produce execution tasks from accepted outcomes and impacts.

A task should be independently actionable and verifiable. Command-level steps remain inside task execution detail rather than becoming project-graph nodes.

### Stage 7 — Deterministic validation

Use code, not an LLM, for:

- schema validation
- cycle detection on hard blocking dependencies
- topological ordering
- readiness calculation
- orphan detection
- duplicate semantic-node checks
- revision consistency
- stale-evidence checks
- human-override preservation

### Stage 8 — Granularity critic

Classify work as too broad, appropriate, or too fine.

Heuristic questions:

- Does this node have one coherent outcome?
- Can one owner reasonably take it end-to-end?
- Is completion objectively testable?
- Does it hide a major independent decision?
- Would failure require independently retrying only part of it?

### Stage 9 — Projection

Keep one canonical reasoning state and derive views rather than regenerating independent plans.

Initial projections:

- Outcome
- Domain
- Dependency
- Risk

Timeline remains experimental until duration/resource semantics exist.

## Runtime interaction with coding agents

Claude Code or Codex remains the execution environment and calls Decomposion as a reasoning/checkpoint service.

```text
request
  -> analyze_change
  -> get_plan
  -> agent explores/implements
  -> report_discovery
  -> inspect_impact when design changes
  -> complete_task with evidence
  -> validate_plan
```

Stateful calls use explicit project/change/revision handles. Mutations use optimistic concurrency and idempotency keys.

## Checkpoint enforcement

Model instructions alone are advisory, not a hard safety boundary.

Strong enforcement, when required, must come from wrappers, hooks, CI, or orchestration that verifies mandatory checkpoints.

## Long-running reasoning

Repository-scale analysis and large document ingestion may not fit one synchronous call.

The architecture must support operation/task handles, status retrieval, cancellation where available, and applying the final graph delta against the expected revision.

## Evidence model

Evidence should be immutable or version-addressable when possible:

- repository commit/blob SHA
- document version/revision
- ETag
- content hash

If newer evidence changes, supporting assertions become stale candidates and require re-validation.

Contradictory credible evidence must remain visible as a conflict rather than being silently resolved by the model.

## Storage boundary

The durable product state is the reasoning graph/IR plus provenance and revision history. Prompts and conversations are derivation mechanisms, not the source of truth.

Persist:

- current reasoning state
- evidence references and versions
- decisions
- unknowns and contradictions
- human overrides
- graph revisions
- engine/model/prompt/schema versions
- evaluation traces
