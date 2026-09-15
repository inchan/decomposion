# Changelog

## 0.2.0.dev0 — unreleased

- Add an installable `decomposion` CLI for provider-free local/cloud experiment preparation.
- Freeze suite inputs, templates, runtime provenance and randomized session order.
- Refuse dirty targets, protocol/model drift, overwrites, stage skipping and edited input/output artifacts.
- Record four actual manual stages for Decomposion rather than a one-shot imitation.
- Add development-container configuration and clean-install/wheel/real-target CI coverage.
- Fix abstention scoring: expected labels and actual abstentions are separate inputs; silence earns no credit.
- Mark fixture evaluation reports explicitly as non-model results.

This is a development version, not a PyPI release or a deployed MCP server.
