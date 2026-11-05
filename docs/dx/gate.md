# The gate — one command, the CI job set, cheapest first (golden-path step 3)

`./scripts/gate.sh` is the only pre-push gate. It runs the exact commands of the
five **blocking** jobs in `.github/workflows/ci.yml`, cheapest first, labelling
each check with the CI job it mirrors so drift is visible instead of guessed.
`--list` prints this table.

**Known gap, stated rather than hidden.** The `documented-commands` job is *not*
mirrored here: it asserts that every command the docs publish still exits 0, and
running it inside the gate it documents would be circular. A green gate therefore
means the five blocking jobs will pass; it does not prove `documented-commands`
will. That job runs only in CI.

| # | Check | Mirrors | Measured | Command |
| --- | --- | --- | --- | --- |
| 1 | ruff | `[ci.yml:lint]` | 0.1–1.2 s | `uv run ruff check .` |
| 2 | runbook-structure | `[ci.yml:lint]` | 0.8–0.9 s | `uv run python scripts/ci/check_runbook_structure.py` |
| 3 | yamllint | `[ci.yml:security]` | 0.8–1.3 s | `uv run yamllint -d relaxed .github/` |
| 4 | catalog-lint | `[ci.yml:lint]` | 2–3.2 s | `uv run python -m agency_agents lint` |
| 5 | types | `[ci.yml:types]` | 0.9 s warm, 24 s cold | `bash scripts/ci/mypy_ratchet.sh` |
| 6 | verify-manifest | `[ci.yml:verify-manifest]` | 8–15 s | `uv run python -m agency_agents verify --all` |
| 7 | test | `[ci.yml:test]` | 14–27 s | `uv run pytest -q --cov=… --cov-fail-under=80` |
| 8 | security-audit | `[ci.yml:security]` | 50–57 s, network | `uv export … && uv run pip-audit …` |

Cheapest first, so common failures cost seconds: three sub-2 s checks catch most
real breakage, and a ruff error never waits behind a 50 s network audit. `types`
precedes the long tail (warm 0.9 s; 24 s is a one-off cold cache) and `test`
precedes `security-audit`, the only networked check. Full ≈ 88 s, `--fast` ≈ 26–34 s.

| Invocation | What it does | When |
| --- | --- | --- |
| `./scripts/gate.sh` | All 8 checks, stops at the first failure | Before pushing |
| `./scripts/gate.sh --fast` | 7 checks: no `security-audit`, pytest without coverage | Inner loop |
| `./scripts/gate.sh --keep-going` | All 8 even after a failure, then aggregates | Debugging a red branch |

Fail-fast is the default: the first failure is what the golden path needs fastest,
and the run prints its time to first failure — M2 measured locally. The last line is
greppable: `GATE RESULT: PASS|FAIL`; `--fast` prints `NOT the full gate` and lists
what it skipped, so it cannot pass for a green gate. Exit codes: `0` pass, `1` check
failed, `2` usage/toolchain error; `uv run` syncs per check, so `mise` stays optional.

`mise.toml` and the workflows disagree in two places, so `mise run ci` is not a
faithful mirror: yamllint is a `security` step in `ci.yml` but a `lint` task in
mise, and mise `test` has no coverage floor while mise `coverage` omits CI's
`--cov-report=xml`. The gate follows `ci.yml`. `quality.yml` is a subset — catalog
lint, verify, bare pytest — plus an `antigravity-staging` job asserting a staged
install into a throwaway `HOME` that a local run cannot cover.
