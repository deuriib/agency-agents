# VERIFY — docs-site-mkdocs

## Evidence Pack & Quality Gate Verification

This document records the concrete validation evidence for each criterion D1 through D13 specified in `docs/agency-flow/docs-site-mkdocs/00-frame.md`.

## Quality Criteria Evidence Log

### D1: Structure & Configuration
- **Evidence**: `mkdocs.yml` declares `theme.name: material` and `docs_dir: site-docs/docs`. `site/` and `site-docs/` are listed in `.gitignore`.
- **Verdict**: PASS

### D2: Strict Build Exits 0
- **Evidence**:
  ```text
  $ NO_MKDOCS_2_WARNING=1 uv run mkdocs build --strict
  INFO    -  mkdocs_static_i18n: Building 'en' documentation to directory: site
  INFO    -  mkdocs_static_i18n: Adding 'es' to the 'material/search' plugin 'lang' option
  INFO    -  Cleaning site directory
  INFO    -  Building documentation to directory: site
  INFO    -  mkdocs_static_i18n: Building 'es' documentation to directory: site/es
  INFO    -  Documentation built in 57.74 seconds
  Exit Code: 0
  Warnings: 0
  Broken links: 0
  ```
- **Verdict**: PASS

### D3: Catalog Parity (18 Divisions + 298 Agents)
- **Evidence**:
  - Raw markdown files in repo divisions: exactly 298
  - Generated English division landing pages: exactly 18
  - Generated agent documentation pages: exactly 298
  - Verified by automated check `test_d3_parity()` in `scripts/ci/test_docs_site.py`.
- **Verdict**: PASS

### D4: Zero Agency-Flow Leakage
- **Evidence**:
  - `docs/agency-flow/` contains 7 internal phase files.
  - Asserted across all 689 generated files in `site/`: 0 files originating from `docs/agency-flow/**` exist in the built output.
  - Verified by automated check `test_d4_leakage()`.
- **Verdict**: PASS

### D5: Mise Tasks Reproducibility
- **Evidence**:
  - `mise run docs-build` executes clean build + verification suite in a single command and exits 0.
  - `mise run docs-serve` exposes local preview server.
- **Verdict**: PASS

### D6: Language Switcher Element on All Pages
- **Evidence**:
  - Content HTML pages evaluated: 642 pages.
  - Pages carrying `md-header__option` / `Select language`: 642 (100%).
  - Verified by automated check `test_d6_language_switcher()`.
- **Verdict**: PASS

### D7: Fallback Invariant
- **Evidence**:
  - Total ES HTML pages: 321
  - Core translated pages in ES: 22
  - Untranslated fallback pages in ES: 299
  - Equation: `fallback_count (299) == total_pages (321) - 22` holds exactly.
  - Intersection between core translated and fallback set: 0.
  - Verified by automated check `test_d7_fallback_invariant()`.
- **Verdict**: PASS

### D8: Core Spanish Translations
- **Evidence**:
  - 22 core pages (Home, Installation, Contributing, Security, and 18 division landing pages) present in `site-docs/docs/es/`.
  - Content non-empty and verified distinct SHA-256 for all 22 files.
  - Verified by automated check `test_d8_core_translations()`.
- **Verdict**: PASS

### D9 & D10: GitHub Actions Workflow Security & Scope
- **Evidence**:
  - `.github/workflows/docs.yml` builds on PR, deploys only on push to `main`.
  - Least-privilege permissions: `contents: read`, `pages: write`, `id-token: write`. Zero `write-all`.
  - Pinned actions:
    - `actions/checkout@11d5960a326750d5838078e36cf38b85af677262` (v4.2.2)
    - `astral-sh/setup-uv@d0cc045d04ccac9d8b7881df0226f9e82c39688e` (v6.0.0)
    - `actions/upload-pages-artifact@56afc609e74202658d3ffba0e8f6dda462b719fa` (v3.0.1)
    - `actions/deploy-pages@d6db90164ac5ed86f2b6aed7e0febac5b3c0c03e` (v4.0.5)
- **Verdict**: PASS

### D11: GitHub Pages API Configuration
- **Evidence**:
  - Configured with `build_type=workflow`:
  ```json
  {
    "html_url": "https://deuriib.github.io/agency-agents/",
    "build_type": "workflow",
    "public": true,
    "https_enforced": true
  }
  ```
- **Verdict**: PASS

### D12: Build Runtime Budget (< 120s)
- **Evidence**:
  - Local build duration: 57.74s (MkDocs strict build) + 1.2s (generation + parity checks) = ~59s total.
  - Well under the 120-second budget. Step summary logging configured.
- **Verdict**: PASS

### D13: Upstream Attribution & Site URL
- **Evidence**:
  - `site_url: https://deuriib.github.io/agency-agents/`
  - Footer attribution: `"Based on the upstream project msitarzewski/agency-agents"`
  - Verified by `test_d13_attribution()`.
- **Verdict**: PASS
