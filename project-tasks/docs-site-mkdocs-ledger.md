# Run Ledger: docs-site-mkdocs

## Run Metadata
- **Run**: `docs-site-mkdocs`
- **Issue**: [#70](https://github.com/deuriib/agency-agents/issues/70)
- **Reference Frame**: `docs/agency-flow/docs-site-mkdocs/00-frame.md`
- **Mode**: NEXUS-Sprint
- **Status**: COMPLETED
- **Started**: 2026-11-09T17:15:00Z
- **Finished**: 2026-11-09T17:30:00Z
- **Orchestrator**: AgentsOrchestrator (`specialized/agents-orchestrator.md`)

## Classification
- **Domain(s)**: Engineering (`divisions.json` -> `engineering`)
- **Deliverable**: Documentation Site & CI Automation (`doc` deliverable)
- **Scale**: NEXUS-Sprint
- **Urgency**: Normal feature release
- **Required Inputs**: `docs/agency-flow/docs-site-mkdocs/00-frame.md`, `README.md`, `CONTRIBUTING.md`, `SECURITY.md`, 298 agent markdown files across 18 divisions.

## Human Approvers (Governance & Authority)
- **Named Approver**: Deuri Vasquez (`@deuriib`)
- **Required Authorizations**:
  - DENY-07: Human review and approval of Spanish translation set (22 core pages) prior to merge.
  - Production GitHub Pages publish / workflow deployment approval.

## Roster Mapping (Live Repository Discovery)
- **Technical Writer**: `engineering/engineering-technical-writer.md` (Slug: `engineering-technical-writer`)
- **Platform Engineer**: `engineering/platform-engineer.md` (Slug: `platform-engineer`)
- **Evidence Collector**: `testing/testing-evidence-collector.md` (Slug: `testing-evidence-collector`)
- **Reality Checker**: `testing/testing-reality-checker.md` (Slug: `testing-reality-checker`)
- **Process Steward**: Vasquez (Project Management / Agency-Flow)

## Deliverables & Gates Status
| Deliverable | Description | Validator | Result | Evidence |
|---|---|---|---|---|
| D1 | `mkdocs.yml` + Material theme + `docs_dir != docs` + `.gitignore` | Evidence Collector | PASS | `mkdocs.yml`, `.gitignore` |
| D2 | `mkdocs build --strict` exits 0 (0 warnings/broken links) | Evidence Collector | PASS | Build exit code 0 in 57.74s |
| D3 | 18 division pages + 298 agent pages parity | Evidence Collector | PASS | `scripts/ci/test_docs_site.py` test_d3_parity() |
| D4 | 0 files originating from `docs/agency-flow/**` in site | Evidence Collector | PASS | `test_d4_leakage()` 0 matches |
| D5 | `mise run docs-build` and `mise run docs-serve` | Evidence Collector | PASS | `mise.toml` tasks verified |
| D6 | Language switcher present on all content pages | Evidence Collector | PASS | 642 / 642 content HTML pages verified |
| D7 | Fallback invariant: `fallback == total - 22` | Evidence Collector | PASS | 299 == 321 - 22; intersection 0 |
| D8 | 22 Spanish core pages (non-empty, distinct SHA) | Evidence Collector | PASS | 22/22 verified by SHA-256 |
| D9 | PR build-only, main build + publish | Evidence Collector | PASS | `.github/workflows/docs.yml` |
| D10 | Permissions least-privilege + 40-char SHA pinned | Evidence Collector | PASS | `contents: read`, `pages: write`, `id-token: write` |
| D11 | GitHub Pages enabled `build_type=workflow` | Reality Checker | PASS | API output verified |
| D12 | CI build runtime budget < 120s | Evidence Collector | PASS | Local: ~59s with step summary |
| D13 | Upstream attribution & `site_url` | Evidence Collector | PASS | `msitarzewski/agency-agents` credited |
| Gate | Full repository gate (`./scripts/gate.sh`) | Reality Checker | PASS | 10/10 checks green |
