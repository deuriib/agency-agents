# FRAME — repo-standards-baseline

## Goal

Make `agency-agents` a production-grade repository: every merge is gated by an
enforced CI quality bar, every release is cut automatically from Conventional
Commits, and the baseline is tested and hardened against supply-chain and
contribution risk. Nothing advances on a promise, a low coverage threshold, or a
manual step.

## Success criteria (measurable)

### CI and quality gates

- [ ] C1. A single required status check named `ci/required` runs on every PR and every push to `main`, aggregating lint, type-check, tests+coverage, and security scan; it is registered as a required check on `main`.
- [ ] C2. CI enforces `pytest --cov --cov-branch --cov-fail-under=80`, with branch coverage reported and a floor of 75%; the threshold is not lowered to match the current 65% baseline.
- [ ] C3. Module coverage floors are met: `cli/main.py` ≥ 75% (from 42%), `core/originality.py` ≥ 80% (from 12%), `core/validator.py` ≥ 85% (from 67%).
- [ ] C4. The suite grows from 101 to ≥ 160 test functions; total runtime < 60 s and unit subset < 30 s on GitHub-hosted runners; zero `sleep`, zero network calls, zero `random` without a seed.
- [ ] C5. Runtime and development dependencies are separated: `pytest`, `pytest-asyncio`, `pytest-cov`, `ruff`, `pre-commit` live in `[dependency-groups].dev`, and `[project].dependencies` contains only `prompt-toolkit`, `pydantic`, `rich`, `typer`.
- [ ] C6. `# pragma: no cover` appears ≤ 5 times and only on `TYPE_CHECKING` blocks or `__main__` guards.

### Local developer experience

- [ ] C7. `.pre-commit-config.yaml` defines ≥ 6 hooks (ruff check, ruff format check, yamllint, trailing-whitespace, end-of-file-fixer, check-merge-conflict, check-added-large-files, custom `agency_agents lint`), and `pre-commit run --all-files` exits 0 on a clean tree.
- [ ] C8. `mise run check` reproduces the CI gate locally and exits 0; `mise tasks` lists every task with a description and no orphan task.

### Release automation

- [ ] C9. `release-please` is configured (`release-please-config.json` + `.release-please-manifest.json`, release type `python`) so that a `feat:` commit merged to `main` opens a release PR that would bump the minor version, with zero manual edits.
- [ ] C10. Merging a release PR produces a `vX.Y.Z` git tag, a `CHANGELOG.md` entry under the new version, and a published GitHub Release carrying the sdist and wheel as assets.
- [ ] C11. `pyproject.toml` `[project].version` is updated by the release process and never edited by hand; `CHANGELOG.md` follows Keep a Changelog sections (`Added`, `Changed`, `Fixed`, `Removed`, `Security`).

### Contribution surface

- [ ] C12. `.github/labels.yml` is the single source of truth for labels, defines ≥ 15 labels across ≥ 5 categories (`type:`, `area:`, `priority:`, `status:`, `good first issue`), and a sync workflow runs on push to `main` producing zero drift.
- [ ] C13. ≥ 4 issue forms exist (bug, feature request, new-agent request, docs/infra task) plus `config.yml` with blank issues disabled and ≥ 2 contact links pointing to the right channels.
- [ ] C14. `PULL_REQUEST_TEMPLATE.md` requires a linked issue, a test-evidence line, and a Conventional Commits type; `CODE_OF_CONDUCT.md` exists at repo root.

### Repository hardening

- [ ] C15. `main` is protected by a repository ruleset (not manual UI clicks): require a pull request, require `ci/required`, block force-push and deletion, and disallow direct pushes. Human approval is **not** required — see Amendments — because GitHub forbids self-approval and a single-maintainer repository would deadlock. Verified with `gh api repos/deuriib/agency-agents/rulesets`.
- [ ] C16. Dependabot is configured for `github-actions` and `uv` ecosystems on a weekly schedule; vulnerability alerts and Dependabot security updates are enabled (`gh api` shows both `enabled`).
- [ ] C17. CodeQL for Python runs on pull requests and on a weekly schedule, and the workflow file is committed in `.github/workflows/`.
- [ ] C18. Every `uses:` reference in `.github/workflows/` is pinned to a full 40-character commit SHA — 0 tag or branch refs — and Dependabot keeps them updated.
- [ ] C19. Every workflow declares an explicit least-privilege `permissions:` block; 0 workflows rely on the default token permissions and 0 use `write-all`.
- [ ] C20. `CODEOWNERS` exists at `.github/CODEOWNERS` covering `.github/`, `src/`, `scripts/`, and `mise.toml`.
- [ ] C21. Documentation drift is zero: `SECURITY.md`, `tools.json` `_note`, and `divisions.json` `_note` contain 0 references to non-existent `scripts/*.sh` files, and `.github/FUNDING.yml` names the fork owner, not the upstream owner.

## Scope

- In: `.github/**` (workflows, issue forms, PR template, `CODEOWNERS`, `dependabot.yml`, `labels.yml`, `FUNDING.yml`), `.pre-commit-config.yaml`, `pyproject.toml` (dev tooling, pytest, coverage, ruff, dependency groups — not runtime behaviour), `mise.toml`, `release-please-config.json`, `.release-please-manifest.json`, `CHANGELOG.md`, test files under `src/agency_agents/tests/`, `CODE_OF_CONDUCT.md`, and documentation corrections for `SECURITY.md` and the catalog `_note` fields.
- Out: PyPI publishing, Trusted Publishing, and any namespace claim (deferred by explicit decision — the repo is a public fork of `msitarzewski/agency-agents`); changes to agent content under the division directories (`engineering/`, `marketing/`, `design/`, etc.); refactoring of `src/agency_agents` business logic beyond the seams required to reach the coverage floors; relocation of tests from `src/agency_agents/tests/` to a top-level `tests/` directory; container images; upstream sync policy; translation work (`CONTRIBUTING_zh-CN.md`, `ja`, `ko`).

## Domain profile

- Domains involved: Engineering
- Deliverable type: code
- Optional phases: research? no — measure? no

Rationale for a single domain: every artifact this project produces is a
configuration or code artifact owned by Engineering. The Testing and Security
divisions appear only as **verifiers** in VERIFY, so they are correctly excluded
from the producer domain profile. Appointing a Project Management producer would
trigger the PM-as-deliverable edge case for label and template governance; that
path was considered and rejected because `.github/` configuration is platform
engineering territory, not a PM deliverable.

## Constraints

- Python 3.13 only; `uv` is the sole package manager. No `pip install`, `poetry`, or `pipx` commands in CI or mise tasks.
- Release tooling must run on GitHub-hosted runners using the default `GITHUB_TOKEN` only — no personal access token, no stored secret.
- The repository is a public fork: no PyPI publication, no upstream write access, no upstream branch pushes.
- Branch protection must be applied through the ruleset API so it is reproducible, never by manual UI configuration.
- Every new workflow must pass `actionlint`-equivalent review: explicit `permissions:`, SHA-pinned actions, `concurrency:` group on PR workflows.
- Test suite wall clock stays under 60 s in CI; the unit subset stays under 30 s (TST-05).
- **Recorded deviation (TST-02)**: tests remain under `src/agency_agents/tests/{unit,integration}/` and are not moved to the top-level `tests/` tree mandated by TST-02. Reason: the package ships tests inside `src/` today, the move touches ~1,358 lines and the build backend config, and mixing it with the coverage work would make VERIFY unable to attribute regressions. Follow-up owner and date required at SHIP.
- No new runtime dependency may be introduced by this project. Dev dependencies only, via `[dependency-groups]`.
- Coverage floors are floors, not targets to be met by excluding code; diminishing the gate to make CI green is a process-gate failure (DENY-04).

## Amendments

- **2026-11-02 — C15 approval count (FRAME reopened).** The original criterion
  required 1 approving review. Independent VERIFY failed C15 because the applied
  ruleset enforces 0. The maintainer explicitly chose to keep 0 approvals and
  amend the criterion rather than add a reviewer or a bypass actor. Reason: this
  is a single-maintainer repository and GitHub does not permit self-approval, so
  a mandatory approval count would block every merge and force a standing bypass
  actor — strictly worse than no approval requirement, because that bypass would
  also disable the status-check rule. The controls that carry the actual risk
  stay enforced and verified: pull request required, `ci/required` required,
  force-push blocked, deletion blocked, and no bypass actors. Both gates are
  re-signed after the amendment.

## Assigned team

- Domain: **Platform Engineer** (`engineering-platform-engineer`) — owns CI/CD workflows, release-please, rulesets, Dependabot, CodeQL, SHA pinning, mise developer experience, and `.github/` contribution surface. Signs the domain gate for C1, C7–C21.
- Domain: **Senior Developer** (`engineering-senior-developer`) — owns test-suite expansion across `core/`, `infrastructure/`, and `cli/`, and the dev-dependency split. Signs the domain gate for C2–C6.
- Verification (not in the domain profile — review-only division): **Reality Checker** (`testing-reality-checker`) for VERIFY sign-off with evidence, supported by **Evidence Collector** (`testing-evidence-collector`) for CI-run and API-snapshot proof.
- Process steward: **Vasquez** (Project Management) — signs the process gate only. Staffing is feasible: Platform Engineer and Senior Developer both exist in the Engineering roster; all 21 criteria are measurable from artifacts (workflow files, `gh api` output, pytest coverage reports, `pre-commit` exit codes).

## Gates

- Domain gate: Product Manager — PASS (re-signed 2026-11-02 after the C15 amendment; C15 amended to no-approval, remaining controls enforced)
- Process gate: Vasquez — PASS (amendment dated and reasoned; only C15 narrowed; C1/C18/C19/C20 untouched; all 21 criteria remain measurable)
