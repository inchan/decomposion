# ADR 0001 — Planning Eval v1 before product expansion

Status: proposed for Step 1 review

## Decision

Decomposion will validate planning quality before expanding the planning engine or visual review UI. Planning Eval v1 uses a constraint-graph reference, multidimensional scorecard, explicit severity/error taxonomy, and separate deterministic/semantic/human judgment layers.

## Consequences

- Existing ten Open WebUI prompts are not promoted to Golden cases automatically.
- Visual UX quality is evaluated later with a separate human-review benchmark.
- No single composite score is used in v1.
- Semantic judges cannot silently replace human adjudication.
- Novel findings remain neutral/unadjudicated until reviewed.
- Step 2 is limited to three deep reference cases before schema expansion.
