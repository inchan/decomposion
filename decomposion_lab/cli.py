"""Provider-free experiment CLI; no command starts a paid model session."""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

from . import __version__
from .core import audit, environment, init_workspace, read_json, record_output, start_run, status
from .protocol import LabError, load_suite


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(prog="decomposion")
    root.add_argument("--version", action="version", version=f"decomposion {__version__}")
    commands = root.add_subparsers(dest="command", required=True)
    commands.add_parser("version")
    commands.add_parser("doctor")
    check = commands.add_parser("check-suite")
    check.add_argument("--suite", type=Path, default=Path("experiments/open-webui"))
    lab = commands.add_parser("lab").add_subparsers(dest="action", required=True)
    init = lab.add_parser("init", help="Clone a pinned target and freeze the protocol; no LLM calls")
    init.add_argument("--suite", type=Path, default=Path("experiments/open-webui"))
    init.add_argument("--profile", choices=("smoke", "full"), default="smoke")
    init.add_argument("--seed", type=int, default=20260915)
    init.add_argument("--source-dir", type=Path, help="Use a clean local checkout at the pinned commit (offline)")
    start = lab.add_parser("start", help="Prepare one independent run checkout and its first request")
    start.add_argument("--run", default="next")
    start.add_argument("--agent", choices=("codex", "claude-code"))
    start.add_argument("--agent-version")
    start.add_argument("--model")
    start.add_argument("--thinking")
    start.add_argument("--execution-environment", choices=("local", "cloud"))
    record = lab.add_parser("record", help="Capture a stage answer and prepare the next stage")
    record.add_argument("--run", required=True)
    record.add_argument("--stage", type=int, required=True)
    record.add_argument("--answer", type=Path, required=True)
    record.add_argument("--duration-seconds", type=float)
    show = lab.add_parser("status")
    verify = lab.add_parser("audit", help="Verify captured input/output hashes, not model quality")
    for cmd in (init, start, record, show, verify):
        cmd.add_argument("--workspace", type=Path, required=True)
    return root


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        if args.command == "version":
            result = {"version": __version__, "distribution": "decomposion-eval", "published": False}
        elif args.command == "doctor":
            result = environment()
            result["agents"] = {"codex": shutil.which("codex"), "claude-code": shutil.which("claude")}
            result["models_called"] = False
        elif args.command == "check-suite":
            suite = load_suite(args.suite)
            result = {"prompts": len(suite["prompts"]), "target": suite["manifest"]["target"],
                      "manifest_sha256": suite["manifest_sha256"], "prompts_sha256": suite["prompts_sha256"]}
        elif args.action == "init":
            lock = init_workspace(args.suite, args.workspace, args.profile, args.seed, args.source_dir)
            result = {"workspace": str(args.workspace.resolve()), "sessions": len(lock["queue"]),
                      "fingerprint": lock["fingerprint"], "models_called": False}
        elif args.action == "start":
            saved = args.workspace / "controls.json"
            controls = read_json(saved) if saved.exists() else {}
            for name in ("agent", "agent_version", "model", "thinking", "execution_environment"):
                value = getattr(args, name)
                if value is not None:
                    controls[name] = value
            if args.run == "next":
                candidates = [r for r in status(args.workspace)["runs"] if r["status"] == "not_started"]
                if not candidates:
                    raise LabError("No unstarted runs remain. Use lab status to find pending outputs.")
                args.run = candidates[0]["run_id"]
            result = start_run(args.workspace, args.run, controls)
            run = args.workspace.resolve() / "runs" / args.run
            result.update(repo_path=str(run / "repo"), request_path=str(run / "request-01.md"),
                          instruction="Open a fresh read-only agent session in repo_path. Supply request_path contents; save the unedited answer outside repo_path. The lab does not launch the agent.")
        elif args.action == "record":
            result = record_output(args.workspace, args.run, args.stage, args.answer, args.duration_seconds)
            if result["pending_stage"]:
                result = {**result, "next_request": str(args.workspace.resolve() / "runs" / args.run / f"request-{result['pending_stage']:02d}.md")}
        elif args.action == "audit":
            result = audit(args.workspace)
        else:
            result = status(args.workspace)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (LabError, OSError, KeyError, TypeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
