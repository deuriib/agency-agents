# BUILD — repo-standards-baseline

> **Wave 1 of 3 in progress.** Wave 1 (release integrity: P1, P2, P4, P5) is
> produced. Waves 2 and 3 are not. This file stays open until all 21 criteria
> are `[x]`.

## Log (one row per FRAME criterion)

- [ ] C1 — aggregate `ci/required` check → pending Wave 2: `.github/workflows/ci.yml` (P3).
- [ ] C2 — coverage thresholds enforced → pending Wave 2: `.github/workflows/ci.yml` coverage step reading `[tool.coverage.report]` in `pyproject.toml` (P2/P3).
- [ ] C3 — module coverage floors → pending Wave 2: `src/agency_agents/tests/unit/` campaign (S1–S4).
- [ ] C4 — ≥160 tests, determinism, runtime budget → pending Wave 2: `src/agency_agents/tests/` growth (S5).
- [x] C5 — runtime vs dev dependency separation → `pyproject.toml` (`[project].dependencies` holds 4 packages; `[dependency-groups].dev` holds 7 tools) + regenerated `uv.lock`.
- [x] C6 — `# pragma: no cover` budget → `grep -rn "pragma: no cover" src/` returns 0 hits.
- [ ] C7 — pre-commit hooks → pending Wave 2: `.pre-commit-config.yaml` (P6).
- [ ] C8 — `mise run check` parity with CI → pending Wave 2: `mise.toml` (P7).
- [ ] C9 — release PR opened from Conventional Commits → `.github/workflows/release.yml` + `release-please-config.json` produced; requires one probe `feat:` PR to observe the computed bump.
- [ ] C10 — tag + GitHub Release with artifacts → `.github/workflows/release.yml` scheduled run; requires the first merged release PR.
- [ ] C11 — version owned by the release process → `release-please-config.json` + `.release-please-manifest.json` seeded at `1.3.0` + `CHANGELOG.md`; "never hand-edited" is unproven until the first release.
- [ ] C12 — labels as code → pending Wave 2: `.github/labels.yml` + `.github/workflows/labels-sync.yml` (P8).
- [ ] C13 — issue forms → pending Wave 2: `.github/ISSUE_TEMPLATE/*.yml` + `config.yml` (P9).
- [ ] C14 — PR template + Code of Conduct → pending Wave 2: `.github/PULL_REQUEST_TEMPLATE.md` + `CODE_OF_CONDUCT.md` (P9/P10).
- [ ] C15 — `main` ruleset protection → pending Wave 3: `scripts/github/apply-ruleset.sh` + `scripts/github/ruleset.json` (P11).
- [ ] C16 — Dependabot + vulnerability alerts → pending Wave 3: `.github/dependabot.yml` + API enablement (P12).
- [ ] C17 — CodeQL for Python → pending Wave 3: `.github/workflows/codeql.yml` (P13).
- [ ] C18 — SHA-pinned actions everywhere → new workflows already pinned; legacy `.github/workflows/quality.yml` sweep pending Wave 3 (P14).
- [ ] C19 — least-privilege `permissions:` in every workflow → pending Wave 3: `.github/workflows/quality.yml` (P15).
- [ ] C20 — `CODEOWNERS` → pending Wave 3: `.github/CODEOWNERS` (P16).
- [ ] C21 — documentation drift zero → pending Wave 3: `SECURITY.md`, `tools.json`, `divisions.json`, `.github/FUNDING.yml` (P17).

## Deviations from PROPOSE

- `pyproject.toml` `description` populated ("A catalog of specialized AI agent personas…") — explicit user instruction during BUILD; it satisfies no FRAME criterion and is recorded here rather than absorbed silently.
- Lock refresh implemented as a step inside the `release-gate` job instead of a separate `lock-refresh` job — same behaviour, one checkout, and the gate cannot pass with a stale lock.
- `ruff check --fix` applied to 19 pre-existing `I001` import-order findings across `src/agency_agents/**` — required to make the P2/C7 baseline green; mechanical only, 99 tests still pass, and `ruff check .` is now clean.
- `.gitignore` extended with `.coverage`, `.coverage.*`, `coverage.xml`, `cov_html/` — otherwise coverage tooling artifacts get committed and pollute the parity check.
- `uv.lock` grew ~960 lines because the dev group now resolves ruff, mypy, pip-audit, pre-commit, and pytest-cov.
- `.github/workflows/quality.yml` touched in Wave 1 instead of Wave 3 — CI failed with `Failed to spawn: pytest` because `astral-sh/setup-uv@v1` ships uv 0.4.4, which predates `[dependency-groups]` (PEP 735, uv 0.4.27) and therefore installed only runtime dependencies. Pinning uv to `0.12.12` fixes it; replacing the whole workflow is still Wave 2/3.

## Artifacts produced (grouped by domain)

- Engineering:
  - `pyproject.toml` — version `1.3.0`, 4 runtime deps, `[dependency-groups].dev`, pytest/coverage/ruff/mypy configuration, populated description.
  - `uv.lock` — regenerated; project entry records `version = "1.3.0"`.
  - `release-please-config.json` — `python` release type, Keep a Changelog sections (Added/Changed/Fixed/Security), package `.`.
  - `.release-please-manifest.json` — seeded at `1.3.0`.
  - `CHANGELOG.md` — Keep a Changelog header, generated entries owned by release-please.
  - `.github/workflows/release.yml` — release-please on push/schedule/dispatch, inline `release-gate`, lock refresh, GITHUB_TOKEN override documented in-file.
  - `.github/actions/quality-gate/action.yml` — shared composite action used by both gates so they cannot drift.
  - `.github/workflows/quality.yml` — `setup-uv` pinned to uv `0.12.12` so `[dependency-groups]` is honoured.
  - `.gitignore` — coverage artifacts ignored.
  - `src/agency_agents/**` (19 files) — import ordering normalised by `ruff --fix`.

## Cross-domain handoffs

- Dev group with `pytest-cov`, `ruff`, `mypy`, `pip-audit` available for the coverage campaign — Owner: Senior Developer — Done.
- Version reconciled to `1.3.0` so release-please has a truthful baseline — Owner: Senior Developer — Done.
- Shared composite action available for `ci.yml` to reuse — Owner: Senior Developer — Done.
- SHA-pinning and least-privilege `permissions:` conventions available to `docs-site-mkdocs` — Owner: Platform Engineer — Pending (due 2026-11-16).
- `ci/required` aggregate gains a docs build job when the site project lands — Owner: Platform Engineer — Pending (due 2026-11-23).
- Per-wave exit checks so VERIFY can attribute regressions — Owner: Senior Developer — Pending (due 2026-11-30).

## Assigned team

- Domain: **Platform Engineer** (`engineering-platform-engineer`) — produced Wave 1: version reconciliation, dependency split, release-please config, release workflow, composite action.
- Domain: **Senior Developer** (`engineering-senior-developer`) — next: Wave 2 test expansion and coverage floors (S1–S5).
- Process steward: **Vasquez** (Project Management) — confirmed 21/21 criteria have a log row, 5 deviations recorded with justification, no PROPOSE deliverable dropped, and 0 unchecked rows claimed as done.

## Gates

- Domain gate: N/A — deferred to VERIFY
- Process gate: Vasquez — PENDING (Wave 1 of 3 complete; 19 of 21 criteria still unchecked, BUILD is not closeable)
