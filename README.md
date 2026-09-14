# decomposion

Decomposion is a **project reasoning layer** for turning complex changes into structured outcomes, impacts, decisions, risks, unknowns, contradictions, dependencies, tasks, and evidence.

It is intentionally not a generic project manager and not another coding agent. The initial product sits **before and alongside** tools such as Claude Code and Codex: it helps determine what must change, what is affected, what is missing, what is still unknown, what must happen first, and what evidence supports the plan.

## Core idea

`Goal -> Outcomes -> Multi-lens Impact Scan -> Gap Critic -> Typed Dependencies -> Tasks -> Projections`

The product is evaluation-first. This architecture is justified only if it materially outperforms strong plain-LLM and structured-prompt baselines on held-out and adversarial cases while controlling speculative noise.

## Why this exists

Most AI planning tools jump from a request directly to tasks. That is fragile for cross-cutting changes. For example, adding document sharing to a RAG SaaS may affect document ownership, authorization, retrieval, historical chat state, auditability, and revocation semantics.

But Decomposion must not turn common patterns into invented facts. If the supplied context does not establish whether a cache, vector database, tenant model, or external-sharing path exists, the engine should surface that uncertainty rather than pretending it knows.

## Repository map

- [`docs/PRODUCT.md`](docs/PRODUCT.md) — positioning, product principles, validation bar
- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — reasoning pipeline and runtime architecture
- [`docs/GRAPH_SCHEMA.md`](docs/GRAPH_SCHEMA.md) — working IR, epistemic states, dependency semantics
- [`docs/MCP.md`](docs/MCP.md) — Claude Code/Codex integration contract
- [`docs/EVALUATION.md`](docs/EVALUATION.md) — development/blind/adversarial evaluation strategy
- [`docs/MVP.md`](docs/MVP.md) — evaluation-first implementation sequence
- [`golden/software/document-sharing.yaml`](golden/software/document-sharing.yaml) — development reference case
- [`golden/software/document-sharing-underspecified.yaml`](golden/software/document-sharing-underspecified.yaml) — adversarial abstention case

## Initial product boundary

The first release should own **Understand** and the front half of **Plan**:

1. ingest current-system context;
2. normalize a proposed change;
3. derive desired outcomes;
4. scan impacts across multiple lenses;
5. challenge the result for omissions, speculation, and contradictions;
6. derive typed dependencies and execution-ready tasks;
7. present one reasoning graph through multiple projections;
8. expose the reasoning layer to local coding agents via MCP.

Direct shell execution, autonomous agent orchestration, deployment, full resource scheduling, and Jira/Linear replacement are explicitly deferred.

## Development standard

Every reasoning change should be evaluated against development, blind, and adversarial cases. Prefer structured graph deltas over prose-only output, deterministic graph validation over LLM guesses, explicit provenance over unsupported certainty, and `unknown` over fabricated confidence.
