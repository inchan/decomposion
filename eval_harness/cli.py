from __future__ import annotations

import argparse
from pathlib import Path

from .golden import GoldenCaseError, load_case


def validate_directory(root: Path) -> int:
    paths = sorted(root.rglob("*.yaml"))
    if not paths:
        print(f"No golden cases found under {root}")
        return 1

    failures = 0
    for path in paths:
        try:
            case = load_case(path)
            print(f"PASS {case.case_id} ({path})")
        except (GoldenCaseError, OSError) as exc:
            failures += 1
            print(f"FAIL {path}: {exc}")

    print(f"\nValidated {len(paths)} golden case(s); failures={failures}")
    return 1 if failures else 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Decomposion golden-set files")
    parser.add_argument("--golden-dir", default="golden", help="Golden-set root directory")
    args = parser.parse_args()
    return validate_directory(Path(args.golden_dir))


if __name__ == "__main__":
    raise SystemExit(main())
