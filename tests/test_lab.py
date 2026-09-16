from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

from decomposion_lab.cli import main
from decomposion_lab.core import (
    audit, exclusive, git, init_workspace, read_json, record_output, start_run, status,
)
from decomposion_lab.protocol import LabError, build_queue, load_suite

CONTROLS = {"agent": "codex", "agent_version": "test-fixture-not-a-live-agent",
            "model": "test-fixture-not-a-model", "thinking": "fixed",
            "execution_environment": "local"}


@pytest.fixture
def prepared(tmp_path):
    source = tmp_path / "source with spaces"
    git("init", str(source))
    (source / "architecture.md").write_text("Documents feed retrieval. Cache presence is unknown.\n")
    git("add", ".", cwd=source)
    git("-c", "user.name=Test", "-c", "user.email=test@example.invalid", "commit", "-m", "fixture", cwd=source)
    commit = git("rev-parse", "HEAD", cwd=source)
    suite = tmp_path / "suite"
    suite.mkdir()
    manifest = {"experiment_id": "test-lab", "version": 1,
                "target": {"repository": "example/project", "clone_url": "https://github.com/example/project.git", "commit": commit},
                "protocol": {"strategies": ["plain", "structured", "decomposion"],
                             "total_prompts": 10, "repeats": 3, "implementation_required": False,
                             "repository_mutation_allowed": False}}
    prompts = {"version": 1, "prompts": [{"id": f"P{i:02d}-change", "change": f"Analyze change {i}."} for i in range(1, 11)]}
    (suite / "manifest.yaml").write_text(yaml.safe_dump(manifest), encoding="utf-8")
    (suite / "prompts.yaml").write_text(yaml.safe_dump(prompts), encoding="utf-8")
    workspace = tmp_path / "lab with spaces"
    init_workspace(suite, workspace, "smoke", 17, source)
    return suite, workspace, source


def answer(tmp_path: Path, text="Fixture report: this is not a model response.") -> Path:
    path = tmp_path / "response.md"
    path.write_text(text, encoding="utf-8")
    return path


def test_matrix_sizes_and_frozen_order(prepared):
    suite, workspace, _ = prepared
    data = load_suite(suite)
    assert len(build_queue(data, "smoke", 17)) == 9
    full = build_queue(data, "full", 17)
    assert len(full) == len({r["run_id"] for r in full}) == 90
    assert full == build_queue(data, "full", 17)
    assert full != build_queue(data, "full", 18)
    assert status(workspace)["quality_evaluated"] is False


def test_init_is_idempotent_without_rewriting_lock(prepared):
    suite, workspace, source = prepared
    old = (workspace / "experiment.lock.json").read_bytes()
    init_workspace(suite, workspace, "smoke", 17, source)
    assert (workspace / "experiment.lock.json").read_bytes() == old
    with pytest.raises(LabError, match="protocol differs"):
        init_workspace(suite, workspace, "full", 17, source)


def test_dirty_repository_never_reset(prepared):
    suite, workspace, source = prepared
    path = workspace / "target" / "architecture.md"
    path.write_text("Keep my edits")
    with pytest.raises(LabError, match="dirty"):
        init_workspace(suite, workspace, "smoke", 17, source)
    assert path.read_text() == "Keep my edits"


def test_existing_unowned_directory_not_adopted(prepared, tmp_path):
    suite, _, source = prepared
    destination = tmp_path / "existing"
    destination.mkdir()
    (destination / "keep.txt").write_text("keep")
    with pytest.raises(LabError):
        init_workspace(suite, destination, "smoke", 17, source)
    assert (destination / "keep.txt").read_text() == "keep"


def test_source_wrong_commit_rejected(prepared, tmp_path):
    suite, _, source = prepared
    (source / "new.txt").write_text("new")
    git("add", ".", cwd=source)
    git("-c", "user.name=Test", "-c", "user.email=test@example.invalid", "commit", "-m", "later", cwd=source)
    with pytest.raises(LabError, match="commit changed"):
        init_workspace(suite, tmp_path / "another", "smoke", 17, source)


def test_run_independence_and_control_lock(prepared):
    _, workspace, _ = prepared
    start_run(workspace, "P01-plain-r01", CONTROLS)
    run = workspace / "runs/P01-plain-r01"
    assert (run / "repo/.git").is_dir()
    assert not (run / "repo/experiment.lock.json").exists()
    with pytest.raises(LabError, match="differ"):
        start_run(workspace, "P01-structured-r01", {**CONTROLS, "model": "different"})
    with pytest.raises(LabError, match="already started"):
        start_run(workspace, "P01-plain-r01", CONTROLS)


def test_actual_stages_required_and_outputs_preserved(prepared, tmp_path):
    _, workspace, _ = prepared
    run_id = "P01-decomposion-r01"
    start_run(workspace, run_id, CONTROLS)
    run = workspace / "runs" / run_id
    with pytest.raises(LabError, match="pending stage"):
        record_output(workspace, run_id, 4, answer(tmp_path))
    assert not (run / "request-02.md").exists()
    for stage in range(1, 5):
        raw = f"Fixture stage {stage}: 가상 테스트, not a model answer.\n"
        record_output(workspace, run_id, stage, answer(tmp_path, raw), duration_seconds=0.5)
        assert (run / f"answer-{stage:02d}.md").read_text() == raw
        if stage < 4:
            assert raw in (run / f"request-{stage + 1:02d}.md").read_text()
    assert read_json(run / "metadata.json")["status"] == "recorded"
    assert status(workspace)["recorded"] == 1
    assert status(workspace)["quality_evaluated"] is False


def test_record_retry_is_idempotent_and_cannot_overwrite(prepared, tmp_path):
    _, workspace, _ = prepared
    run_id = "P01-plain-r01"
    start_run(workspace, run_id, CONTROLS)
    saved = record_output(workspace, run_id, 1, answer(tmp_path, "original"))
    assert saved == record_output(workspace, run_id, 1, answer(tmp_path, "original"))
    with pytest.raises(LabError, match="never overwrite"):
        record_output(workspace, run_id, 1, answer(tmp_path, "changed"))


def test_tampered_request_rejected(prepared, tmp_path):
    _, workspace, _ = prepared
    run_id = "P01-plain-r01"
    start_run(workspace, run_id, CONTROLS)
    (workspace / "runs" / run_id / "request-01.md").write_text("changed instructions")
    with pytest.raises(LabError, match="Request changed"):
        record_output(workspace, run_id, 1, answer(tmp_path))


def test_tampered_prior_stage_rejected(prepared, tmp_path):
    _, workspace, _ = prepared
    run_id = "P01-decomposion-r01"
    start_run(workspace, run_id, CONTROLS)
    record_output(workspace, run_id, 1, answer(tmp_path))
    (workspace / "runs" / run_id / "answer-01.md").write_text("changed")
    with pytest.raises(LabError, match="previous answer changed"):
        record_output(workspace, run_id, 2, answer(tmp_path))


def test_modified_target_cannot_be_recorded(prepared, tmp_path):
    _, workspace, _ = prepared
    run_id = "P01-plain-r01"
    start_run(workspace, run_id, CONTROLS)
    (workspace / "runs" / run_id / "repo/architecture.md").write_text("mutated")
    with pytest.raises(LabError, match="dirty"):
        record_output(workspace, run_id, 1, answer(tmp_path))


@pytest.mark.parametrize("duration", [-1, float("nan"), float("inf")])
def test_invalid_duration(prepared, tmp_path, duration):
    with pytest.raises(LabError, match="finite"):
        record_output(prepared[1], "P01-plain-r01", 1, answer(tmp_path), duration)


def test_empty_answer_is_not_success(prepared, tmp_path):
    with pytest.raises(LabError, match="non-empty"):
        record_output(prepared[1], "P01-plain-r01", 1, answer(tmp_path, " \n"))


def test_lock_rejects_concurrent_writes(prepared):
    with exclusive(prepared[1]):
        with pytest.raises(LabError, match="locked"):
            start_run(prepared[1], "P01-plain-r01", CONTROLS)
    assert not (prepared[1] / ".lab-lock").exists()


def test_protocol_tampering_is_detected(prepared):
    path = prepared[1] / "experiment.lock.json"
    lock = json.loads(path.read_text())
    lock["queue"][0]["change"] = "leaked expected answer"
    path.write_text(json.dumps(lock))
    with pytest.raises(LabError, match="lock was modified"):
        status(prepared[1])


@pytest.mark.parametrize("field,value", [
    ("commit", "main"), ("commit", "-option"),
    ("clone_url", "https://user:secret@github.com/example/project.git"),
    ("clone_url", "ext::sh -c something"), ("repository", "../escape"),
])
def test_unsafe_target_manifest(prepared, field, value):
    suite, _, _ = prepared
    path = suite / "manifest.yaml"
    data = yaml.safe_load(path.read_text())
    data["target"][field] = value
    path.write_text(yaml.safe_dump(data))
    with pytest.raises(LabError):
        load_suite(suite)


def test_prompt_rejects_embedded_gold(prepared):
    path = prepared[0] / "prompts.yaml"
    data = yaml.safe_load(path.read_text())
    data["prompts"][0]["expected"] = ["secret"]
    path.write_text(yaml.safe_dump(data))
    with pytest.raises(LabError, match="no answers"):
        load_suite(prepared[0])


def test_prompt_ids_are_unique(prepared):
    path = prepared[0] / "prompts.yaml"
    data = yaml.safe_load(path.read_text())
    data["prompts"][1]["id"] = data["prompts"][0]["id"]
    path.write_text(yaml.safe_dump(data))
    with pytest.raises(LabError, match="Duplicate"):
        load_suite(prepared[0])


def test_cli_reports_failures_and_supports_paths_with_spaces(prepared, capsys):
    suite, workspace, _ = prepared
    assert main(["check-suite", "--suite", str(suite)]) == 0
    assert main(["lab", "status", "--workspace", str(workspace)]) == 0
    assert '"quality_evaluated": false' in capsys.readouterr().out
    assert main(["lab", "status", "--workspace", str(workspace / "missing")]) == 2


def test_cli_start_can_reuse_frozen_controls(prepared):
    workspace = str(prepared[1])
    assert main(["lab", "start", "--workspace", workspace, "--agent", "codex",
                 "--agent-version", "fixture", "--model", "fixture", "--thinking", "fixed",
                 "--execution-environment", "local"]) == 0
    assert main(["lab", "start", "--workspace", workspace]) == 0


def test_package_and_cli_versions_match():
    import tomllib
    from decomposion_lab import __version__
    assert tomllib.loads(Path("pyproject.toml").read_text())["project"]["version"] == __version__


def test_audit_detects_completed_answer_edits(prepared, tmp_path):
    workspace = prepared[1]
    run_id = "P01-plain-r01"
    start_run(workspace, run_id, CONTROLS)
    assert audit(workspace)["verified_runs"] == 1
    record_output(workspace, run_id, 1, answer(tmp_path))
    assert audit(workspace)["verified_runs"] == 1
    (workspace / "runs" / run_id / "answer.md").write_text("changed after completion")
    with pytest.raises(LabError, match="Final answer"):
        audit(workspace)


def test_audit_multi_stage(prepared, tmp_path):
    workspace = prepared[1]
    run_id = "P01-decomposion-r01"
    start_run(workspace, run_id, CONTROLS)
    for stage in range(1, 5):
        record_output(workspace, run_id, stage, answer(tmp_path, f"stage {stage}"))
        assert audit(workspace)["verified_runs"] == 1


def test_bad_version_and_profile_rejected(prepared):
    data = load_suite(prepared[0])
    with pytest.raises(LabError, match="profile"):
        build_queue(data, "typo", 1)
    path = prepared[0] / "manifest.yaml"
    contents = yaml.safe_load(path.read_text())
    contents["version"] = True
    path.write_text(yaml.safe_dump(contents))
    with pytest.raises(LabError, match="positive integer"):
        load_suite(prepared[0])


def test_missing_controls_and_unknown_run_rejected(prepared):
    with pytest.raises(LabError, match="Provide exact"):
        start_run(prepared[1], "P01-plain-r01", {})
    with pytest.raises(LabError, match="Unknown run"):
        start_run(prepared[1], "../../escape", CONTROLS)


def test_crlf_is_preserved_and_audited(prepared, tmp_path):
    workspace = prepared[1]
    run_id = "P01-plain-r01"
    start_run(workspace, run_id, CONTROLS)
    raw = tmp_path / "windows-output.md"
    raw.write_bytes(b"first\r\nsecond\r\n")
    record_output(workspace, run_id, 1, raw)
    assert (workspace / "runs" / run_id / "answer.md").read_bytes() == raw.read_bytes()
    assert audit(workspace)["verified_runs"] == 1
