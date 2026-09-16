from planning_eval.model import ErrorCode, Severity


def test_severity_is_frozen() -> None:
    assert {item.value for item in Severity} == {"critical", "major", "minor"}


def test_v1_error_taxonomy_contains_core_failure_modes() -> None:
    required = {
        "MISS_CRITICAL",
        "MISS_MAJOR",
        "FALSE_IMPACT",
        "UNSUPPORTED_CLAIM",
        "FALSE_CERTAINTY",
        "BAD_DEPENDENCY",
        "MISSING_DEPENDENCY",
        "UNDER_DECOMPOSITION",
        "OVER_DECOMPOSITION",
        "MISSING_DECISION",
        "MISSING_RISK",
        "DUPLICATE_PLAN_ITEM",
        "UNTRACEABLE_PLAN_ITEM",
    }
    assert required <= {item.value for item in ErrorCode}
