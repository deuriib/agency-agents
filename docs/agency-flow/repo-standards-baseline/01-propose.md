# PROPOSE — repo-standards-baseline

## Approach

Build the whole baseline on one principle: a single aggregate check (`ci/required`)
proves every PR, and every other artifact (release, labels, templates, security
scans) is wired to feed it or to be fed by it. Run the work in three ordered waves
— **Wave 1 release integrity**, **Wave 2 quality gate**, **Wave 3 hardening** — so
that VERIFY can attribute a regression to one wave instead of a 21-criterion
blob. Release automation uses the repository's `GITHUB_TOKEN` (explicit user
override, recorded below), with a `schedule` backstop and an in-workflow gate,
because `GITHUB_TOKEN`-created PRs cannot trigger other workflows.

**Rejected alternative**: adopt a GitHub App token (or a fine-grained PAT) to let
the standard `ci/required` workflow run on release-please PRs. Rejected because
the user explicitly chose `GITHUB_TOKEN` and a zero-secret setup; the cost is
that release PRs are gated by an in-workflow job instead of the reusable CI
workflow, and the maintainer performs the final merge click.

## Planned deliverables (grouped by domain)

### Engineering — Platform Engineer

- **P1. Version reconciliation** — `pyproject.toml` `[project].version` `0.1.0` → `1.3.0`, matching `src/agency_agents/__init__.py`; no other change. Supports **C11** (single source of version truth) and unblocks **C9/C10**.
- **P2. Dependency groups and tool config** — move `pytest`, `pytest-asyncio` out of `[project].dependencies`; add `[dependency-groups].dev` with `pytest-cov`, `ruff`, `pre-commit`, `mypy`, `pip-audit`; add `[tool.pytest.ini_options]` (testpaths, `addopts = --cov --cov-branch`), `[tool.coverage.*]`, a **narrow** `[tool.ruff]` rule baseline, and a `[tool.mypy]` strict block (`strict = true`, no `ignore_missing_imports` blanket). Supports **C1**, **C2**, **C5**, **C6**.
- **P3. `ci.yml`** — one workflow with jobs `lint`, `types` (non-blocking in Wave 2, blocking from Wave 3, backed by the `[tool.mypy]` config from P2), `test`, `coverage-guard`, and `security` (dependency audit via `pip-audit --strict` plus `actionlint` on the workflow files). A final job literally named `ci/required` `needs:` every other job and fails if any failed. Each job invokes the shared composite action `.github/actions/quality-gate/action.yml`, which is also what `release.yml` calls, so the two gates cannot drift. Triggers: `pull_request`, `push` to `main`, plus `workflow_dispatch`. Supports **C1**, **C2**, **C4**.
- **P4. `release.yml`** — release-please action (`GITHUB_TOKEN`), `schedule` backstop at 06:00 UTC, in-workflow `release-gate` job that checks out the release PR branch and runs lint+test+coverage before permitting merge; `workflow_dispatch` for a manual tag pass. Supports **C9**, **C10**, **C11**.
- **P5. `release-please-config.json` + `.release-please-manifest.json` + `CHANGELOG.md`** — `release-type: python`, manifest seeded at `1.3.0`, changelog sections `Added/Changed/Fixed/Removed/Security`. Supports **C9**, **C10**, **C11**.
- **P6. `.pre-commit-config.yaml`** — `pre-commit-hooks` (trailing-whitespace, end-of-file-fixer, check-merge-conflict, check-added-large-files, check-yaml, check-toml), `ruff` (check + format check), `yamllint`, and one `repo: local` hook invoking `agency_agents lint`. Pinned to `rev:` tags. Supports **C7**.
- **P7. `mise.toml` rewrite** — every task gets `description`; add `check` (lint + types + test + coverage + verify), `ci` (exact CI parity), `hooks` (install pre-commit), `release-dry-run`; remove the misleading `full-pipeline` alias. Supports **C8**.
- **P8. `.github/labels.yml` + `labels-sync.yml`** — 21 labels across `type:`, `area:`, `priority:`, `status:`, `good first issue`; sync via `EndBug/label-sync` pinned to SHA. Supports **C12**.
- **P9. Issue forms and PR template** — `.github/ISSUE_TEMPLATE/{bug-report,feature-request,new-agent-request,docs-or-infra}.yml` + `config.yml` (blank issues disabled, contact links) ; rewritten `PULL_REQUEST_TEMPLATE.md` requiring linked issue, Conventional Commit type, and test evidence. Supports **C13**, **C14**.
- **P10. `CODE_OF_CONDUCT.md`** — Contributor Covenant v2.1 with a named enforcement contact. Supports **C14**.
- **P11. Ruleset as code** — `scripts/github/apply-ruleset.sh` + `ruleset.json` applied with `gh api`; requires PR, requires `ci/required`, 1 approval, blocks force-push and deletion. Bypass is **actor-scoped** (repository admin only) and cannot be scoped to a PR type — the release PR merge is therefore a documented, logged admin action, not a ruleset rule. Every bypass is recorded in the PR body with the reason. Supports **C15**.
- **P12. `.github/dependabot.yml`** — `github-actions` and `uv` ecosystems, weekly, grouped minor/patch updates; plus enabling vulnerability alerts and security updates through the API. Supports **C16**.
- **P13. `.github/workflows/codeql.yml`** — `github/codeql-action` for Python on `pull_request`, `push` to `main`, and weekly `schedule`. Supports **C17**.
- **P14. SHA pinning sweep** — every `uses:` across all workflows pinned to a 40-char SHA with a trailing `# vX.Y.Z` comment. Supports **C18**.
- **P15. Permissions sweep** — explicit `permissions:` block in every workflow, least privilege, no `write-all`. Supports **C19**.
- **P16. `.github/CODEOWNERS`** — coverage for `.github/`, `src/`, `scripts/`, `mise.toml`, `*.toml`, `*.json`. Supports **C20**.
- **P17. Documentation drift repair** — `SECURITY.md` rewritten for the Python CLI (no `scripts/*.sh`), `tools.json` and `divisions.json` `_note` fields corrected to reference the Python validators, `.github/FUNDING.yml` re-pointed to the fork owner. Supports **C21**.

### Engineering — Senior Developer

- **S1. Coverage floor campaign** — raise total coverage from 65% to ≥ 80% line / ≥ 75% branch by adding behavioural tests, prioritising the three worst modules. Supports **C2**, **C3**, **C6**.
- **S2. `cli/main.py` tests** — Typer `CliRunner` coverage for every command, flag, and error path; target ≥ 75% (from 42%). Supports **C3**.
- **S3. `core/originality.py` tests** — duplicate-detection behaviour, thresholds, and reporting; target ≥ 80% (from 12%). Supports **C3**.
- **S4. `core/validator.py` tests** — frontmatter, division, and naming validation paths; target ≥ 85% (from 67%). Supports **C3**.
- **S5. Test-suite hygiene** — reach ≥ 160 test functions, remove the 7 `assert len(...)`-only assertions by adding invariant checks, keep the unit subset under 30 s and total under 60 s. Supports **C4**, **C6**.

## Recorded override (user instruction)

- **Override**: the user explicitly chose the repository `GITHUB_TOKEN` for release automation over a GitHub App token or a fine-grained PAT.
- **Conflict**: GitHub suppresses workflows triggered by `GITHUB_TOKEN`-created events. Therefore release-please PRs will not run the reusable `ci.yml` workflow, and the merge commit will not trigger the tagging run.
- **Consequence accepted**: release PRs are gated by the in-workflow `release-gate` job instead of the standard required check; the maintainer performs the merge click; the tag and GitHub Release are produced by the 06:00 UTC scheduled run (worst case ~24 h after merge) or by `workflow_dispatch`.
- **Unaffected**: C9, C10, and C11 remain satisfiable and measurable; the "zero manual steps" ambition is reduced to "zero manual edits", with one manual merge.

## Risks

- **Release PR cannot merge because `ci/required` never reports on it** — mitigation: the `release-gate` job inside `release.yml` runs the same lint/types/test/coverage steps on the release branch, then the maintainer performs an actor-scoped admin merge; every bypass is logged in the PR body. Severity: **high**.
- **Two parallel gates (`ci/required` and `release-gate`) drift apart** — mitigation: both invoke the same composite action so their steps cannot diverge; `ci/required` stays the only required check and the release path is a documented exception, never a second gate. Severity: **medium**.
- **`uv.lock` goes stale after a version bump** — release-please has no Python lockfile updater, so the locked project version drifts; mitigation: CI runs `uv sync` without `--locked` in Wave 1, and a `lock-refresh` job runs `uv lock` on the release branch and commits it before the gate. Severity: **medium**.
- **Version drift produces a nonsense first release** — `0.1.0` vs `1.3.0` today; mitigation: P1 lands and is verified before release-please is enabled. Severity: **high**.
- **Ruff flags hundreds of pre-existing violations and CI is red on day one** — mitigation: P2 ships a deliberately narrow `select` set (`E9,F63,F7,F82,I`), expands by rule with a tracked issue, and never adds blanket `noqa`. Severity: **high**.
- **Coverage pushed to 80% with assertion-free tests** — mitigation: TST-04 enforced in review; Reality Checker samples 10 new tests and confirms they fail when the implementation is mutated. Severity: **medium**.
- **Ruleset bypass becomes a habit** — mitigation: bypass limited to one actor, logged, and reviewed in SHIP follow-ups. Severity: **medium**.
- **21 criteria in one BUILD lose traceability** — mitigation: three waves with independent exit checks; BUILD log groups by wave. Severity: **medium**.
- **`docs-site-mkdocs` blocks on conventions that do not exist yet** — mitigation: dependency rows below with owner and date. Severity: **low**.

## Verification plan

- **C1 (aggregate required check)** → Reality Checker reads `gh api repos/.../rulesets` and `gh pr checks` on a probe PR; Engineering confirms `ci/required` aggregates `lint`, `types`, `test`, `coverage-guard`, and `security`.
- **C2 (coverage thresholds)** → Evidence Collector captures the `pytest --cov --cov-branch` summary from a CI run showing fail-under 80 and branch ≥ 75.
- **C3 (module floors)** → Evidence Collector captures the per-module coverage table with `cli/main.py` ≥ 75, `originality.py` ≥ 80, `validator.py` ≥ 85.
- **C4 (suite size and determinism)** → Senior Developer runs `pytest --durations=10`; Evidence Collector confirms ≥ 160 tests, < 60 s total, < 30 s unit, and greps for `sleep`/network/`random`.
- **C5 (dependency split)** → Reality Checker inspects `pyproject.toml` and `uv.lock` to confirm runtime deps are the four declared ones and test tools live in `[dependency-groups].dev`.
- **C6 (`pragma: no cover` budget)** → Engineering greps the source; Reality Checker counts ≤ 5 occurrences and validates each is a `TYPE_CHECKING` or `__main__` guard.
- **C7 (pre-commit)** → Evidence Collector runs `pre-commit run --all-files` on a clean tree and captures exit code 0 and the hook list.
- **C8 (mise parity)** → Engineering runs `mise run check` and diffs its steps against `ci.yml`; Reality Checker confirms exit 0 and no orphan tasks.
- **C9 (release PR)** → Platform Engineer pushes a `feat:` commit to a scratch branch merged to `main`; Evidence Collector captures the release PR body showing the computed version bump and no manual edits.
- **C10 (tag and release)** → Evidence Collector captures `gh release view` with the tag, the changelog section, and the sdist/wheel assets.
- **C11 (version ownership)** → Reality Checker confirms `pyproject.toml` and `__init__.py` both read the released version, and that the release PR is the only writer.
- **C12 (labels)** → Engineering captures `gh label list` count and the sync workflow run; Reality Checker confirms idempotency by re-running the sync with zero diff.
- **C13 (issue forms)** → Evidence Collector captures the four forms plus `config.yml` via `gh api` and the rendered new-issue chooser.
- **C14 (PR template and CoC)** → Reality Checker inspects `PULL_REQUEST_TEMPLATE.md` for the three required sections and confirms `CODE_OF_CONDUCT.md` exists with a contact.
- **C15 (ruleset)** → Evidence Collector captures `gh api repos/.../rulesets` showing required PR, required check, approval count, blocked force-push and deletion; then attempts a direct push and records the rejection.
- **C16 (Dependabot)** → Evidence Collector captures `gh api repos/...` showing vulnerability alerts and security updates enabled, plus the `dependabot.yml` ecosystems.
- **C17 (CodeQL)** → Evidence Collector captures a successful CodeQL run on a PR and the scheduled workflow registration.
- **C18 (SHA pinning)** → Engineering greps all `uses:` lines for 40-char SHAs; Reality Checker confirms 0 tag/branch refs.
- **C19 (permissions)** → Reality Checker inspects every workflow for an explicit `permissions:` block and confirms 0 `write-all`.
- **C20 (CODEOWNERS)** → Engineering confirms `.github/CODEOWNERS` exists; GitHub shows requested reviewers on a probe PR touching `src/`.
- **C21 (drift zero)** → Reality Checker greps the four documents for `scripts/*.sh` references and confirms 0 hits, and confirms `FUNDING.yml` names the fork owner.

## Cross-domain dependencies

- Release workflow cannot be wired until the `GITHUB_TOKEN` mechanics and the `schedule` backstop are frozen in a written design. — Owner: Platform Engineer — Due: 2026-11-09.
- Test expansion cannot start until `pytest-cov` and the `[dependency-groups].dev` split land, otherwise coverage cannot be measured locally. — Owner: Platform Engineer — Due: 2026-11-09.
- Release-please cannot be enabled until the version reconciliation (P1) is merged and `uv.lock` is regenerated. — Owner: Platform Engineer — Due: 2026-11-09.
- `docs-site-mkdocs` needs the SHA-pinning and least-privilege `permissions:` conventions from `ci.yml` before its Pages workflow can be written. — Owner: Platform Engineer — Due: 2026-11-16.
- `docs-site-mkdocs` needs the `ci/required` aggregate to gain a docs build job when that project lands, otherwise its build is ungated. — Owner: Platform Engineer — Due: 2026-11-23.
- VERIFY cannot start until Waves 1–3 each report their own exit check, otherwise a 21-criterion verdict cannot attribute failures. — Owner: Senior Developer — Due: 2026-11-30.

## Assigned team

- Domain (release and CI): **Platform Engineer** (`engineering-platform-engineer`) — P1–P17, owns `GITHUB_TOKEN` release mechanics, ruleset-as-code, SHA pinning, labels, templates, Dependabot, CodeQL, drift repair.
- Domain (tests and coverage): **Senior Developer** (`engineering-senior-developer`) — S1–S5, owns coverage floors, suite growth, determinism budget, assertion quality.
- Verification (review-only, not producer domain): **Reality Checker** (`testing-reality-checker`) for the independent verdict; **Evidence Collector** (`testing-evidence-collector`) for CI logs, `gh api` snapshots, and probe-PR evidence.
- Process steward: **Vasquez** (Project Management) — signs the process gate. Confirmed: all 21 criteria map to at least one deliverable; all six dependencies carry an owner and an absolute date; no deliverable adds a criterion beyond FRAME.

## Gates

- Domain gate: Software Architect — PASS (approach and sequencing sound; C1–C21 mapped one-to-one; verification plan exhaustive; residual editorial items deferred to BUILD)
- Process gate: Vasquez — PASS (path correct; 6/6 dependencies carry owner and absolute date; domain owners and process steward named; no unowned boundary; override recorded explicitly)
