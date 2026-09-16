# Planning Eval v1 scorecard

The scorecard is diagnostic, not a leaderboard.

| Metric | Direction | Interpretation |
|---|---:|---|
| Critical coverage | higher | fraction of required critical obligations semantically satisfied |
| Major coverage | higher | fraction of required major obligations satisfied |
| Minor coverage | higher | optional refinement coverage |
| Decision recall | higher | required unresolved decisions surfaced |
| Risk recall | higher | required material risks surfaced |
| Impact coverage | higher | required impact obligations surfaced |
| Required dependency recall | higher | required relationships preserved |
| Bad dependency count | lower | materially wrong relationships |
| Unsupported claim count | lower | architecture/system facts asserted without support |
| Uncertainty accuracy | higher | required unknowns explicitly preserved without contradictory assertion |
| Under/over decomposition | lower | adjudicated granularity failures |
| Untraceable item count | lower | important items with no reason/evidence/outcome relationship |
| Unadjudicated novel findings | neutral | potentially valuable or noisy; human/semantic review required |

A future release gate may make selected critical misses hard failures, but v1 does not invent thresholds before observing real baseline distributions and reviewer agreement.