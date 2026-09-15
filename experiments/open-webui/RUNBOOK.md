# Open WebUI experiment protocol v2

The executable instructions now live in [LOCAL_LAB.md](../../docs/LOCAL_LAB.md).
This replaces the previous shared-checkout/manual-folder protocol.

- Target stays pinned to `0a7c15832fb30b1903753e83f81dc7d27e5b0944`.
- All ten cross-cutting prompts in `prompts.yaml` are retained.
- `decomposion lab init` freezes inputs and builds a seeded 9/90-session queue.
- `lab start` prepares an independent checkout lazily, never resets existing work.
- Plain/structured have one recorded stage; decomposion has four recorded stages.
- `lab record` captures raw stage outputs, generates the next request, and rejects skipped stages.
- `lab status` reports capture progress, not reasoning quality.

No agent/model is launched by these commands. Supply each request in a fresh read-only
agent session, with the same selected model/version/settings. A separate directory is
not an OS sandbox. Use separate VM/container boundaries when strict isolation is needed.

A vague request does not imply the repository contains no evidence. For P10, reward
unknowns only where the pinned source plus request really leave something unresolved.
Do not reward refusal to recognize existing code, or plans to implement a feature that
already exists unchanged. These are experiment prompts, not independently validated
Golden answers. No 90-session model experiment is claimed to have been run.
