# Graph Schema

## Schema maturity

This document defines the current working IR, not a permanently frozen ontology. New node or edge kinds should be promoted only after repeated evaluation failures demonstrate the need.

## Minimal canonical node kinds

- `system` — existing component/domain/data store/external system
- `goal` — requested change intent
- `outcome` — state that must become true
- `decision` — unresolved choice that constrains downstream work
- `risk` — uncertainty or failure mode
- `task` — executable, independently verifiable work
- `evidence` — version-addressable support for graph assertions

`deliverable` and `milestone` remain candidate kinds until evaluation demonstrates that representing them as first-class nodes improves reasoning or UX.

## Epistemic state

Every material assertion must expose what we know and how we know it.

Canonical epistemic states:

- `observed` — directly supported by current evidence
- `inferred` — reasoned from evidence
- `proposed` — future design choice
- `unknown` — required fact is not established by available evidence
- `contradicted` — credible evidence conflicts
- `human_confirmed` — explicitly accepted or edited by a human

`unknown` is a valid result. The engine must not convert missing information into an inferred fact just to complete a graph.

## Working edge kinds

Semantic relationships:

- `contains`
- `affects`
- `mitigates`
- `evidences`
- `invalidates`

Execution relationships:

- `requires_decision`
- `requires_information`
- `requires_data`
- `requires_contract`
- `blocks_execution`
- `produces_for`

Concurrency is not stored simply because two nodes have no dependency. Potential parallelism is derived from the dependency graph. Explicit resource or safety constraints may be stored separately as concurrency constraints.

## Dependency execution semantics

Every execution edge must declare:

- `semantic_type` — why the relationship exists;
- `execution_effect` — `blocking`, `non_blocking`, or `advisory`;
- `strength` — `hard` or `soft`;
- `resolution_condition` — objective condition that satisfies the dependency;
- `invalidation_policy` — whether upstream change reopens or merely warns downstream work.

Example:

```json
{
  "id": "edge_acl_decision_retrieval",
  "from": "decision_acl_model",
  "to": "task_retrieval_acl",
  "semantic_type": "requires_decision",
  "execution_effect": "blocking",
  "strength": "hard",
  "resolution_condition": "decision_acl_model.status == 'resolved'",
  "invalidation_policy": "reopen_downstream",
  "rationale": "Retrieval enforcement cannot be implemented until ACL semantics are chosen.",
  "evidence_ids": ["ev_456"]
}
```

## Node contract

```json
{
  "id": "task_retrieval_acl",
  "kind": "task",
  "title": "Apply document ACL to retrieval",
  "summary": "Ensure retrieval returns only documents visible to the requesting principal.",
  "status": "proposed",
  "epistemic_state": "inferred",
  "confidence_signal": "high",
  "tags": ["rag", "permission"],
  "attributes": {
    "domain": "retrieval",
    "actor": "user",
    "risk_level": "high"
  },
  "evidence_ids": ["ev_123"],
  "created_by": "impact_scanner"
}
```

`confidence_signal` is not a calibrated probability. Raw model confidence may be retained in trace metadata for later calibration experiments.

## Evidence contract

Evidence must be version-addressable where possible.

```json
{
  "id": "ev_...",
  "source_type": "repository_file",
  "source": "docs/architecture.md",
  "location": "Permission Model",
  "content_hash": "sha256:...",
  "version": {
    "repository_commit": "abc123...",
    "blob_sha": "def456..."
  },
  "captured_at": "ISO-8601 timestamp"
}
```

For mutable document systems use the strongest available immutable identifier: document version, revision number, ETag, content hash, or equivalent.

## Staleness and contradiction

An assertion becomes `stale_candidate` when its supporting evidence version is no longer current.

When credible sources disagree, do not silently choose one. Create a contradiction record containing:

- conflicting assertions;
- evidence references;
- source freshness;
- confidence/provenance;
- resolution owner or required follow-up.

## Invariants

1. A completed `task` requires completion evidence.
2. A `decision` may block tasks but must never be silently converted into an implementation task.
3. Hard blocking execution edges must remain acyclic.
4. Human-confirmed nodes and edges cannot be deleted by re-analysis without an explicit conflict record.
5. Every inferred high-impact node must retain rationale and provenance.
6. Unknown facts must not satisfy hard dependency conditions.
7. Contradicted facts must not be silently promoted to observed state.
8. Projection metadata must not alter canonical graph semantics.
9. Re-analysis against newer evidence must mark affected assertions for freshness review.

## Projection model

Views are projections over the same graph, not separate plans.

Initial projections:

- Outcome
- Domain
- Dependency
- Risk

Timeline remains experimental until duration/resource semantics exist.

## Revision model

Every graph mutation creates a revision containing:

- revision id;
- previous revision id;
- added/removed/modified nodes and edges;
- triggering actor/tool call;
- evidence versions used;
- human overrides preserved or conflicted.

Mutating clients should use optimistic concurrency with `expected_revision`. A stale writer must receive an explicit revision conflict instead of overwriting newer reasoning.
