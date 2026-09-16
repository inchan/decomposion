"""Create an isolated local interpreter and install this checkout, not a PyPI namesake."""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
import venv
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--venv", type=Path)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    target = args.venv or root / ".venv"
    if sys.version_info < (3, 11):
        parser.error("Python 3.11 or newer is required")
    if target.is_symlink():
        parser.error("Refusing a symlink virtual environment")
    if target.exists() and not (target / "pyvenv.cfg").is_file():
        parser.error("Existing directory is not a virtual environment; choose another path")
    if not target.exists():
        venv.EnvBuilder(with_pip=True).create(target)
    python = target.resolve() / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    subprocess.run([str(python), "-m", "pip", "install", "-e", f"{root}[dev]"], check=True)
    subprocess.run([str(python), "-m", "pip", "check"], check=True)
    subprocess.run([str(python), "-m", "decomposion_lab.cli", "doctor"], check=True)
    print(f"Installed from {root}. No target application or LLM was started.")
    print(f"Run: {python} -m pytest {root / 'tests'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
