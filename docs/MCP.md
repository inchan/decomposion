# MCP / Agent Integration Contract

## Goal

Expose Decomposion as a project-reasoning service that local coding agents can call without surrendering shell execution or repository control.

The coding agent owns implementation. Decomposion owns project structure, impact reasoning, dependency reasoning, evidence, and plan state.

The protocol must assume that agents retry calls, multiple actors may mutate the same graph, evidence may become stale, and some reasoning jobs may be long-running.

## Identity and state handles

Every stateful request should carry explicit handles:

- `project_id`
- `change_id`
- `expected_revision` for mutations
- `operation_key` for idempotency

Responses that mutate state return the new `revision_id`.

A mutation against a stale revision must fail with an explicit `REVISION_CONFLICT` rather than silently overwriting newer reasoning.

## Proposed tools

### `project.get_context`

Input:

- project_id
- change_id
- optional revision_id

Returns the current System Graph summary, active change, human constraints, unresolved decisions, unknowns, contradictions, and evidence references.

### `project.analyze_change`

Input:

- project_id
- change statement
- optional scope/exclusions
- optional current evidence
- operation_key

Output:

- change_id
- revision_id
- normalized goal
- outcomes
- impact candidates
- decisions
- risks
- unknowns
- contradictions
- initial dependency graph

Analysis may return a long-running task handle when work cannot safely complete in one synchronous call.

### `project.get_plan`

Returns execution-ready tasks whose hard prerequisites are satisfied, plus blocked work, unresolved unknowns, and why each item is blocked.

### `project.inspect_impact`

Called before material design changes.

Input:

- project_id
- change_id
- expected_revision
- proposed design/change
- affected files/components if known
- operation_key

Output:

- revision_id
- newly affected domains
- invalidated assumptions
- required decisions
- new unknowns/contradictions
- migration/backward-compatibility concerns
- additional tasks/risks

### `project.report_discovery`

Records architecture facts discovered by the coding agent.

Agent statements are never automatically promoted to observed truth. They retain provenance until verified by repository/document evidence or confirmed by a human.

### `project.report_blocker`

Input:

- project_id
- change_id
- expected_revision
- blocked task
- observed blocker
- evidence
- attempted approaches
- operation_key

Output classifies the blocker as one or more of:

- task failure
- missing decision
- missing information
- contradiction
- stale assumption
- graph defect

### `project.complete_task`

Requires:

- task_id
- expected_revision
- operation_key
- completion evidence such as changed files, tests, commit, artifact, or explicit non-code result.

Completion updates downstream readiness deterministically.

### `project.validate_plan`

Challenges overall completion for:

- uncovered outcomes
- unresolved critical decisions
- unmitigated critical risks
- unresolved unknowns that block correctness
- contradictions
- affected domains without work/evidence
- incomplete required tasks
- stale evidence or assumptions

### `project.get_next_tasks`

Returns ready tasks ordered by dependency constraints and an optional strategy such as risk-first or maximum safe parallelism.

Parallelism should be derived from dependencies plus explicit concurrency constraints rather than stored as a universal pairwise relation.

## Checkpoint policy

Project instructions may request these calls, but instruction text alone is not a hard enforcement boundary.

Recommended lifecycle:

1. call `analyze_change` before implementation;
2. call `get_plan` before selecting work;
3. call `report_discovery` for materially new system facts;
4. call `inspect_impact` before changing architecture/contracts/data models;
5. call `complete_task` with evidence;
6. call `validate_plan` before claiming completion.

For environments requiring stronger enforcement, use wrapper scripts, hooks, CI checks, or an orchestration layer that verifies required Decomposion checkpoints rather than relying solely on model compliance.

## Long-running work

Repository-scale analysis, large document ingestion, or full graph re-analysis may exceed a normal synchronous tool call.

The integration should therefore support a task lifecycle compatible with the surrounding MCP/runtime capabilities:

- create/start work;
- receive task/operation handle;
- poll or receive completion state;
- cancel when supported;
- retrieve final graph delta;
- apply the delta against the expected revision.

Long-running results must still honor revision conflict checks before mutation.

## What must remain deterministic

MCP handlers may delegate semantic reasoning to the reasoning pipeline, but these properties belong in code:

- schema validation
- graph invariant validation
- cycle detection
- readiness calculation
- topological ordering
- preserved human overrides
- revision creation
- idempotency
- optimistic concurrency
- operation replay protection
- stale-evidence checks

## Idempotency

Every mutation accepts a stable `operation_key`. Repeated retries with the same key must return the original logical result and must not duplicate decisions, tasks, evidence, edges, or revisions.

## Trust boundary

Provenance examples:

- `agent_observed`
- `agent_inferred`
- `human_confirmed`
- `repository_evidence`
- `document_evidence`

Evidence should carry immutable or version-addressable identifiers where available.

## Authentication and authorization

The service must distinguish protocol transport identity from project authorization.

At minimum validate:

- caller identity/session as provided by the deployment environment;
- project access;
- allowed mutation scope;
- requested change/revision ownership;
- server-supported protocol/tool version.

Do not assume possession of a project_id implies authorization.

## Versioning

Version the Decomposion tool contract independently from model prompts.

Breaking request/response schema changes require a protocol/tool version transition. Persist analysis metadata with engine version, model configuration, prompt version, and schema version for reproducibility.

## Future adapters

Once the reasoning core is stable:

- GitHub adapter: code and PR evidence
- Linear/Jira adapter: work-item projection and sync
- Docs connectors: architecture/product evidence
- CI adapter: completion evidence

Adapters feed or consume the graph. They must not become the source of decomposition logic.
