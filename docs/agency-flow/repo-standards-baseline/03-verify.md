# VERIFY — repo-standards-baseline

## Independence check

- Builders named in `02-build.md`: **Platform Engineer**, **Senior Developer**.
- Verifier: **Reality Checker** (`testing-reality-checker`) — review-only division, absent from the BUILD log.
- Verdict: **independent**. Checked before this file was opened.

## Result per criterion

Every row is evidence the verifier reproduced by running commands, not text copied from the BUILD log.

- **C1 PASS** — `.github/workflows/ci.yml` job `required` (display name `ci/required`) aggregates `lint`, `types`, `test`, `verify-manifest`, `security`; ruleset 26387961 lists it as required; `check-runs` on `main` report `ci/required => success`.
- **C2 PASS** — CI enforces `--cov --cov-branch --cov-fail-under=80`; measured **92.8% line / 87.9% branch**.
- **C3 PASS** — `cli/main.py` 96.6%, `core/originality.py` 97.8%, `core/validator.py` 100.0%.
- **C4 PASS** — 195 test functions, 4.13s with coverage, unit subset 117 in 0.67s, 0 `sleep` / `random` / network.
- **C5 PASS** — 4 runtime dependencies; test, lint and audit tooling in `[dependency-groups].dev`.
- **C6 PASS** — `grep -rn "pragma: no cover" src/` returns 0.
- **C7 PASS** — 10 hooks, `pre-commit run --all-files` exits 0; hook repositories pinned to commit SHAs.
- **C8 PASS** — `mise run check` exits 0 and now runs lint, types, coverage, security and verify; `ci` is an alias.
- **C9 PASS** — release PR #41 auto-opened with a minor bump from `feat(ci)` #40, no manual edits.
- **C10 PASS** — tag `v1.6.0`, release published, assets `agency_agents-1.6.0-py3-none-any.whl` and `.tar.gz`.
- **C11 PASS** — the release commit wrote `1.5.0 → 1.6.0` in both `pyproject.toml` and `src/agency_agents/__init__.py`.
- **C12 PASS** — 31 declared labels, 31 in the repository, set difference empty in both directions.
- **C13 PASS** — 4 issue forms + `config.yml` with blank issues disabled and 3 contact links.
- **C14 PASS** — PR template requires `Closes #`, a Conventional type and a test-evidence block; `CODE_OF_CONDUCT.md` present.
- **C15 PASS** — ruleset 26387961: `enforcement: active`, `pull_request` required, `required_status_checks` = `ci/required` (strict), `deletion` and `non_fast_forward`, `bypass_actors: []`, `current_user_can_bypass: never`. Criterion amended in FRAME (see Amendments); the verifier judged the amendment legitimate and not a formality, because with zero bypass actors the maintainer cannot merge a red PR.
- **C16 PASS** — Dependabot covers `github-actions` and `uv` weekly; vulnerability alerts, security updates and automated fixes all enabled.
- **C17 PASS** — `codeql.yml` on `pull_request`, `push` and cron `17 4 * * 1`; `analyze` succeeded.
- **C18 PASS** — 31 remote `uses:` references, all 40-character SHAs, 0 tag refs.
- **C19 PASS** — all 5 workflows declare explicit `permissions:`; 0 `write-all`.
- **C20 PASS** — `CODEOWNERS` covers `.github/`, `/src/`, `/scripts/`, `/mise.toml`.
- **C21 PASS** — 0 `scripts/*.sh` references in `SECURITY.md`, `tools.json`, `divisions.json`; `FUNDING.yml` names `deuriib`.

## Verification passes

### Pass 1 — FAIL

Twenty criteria passed. **C15 FAILED**: the applied ruleset enforced 0 approvals while FRAME required 1, and the divergence was not recorded in the BUILD log. Six further findings were raised: the type-check leg could not fail, the aggregate accepted `skipped`, `mise run check` did not mirror CI, the changelog lacked `Removed` and its preamble, ten labels were unmanaged, and pre-commit was pinned by tag.

### Pass 2 — PASS-WITH-CONDITIONS

Everything above was re-checked. C15 was judged **PASS** against the amended contract. Five findings were confirmed fixed, and the ratchet was proven empirically: the verifier inserted a deliberate type error, observed `current=40 baseline=39` and exit 1, then removed it.

One condition remained: the shared composite action `.github/actions/quality-gate/action.yml` still ran bare `mypy` with `continue-on-error: true`, so the release path's type-check was decorative while `ci.yml` had moved to the ratchet — the two gates had drifted, which is precisely what the shared action exists to prevent.

### Condition resolved

The composite action now calls `bash scripts/ci/mypy_ratchet.sh`, identical to `ci.yml`. `grep -c continue-on-error` on the action returns 0. Both gates invoke the same script, so the drift is closed at the source.

## Findings

All findings are resolved. Listed with their original severity so the record is not flattering.

- **high — C15 approval count.** Resolved by amending FRAME with a dated, reasoned entry and re-signing both gates.
- **high — decorative type-check.** Resolved with a ratchet baseline (39 production errors, tests excluded). Proven to fail on regression.
- **medium — `skipped` accepted.** Resolved; the aggregate fails on `skipped`.
- **medium — `mise run check` parity.** Resolved; `check` mirrors CI and `ci` aliases it.
- **medium — changelog sections.** Resolved; `removed` maps to `Removed` and the preamble is restored.
- **medium — unmanaged labels.** Resolved; 31 declared, 31 present, no drift either direction.
- **low — pre-commit pinned by tag.** Resolved; all three revs are commit SHAs.

## Conditions carried to SHIP

- **Label deletion drift is undetectable** — the sync is additive and never deletes, so a label removed from `labels.yml` survives in the repository. Accepted as a deliberate trade-off to avoid destroying release-please's automation labels. — Owner: Platform Engineer — Due: 2026-11-23.
- **The mypy baseline tolerates 39 production errors** — the ratchet prevents growth but the backlog is real. Ratcheting down is a standing task, not a one-off. — Owner: Senior Developer — Due: 2026-12-14.

## Assigned team

- Domain (verifier): **Reality Checker** (`testing-reality-checker`) — independent, review-only division; ran two passes.
- Process steward: **Vasquez** (Project Management) — confirmed independence before opening the file, refused a passing verdict over a failing row in pass 1, and required the composite-action drift to be closed before signing pass 2.

## Gates

- Domain gate: Reality Checker — **PASS** (21/21 criteria verified; one condition raised in pass 2 and resolved before closure)
- Process gate: Vasquez — **PASS** (independence confirmed; every row carries reproduced evidence; findings severity-rated and resolved; two conditions carried to SHIP with owner and due date)
