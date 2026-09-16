# planning_eval

This package contains Planning Eval v1 primitives. It is intentionally small.

- `model.py`: reference/candidate constraint models and error taxonomy.
- `schema.py`: deterministic reference-graph invariants.
- `evaluator.py`: narrow deterministic self-test evaluator; **not a semantic judge**.
- `adjudication.py`: typed semantic/human findings for judgments such as granularity.

Do not interpret exact/alias matching as the final quality evaluator. Step 2 will test whether three deep reference cases can be represented without changing the contract; semantic matching and judge calibration come later.