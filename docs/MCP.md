# MCP / Agent Integration Contract

## Goal

Expose Decomposion as a project-reasoning service that local coding agents can call without surrendering shell execution or repository control.

The coding agent owns implementation. Decomposion owns project structure, impact reasoning, dependency reasoning, evidence, and plan state.

## Proposed tools

### `project.get_context`

Returns the current System Graph summary, active change, human constraints, unresolved decisions, and relevant evidence references.

### `project.analyze_change`

Input:

- change statement
- optional scope/exclusions
- optional current evidence

Output:

- normalized goal
- outcomes
- impact candidates
- decisions
- risks
- initial dependency graph

### `project.get_plan`

Returns execution-ready tasks whose hard prerequisites are satisfied, plus blocked work and why it is blocked.

### `project.inspect_impact`

Called before material design changes.

Input:

- proposed design/change
- affected files/components if known

Output:

- newly affected domains
- invalidated assumptions
- required decisions
- migration/backward-compatibility concerns
- additional tasks/risks

### `project.report_discovery`

Records architecture facts discovered by the coding agent, e.g. an undocumented semantic cache or authorization path.

The reasoning engine updates the System Graph and computes graph deltas rather than rebuilding the project from scratch.

### `project.report_blocker`

Input:

- blocked task
- observed blocker
- evidence
- attempted approaches

Output:

- whether this is a task failure, missing decision, missing information, or graph defect
- newly created decision/risk/dependency nodes
- available next work

### `project.complete_task`

Requires evidence such as changed files, tests, commit, artifact, or explicit non-code result.

Completion must update downstream readiness deterministically.

### `project.validate_plan`

Challenges overall completion:

- uncovered outcomes
- unresolved critical decisions
- unmitigated critical risks
- affected domains without work/evidence
- incomplete required tasks
- contradictions between graph and new evidence

### `project.get_next_tasks`

Returns ready tasks ordered by dependency constraints and optional optimization preference such as critical path, risk-first, or maximum parallelism.

## Checkpoint policy

For an initial Claude Code/Codex integration, recommend project instructions that enforce:

1. call `analyze_change` before implementation begins;
2. call `get_plan` before selecting implementation work;
3. call `report_discovery` for materially new system facts;
4. call `inspect_impact` before changing architecture/contracts/data models;
5. call `complete_task` with evidence;
6. call `validate_plan` before claiming the feature/project is complete.

## What must remain deterministic

MCP handlers should delegate semantic reasoning to the reasoning pipeline, but these properties should be checked in code:

- schema validation
- graph invariant validation
- cycle detection
- readiness calculation
- topological ordering
- preserved human overrides
- revision creation
- idempotency of repeated tool calls

## Idempotency

Every mutation tool should accept or internally derive a stable operation key. Repeated agent retries must not duplicate decisions, tasks, evidence, or edges.

## Trust boundary

The service should never assume that an agent's statement is observed truth.

Agent-supplied information is recorded with provenance such as:

- `agent_observed`
- `agent_inferred`
- `human_confirmed`
- `repository_evidence`

Important claims can later be verified by repository connectors.

## Future adapters

Once the reasoning core is stable:

- GitHub adapter: code and PR evidence
- Linear/Jira adapter: work-item projection and sync
- Docs connectors: architecture/product evidence
- CI adapter: completion evidence

Adapters feed or consume the graph. They must not become the source of decomposition logic.
