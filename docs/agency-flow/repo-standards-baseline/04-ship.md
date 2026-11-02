# SHIP — repo-standards-baseline

## Release notes (user-facing)

The repository can now be contributed to and released without a maintainer
babysitting it. Every pull request has to pass one enforced check — lint, types,
tests with a coverage floor, manifest verification and a dependency audit — and
that check cannot be bypassed, not even by the owner. Releases are cut from
Conventional Commit messages: the version, the changelog and the attached
packages are produced automatically. The test suite grew from 101 to 195 tests
and coverage from 65% to 92.8%.

Nothing changes for people who only use the agent catalog. This release is about
the repository itself: how changes get in, and how releases get out.

## Version / tag

`v1.6.2` (latest released tag; `v1.4.0` through `v1.6.2` were cut during this
project). Distribution is GitHub Releases only — this repository does not publish
to PyPI; the wheel and sdist are attached to each release as assets.

## Changelog

- `chore(deps)` — split test and lint tooling into `[dependency-groups].dev`; configure pytest, coverage, ruff and mypy in `pyproject.toml`.
- `chore(deps)` — regenerate `uv.lock` against the new dependency layout.
- `feat(release)` — automate version bumps and changelog entries from Conventional Commits via release-please, with the manifest seeded at the real version.
- `feat(release)` — cut tagged releases with the sdist and wheel attached as assets, and publish `ci/required` on release PRs from the gate that actually ran.
- `feat(ci)` — add the shared `quality-gate` composite action so the CI gate and the release gate cannot drift.
- `ci` — pin uv to `0.12.12`, scope permissions to read and pin actions by SHA in the legacy workflow.
- `chore` — ignore coverage artifacts in `.gitignore`.
- `style` — normalise import order across 19 source files with ruff.
- `feat(ci)` — add the aggregate `ci/required` check over lint, types, tests, manifest verification and dependency audit.
- `feat(ci)` — manage labels as code: 31 labels across 5 categories, applied by an idempotent sync script.
- `feat` — add four issue forms (bug, feature, new agent, docs/infra) with blank issues disabled and three contact links.
- `docs` — require a linked issue, a Conventional commit type and test evidence in the pull request template.
- `docs` — add the Contributor Covenant 2.1.
- `feat(ci)` — add pre-commit with ten hooks, pinned to commit SHAs, with Markdown exempt from whitespace rewriting.
- `feat(devx)` — mirror the CI gate in mise tasks: `check`, `ci`, `hooks`, `hooks-run`, `version`.
- `feat(ci)` — protect `main` with a ruleset applied as code: pull request required, `ci/required` required, force-push and deletion blocked, zero bypass actors.
- `feat(security)` — add CodeQL for Python on pull requests, pushes to `main` and a weekly schedule.
- `feat(security)` — track the `github-actions` and `uv` ecosystems weekly with Dependabot.
- `chore` — add `CODEOWNERS` for CI, source, scripts, tooling and the agent catalog.
- `docs(security)` — rewrite `SECURITY.md` for the Python CLI, documenting the controls that actually exist.
- `docs` — repair drift in `tools.json`, `divisions.json` and `FUNDING.yml`.
- `style` — normalise trailing whitespace and final newlines in 15 code and config files.
- `test` — add 97 test functions and 224 assertions, raising coverage from 65.2% to 92.8% (branch 87.9%).
- `ci` — add a mypy ratchet with a recorded baseline of 39 production type errors, so the type-check leg can fail.

## References

- FRAME: `00-frame.md` (C15 amended 2026-11-02, both gates re-signed)
- PROPOSE: `01-propose.md`
- BUILD: `02-build.md`
- VERIFY: `03-verify.md` (verdict: **`PASS`** on the domain gate — pass 1 `FAIL` on C15, pass 2 `PASS-WITH-CONDITIONS`, condition resolved before closure)

## Follow-ups carried from VERIFY

- Label deletion drift is undetectable: the sync is additive and never deletes, so a label removed from `labels.yml` survives in the repository. Accepted as a deliberate trade-off to avoid destroying release-please's automation labels. — Owner: Platform Engineer. Due: 2026-11-23.
- The mypy baseline tolerates 39 production type errors: the ratchet prevents growth, but the backlog is real and ratcheting down is a standing task, not a one-off. — Owner: Senior Developer. Due: 2026-12-14.

## Assigned team

- Domain: **Platform Engineer** (`engineering-platform-engineer`) — produced the release, CI, labels, templates and hardening artifacts.
- Domain: **Senior Developer** (`engineering-senior-developer`) — produced the coverage campaign and the type-check ratchet baseline.
- Verifier (VERIFY only, review-only division): **Reality Checker** (`testing-reality-checker`).
- Process steward: **Vasquez** (Project Management) — confirmed VERIFY closed with a passing domain gate before opening SHIP, that all four references are present, that the VERIFY verdict is quoted rather than paraphrased, and that both conditions are carried forward with an owner and a date.

## Gates

- Domain gate: N/A — passed at VERIFY
- Process gate: Vasquez — PASS (references complete; verdict quoted; 2/2 VERIFY conditions carried with owner and date; changelog is a bijection with BUILD artifacts; no new scope introduced)
