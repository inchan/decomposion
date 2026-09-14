# decomposion

Decomposion is a **project reasoning layer** for turning complex changes into structured outcomes, impacts, decisions, risks, dependencies, and execution-ready work graphs.

It is intentionally not a generic project manager and not another coding agent. The initial product sits **before and alongside** tools such as Claude Code and Codex: it helps determine what must change, what is affected, what is missing, what must happen first, and what evidence supports the plan.

## Core idea

`Goal -> Outcomes -> Multi-lens Impact Scan -> Gap Critic -> Typed Dependencies -> Tasks -> Projections`

The canonical graph distinguishes system facts, outcomes, decisions, risks, deliverables, tasks, milestones, evidence, and typed relationships. The same graph can then be projected by Outcome, Domain, Dependency, Risk, Actor, or Timeline.

## Why this exists

Most AI planning tools jump from a request directly to tasks. That is fragile for cross-cutting changes. For example, adding document sharing to a RAG SaaS may affect document ownership, organization boundaries, retrieval authorization, vector metadata, semantic caches, existing chat history, audit trails, and revocation semantics. The product thesis is that discovering and structuring those hidden impacts is more valuable than merely generating a longer task list.

## Repository map

- [`docs/PRODUCT.md`](docs/PRODUCT.md) — positioning, product principles, MVP wedge
- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — reasoning pipeline and runtime architecture
- [`docs/GRAPH_SCHEMA.md`](docs/GRAPH_SCHEMA.md) — canonical graph and invariants
- [`docs/MCP.md`](docs/MCP.md) — Claude Code/Codex integration contract
- [`docs/EVALUATION.md`](docs/EVALUATION.md) — 100-case golden-set strategy and scoring
- [`docs/MVP.md`](docs/MVP.md) — implementation phases and explicit non-goals
- [`golden/software/document-sharing.yaml`](golden/software/document-sharing.yaml) — first reference golden case

## Initial product boundary

The first release should own **Understand** and the front half of **Plan**:

1. ingest current-system context;
2. normalize a proposed change;
3. derive desired outcomes;
4. scan impacts across multiple lenses;
5. challenge the result for omissions;
6. derive typed dependencies and execution-ready tasks;
7. present one canonical graph through multiple projections;
8. expose the reasoning layer to local coding agents via MCP.

Direct shell execution, autonomous agent orchestration, deployment, full resource scheduling, and Jira/Linear replacement are explicitly deferred until the reasoning core proves itself on the golden set.

## Development standard

Every reasoning change should be evaluated against golden cases. Prefer structured graph deltas over prose-only agent output, deterministic graph validation over LLM guesses, and explicit provenance over unsupported certainty.
