# Planning Eval v1 evaluator self-test matrix

| Controlled mutation | Expected behavior | Layer |
|---|---|---|
| exact concept replaced by authored equivalent alias | still matched | deterministic self-test |
| remove required critical task | `MISS_CRITICAL` | deterministic self-test |
| remove required decision | `MISSING_DECISION` | deterministic self-test |
| remove required risk | `MISSING_RISK` | deterministic self-test |
| assert required unknown as fact | `FALSE_CERTAINTY` | deterministic self-test |
| say nothing about required unknown | `FALSE_CERTAINTY` | deterministic self-test |
| assert and abstain on same unknown | `FALSE_CERTAINTY` | deterministic self-test |
| reverse required dependency | `BAD_DEPENDENCY` | deterministic self-test |
| omit required dependency | `MISSING_DEPENDENCY` | deterministic self-test |
| hard dependency cycle | structural invariant failure | deterministic |
| add novel candidate finding | neutral `unadjudicated_novel` | deterministic |
| collapse review-critical concepts into an ambiguous mega-task | `UNDER_DECOMPOSITION` after rationale | semantic/human |
| split a trivial unit into redundant fragments | `OVER_DECOMPOSITION` after rationale | semantic/human |
| paraphrase not listed as an authored alias | semantic match/abstain | semantic |

The deterministic layer is intentionally conservative. Passing these tests proves evaluator mechanics, not real-world planning quality.