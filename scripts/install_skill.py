"""Install the same self-contained skill for Codex or Claude Code. No pip/API needed."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import sys
import tempfile

VERSION = '0.2.0'
ROOT = Path(__file__).resolve().parents[1]


def install(project: Path, agent: str) -> dict:
    project = project.resolve(strict=True)
    if not project.is_dir() or agent not in {'codex', 'claude'}:
        raise ValueError('supply an existing project directory and codex/claude')
    destination = project / ('.agents' if agent == 'codex' else '.claude') / 'skills' / 'decomposion'
    if any(p.is_symlink() for p in (destination, *destination.parents)):
        raise ValueError('refusing symlink installation path')
    files = {
        'SKILL.md': (ROOT / 'skills/decomposion/SKILL.md').read_bytes(),
        'scripts/review.py': (ROOT / 'skills/decomposion/scripts/review.py').read_bytes(),
        'scripts/_core.py': (ROOT / 'planning_eval/core.py').read_bytes(),
    }
    manifest = {'name': 'decomposion', 'version': VERSION,
                'files_sha256': {k: hashlib.sha256(v).hexdigest() for k, v in files.items()}}
    files['INSTALL.json'] = (json.dumps(manifest, sort_keys=True, indent=2) + '\n').encode()
    if destination.exists():
        existing = {p.relative_to(destination).as_posix(): p.read_bytes()
                    for p in destination.rglob('*') if p.is_file() and not p.is_symlink()}
        if any(p.is_symlink() for p in destination.rglob('*')) or existing != files:
            raise ValueError('existing skill differs; preserve/rename it before installing this version')
        return {'status': 'unchanged', 'path': str(destination), **manifest}
    destination.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix='.decomposion-install-', dir=destination.parent))
    try:
        for name, data in files.items():
            path = staging / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
        # Reserve the name; an existing installation is never replaced.
        destination.mkdir(exist_ok=False)
        for child in staging.iterdir():
            child.rename(destination / child.name)
    finally:
        shutil.rmtree(staging)
    return {'status': 'installed', 'path': str(destination), **manifest}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--agent', required=True, choices=('codex', 'claude'))
    parser.add_argument('--project', required=True, type=Path)
    args = parser.parse_args()
    if sys.version_info < (3, 11):
        parser.error('Python 3.11 or later required')
    try:
        print(json.dumps(install(args.project, args.agent), indent=2))
        return 0
    except (OSError, ValueError) as exc:
        print(f'Install failed: {exc}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
