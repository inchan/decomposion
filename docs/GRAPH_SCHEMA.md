# Graph Schema

## Canonical node kinds

The graph is intentionally richer than a task DAG.

- `system` — existing component/domain/data store/external system
- `goal` — requested change intent
- `outcome` — state that must become true
- `decision` — unresolved choice that constrains downstream work
- `risk` — uncertainty or failure mode
- `deliverable` — concrete artifact or contract
- `task` — executable, independently verifiable work
- `milestone` — meaningful completion boundary

## Canonical edge kinds

- `contains`
- `affects`
- `requires_decision`
- `requires_information`
- `requires_data`
- `requires_contract`
- `blocks_execution`
- `produces_for`
- `invalidates`
- `mitigates`
- `evidences`
- `can_parallelize_with`

## Node contract

```json
{
  "id": "node_...",
  "kind": "task",
  "title": "Apply document ACL to retrieval",
  "summary": "Ensure retrieval returns only documents visible to the requesting principal.",
  "status": "proposed",
  "confidence": 0.92,
  "source_type": "inferred",
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

## Edge contract

```json
{
  "id": "edge_...",
  "from": "decision_acl_model",
  "to": "task_retrieval_acl",
  "kind": "requires_decision",
  "rationale": "Retrieval enforcement cannot be implemented until the ACL semantics are chosen.",
  "confidence": 0.98,
  "evidence_ids": ["ev_456"]
}
```

## Evidence contract

```json
{
  "id": "ev_...",
  "source": "docs/architecture.md",
  "location": "Permission Model",
  "excerpt_hash": "sha256:...",
  "captured_at": "ISO-8601 timestamp",
  "content": "Optional normalized excerpt or structured fact"
}
```

## Invariants

1. A `task` cannot be the only child of an `outcome` if the outcome spans multiple affected domains and no impact analysis exists.
2. A completed `task` requires completion evidence.
3. A `decision` may block tasks but must never be silently converted into an implementation task.
4. `can_parallelize_with` is symmetric at query time.
5. `blocks_execution`, `requires_*`, and `produces_for` must remain acyclic within the execution subgraph.
6. Human-confirmed nodes and edges cannot be deleted by re-analysis without an explicit conflict record.
7. Every inferred high-impact node should retain a rationale and evidence reference where evidence exists.
8. Projection metadata must not alter canonical graph semantics.

## Projection model

Views are projections over the same graph, not separate plans.

A projection may define:

- visible node kinds
- grouping axis
- ordering axis
- edge filter
- collapsed depth
- highlight predicate

Example:

```json
{
  "name": "risk-view",
  "group_by": "attributes.risk_level",
  "visible_kinds": ["outcome", "decision", "risk", "task"],
  "edge_kinds": ["affects", "mitigates", "blocks_execution"]
}
```

## Revision model

Every analysis that changes the graph creates a revision with:

- previous revision id
- added nodes/edges
- removed nodes/edges
- modified fields
- reason
- triggering actor/tool call
- human overrides preserved or conflicted

This enables explainable re-planning and later evaluation.
