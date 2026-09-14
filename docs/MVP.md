# MVP Implementation Plan

## Goal

Validate one thesis before expanding scope:

> Given existing software context and a proposed change, can Decomposion reveal meaningful affected areas, hidden concerns, dependencies, and decisions that a competent team might otherwise miss?

## Phase 1 — Canonical graph core

Build:

- typed node/edge schema
- graph persistence
- revision history
- deterministic invariant validation
- topological ordering and readiness calculation
- evidence/provenance model

Exit criteria:

- graph can round-trip without semantic loss;
- deterministic validators catch cycles/orphans/invalid edge combinations;
- human-confirmed edits survive re-analysis.

## Phase 2 — Reasoning pipeline

Implement independently evaluable stages:

1. Context Mapper
2. Goal normalizer
3. Outcome Decomposer
4. Multi-lens Impact Scanner
5. Gap Critic
6. Dependency derivation
7. Task synthesis
8. Granularity Critic

Each stage consumes and returns structured graph deltas rather than prose-only output.

Exit criteria:

- stage outputs can be scored separately on golden cases;
- every inferred high-impact addition has rationale/confidence;
- pipeline can explain why a node/edge exists.

## Phase 3 — Golden-set harness

Start with 20 high-quality cases before expanding to 100.

Prioritize:

- document sharing in RAG SaaS
- account deletion
- SSO
- document versioning
- external API
- role/permission redesign
- billing-plan change
- data migration
- semantic cache introduction
- tenant isolation
- webhook support
- audit logging
- background-job redesign
- storage-provider migration
- search index change
- chat history retention
- API versioning
- file-sharing expiration
- incident recovery change
- feature-flag rollout

Exit criteria:

- repeatable baseline score;
- failure taxonomy documented;
- regression comparison automated.

## Phase 4 — Graph + Chat UI

First UI should support:

- Current System Map
- Change Graph
- Outcome view
- Domain view
- Dependency view
- Risk view
- click node for evidence/rationale
- accept/reject/edit an inferred node
- natural-language graph operations, e.g. `look again from a security perspective`

Do not build project-management chrome yet.

## Phase 5 — MCP integration

Expose the core tools in `docs/MCP.md`.

Target flow:

- Claude Code/Codex calls Decomposion before implementation;
- reports architecture discoveries during work;
- requests impact review before material design deviations;
- marks tasks complete with evidence;
- requests final plan validation.

## Phase 6 — Evidence connectors

Add in this order unless evaluation disproves the priority:

1. local/project documents
2. Git repository evidence
3. GitHub metadata/PR evidence
4. Linear/Jira
5. broader document systems

## Explicitly defer

- direct shell execution
- autonomous coding-agent orchestration
- automatic deployment
- resource scheduling
- generalized workflow builder
- full PM replacement
- many-agent routing

## Product success signal

The strongest early signal is not task-generation quality.

It is repeated user feedback equivalent to:

> `I had not considered that affected area / risk / dependency.`

The second signal is that users accept the generated structure as the starting point for actual implementation planning rather than rewriting it from scratch.
