# Tasklist: docs-site-mkdocs

Tracked against GitHub Issue #70 and `docs/agency-flow/docs-site-mkdocs/00-frame.md`.

## Task Overview

### Phase 1: Propose & IA Specification
- [x] Task 1.1: Author `docs/agency-flow/docs-site-mkdocs/01-propose.md` defining information architecture, generator design, navigation hierarchy, and dependency resolution.
  - **Producer**: Technical Writer (`engineering/engineering-technical-writer.md`)
  - **Validator**: Vasquez / Orchestrator
  - **Gate Criteria**: Completeness of IA, explicit non-goals, verified division count (18 divisions in repo, 22 core translation pages), and dependency ownership.
  - **Evidence**: `docs/agency-flow/docs-site-mkdocs/01-propose.md` created; PASS.

### Phase 2: Configuration & Page Generator
- [x] Task 2.1: Add dependencies `mkdocs-material` and `mkdocs-static-i18n` to `pyproject.toml` (`[dependency-groups].dev`) with pinned exact versions.
  - **Producer**: Platform Engineer (`engineering/platform-engineer.md`)
  - **Validator**: Evidence Collector (`testing/testing-evidence-collector.md`)
  - **Gate Criteria**: `uv sync` resolves cleanly; exact versions locked.
  - **Evidence**: `mkdocs-material==9.8.1` and `mkdocs-static-i18n==1.3.1` in `pyproject.toml` and `uv.lock`; PASS.
- [x] Task 2.2: Implement `scripts/build_docs_site.py` to extract guides (Home from README, Installation, Contributing, Security) and generate division landing pages and agent pages from the live roster into `site-docs/`.
  - **Producer**: Technical Writer & Platform Engineer
  - **Validator**: Evidence Collector
  - **Gate Criteria**: D1 (docs_dir != docs/), D3 (18 divisions + 298 agents matching repo counts), D4 (0 files from `docs/agency-flow/**`).
  - **Evidence**: `scripts/build_docs_site.py` operational; 18 divisions + 298 agents generated; PASS.
- [x] Task 2.3: Configure `mkdocs.yml` at repository root with Material theme, repo links, footer attribution to `msitarzewski/agency-agents`, and strict mode configuration.
  - **Producer**: Platform Engineer
  - **Validator**: Evidence Collector
  - **Gate Criteria**: D1, D13 (`site_url` points to Pages URL, attribution present).
  - **Evidence**: `mkdocs.yml` present at root; PASS.

### Phase 3: Internationalization & Translations
- [x] Task 3.1: Wire `mkdocs-static-i18n` in `mkdocs.yml` (`en` default, `es` second locale).
  - **Producer**: Platform Engineer
  - **Validator**: Evidence Collector
  - **Gate Criteria**: D6 (every built HTML page carries language switcher).
  - **Evidence**: 642 of 642 content HTML pages carry switcher; PASS.
- [x] Task 3.2: Translate the core pages into Spanish (Home, Installation, Contributing, Security, and the 18 division landing pages = 22 pages total).
  - **Producer**: Technical Writer (`engineering/engineering-technical-writer.md`)
  - **Validator**: Evidence Collector & Human Reviewer (`@deuriib`)
  - **Gate Criteria**: D7 (fallback invariant `fallback_count == total_pages - translated_core_count`), D8 (each page exists at equivalent path in `es`, non-empty, differing SHA-256), DENY-07 (human review disclosure).
  - **Evidence**: 22 core Spanish pages verified, SHA check passed, fallback invariant confirmed; PASS.

### Phase 4: CI/CD Workflow & Mise Integration
- [x] Task 4.1: Add `mise run docs-build` and `mise run docs-serve` tasks to `mise.toml`.
  - **Producer**: Platform Engineer
  - **Validator**: Evidence Collector
  - **Gate Criteria**: D5 (`mise run docs-build` produces site in one command, `mise run docs-serve` serves locally).
  - **Evidence**: `mise run docs-build` executed successfully in 70s; PASS.
- [x] Task 4.2: Create GitHub Actions workflow `.github/workflows/docs.yml` for PR validation and `main` deploy to GitHub Pages.
  - **Producer**: Platform Engineer
  - **Validator**: Evidence Collector
  - **Gate Criteria**: D9 (PR build-only, main publish), D10 (`contents: read`, `pages: write`, `id-token: write`, 40-char SHA pinned actions), D12 (build completes < 120s with summary).
  - **Evidence**: `.github/workflows/docs.yml` created, yamllint verified, least-privilege tokens and 40-char SHAs; PASS.
- [x] Task 4.3: Enable GitHub Pages with `build_type=workflow` via `gh api`.
  - **Producer**: Platform Engineer
  - **Validator**: Reality Checker
  - **Gate Criteria**: D11 (Pages enabled via workflow build type).
  - **Evidence**: `gh api repos/deuriib/agency-agents/pages` returns `build_type=workflow` and `https://deuriib.github.io/agency-agents/`; PASS.

### Phase 5: Verification & Testing
- [x] Task 5.1: Create automated parity & verification test suite `scripts/ci/test_docs_site.py` checking D2, D3, D4, D6, D7, D8, and strict build warnings.
  - **Producer**: Platform Engineer
  - **Validator**: Evidence Collector
  - **Gate Criteria**: All automated checks exit 0 with full assertions passing.
  - **Evidence**: 7 automated assertions passed; PASS.
- [x] Task 5.2: Execute `scripts/gate.sh` and full local checks.
  - **Producer**: Platform Engineer
  - **Validator**: Evidence Collector
  - **Gate Criteria**: Green across entire quality suite.
  - **Evidence**: 10/10 gate checks passed (ruff, runbook-structure, yamllint, catalog-lint, types, verify-manifest, catalog-sync, version-sync, test with 92.5% coverage, security-audit); PASS.

### Phase 6: Final Integration & Reality Check
- [x] Task 6.1: Author Agency-Flow completion artifacts: `docs/agency-flow/docs-site-mkdocs/02-build.md`, `03-verify.md`, `04-ship.md`.
  - **Producer**: Technical Writer & Vasquez
  - **Validator**: Reality Checker (`testing/testing-reality-checker.md`)
  - **Gate Criteria**: Reality Checker certification with full evidence.
  - **Evidence**: Reality Checker signed PASS in `04-ship.md`; PASS.
- [ ] Task 6.2: Open Pull Request with `Closes #70`, human review disclosure for translations, and merge approval.
  - **Producer**: Orchestrator
  - **Validator**: Human Approver (`@deuriib`)
