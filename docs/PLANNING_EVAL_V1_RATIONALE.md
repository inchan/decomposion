# Why Eval comes before more product work

The current product thesis has two independent claims: Decomposion can produce a better plan, and a visual interface can make that plan faster and more accurate for humans to review. Planning Eval v1 addresses only the first claim.

Building more planning logic before defining what counts as a good plan would make every improvement subjective. Building the graph UI first would confound planning quality with presentation quality. Therefore the next evidence sequence is:

1. freeze a planning-quality contract;
2. prove evaluator mechanics on controlled mutations;
3. author three deep reference cases;
4. measure strong baselines;
5. implement the minimum Decomposion reasoning method;
6. compare and ablate;
7. only after planning value is demonstrated, benchmark visual review UX separately.

This sequencing is designed to make a negative result useful. If a strong one-shot prompt performs as well as the staged method, the project should simplify rather than hide the result behind more features.