# VERIFY — repo-standards-baseline

## Independence check

- Builders named in `02-build.md`: **Platform Engineer**, **Senior Developer**.
- Verifier: **Reality Checker** (`testing-reality-checker`) — review-only division, does not appear in the BUILD log.
- Verdict: **independent**. Checked before this file was opened.

## Result per criterion

Evidence below was produced by the verifier re-running every command, not by reading the BUILD log.

- **C1 PASS** — `.github/workflows/ci.yml` defines job `required` with display name `ci/required` on `pull_request` and `push: main`; ruleset 26387961 lists it as a required status check; `gh api commits/main/check-runs` reports `ci/required => success`.
- **C2 PASS** — CI runs `--cov --cov-branch --cov-report=term-missing --cov-fail-under=80`; measured **92.8% line / 87.9% branch** independently.
- **C3 PASS** — `cli/main.py` **96.6%**, `core/originality.py` **97.8%**, `core/validator.py` **100.0%**.
- **C4 PASS** — 195 test functions, 195 passed; 4.13s with coverage; unit subset 117 passed in 0.67s; 0 `sleep`, 0 `random`, 0 network imports.
- **C5 PASS** — `[project].dependencies` holds exactly 4 packages; `[dependency-groups].dev` holds the test, lint and audit tooling.
- **C6 PASS** — `grep -rn "pragma: no cover" src/` returns 0.
- **C7 PASS** — 10 hooks; `pre-commit run --all-files` exits 0 on a clean tree. The `ruff format --check` hook enumerated in PROPOSE P6 is absent (recorded deviation).
- **C8 PASS** — `mise run check` exits 0 in 5.30s.
- **C9 PASS** — `release-please-config.json` (`python`, `packages["."]`) + manifest at `1.6.0`; PR #41 was auto-opened with a minor bump from `feat(ci)` #40.
- **C10 PASS** — tag `v1.6.0`, release not draft, assets `agency_agents-1.6.0-py3-none-any.whl` and `agency_agents-1.6.0.tar.gz`.
- **C11 PASS** — commit `df5091e` wrote `1.5.0 → 1.6.0` in both `pyproject.toml` and `src/agency_agents/__init__.py`, with no hand edit.
- **C12 PASS** — 21 labels across 5 categories; programmatic comparison against the repository shows 0 drift.
- **C13 PASS** — 4 forms + `config.yml` with `blank_issues_enabled: false` and 3 contact links.
- **C14 PASS** — template requires `Closes #`, a Conventional type and a test-evidence block; `CODE_OF_CONDUCT.md` present.
- **C15 FAIL** — the `main-protection` ruleset enforces `required_approving_review_count: 0`. FRAME C15 requires **1 approval**. The divergence was not implemented as written and was not recorded as a deviation in the BUILD log.
- **C16 PASS** — Dependabot covers `github-actions` and `uv` weekly; vulnerability alerts, security updates and automated security fixes all report enabled.
- **C17 PASS** — `codeql.yml` runs on `pull_request`, `push` and cron `17 4 * * 1`; `analyze` succeeded on HEAD.
- **C18 PASS** — 31 remote `uses:` references, all 40-character SHAs, 0 tag or branch refs.
- **C19 PASS** — all 5 workflows declare an explicit `permissions:` block; 0 `write-all`.
- **C20 PASS** — `CODEOWNERS` covers `.github/`, `/src/`, `/scripts/`, `/mise.toml`.
- **C21 PASS** — 0 references to removed `scripts/*.sh` in `SECURITY.md`, `tools.json` and `divisions.json`; `FUNDING.yml` names `deuriib`.

## Findings

### Engineering — high

- **C15 approval requirement silently dropped.** The ruleset requires 0 approvals where FRAME requires 1. Not implemented and not declared. This is the pattern the two-gate model exists to catch: a criterion that is partially true but logged as fully done.
- **The type-check leg of `ci/required` cannot fail.** `mypy` reports 191 errors and the step is `continue-on-error: true`, so the aggregate check is green with a standing red type-check. C1's "type-check" clause is nominal, not enforced.

### Engineering — medium

- The aggregate check treats `skipped` as success: `grep -Eq '"result": "(failure|cancelled)"'` does not fail on a skipped dependency, so a job that never runs can pass the gate.
- `mise run check` omits `types` and the dependency audit; only `mise run ci` mirrors the pipeline. C8's "reproduces the CI gate" is true of `ci`, not of `check`.
- `release-please` cannot emit a `Removed` changelog section as configured, and it rewrote the Keep a Changelog preamble out of `CHANGELOG.md` on the first release.
- `labels.yml` is not a strict single source of truth: 10 repository labels are unmanaged (8 GitHub defaults plus `autorelease: pending|tagged`) and the sync never deletes.

### Engineering — low

- `pre-commit` hooks are pinned by tag (`rev:`), not by commit SHA. Only CI workflows are SHA-pinned.

## Spot-checked tests

The verifier inspected five of the 97 new tests and confirmed they assert behaviour rather than counts:

- `test_jaccard_partial_overlap_matches_window_count` — exact set-ratio assertion.
- `test_is_agent_false_for_unreadable_path` — OSError swallowed, returns False.
- `test_alias_display_name_resolves_when_distinct_from_stem` — identity resolution.
- `test_vibe_multi_file` — two outputs, exact filenames.
- `test_all_tools_installation` — 17 tools, asserts real destination paths exist.

## Verdict

- Domain gate: **FAIL** — C15 is measurably unmet (0 approvals vs 1 required) and its divergence was not recorded.
- Process gate: Vasquez — **PASS** (independence confirmed; 21/21 criteria carry evidence generated by the verifier; findings grouped and severity-rated; verdict consistent with the failing row).

## Return to BUILD

A `FAIL` row closes VERIFY as failed; SHIP does not open. The following must return to BUILD, and C15 additionally requires a FRAME decision because it is a contract change, not a defect:

- **C15 — approval model.** Either raise `required_approving_review_count` to 1, which deadlocks a single-maintainer repository because GitHub forbids self-approval, or amend FRAME C15 to 0 approvals with the rationale written down. This is a user decision, not an engineering one. — Owner: Vasquez (to obtain the decision) + Platform Engineer (to apply) — Due: 2026-11-09.
- **Type-check leg.** Make `mypy` blocking by fixing or explicitly scoping the 191 errors, or amend C1 so it does not claim type-check aggregation. — Owner: Senior Developer — Due: 2026-11-16.
- **Aggregate skipped-handling.** Fail the aggregate on `skipped` as well as `failure` and `cancelled`. — Owner: Platform Engineer — Due: 2026-11-09.
- **`mise run check` parity.** Include the type-check and dependency audit, or rename the task so its name matches what it does. — Owner: Platform Engineer — Due: 2026-11-09.
- **Changelog sections.** Map a `Removed` section and restore the Keep a Changelog preamble. — Owner: Platform Engineer — Due: 2026-11-16.
- **Label ownership.** Decide whether the sync deletes unmanaged labels or whether the repository declares them out of scope. — Owner: Platform Engineer — Due: 2026-11-16.
- **pre-commit pinning.** Pin hook repositories to commit SHAs. — Owner: Platform Engineer — Due: 2026-11-23.

## Assigned team

- Domain (verifier): **Reality Checker** (`testing-reality-checker`) — independent, review-only division.
- Process steward: **Vasquez** (Project Management) — confirmed independence before opening the file, verified that every row carries evidence, and refused to sign a passing verdict over a failing row.

## Gates

- Domain gate: Reality Checker — **FAIL** (C15 unmet: 0 approvals required, 1 in the contract; divergence unrecorded)
- Process gate: Vasquez — **PASS** (independence confirmed; evidence per criterion; verdict consistent; 7 return-to-BUILD items owned and dated)
