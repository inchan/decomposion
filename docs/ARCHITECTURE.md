# Architecture

## Overview

Decomposion is a reasoning layer between human intent and execution agents.

```text
Human / PM / Engineer
        |
        v
Change request + context
        |
        v
+---------------------------+
| Project Reasoning Engine  |
|---------------------------|
| Context Mapper            |
| Outcome Decomposer        |
| Impact Scanner            |
| Gap Critic                |
| Dependency Solver         |
| Granularity Critic        |
| Projection Engine         |
+---------------------------+
        |
        v
Project Graph
        |
        +--> Human graph/chat UI
        +--> Claude Code / Codex via MCP
        +--> Linear/Jira/GitHub adapters later
```

## Pipeline

### Stage 0 — Context ingestion

Build an evidence-backed current System Graph from documents and, later, repositories and project systems.

Each inferred fact should record provenance and confidence.

### Stage 1 — Goal normalization

Convert the raw request into a bounded change statement:

- intent
- scope
- explicit exclusions
- constraints
- success criteria

### Stage 2 — Outcome decomposition

Generate states that must become true when the change is complete. Do not generate implementation steps yet.

### Stage 3 — Multi-lens impact scan

Run the proposed change against a configurable set of lenses:

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

Each candidate impact must include:

- source outcome
- affected graph entity
- impact type
- rationale
- evidence references
- confidence

### Stage 4 — Gap critic

A separate reasoning pass challenges the graph rather than extending it blindly.

Questions include:

- Which actor or lifecycle phase is absent?
- Are create/read/update/delete/revoke paths covered?
- What happens to existing data?
- What happens on partial failure?
- Are tenant/organization boundaries crossed?
- Does an existing cache/index/history retain inaccessible data?
- Are external systems affected?
- Are decisions being disguised as tasks?

### Stage 5 — Dependency derivation

Derive typed edges before scheduling.

Edge types:

- `requires_decision`
- `requires_information`
- `requires_data`
- `requires_contract`
- `blocks_execution`
- `produces_for`
- `invalidates`
- `can_parallelize_with`

### Stage 6 — Task synthesis

Only now produce execution tasks from outcomes and impacts.

A task should be independently actionable and verifiable. Internal command-level steps remain inside task execution details rather than becoming graph nodes.

### Stage 7 — Deterministic graph validation

Use code, not an LLM, for:

- cycle detection
- topological ordering
- orphan detection
- duplicate-edge detection
- unreachable outcome detection
- impossible dependency constraints
- critical path once duration data exists

### Stage 8 — Granularity critic

Classify nodes as:

- too broad
- appropriate
- too fine

Suggested heuristic questions:

- Does this node have one coherent outcome?
- Can one owner reasonably take it end-to-end?
- Is completion objectively testable?
- Does it hide a major independent decision?
- Would failure require independently retrying only part of it?

### Stage 9 — Projection

Keep one canonical graph and derive views rather than regenerating independent plans.

Initial projections:

- Outcome view
- Domain view
- Dependency view
- Risk view

## Runtime interaction with coding agents

The recommended initial integration reverses orchestration: Claude Code or Codex remains the execution environment and calls Decomposion as a planning/checkpoint service.

```text
request
  -> analyze_change
  -> get_plan
  -> agent explores/implements
  -> report_discovery (when reality differs)
  -> inspect_impact (before material design changes)
  -> complete_task
  -> validate_plan
  -> get_next_tasks
```

This avoids owning shell execution, credentials, IDE integration, model routing, and sandboxing in the first version.

## Mandatory checkpoints

The integration should not rely only on the model remembering to use the service.

Minimum lifecycle contract:

1. `analyze_change` before implementation
2. `get_plan` before selecting work
3. `report_discovery` when new architecture facts materially change impact
4. `inspect_impact` before a significant design deviation
5. `complete_task` with evidence
6. `validate_plan` before declaring the overall change complete

## Evidence model

Every important graph assertion should be one of:

- `observed` — supported directly by source evidence
- `inferred` — reasoned from evidence
- `proposed` — future design choice
- `human_confirmed` — explicitly accepted/edited by a person

Never display inferred facts as confirmed architecture.

## Storage boundary

The graph should be the durable product state. LLM prompts and conversations are transient derivation mechanisms.

Persist:

- canonical graph
- evidence references
- decisions
- human overrides
- graph revisions
- analysis run metadata
- evaluation traces for golden-set runs
