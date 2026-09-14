# Product Direction

## Positioning

Decomposion is not a generic project-management tool and not another coding agent.

It is a **project reasoning layer** that turns a complex change request into a structured graph of:

- Outcomes
- Affected domains
- Decisions
- Risks
- Dependencies
- Tasks
- Evidence

The product should answer five questions reliably:

1. What must become true?
2. What will this change affect?
3. What are we missing?
4. What must be decided or completed first?
5. What view should each person see now?

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
- Decisions and risks
- Typed Dependency Graph
- Execution-ready work graph
- Multiple projections: Outcome, Domain, Dependency, Risk

## Core UX

### 1. Understand current system

Create a System Graph from evidence before generating tasks.

### 2. Analyze a change

Do not jump directly to implementation tasks. First derive outcomes, then scan impact across multiple lenses.

### 3. Critique the analysis

Look specifically for omissions, cross-cutting concerns, lifecycle gaps, permission gaps, failure modes, migration concerns, and external-system effects.

### 4. Build the work graph

Only after outcomes and impacts are understood should implementation work be generated and ordered.

### 5. Re-project the same graph

The underlying project graph stays stable while the UI can project it by:

- Outcome
- Domain
- Dependency
- Risk
- Actor
- Timeline

## Product principles

1. **Outcome before task.**
2. **Evidence before certainty.** Separate observed system facts from model inference.
3. **Multiple lenses beat one perfect decomposition axis.**
4. **Edges are typed.** `blocks` is not enough.
5. **Not every node is a task.** Decisions, risks, outcomes, milestones, and deliverables are first-class.
6. **Graph structure is deterministic where possible.** LLMs reason about meaning; code checks cycles, ordering, reachability, critical paths, duplicates, and invariants.
7. **Human edits are authoritative.** Re-planning must preserve explicit user constraints.
8. **The first wow moment is discovering something the user missed.**

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
