# Decomposion survival gate: measured evidence before product expansion

## Decision (2026-10-24)

**Keep the existing subscription-agent Skill as the only primary product.**
Do not add an orchestrator, database, proprietary scheduler, or new UI framework.
The current priority is proving that users can inspect the original request, split
rationale, and stopping boundary, then showing that the decomposition improves
independent task outcomes against a plain-agent baseline.

## Evidence hierarchy

1. **Deterministic enumeration**: falsifies universal claims under stated assumptions.
2. **Actual isolated agent runs**: measures task success, wall time, tokens, handoff
   and merge effort on the same pinned code and hidden acceptance tests.
3. **Human usability tests**: measures comprehension, omission detection and reuse.

Never present (1) as evidence for (2) or (3). Tests passing prove implementation
consistency, not Decomposion superiority.

## Experiment 0 — exact synthetic counterexamples

Run `python -m experiments.decomposition_boundary --out /tmp/boundary.csv`.
Three fixed workload distributions, two identical workers, four overhead assumptions,
exact exhaustive assignment. Total pure work is 120 units in every comparison.
Overhead is charged per task beyond the first on the critical path as a deliberately
simplified accounting assumption. No dependencies, merge conflicts, failures or model
calls are simulated. Results are deterministic, not confidence intervals.

Hypotheses tested: universal benefit of splitting; effect of unsplittable bottlenecks;
sensitivity to handoff cost. All must have counterexamples. This experiment is a
**guardrail against unjustified optimization claims**, not an optimizer.

## Gate 1 — first human use (not yet measured)

Recruit at least 5 independent developers. Give each a real task and collect the
raw output and whether they could correctly identify original request, split axis,
children, why each split occurred, and what remains unknown. Preserve failures.
Compare ID-list output against named decomposition tree on the same plan. Record
time-to-answer and factual accuracy. Do not call this gate complete from CI.

## Gate 2 — independent plan-quality comparison (not yet measured)

Freeze 5 repository tasks, source commits, and hidden acceptance tests. Randomize
plain prompt vs Decomposion within the same model/effort budget. Use independent
reviewers blind to strategy for missed obligations, unsupported claims, and
unnecessary work. Track token and wall-time cost. Do not change the golden set after
seeing candidate plans. Minimum 3 repeated runs per condition for a pilot; this is
not sufficient to claim population-wide significance.

## Gate 3 — execution efficiency (not yet measured)

Only after Gate 2, execute coarse/normal/fine plans on identical isolated worktrees,
same model, same task, same acceptance tests. Start with one agent, then two agents.
Include integration and rework time, quality regressions and cost. Missing dependency
edges are NOT proof that tasks are safe to run concurrently.

## Stop / pivot rules

If independent users cannot interpret the decomposition, fix presentation before
building a new graph app. If plan quality does not improve against a plain prompt,
retain only useful structured export/evaluation tooling; do not claim superior
planning. If quality improves but execution time does not, position as a planning
review tool, not a speed optimizer. If repeat usage remains absent, freeze feature
development and maintain the minimal open-source skill.

## Constraints

No fabricated benchmark, no guessed savings percentage, no automatic feature
expansion. Every completed gate needs raw observations, immutable test input,
source revision, method, measured outcome, and an explicit limitation statement.
