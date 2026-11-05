# M9 — Stale sample count

**Verdict: `NOT APPLICABLE` — an empty population, not a clean "0".** M9 counts samples whose
*pinned* version differs from **this project's released version**; none names it, so there is no
denominator — `NOT APPLICABLE` for G3 clause 3.5, not a claimed zero.

## Why the population is empty, and the count that proves it

M9 exists for the tutorial saying `pip install acme-sdk==1.2.0` while 1.4.0 shipped. This repo
ships **content** — persona markdown rendered by a CLI — not an SDK with a versioned call
surface, and it is not on an index yet (`…/02-build.md:91` defers publishing). Documented commands
carry no version token: `install --runbook <slug>` resolves to whatever the checkout declares.

Pins *do* exist — **16 version literals across 5 persona files**: `^7.0.0` in
`engineering/engineering-rapid-prototyper.md:73`, `pragma solidity ^0.8.24` in
`engineering/engineering-solidity-smart-contract-engineer.md:70`, `espressif32@6.5.0` in
`engineering/engineering-embedded-firmware-engineer.md:124`, `mcp>=1,<2` in
`specialized/specialized-mcp-builder.md:113` — all third-party, so none can differ from a
release of this project. Version sources agree on **1.8.0** (`pyproject.toml:3`, the manifest,
`__init__.py:4`, `CHANGELOG.md:10`).

## Re-runnable audit

```bash
FILES=$(find . -name '*.md' -not -path './.venv/*' -not -path './.git/*' -not -name 'm9-stale-samples.md')
grep -nE '(pip|uv pip|uvx|uv tool) install[^|]*==' $FILES  # exit 1: no pin on an install line
grep -nE 'agency-agents==|agency_agents==' $FILES          # exit 1: this project never pinned
grep -hE '(@|\^)[0-9]+\.[0-9]+' $FILES | wc -l             # 15: third-party ranges only
grep -h 'pip install' $FILES | wc -l                       # 5: personas and audit prose
```

## Nearest real drift: name drift (M8), and one pin-rot risk

- `docs/dx/bootstrap.md:35` — "`agency_agents:main` must exist"; shipped is `pyproject.toml:16` → `agency_agents.cli.main:main`.
- `docs/dx/golden-path.md:91` — "`agency-agents runbooks install`"; shipped is `install --runbook <slug>`; that subcommand exits 2 (D-002).

Both are repair tickets outside this audit's edit scope; `docs/dx/baseline.md:85` and
`newcomer-reading-path.md:61` print `agency_agents:main` correctly, as the pre-fix defect *record*. The pin
likeliest to rot is `mcp>=1,<2`: its own comment says SDK 2.x changes the server API, and nothing in CI
runs persona snippets. Owner: Developer Advocate.
