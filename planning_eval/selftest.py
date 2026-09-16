"""Controlled labels validate counting/transport, not a semantic judge's accuracy."""
from __future__ import annotations

from copy import deepcopy

from .core import digest, evaluate, review_template, validate_plan


def fixture():
    case = {"schema_version": 1, "id": "synthetic", "status": "development_unvalidated",
            "target": {"repository": "fixture/only", "commit": "0" * 40}, "change": "Plan a permission check.",
            "sources": [{"id": "S", "path": "app.py", "blob": "0" * 40, "start": 1, "end": 1, "anchor": "fixture"}],
            "obligations": [
                {"id": "policy", "kind": "decision", "severity": "critical", "requirement": "Decide rights.", "acceptance": "Explicit rights decision.", "basis": ["request"]},
                {"id": "auth", "kind": "task", "severity": "critical", "requirement": "Check access.", "acceptance": "Explicit authorization work.", "basis": ["S"]},
                {"id": "cache", "kind": "unknown", "severity": "major", "requirement": "Cache unknown.", "acceptance": "Do not assume a cache.", "basis": ["request"]}],
            "dependencies": [{"before": "policy", "after": "auth", "severity": "critical", "reason": "Rights define the authorization behavior."}]}
    nodes = [{"id": "d", "kind": "decision", "state": "proposed", "text": "Choose who may read.", "evidence": ["request"], "traces_to": []},
             {"id": "t", "kind": "task", "state": "proposed", "text": "Authorize content for its recipient.", "evidence": ["S"], "traces_to": ["d"]},
             {"id": "u", "kind": "unknown", "state": "unknown", "text": "Whether a cache exists is unknown.", "evidence": ["request"], "traces_to": []}]
    plan = {"nodes": nodes, "edges": [{"from": "d", "to": "t", "relation": "precedes"}]}
    review = review_template(case, plan)
    review.update(reviewer="controlled-labels", reviewer_kind="fixture")
    for row, node in zip(review["judgments"], nodes):
        row.update(verdict="met", support=[{"node": node["id"], "quote": node["text"]}], reason="Controlled fixture label, not inferred semantic correctness.")
    return case, plan, review


def selftest():
    case, plan, review = fixture()
    results = []
    score = evaluate(case, plan, review)
    results.append(("labeled_valid_plan", not score["findings"]))
    unresolved = evaluate(case, plan)
    results.append(("unreviewed_stays_pending", unresolved["metrics"]["critical_coverage"]["pending"] == 2))
    broken, labeled = deepcopy(plan), deepcopy(review)
    broken["nodes"] = [n for n in broken["nodes"] if n["id"] != "t"]
    broken["edges"] = []
    labeled["plan_sha256"] = digest(broken)
    labeled["judgments"][1].update(verdict="missing", support=[], reason="Controlled deletion of required work.")
    score = evaluate(case, broken, labeled)
    results.append(("labeled_critical_omission", any(f["code"] == "MISS_CRITICAL" for f in score["findings"])))
    results.append(("missing_endpoint_counts_dependency", any(f["code"] == "MISSING_DEPENDENCY" for f in score["findings"])))
    broken, labeled = deepcopy(plan), deepcopy(review)
    broken["edges"][0].update({"from": "t", "to": "d"})
    labeled["plan_sha256"] = digest(broken)
    results.append(("reversed_precedence", any(f["code"] == "BAD_DEPENDENCY" for f in evaluate(case, broken, labeled)["findings"])))
    broken = deepcopy(plan)
    broken["edges"].append({"from": "t", "to": "d", "relation": "precedes"})
    results.append(("hard_cycle", any(f["code"] == "HARD_CYCLE" for f in validate_plan(broken))))
    broken["edges"][1]["relation"] = "affects"
    results.append(("influence_cycle_is_not_execution_cycle", not any(f["code"] == "HARD_CYCLE" for f in validate_plan(broken))))
    broken, labeled = deepcopy(plan), deepcopy(review)
    broken["nodes"][2].update(state="observed", text="A cache exists.")
    labeled["plan_sha256"] = digest(broken)
    labeled["judgments"][2].update(verdict="contradicted", support=[{"node": "u", "quote": "A cache exists."}], reason="Controlled unsupported certainty.")
    results.append(("labeled_false_certainty", any(f["code"] == "FALSE_CERTAINTY" for f in evaluate(case, broken, labeled)["findings"])))
    for label, bad in (("stale_review_rejected", {**review, "plan_sha256": "bad"}),
                       ("fabricated_quote_rejected", deepcopy(review))):
        if label.startswith("fabricated"):
            bad["judgments"][0]["support"][0]["quote"] = "Not present in the candidate."
        try:
            evaluate(case, plan, bad)
            results.append((label, False))
        except ValueError:
            results.append((label, True))
    return [{"name": name, "passed": passed} for name, passed in results]
