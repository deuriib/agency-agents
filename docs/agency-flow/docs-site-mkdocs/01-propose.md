# PROPOSE — docs-site-mkdocs

## Context & Alignment

This document proposes the technical implementation for GitHub Issue #70 and `docs/agency-flow/docs-site-mkdocs/00-frame.md`: publishing a documentation site for `agency-agents` on GitHub Pages using MkDocs Material, bilingual in English and Spanish, generated deterministically from existing repository content.

### Alignment with Frame Constraints
1. **`docs_dir` Selection**: Dedicated directory `site-docs/` (never `docs/`), strictly isolating internal `docs/agency-flow/**` phase artifacts from publication.
2. **Version Pinning**: Exact pinning in `pyproject.toml` `[dependency-groups].dev`:
   - `mkdocs-material==9.8.1`
   - `mkdocs-static-i18n==1.3.1`
3. **Deterministic Page Generator**: Single committed Python generator `scripts/build_docs_site.py` that parses all 18 divisions in `divisions.json` and all 298 agent markdown files, rendering navigation and landing pages. Regeneration is reproducible in < 15 seconds.
4. **Bilingual Architecture**: English default locale (`site-docs/docs/`) with Spanish translations (`site-docs/docs/es/`) for core guides (Home, Installation, Contributing, Security) and 18 division overview landing pages (total 22 core pages). Fallback behavior is verified via parity assertions.
5. **Least-Privilege CI/CD**: Workflow `.github/workflows/docs.yml` declaring only `contents: read`, `pages: write`, and `id-token: write`, using 40-character commit SHAs for all actions, building on PRs and publishing only on push to `main`.

## Information Architecture (IA) & Navigation

The documentation site structure:

```text
site-docs/docs/
├── index.md                      # English Home (from README.md summary & overview)
├── installation.md               # Tool installation guide (CLI, Cursor, Claude Code, etc.)
├── contributing.md               # Contributing guide (from CONTRIBUTING.md)
├── security.md                   # Security policy (from SECURITY.md)
├── divisions/
│   ├── academic/
│   │   ├── index.md              # Division landing page (Spanish counterpart available)
│   │   ├── academic-anthropologist.md
│   │   └── ...
│   ├── design/
│   │   ├── index.md
│   │   └── ...
│   ├── engineering/
│   │   ├── index.md
│   │   └── ...
│   ├── ... (all 18 divisions)
└── es/                           # Spanish localized pages
    ├── index.md                  # Spanish Home
    ├── installation.md           # Spanish Installation
    ├── contributing.md           # Spanish Contributing
    ├── security.md               # Spanish Security
    └── divisions/
        ├── academic/index.md
        ├── design/index.md
        ├── engineering/index.md
        └── ... (all 18 division landing pages)
```

## Catalog Metrics
- **Divisions**: 18 canonical divisions defined in `divisions.json`:
  `academic`, `design`, `engineering`, `finance`, `game-development`, `gis`, `healthcare`, `marketing`, `paid-media`, `product`, `project-management`, `research`, `sales`, `security`, `spatial-computing`, `specialized`, `support`, `testing`.
  *(Note on Frame D3/D8: Repository catalog has 18 divisions; 4 core guides + 18 divisions = 22 translated pages total)*
- **Agents**: Exactly 298 agent markdown persona files across the 18 division trees.

## Dependencies & Timing
- Upstream Dependency `repo-standards-baseline`: Satisfied (SHA-pinned actions, least-privilege tokens, `ci.yml` matrix).
- Human Review (DENY-07): Required prior to PR merge for the 22 Spanish translations.
- Ownership:
  - Technical Writer: Information architecture, content extraction, Spanish translations, documentation artifacts.
  - Platform Engineer: Build script, MkDocs configuration, i18n setup, GitHub Actions workflow, mise tasks.
