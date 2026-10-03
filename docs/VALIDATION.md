# Validation status

Validated in the build environment on 2026-10-03:

- Python source compilation: passed.
- Synthetic data generation: passed (6,000 rows).
- Baseline propensity training: passed.
- Unit/API tests: passed using the environment's installed dependencies.

The sandbox used to assemble this repository has no outbound PyPI access, so a clean `pip install -e '.[dev]'` could not be re-executed there. The failure was dependency download/network related, not an application test failure. CI is configured to install dependencies in a normal GitHub Actions environment.

Baseline training metrics are intentionally training-set-only and are not represented as production validation. The production roadmap requires out-of-time validation and randomized business experimentation.
