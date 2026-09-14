# Golden Set and Evaluation

## Purpose

The golden set is not a collection of pretty examples. It is the regression suite for the reasoning product.

A good evaluation must detect whether a model/prompt/engine revision:

- misses important outcomes or affected domains;
- invents irrelevant work;
- creates incorrect dependencies;
- over- or under-decomposes;
- hides decisions inside tasks;
- fails to discover cross-cutting concerns;
- produces a graph that humans cannot understand.

## Suggested 100-case distribution

- Software feature changes: 20
- New SaaS/product slices: 15
- AI/data systems: 15
- Infrastructure/security: 15
- Operations/incidents/migrations: 10
- Business/marketing launches: 10
- Organization/process changes: 10
- Mixed complex projects: 5

The first production wedge should primarily score software-change cases while retaining cross-domain cases to prevent overfitting.

## Golden case structure

```yaml
id: software.document-sharing
context:
  summary: Existing RAG SaaS with documents, retrieval and chat.
  evidence: []
change: Add document sharing between users and organizations.
expected:
  outcomes:
    must_detect: []
    nice_to_detect: []
  impacted_domains:
    must_detect: []
  hidden_concerns:
    must_detect: []
  decisions:
    must_detect: []
  risks:
    must_detect: []
  dependencies:
    must_include: []
    must_not_include: []
  noise:
    forbidden_or_irrelevant: []
  granularity:
    examples_too_broad: []
    examples_appropriate: []
    examples_too_fine: []
```

## Scorecard (100 points)

- Outcome coverage: 15
- Domain impact coverage: 15
- Cross-cutting impact coverage: 15
- Hidden/missing concern discovery: 20
- Dependency correctness: 10
- Granularity quality: 10
- Correct separation of decisions/risks/tasks: 5
- Noise control / precision: 5
- Human comprehensibility: 5

Missing-coverage recall intentionally has the highest weight because the primary product value is finding what the team would otherwise overlook.

## Machine-computable metrics

Where possible compute:

- Outcome recall / precision
- Domain impact recall / precision
- Hidden-concern recall
- Required-edge recall
- Forbidden-edge rate
- Irrelevant-node rate
- Cycle count
- Orphan required-outcome count
- Duplicate semantic-node rate
- Human-override preservation rate

Semantic matches should use stable concept identifiers in the golden set, not literal string equality.

## Human rubric

Some qualities require human review:

- Is the graph easier to reason about than the raw requirement?
- Are sibling nodes expressed at a coherent abstraction level?
- Would a technical lead trust this graph enough to start a design review?
- Did the output surface a genuinely useful surprise?
- Are uncertainty and evidence represented honestly?

## Evaluation protocol

For every engine revision:

1. Freeze model and prompt configuration.
2. Run all applicable golden cases.
3. Store graph output and trace metadata.
4. Compute automatic scores.
5. Sample failures and score human rubric.
6. Compare against previous baseline.
7. Reject regressions in critical recall even if aggregate score improves.

## Release gates

Initial recommendation:

- zero graph invariant violations;
- zero execution cycles in accepted plans;
- no regression in must-detect hidden-concern recall;
- bounded irrelevant-node rate;
- all human-confirmed constraints preserved after re-analysis.

Numeric thresholds should be set only after the first baseline run rather than invented in advance.
