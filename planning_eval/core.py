"""Reference constraints, graph checks and auditable review scoring.

No substring/embedding heuristic turns a model answer into a semantic grade.
A review supplies judgments; this module validates their provenance and counts them.
"""
from __future__ import annotations

import hashlib
import json
from collections import Counter, deque
from pathlib import Path
from typing import Any

KINDS = {"outcome", "task", "impact", "decision", "risk", "unknown"}
STATES = {"observed", "inferred", "proposed", "unknown", "contradicted"}
SEVERITIES = ("critical", "major", "minor")
RELATIONS = {"precedes", "informs", "affects"}
ISSUE_CODES = {"UNDER_DECOMPOSITION", "OVER_DECOMPOSITION", "UNSUPPORTED_CLAIM", "FALSE_IMPACT", "BAD_DEPENDENCY"}


def digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False, allow_nan=False,
                                    separators=(",", ":")).encode()).hexdigest()


def load_json(path: str | Path) -> dict:
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"duplicate JSON key: {key}")
            result[key] = value
        return result
    value = json.loads(Path(path).read_bytes().decode("utf-8"), object_pairs_hook=unique,
                       parse_constant=lambda value: (_ for _ in ()).throw(ValueError(f"nonfinite JSON: {value}")))
    if not isinstance(value, dict):
        raise ValueError("JSON root must be an object")
    return value


def text(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be nonempty text")
    return value


def records(value: Any, name: str) -> list[dict]:
    if not isinstance(value, list) or any(not isinstance(v, dict) for v in value):
        raise ValueError(f"{name} must be a list of objects")
    return value


def strings(value: Any, name: str) -> list[str]:
    if not isinstance(value, list) or any(not isinstance(v, str) or not v.strip() for v in value):
        raise ValueError(f"{name} must be a list of nonempty strings")
    if len(value) != len(set(value)):
        raise ValueError(f"duplicate values in {name}")
    return value


def index(items: list[dict], name: str) -> dict[str, dict]:
    result = {}
    for item in records(items, name):
        key = text(item.get("id"), f"{name}.id")
        if key in result:
            raise ValueError(f"duplicate {name} id: {key}")
        result[key] = item
    return result


def reachable(start: str, end: str, pairs: list[tuple[str, str]]) -> bool:
    """Strict (nonzero-length) reachability. Only callers' precedence edges enter."""
    adjacency: dict[str, list[str]] = {}
    for source, target in pairs:
        adjacency.setdefault(source, []).append(target)
    queue, seen = deque(adjacency.get(start, [])), set()
    while queue:
        current = queue.popleft()
        if current == end:
            return True
        if current not in seen:
            seen.add(current)
            queue.extend(adjacency.get(current, []))
    return False


def has_cycle(ids: set[str], pairs: list[tuple[str, str]]) -> bool:
    incoming = {node: 0 for node in ids}
    adjacency: dict[str, list[str]] = {}
    for source, target in pairs:
        incoming[target] += 1
        adjacency.setdefault(source, []).append(target)
    queue, visited = deque(k for k, count in incoming.items() if count == 0), 0
    while queue:
        source = queue.popleft()
        visited += 1
        for target in adjacency.get(source, []):
            incoming[target] -= 1
            if not incoming[target]:
                queue.append(target)
    return visited != len(ids)


def validate_case(case: dict) -> None:
    if case.get("schema_version") != 1 or type(case.get("schema_version")) is not int:
        raise ValueError("unsupported case schema_version")
    text(case.get("id"), "case.id")
    if case.get("status") != "development_unvalidated":
        raise ValueError("these cases must remain development_unvalidated")
    text(case.get("change"), "change")
    target = case.get("target", {})
    import re
    if not isinstance(target, dict) or not re.fullmatch(r"[0-9a-f]{40}", target.get("commit", "")):
        raise ValueError("target must pin a full git commit")
    sources = index(case.get("sources"), "sources")
    if not sources:
        raise ValueError("at least one evidence source is required")
    from pathlib import PurePosixPath
    for source in sources.values():
        path = text(source.get("path"), "source.path")
        if PurePosixPath(path).is_absolute() or ".." in PurePosixPath(path).parts or "\\" in path or ":" in path:
            raise ValueError("unsafe source path")
        if not re.fullmatch(r"[0-9a-f]{40}", source.get("blob", "")):
            raise ValueError("source must pin a git blob")
        start, end = source.get("start"), source.get("end")
        if type(start) is not int or type(end) is not int or not 1 <= start <= end:
            raise ValueError("invalid source line range")
        text(source.get("anchor"), "source.anchor")
    obligations = index(case.get("obligations"), "obligations")
    if not obligations:
        raise ValueError("empty reference")
    for obligation in obligations.values():
        if obligation.get("kind") not in KINDS or obligation.get("severity") not in SEVERITIES:
            raise ValueError("invalid obligation kind/severity")
        text(obligation.get("requirement"), "obligation.requirement")
        text(obligation.get("acceptance"), "obligation.acceptance")
        basis = strings(obligation.get("basis"), "obligation.basis")
        if not basis or not set(basis) <= set(sources) | {"request"}:
            raise ValueError("missing or unknown obligation basis")
    dependencies = records(case.get("dependencies", []), "dependencies")
    seen, pairs = set(), []
    for edge in dependencies:
        pair = (edge.get("before"), edge.get("after"))
        if any(node not in obligations for node in pair) or pair[0] == pair[1] or pair in seen:
            raise ValueError("invalid reference dependency")
        if edge.get("severity") not in SEVERITIES:
            raise ValueError("invalid dependency severity")
        text(edge.get("reason"), "dependency.reason")
        seen.add(pair)
        pairs.append(pair)
    if has_cycle(set(obligations), pairs):
        raise ValueError("cyclic reference precedence")


def validate_plan(plan: dict) -> list[dict]:
    """Shape errors raise; structurally bad but parseable graphs produce findings."""
    nodes = index(plan.get("nodes"), "nodes")
    findings = [] if nodes else [{"code": "EMPTY_PLAN"}]
    for node in nodes.values():
        if node.get("kind") not in KINDS or node.get("state") not in STATES:
            raise ValueError("invalid candidate kind/state")
        text(node.get("text"), "node.text")
        strings(node.get("evidence", []), "node.evidence")
        traces = strings(node.get("traces_to", []), "node.traces_to")
        if any(t not in nodes or t == node["id"] for t in traces):
            findings.append({"code": "INVALID_TRACE", "node": node["id"]})
        if node["kind"] == "task" and not traces and not node.get("evidence"):
            findings.append({"code": "UNTRACEABLE_PLAN_ITEM", "node": node["id"]})
    pairs, seen = [], set()
    for edge in records(plan.get("edges"), "edges"):
        source, target, relation = edge.get("from"), edge.get("to"), edge.get("relation")
        if not all(isinstance(v, str) for v in (source, target, relation)) or relation not in RELATIONS:
            raise ValueError("invalid edge relation/endpoint type")
        key = source, target, relation
        if key in seen:
            findings.append({"code": "DUPLICATE_EDGE", "edge": edge})
        seen.add(key)
        if source not in nodes or target not in nodes or source == target:
            findings.append({"code": "INVALID_EDGE", "edge": edge})
        elif relation == "precedes":
            pairs.append((source, target))
    if has_cycle(set(nodes), pairs):
        findings.append({"code": "HARD_CYCLE"})
    return findings


def review_template(case: dict, plan: dict) -> dict:
    validate_case(case)
    validate_plan(plan)
    return {
        "case_sha256": digest(case), "plan_sha256": digest(plan),
        "reviewer": "UNASSIGNED", "reviewer_kind": "unassigned", "judge_calibrated": False,
        "judgments": [{"obligation": ob["id"], "verdict": "unresolved", "support": [], "reason": ""}
                      for ob in case["obligations"]],
        "plan_issues": [],
    }


def evaluate(case: dict, plan: dict, review: dict | None = None) -> dict:
    validate_case(case)
    structure = validate_plan(plan)
    nodes, obligations = index(plan["nodes"], "nodes"), index(case["obligations"], "obligations")
    source_ids = {source["id"] for source in case["sources"]}
    for node in nodes.values():
        if not set(node.get("evidence", [])) <= source_ids | {"request"}:
            structure.append({"code": "UNKNOWN_EVIDENCE_ID", "node": node["id"]})
    review = review_template(case, plan) if review is None else review
    if review.get("case_sha256") != digest(case) or review.get("plan_sha256") != digest(plan):
        raise ValueError("review is stale or belongs to another case/plan")
    if review.get("reviewer_kind") not in {"unassigned", "human", "llm", "fixture"}:
        raise ValueError("invalid reviewer_kind")
    rows = records(review.get("judgments"), "judgments")
    if len(rows) != len(obligations) or {r.get("obligation") for r in rows} != set(obligations):
        raise ValueError("review must cover every obligation exactly once")
    matches, verdicts, findings = {}, {}, list(structure)
    for row in rows:
        oid, verdict = row["obligation"], row.get("verdict")
        if verdict not in {"met", "missing", "contradicted", "unresolved"}:
            raise ValueError("invalid review verdict")
        support = records(row.get("support"), "support")
        if verdict != "unresolved":
            if review["reviewer_kind"] == "unassigned" or review.get("reviewer") in {None, "", "UNASSIGNED"}:
                raise ValueError("assigned reviewer required")
            text(row.get("reason"), "judgment.reason")
        if verdict in {"met", "contradicted"} and not support:
            raise ValueError("met/contradicted requires an exact candidate quote")
        if verdict == "missing" and support:
            raise ValueError("missing verdict cannot claim supporting nodes")
        for span in support:
            nid = span.get("node")
            if nid not in nodes or text(span.get("quote"), "support.quote") not in nodes[nid]["text"]:
                raise ValueError("review quote not found in candidate node")
        ob = obligations[oid]
        if verdict == "met" and ob["kind"] in {"decision", "risk", "unknown"}:
            if not any(nodes[s["node"]]["kind"] == ob["kind"] for s in support):
                raise ValueError("decision/risk/unknown credit needs an explicitly typed node")
        if verdict == "met" and ob["kind"] == "unknown":
            if any(nodes[s["node"]]["state"] not in {"unknown", "contradicted"} for s in support):
                raise ValueError("asserted fact cannot receive uncertainty credit")
        verdicts[oid] = verdict
        matches[oid] = {s["node"] for s in support} if verdict == "met" else set()
        if verdict in {"missing", "contradicted"}:
            code = ("FALSE_CERTAINTY" if ob["kind"] == "unknown" else "CONTRADICTED_OBLIGATION") if verdict == "contradicted" else f"MISS_{ob['severity'].upper()}"
            findings.append({"code": code, "severity": ob["severity"], "obligation": oid, "kind": ob["kind"]})
    for issue in records(review.get("plan_issues", []), "plan_issues"):
        if issue.get("code") not in ISSUE_CODES or issue.get("severity") not in SEVERITIES:
            raise ValueError("invalid reviewed plan issue")
        if review["reviewer_kind"] == "unassigned":
            raise ValueError("assigned reviewer required for plan issues")
        text(issue.get("reason"), "issue.reason")
        if not strings(issue.get("nodes"), "issue.nodes") or not set(issue["nodes"]) <= set(nodes):
            raise ValueError("reviewed issue requires existing nodes")
        findings.append(dict(issue))
    pairs = [(e["from"], e["to"]) for e in plan["edges"] if e["relation"] == "precedes"]
    dep_met, dep_pending = 0, 0
    for edge in case.get("dependencies", []):
        before, after = edge["before"], edge["after"]
        if any(verdicts[k] == "unresolved" for k in (before, after)):
            dep_pending += 1
        elif any(reachable(a, b, pairs) for a in matches[before] for b in matches[after] if a != b):
            dep_met += 1
        else:
            reverse = any(reachable(b, a, pairs) for a in matches[before] for b in matches[after] if a != b)
            findings.append({"code": "BAD_DEPENDENCY" if reverse else "MISSING_DEPENDENCY",
                             "severity": edge["severity"], "before": before, "after": after})
    def coverage(ids):
        counts = Counter(verdicts[i] for i in ids)
        total, met, pending = len(ids), counts["met"], counts["unresolved"]
        return {"met": met, "total": total, "pending": pending,
                "lower_bound": met / total if total else None,
                "upper_bound": (met + pending) / total if total else None}
    metrics = {f"{s}_coverage": coverage([k for k, o in obligations.items() if o["severity"] == s]) for s in SEVERITIES}
    metrics.update({f"{k}_coverage": coverage([i for i, o in obligations.items() if o["kind"] == k])
                    for k in ("decision", "risk", "impact", "unknown")})
    metrics["dependency_coverage"] = {"met": dep_met, "total": len(case.get("dependencies", [])), "pending": dep_pending}
    used = set().union(*matches.values())
    pending = sum(v == "unresolved" for v in verdicts.values())
    return {
        "case_id": case["id"], "case_sha256": digest(case), "plan_sha256": digest(plan),
        "structurally_valid": not structure,
        "review_status": "pending" if pending else "complete",
        "reviewer_kind": review["reviewer_kind"], "reference_validated": False,
        "quality_claim_allowed": False, "metrics": metrics, "findings": findings,
        "critical_failures": sum(f.get("severity") == "critical" for f in findings),
        "unadjudicated_nodes": sorted(set(nodes) - used),
        "not_measured": ["general_precision", "semantic_evidence_support", "human_review_speed", "business_value"],
    }
