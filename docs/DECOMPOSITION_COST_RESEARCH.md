# Decomposition granularity: falsification experiment

## Purpose
Evaluate whether "more decomposition always reduces completion time" can hold under a simple, transparent scheduling model. This is a **counterexample**, not a real agent benchmark, and does not identify a universal optimum.

## Assumptions
- Two identical agents; total pure work = 120 synthetic time units.
- No precedence constraints, file conflicts, context limits, failure or stochasticity.
- Each indivisible task assigned to exactly one worker.
- Exhaustive search over all worker assignments finds minimum maximum load.
- Add a **hypothetical serial overhead** of h per extra task, including the first split from a single task. Formula: estimated makespan = minimum maximum load + h*(number of tasks - 1).
- Overhead is a sensitivity parameter, **not measured**. This model deliberately simplifies coordination and may overestimate serial overhead.

## Hypotheses and results
1. More tasks are always faster: **falsified**. Balanced 4×30 vs 8×15 gives the same 60-unit pure makespan; with h=2 the finer option takes 74 vs 66.
2. More tasks never help with fixed worker count: **falsified**. Skewed 80/20/10/10 gives 80 units; splitting 80 into 40/40 gives 60 units before overhead, despite only two workers.
3. There is a universal optimal task count: **not supported**. Winner changes with distribution and overhead. In the skewed example, fine wins for h=0,2,5,10 and ties at h=20.
4. An agent-efficiency score can be inferred from the plan graph alone: **not supported**. Actual task durations, coordination, integration, conflicts, and model capabilities are missing.

## Simulated adversarial panel (not real external reviewers)
- Scheduling researcher: the exhaustive two-worker partition is valid **within the specified model**, but ignores dependencies and heterogeneity.
- Coding-agent engineer: "one task" is not always indivisible; splitting can also reduce context pressure or increase merge conflicts.
- Evaluation researcher: no general performance conclusion is permitted without independent tasks, repeated runs, and measured outcomes.
- Product reviewer: do not expose a numeric optimality score to users until calibrated against real outcomes.

## Decision
Keep granularity levels as user-requested work-unit sizes, not optimality ranks. Keep decomposition, agent assignment and presentation depth separate. In future, measure wall time, quality, rework, conflict, context and integration before claiming optimal splits. Do not add a scheduler or optimizer now.

## Reproduce
`python experiments/decomposition_cost.py` (run from a temporary directory if you want to keep the repository clean). Output: `results.csv` with 15 deterministic rows.

## Limitations
This experiment **does not** validate the quality of decomposion Skill, prove Tree superiority, test actual subscription agents, or compare decomposition axes. It only rejects universal claims through explicit counterexamples.
