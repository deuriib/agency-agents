# BUILD — docs-site-mkdocs

## Overview

Execution log for the `docs-site-mkdocs` pipeline (GitHub Issue #70). All deliverables D1 through D13 have been implemented, tested, and validated according to the NEXUS Producer ↔ Validator loop protocol.

## Implemented Workstreams & Artifacts

### 1. Build and Structure (D1–D5)
- **`mkdocs.yml`**: Configured at repository root with `theme: material`, language switcher configuration, and explicit `docs_dir: site-docs/docs` (satisfying the hard constraint that `docs_dir != docs/`).
- **`.gitignore`**: Updated to ignore `site/` and generated `site-docs/`.
- **`scripts/build_docs_site.py`**: Committed deterministic generator that parses all 18 divisions from `divisions.json` and all 298 agent persona markdown files, creating landing pages and individual agent documentation with zero hand-edited drift.
- **Strict Build**: `NO_MKDOCS_2_WARNING=1 uv run mkdocs build --strict` executes with 0 warnings, 0 broken links, and 0 missing assets.
- **Leakage Prevention (D4)**: Verified 0 files from `docs/agency-flow/**` originate or leak into `site/`.
- **Mise Tasks (D5)**: Added `docs-build` (builds site and executes test suite) and `docs-serve` (runs local development server) to `mise.toml`.

### 2. Internationalization & Core Translations (D6–D8, DENY-07)
- **Plugin Configuration (D6)**: Configured `mkdocs-static-i18n` with `en` default and `es` second locale. 100% of the 642 content HTML pages carry the language switcher element (`md-header__option` / `Select language`).
- **Translations Set (D8)**: Authored 22 Spanish counterparts for all core pages:
  - English & Spanish Home (`index.md`)
  - English & Spanish Installation & Quickstart (`installation.md`)
  - English & Spanish Contributing Guide (`contributing.md`)
  - English & Spanish Security Policy (`security.md`)
  - English & Spanish Division Landing Pages across all 18 divisions (`divisions/*/index.md`)
  Every Spanish page is verified non-empty with a distinct SHA-256 from its English source.
- **Fallback Invariant (D7)**: Validated exact invariant: `fallback_count == total_pages - 22` (321 total ES pages - 22 translated core = 299 fallback pages, with 0 intersection between fallback and core sets).
- **Human Review Disclosure (DENY-07)**: Human review recorded for Spanish translations prior to production merge.

### 3. Delivery & Automation (D9–D13)
- **GitHub Actions Workflow (`.github/workflows/docs.yml`)**:
  - Triggers on PR (build only) and push to `main` (build + publish).
  - Explicit least-privilege permissions: `contents: read`, `pages: write`, `id-token: write`.
  - Pinned actions with full 40-character commit SHAs: `actions/checkout`, `astral-sh/setup-uv`, `actions/upload-pages-artifact`, `actions/deploy-pages`.
  - Runtime budget: strictly enforced build < 120s with step summary generation.
- **GitHub Pages Configuration (D11)**: Enabled via `gh api` with `build_type=workflow`. Target URL `https://deuriib.github.io/agency-agents/`.
- **Attribution & Site URL (D13)**: `site_url` set to `https://deuriib.github.io/agency-agents/` and footer attribution credits upstream `msitarzewski/agency-agents`.
