# Product Direction

## Positioning

Decomposion is not a generic project-management tool and not another coding agent.

It is a **project reasoning layer** that turns a complex change request into a structured, evidence-aware model of:

- Outcomes
- Affected domains
- Decisions
- Risks
- Unknowns
- Contradictions
- Dependencies
- Tasks
- Evidence

The product should answer six questions reliably:

1. What must become true?
2. What will this change affect?
3. What are we missing?
4. What do we not know yet?
5. What must be decided or completed first?
6. What view should each person see now?

## Initial wedge

Start with software change-impact analysis for existing products.

Input:

- Existing product/system context
- Product and architecture documents
- Optional repository evidence
- A change request, e.g. `Add document sharing to our RAG SaaS`

Output:

- Current System Map
- Desired Outcomes
- Impact Map
- Missing concerns
- Unknowns and contradictions
- Decisions and risks
- Typed Dependency Graph
- Execution-ready work graph
- Multiple projections: Outcome, Domain, Dependency, Risk, and optionally Actor when useful

## Core UX

### 1. Understand current system

Create an evidence-backed system model before generating tasks. When evidence is missing or contradictory, show that explicitly.

### 2. Analyze a change

Do not jump directly to implementation tasks. First derive outcomes, then scan impact across multiple lenses.

### 3. Critique the analysis

Look not only for omissions but also for speculation, contradictions, missing information, lifecycle gaps, permission gaps, failure modes, migration concerns, and external-system effects.

### 4. Build the work graph

Only after outcomes, impacts, decisions, and unknowns are understood should implementation work be generated and ordered.

### 5. Re-project the same reasoning state

The underlying graph stays stable while the UI projects it by:

- Outcome
- Domain
- Dependency
- Risk
- Actor when the graph contains meaningful actor metadata

Timeline is deferred until duration/resource semantics are trustworthy.

## Product principles

1. **Outcome before task.**
2. **Evidence before certainty.** Separate observed facts from inference and proposals.
3. **Unknown is a valid answer.** Missing evidence must not be converted into fabricated structure.
4. **Contradictions remain visible.** Do not silently choose a convenient source.
5. **Multiple lenses beat one perfect decomposition axis.**
6. **Edges have execution semantics.** A semantic relationship is not automatically a scheduling dependency.
7. **Not every node is a task.** Decisions, risks, outcomes, unknowns, and evidence are first-class reasoning concepts.
8. **Graph structure is deterministic where possible.** LLMs reason about meaning; code checks invariants, readiness, cycles, revisions, and stale evidence.
9. **Human edits are authoritative.** Re-planning must preserve explicit user constraints or record a conflict.
10. **The product must beat a strong baseline.** A complex architecture is unjustified if a good plain-LLM prompt performs equivalently.

## Product value hypothesis

The first `wow` moment is not merely discovering something surprising.

It is discovering something that is simultaneously:

- correct;
- actionable;
- non-obvious;
- supported or honestly marked uncertain;
- worth the review cost.

The product fails if it produces many impressive-sounding but low-value concerns.

## Non-goals for MVP

- Replacing Jira, Linear, or Asana
- Running coding agents directly
- Full resource planning
- Team chat
- Automatic merge/deployment
- Full Gantt/project accounting
- General-purpose workflow automation

## Expansion path

`Understand -> Plan -> Execute`

The first release owns `Understand` and the front half of `Plan`. Execution systems such as Claude Code, Codex, Linear, Jira, and GitHub are integrations, not the core product.

## Validation bar

Before expanding scope, demonstrate on held-out and adversarial cases that Decomposion materially improves useful-impact discovery over:

1. a strong plain-LLM prompt;
2. a strong structured checklist prompt.

If the gain is marginal, simplify or change the reasoning architecture rather than adding more graph types and orchestration features.
