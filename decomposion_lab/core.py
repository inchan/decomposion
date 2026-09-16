"""Fail-closed workspaces and append-only manual experiment records.

This module never invokes a coding agent or an LLM provider. Filesystem isolation
is organizational; use a separate container/VM for an actual security boundary.
"""
from __future__ import annotations

import contextlib
import importlib.metadata
import json
import math
import os
import platform
import shutil
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from . import __version__
from .protocol import LabError, build_queue, digest, json_bytes, load_suite, render_request


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def git(*args: str, cwd: Path | None = None) -> str:
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    env.update(GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull, GIT_TERMINAL_PROMPT="0")
    try:
        result = subprocess.run(
            ["git", "-c", f"core.hooksPath={os.devnull}", *args], cwd=cwd,
            env=env, text=True, encoding="utf-8", errors="replace", capture_output=True,
            timeout=300, check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise LabError(f"Git unavailable or timed out: {exc}") from exc
    if result.returncode:
        raise LabError(f"Git failed: {result.stderr.strip()}")
    return result.stdout.strip()


def environment() -> dict:
    versions = {}
    for name in ("PyYAML", "pytest", "setuptools"):
        try:
            versions[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            versions[name] = None
    files = sorted(Path(__file__).parent.glob("*.py"))
    source_hash = digest(b"".join(p.name.encode() + b"\0" + p.read_bytes() for p in files))
    return {"package_version": __version__, "source_sha256": source_hash,
            "python": platform.python_version(), "platform": platform.platform(),
            "dependencies": versions, "git": git("--version")}


def write_json(path: Path, data: dict | list) -> None:
    temporary = path.with_name(path.name + ".tmp")
    with temporary.open("xb") as handle:
        handle.write(json_bytes(data))
    os.replace(temporary, path)


def read_json(path: Path) -> dict:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise LabError(f"Invalid/missing record {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise LabError(f"{path} must contain an object")
    return data


def inside(root: Path, *parts: str) -> Path:
    path = root.joinpath(*parts)
    if not path.resolve().is_relative_to(root.resolve()):
        raise LabError("Workspace path escapes its root")
    return path


@contextlib.contextmanager
def exclusive(root: Path):
    lock = root / ".lab-lock"
    try:
        lock.mkdir()
    except FileExistsError as exc:
        raise LabError("Workspace locked. Check for another process; inspect/remove a stale .lab-lock manually.") from exc
    try:
        (lock / "owner.json").write_bytes(json_bytes({"pid": os.getpid(), "created_at": utcnow()}))
        yield
    finally:
        shutil.rmtree(lock)


def verify_repository(path: Path, commit: str) -> None:
    if path.is_symlink() or not (path / ".git").is_dir():
        raise LabError(f"Expected an independent checkout: {path}")
    if git("rev-parse", "HEAD", cwd=path) != commit:
        raise LabError("Target commit changed; refusing to reset or overwrite it")
    if git("status", "--porcelain", "--untracked-files=all", "--ignored", cwd=path):
        raise LabError("Target checkout is dirty (including ignored files); refusing to overwrite it")


def init_workspace(suite_path: Path, workspace: Path, profile: str, seed: int,
                   source: Path | None = None) -> dict:
    suite_path = suite_path.resolve()
    if workspace.is_symlink():
        raise LabError("Workspace itself must not be a symlink")
    workspace = workspace.resolve()
    # Avoid discovering the controller's instructions/gold via an ancestor directory.
    try:
        controller = Path(git("rev-parse", "--show-toplevel", cwd=suite_path)).resolve()
    except LabError:
        controller = suite_path
    if workspace.is_relative_to(controller):
        raise LabError("Use a workspace outside the controller repository")
    suite = load_suite(suite_path)
    queue = build_queue(suite, profile, seed)
    identity = {"suite": suite, "profile": profile, "seed": seed, "queue": queue}
    fingerprint = digest(json_bytes(identity))
    if workspace.exists():
        lock = read_json(workspace / "experiment.lock.json")
        if lock.get("fingerprint") != fingerprint:
            raise LabError("Workspace protocol differs. Use a new directory; old results are preserved.")
        if lock["environment"]["source_sha256"] != environment()["source_sha256"]:
            raise LabError("Lab implementation changed; create a new workspace")
        verify_repository(workspace / "target", suite["manifest"]["target"]["commit"])
        return lock
    target = suite["manifest"]["target"]
    if source is not None:
        source = source.resolve()
        verify_repository(source, target["commit"])
    workspace.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix=".decomposion-init-", dir=workspace.parent))
    try:
        checkout = staging / "target"
        if source is not None:
            git("clone", "--no-hardlinks", "--no-checkout", "--", str(source), str(checkout))
        else:
            git("init", str(checkout))
            git("remote", "add", "origin", target["clone_url"], cwd=checkout)
            git("fetch", "--depth=1", "origin", target["commit"], cwd=checkout)
        git("checkout", "--detach", target["commit"], cwd=checkout)
        verify_repository(checkout, target["commit"])
        (staging / "runs").mkdir()
        lock = {**identity, "fingerprint": fingerprint, "created_at": utcnow(),
                "environment": environment(), "mode": "manual-planning-only"}
        write_json(staging / "experiment.lock.json", lock)
        # A concurrent init must not replace an existing workspace.
        try:
            workspace.mkdir()
        except FileExistsError as exc:
            raise LabError("Workspace appeared during initialization; refusing replacement") from exc
        for child in sorted(staging.iterdir(), key=lambda p: p.name == "experiment.lock.json"):
            child.rename(workspace / child.name)
        return lock
    finally:
        if staging.exists():
            shutil.rmtree(staging)


def load_lock(workspace: Path) -> dict:
    lock = read_json(workspace / "experiment.lock.json")
    identity = {k: lock[k] for k in ("suite", "profile", "seed", "queue")}
    if digest(json_bytes(identity)) != lock.get("fingerprint"):
        raise LabError("Experiment lock was modified. Create a new workspace instead.")
    return lock


def start_run(workspace: Path, run_id: str, controls: dict) -> dict:
    workspace = workspace.resolve()
    required = {"agent", "agent_version", "model", "thinking", "execution_environment"}
    if set(controls) != required or any(not isinstance(v, str) or not v.strip() for v in controls.values()):
        raise LabError("Provide exact agent/version/model/thinking/environment controls")
    with exclusive(workspace):
        lock = load_lock(workspace)
        if lock["environment"]["source_sha256"] != environment()["source_sha256"]:
            raise LabError("Lab implementation changed; create a new workspace")
        row = next((r for r in lock["queue"] if r["run_id"] == run_id), None)
        if row is None:
            raise LabError(f"Unknown run ID: {run_id}")
        controls_path = workspace / "controls.json"
        if controls_path.exists() and read_json(controls_path) != controls:
            raise LabError("Agent/model/settings differ from this experiment. Use a new workspace.")
        run = inside(workspace, "runs", run_id)
        if run.exists():
            raise LabError("Run already started; use status/record or create a new experiment")
        target = workspace / "target"
        commit = lock["suite"]["manifest"]["target"]["commit"]
        verify_repository(target, commit)
        staging = Path(tempfile.mkdtemp(prefix=".run-", dir=workspace / "runs"))
        try:
            git("clone", "--no-hardlinks", "--no-checkout", "--", str(target), str(staging / "repo"))
            git("checkout", "--detach", commit, cwd=staging / "repo")
            verify_repository(staging / "repo", commit)
            request = render_request(lock, row, 1, []).encode()
            (staging / "request-01.md").write_bytes(request)
            meta = {"run_id": run_id, "strategy": row["strategy"], "prompt_id": row["prompt_id"],
                    "repeat": row["repeat"], "controls": controls, "environment": environment(),
                    "target_commit": commit, "experiment_fingerprint": lock["fingerprint"],
                    "started_at": utcnow(), "status": "awaiting_output", "stages": [],
                    "pending_stage": 1, "request_sha256": digest(request),
                    "stage_count": len(lock["suite"]["templates"]["stages"][row["strategy"]])}
            write_json(staging / "metadata.json", meta)
            if not controls_path.exists():
                write_json(controls_path, controls)
            staging.rename(run)
            return meta
        finally:
            if staging.exists():
                shutil.rmtree(staging)


def record_output(workspace: Path, run_id: str, stage: int, answer_path: Path,
                  duration_seconds: float | None = None) -> dict:
    if duration_seconds is not None and (not math.isfinite(duration_seconds) or duration_seconds < 0):
        raise LabError("duration_seconds must be finite and non-negative")
    answer = answer_path.read_bytes()
    if not answer.strip() or len(answer) > 10_000_000:
        raise LabError("Answer must be non-empty and at most 10 MB")
    try:
        answer.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise LabError("Answer must be UTF-8 text") from exc
    workspace = workspace.resolve()
    with exclusive(workspace):
        lock = load_lock(workspace)
        if lock["environment"]["source_sha256"] != environment()["source_sha256"]:
            raise LabError("Lab implementation changed; create a new workspace")
        row = next((r for r in lock["queue"] if r["run_id"] == run_id), None)
        if row is None:
            raise LabError("Run does not belong to this experiment")
        run = inside(workspace, "runs", run_id)
        meta = read_json(run / "metadata.json")
        if meta["experiment_fingerprint"] != lock["fingerprint"]:
            raise LabError("Run belongs to another protocol revision")
        verify_repository(run / "repo", meta["target_commit"])
        # Idempotent retry must not accidentally submit a second stage.
        if 1 <= stage <= len(meta["stages"]):
            stored = inside(run, f"answer-{stage:02d}.md").read_bytes()
            if digest(answer) == meta["stages"][stage - 1]["answer_sha256"] == digest(stored):
                return meta
            raise LabError("Recorded output differs; never overwrite an existing answer")
        if stage != meta["pending_stage"] or meta["status"] == "recorded":
            raise LabError("Record exactly the pending stage, not a later/final-only answer")
        request = inside(run, f"request-{stage:02d}.md").read_bytes()
        if digest(request) != meta["request_sha256"]:
            raise LabError("Request changed after preparation; this run is not comparable")
        prior = []
        for prior_stage in meta["stages"]:
            data = inside(run, f"answer-{prior_stage['stage']:02d}.md").read_bytes()
            if digest(data) != prior_stage["answer_sha256"]:
                raise LabError("A previous answer changed; refusing contaminated stage")
            prior.append(data.decode("utf-8"))
        artifact = inside(run, f"answer-{stage:02d}.md")
        if artifact.exists() and artifact.read_bytes() != answer:
            raise LabError("Conflicting partial output exists; inspect before retrying")
        artifact.write_bytes(answer)
        meta["stages"].append({"stage": stage, "answer_sha256": digest(answer),
                               "request_sha256": digest(request), "recorded_at": utcnow(),
                               "operator_measured_seconds": duration_seconds})
        if stage == meta["stage_count"]:
            (run / "answer.md").write_bytes(answer)
            meta.update(status="recorded", pending_stage=None, ended_at=utcnow())
        else:
            next_request = render_request(lock, row, stage + 1, prior + [answer.decode("utf-8")]).encode()
            (run / f"request-{stage + 1:02d}.md").write_bytes(next_request)
            meta.update(pending_stage=stage + 1, request_sha256=digest(next_request))
        write_json(run / "metadata.json", meta)
        return meta


def status(workspace: Path) -> dict:
    workspace = workspace.resolve()
    lock = load_lock(workspace)
    rows = []
    for row in lock["queue"]:
        path = inside(workspace, "runs", row["run_id"], "metadata.json")
        meta = read_json(path) if path.exists() else {}
        rows.append({"run_id": row["run_id"], "status": meta.get("status", "not_started"),
                     "pending_stage": meta.get("pending_stage")})
    return {"experiment": lock["suite"]["manifest"]["experiment_id"],
            "fingerprint": lock["fingerprint"], "runs": rows,
            "recorded": sum(r["status"] == "recorded" for r in rows), "total": len(rows),
            "quality_evaluated": False,
            "note": "Recorded means captured, not correct. No live models or quality scores are produced by the lab."}


def audit(workspace: Path) -> dict:
    """Verify captured artifacts against recorded hashes; do not grade their meaning."""
    workspace = workspace.resolve()
    lock = load_lock(workspace)
    verified = 0
    for row in lock["queue"]:
        run = inside(workspace, "runs", row["run_id"])
        if not run.exists():
            continue
        meta = read_json(run / "metadata.json")
        if meta["experiment_fingerprint"] != lock["fingerprint"]:
            raise LabError(f"{row['run_id']}: wrong experiment fingerprint")
        verify_repository(run / "repo", lock["suite"]["manifest"]["target"]["commit"])
        prior = []
        for index, item in enumerate(meta["stages"], 1):
            if item["stage"] != index:
                raise LabError("Nonsequential recorded stages")
            request = inside(run, f"request-{index:02d}.md").read_bytes()
            expected_request = render_request(lock, row, index, prior).encode()
            answer = inside(run, f"answer-{index:02d}.md").read_bytes()
            if digest(request) != item["request_sha256"] or request != expected_request:
                raise LabError("Recorded request integrity check failed")
            if digest(answer) != item["answer_sha256"]:
                raise LabError("Recorded answer integrity check failed")
            prior.append(answer.decode("utf-8"))
        count = len(lock["suite"]["templates"]["stages"][row["strategy"]])
        if meta["status"] == "recorded":
            if len(prior) != count or inside(run, "answer.md").read_bytes() != prior[-1].encode("utf-8"):
                raise LabError("Final answer does not match the recorded last stage")
        else:
            pending = meta["pending_stage"]
            if pending != len(prior) + 1:
                raise LabError("Pending stage is inconsistent")
            request = inside(run, f"request-{pending:02d}.md").read_bytes()
            if request != render_request(lock, row, pending, prior).encode() or digest(request) != meta["request_sha256"]:
                raise LabError("Pending request integrity check failed")
        verified += 1
    return {"verified_runs": verified, "quality_evaluated": False,
            "note": "Integrity checks detect accidental changes, not malicious rewriting of all hashes."}
