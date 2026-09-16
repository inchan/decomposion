from planning_eval.model import CandidateNode, CandidatePlan, Kind
from planning_eval.traceability import untraceable_node_ids


def test_untraceable_nodes_are_structurally_detected() -> None:
    plan = CandidatePlan(
        nodes=(
            CandidateNode("bare", Kind.TASK, "bare task"),
            CandidateNode("evidenced", Kind.TASK, "evidenced task", evidence=("architecture.md#auth",)),
            CandidateNode("traced", Kind.TASK, "traced task", traces_to=("outcome:secure-sharing",)),
        )
    )
    assert untraceable_node_ids(plan) == ("bare",)
