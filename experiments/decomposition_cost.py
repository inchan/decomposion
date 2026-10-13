"""Deterministic, synthetic two-worker scheduling counterexamples. No model calls."""
import itertools
import csv
from pathlib import Path

def best(durations, agents=2):
    return min(max(sum(t for t, a in zip(durations, assignment) if a == worker)
                   for worker in range(agents))
               for assignment in itertools.product(range(agents), repeat=len(durations)))

SCENARIOS = {
    "balanced": ([30]*4, [15]*8),
    "skewed": ([80,20,10,10], [40,40,20,10,10]),
    "one_block": ([120], [30]*4),
}

def run():
    rows = []
    for name, (coarse, fine) in SCENARIOS.items():
        assert sum(coarse) == sum(fine) == 120
        for overhead in (0,2,5,10,20):
            c = best(coarse) + overhead*(len(coarse)-1)
            f = best(fine) + overhead*(len(fine)-1)
            rows.append(dict(scenario=name, overhead_per_added_task=overhead,
                             coarse_tasks=len(coarse), fine_tasks=len(fine),
                             coarse_time=c, fine_time=f,
                             winner="fine" if f<c else "coarse" if c<f else "tie"))
    return rows

if __name__ == "__main__":
    rows = run()
    with Path("results.csv").open("w", newline="") as stream:
        writer=csv.DictWriter(stream,fieldnames=rows[0])
        writer.writeheader()
        writer.writerows(rows)
    print(f"{len(rows)} synthetic comparisons written")
