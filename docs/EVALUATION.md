# Golden Set and Evaluation

## Purpose

The evaluation suite exists to falsify the product thesis, not to confirm our preferred decomposition style.

The central question is:

> Does Decomposion discover correct, actionable impacts, missing decisions, and dependencies better than a strong plain-LLM baseline without increasing speculative noise?

A good evaluation must detect whether a model/prompt/engine revision:

- misses important outcomes or affected domains;
- invents irrelevant work;
- creates incorrect dependencies;
- over- or under-decomposes;
- hides decisions inside tasks;
- fails to abstain when evidence is insufficient;
- fails to surface contradictions or stale evidence;
- produces a graph that humans cannot understand.

## Dataset partitions

Never use one homogeneous golden set for both development and product claims.

### Development set

Cases visible to engine authors. Useful for prompt design and regression debugging.

### Blind test set

Cases whose expected concerns are authored or reviewed independently and not exposed during prompt iteration. Ideally, the person producing the expected answer does not see Decomposion output first.

### Adversarial set

Include:

- incomplete architecture context;
- contradictory documentation;
- misleading feature descriptions;
- changes that affect fewer systems than they appear to;
- tempting but irrelevant domains;
- missing information that should trigger abstention;
- cases where the correct answer is `no material impact` for a candidate area.

## Suggested 100-case distribution

- Software feature changes: 20
- New SaaS/product slices: 15
- AI/data systems: 15
- Infrastructure/security: 15
- Operations/incidents/migrations: 10
- Business/marketing launches: 10
- Organization/process changes: 10
- Mixed complex projects: 5

The first production wedge should primarily score software-change cases while retaining other cases to expose overfitting.

## Required baselines

Every test case should run against the same context under at least:

1. **Plain LLM baseline** — one strong prompt asking for impact, omissions, risks, and dependencies.
2. **Structured-prompt baseline** — same model with a carefully engineered checklist but no persistent graph architecture.
3. **Decomposion** — full reasoning pipeline.

Where possible freeze model version, reasoning settings, and context window for fair comparison.

A high absolute score is not enough. The product must demonstrate incremental value over a good baseline.

## Golden case structure

```yaml
id: software.document-sharing
partition: development
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
    must_not_invent: []
  hidden_concerns:
    must_detect: []
  decisions:
    must_detect: []
  risks:
    must_detect: []
  unknowns:
    should_abstain_on: []
  contradictions:
    should_flag: []
  dependencies:
    must_include: []
    must_not_include: []
  noise:
    forbidden_or_irrelevant: []
```

## Core metrics

Measure both recall and precision.

- Outcome recall / precision
- Domain impact recall / precision
- Hidden-concern recall / precision
- Decision recall
- Required-edge recall
- Forbidden-edge rate
- Irrelevant-node rate
- Abstention precision / recall
- Contradiction-detection rate
- Stale-evidence detection rate
- Human-override preservation rate
- Duplicate semantic-node rate

## Product-value metrics

A discovery should not be rewarded merely for being surprising.

For sampled outputs, human reviewers score:

- **Correctness** — is it actually true or reasonably required?
- **Actionability** — would it change design, scope, validation, or sequencing?
- **Non-obviousness** — was it meaningfully beyond the obvious implementation checklist?
- **Evidence quality** — is the claim supported or clearly labeled as uncertain?
- **Noise cost** — how much reviewer effort is wasted by this suggestion?

Useful Surprise = correctness × actionability × non-obviousness, with an explicit penalty for noise.

## Confidence policy

Raw model confidence may be stored for research, but must not be presented as calibrated probability until calibration is demonstrated on held-out data.

Initial UI should prefer qualitative epistemic states:

- observed;
- strongly_supported;
- hypothesis;
- unknown;
- contradicted.

If numeric confidence is later exposed, publish calibration metrics such as reliability curves or expected calibration error for the relevant task family.

## Evaluation protocol

For every engine revision:

1. Freeze model and prompt configuration.
2. Run development, blind, and adversarial partitions separately.
3. Run required baselines on the same inputs.
4. Store graph output and trace metadata.
5. Compute automatic scores.
6. Human-review a stable sample of high-impact discoveries and false positives.
7. Compare against previous Decomposion version and baseline deltas.
8. Reject regressions in critical recall, abstention, or noise even if aggregate score improves.

Blind expected answers should remain inaccessible to prompt/engine iteration until the evaluation run is committed. When practical, use a different reviewer or external domain expert to adjudicate ambiguous cases.

## Release gates

Initial qualitative gates:

- zero graph invariant violations;
- zero execution cycles in accepted hard-dependency plans;
- material improvement over plain and structured LLM baselines on held-out cases;
- no regression in must-detect hidden-concern recall;
- bounded irrelevant-node rate;
- acceptable abstention behavior on underspecified cases;
- all human-confirmed constraints preserved after re-analysis;
- contradictions are surfaced instead of silently resolved by the model.

Numeric thresholds should be derived from the first baseline runs rather than invented in advance.
