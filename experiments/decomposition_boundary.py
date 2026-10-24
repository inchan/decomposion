"""Bounded, reproducible decomposition counterexamples; NOT agent performance data."""
from __future__ import annotations
import csv
import itertools
import json
from pathlib import Path

CASES = {
    "balanced": ((30, 30, 30, 30), (15,) * 8),
    "skewed": ((80, 20, 10, 10), (40, 40, 20, 10, 10)),
    "unsplittable": ((80, 20, 10, 10), (80, 10, 10, 10, 10)),
}
OVERHEADS = (0, 2, 8, 20)


def makespan(tasks: tuple[int, ...], workers: int = 2) -> int:
    """Exact optimum for independent tasks with identical workers, not a DAG."""
    if workers < 1 or len(tasks) > 16 or any(t <= 0 for t in tasks):
        raise ValueError("bounded positive tasks and workers required")
    best = sum(tasks)
    for assignment in itertools.product(range(workers), repeat=len(tasks)):
        loads = [0] * workers
        for task, worker in zip(tasks, assignment):
            loads[worker] += task
        best = min(best, max(loads))
    return best


def run() -> list[dict]:
    rows = []
    for case, (coarse, fine) in CASES.items():
        assert sum(coarse) == sum(fine) == 120
        for overhead in OVERHEADS:
            a = makespan(coarse) + overhead * (len(coarse) - 1)
            b = makespan(fine) + overhead * (len(fine) - 1)
            rows.append({
                "case": case, "overhead": overhead, "coarse": a, "fine": b,
                "winner": "coarse" if a < b else "fine" if b < a else "tie",
            })
    return rows


def main() -> None:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    if args.out.exists():
        parser.error("output exists: preserve previous measurement")
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("x", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["case", "overhead", "coarse", "fine", "winner"])
        writer.writeheader()
        writer.writerows(run())
    print(json.dumps({"cases": len(run()), "type": "synthetic_exact_enumeration",
                      "live_agent_runs": 0, "out": str(args.out)}))


if __name__ == "__main__":
    main()
