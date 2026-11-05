# Baseline — Developer Experience Platform runbook (G1)

The before-state, frozen before anything was built. Every number names the
artifact that produced it. A metric with no source is recorded as `UNMEASURED`
with a reason, an owner and a measurement date — never as a zero and never blank.

| Field | Value |
| --- | --- |
| Runbook | `strategy/runbooks/scenario-developer-experience-platform.md` |
| Mode | NEXUS-Sprint |
| Baseline frozen | 2026-11-05 |
| Branch measured | `feat/cli-runbooks-tui` (identical tree to `main` at `1452c6d`) |
| Signed by | DX Engineer, Analytics Reporter |
| Executor of the clean-room run | ENGINEER-EXECUTED — **not** a human subject (see §6) |

---

## 1. Sources

Nothing in this document is a memory. Each source is re-runnable.

| Source | Artifact | Reproduces |
| --- | --- | --- |
| CI history | `scripts/ci/ci_metrics.py` | M2, M3, M4 |
| Clean-machine run | `scripts/ci/cleanroom_onboarding.sh` + `scripts/ci/cleanroom.Dockerfile` | M1, M5, M6 |
| Documented path under test | `scripts/ci/paths/baseline.sh` | M6 step list |
| Gate wiring | `.github/workflows/ci.yml`, `.github/workflows/quality.yml` | M8 |
| Source reading | `docs/dx/newcomer-reading-path.md` | undocumented steps, couplings |

Reproduce the CI numbers:

```bash
uv run python scripts/ci/ci_metrics.py --limit 20
```

Reproduce the clean-machine numbers:

```bash
bash scripts/ci/cleanroom_onboarding.sh \
  --path scripts/ci/paths/baseline.sh --ref feat/cli-runbooks-tui --build-image
```

## 2. Measured baseline

| Metric | Value | Status | Definition source |
| --- | --- | --- | --- |
| M1 Time to first success | **No documented path completes.** The console script fails at step 5 of 5; no duration exists to record | MEASURED (as a failure) | Clean-room transcript `step_5_exit: 1` |
| M2 CI time to first failure | `UNMEASURED` — see §3 | UNMEASURED | `ci_metrics.py` |
| M3 CI pipeline duration | CI: **p50 33s / p90 51s**. Project Quality Check: **p50 42s / p90 58s** | MEASURED | `ci_metrics.py` over 20 runs/workflow |
| M4 Flake rate | **0.0%** — 0 flakes across 39 completed gating runs | MEASURED | `ci_metrics.py` |
| M5 Bootstrap failure rate | **100%** — 1 of 1 clean-machine attempts exited non-zero | MEASURED | Clean-room transcript |
| M6 Step count | **5 steps**, of which **2 are undocumented** | MEASURED | `scripts/ci/paths/baseline.sh` |
| M7 Tool decision pass | **0 decisions recorded** → 0% | MEASURED (as absent) | `docs/dx/m7-tool-decisions.md` |
| M8 Documented-command pass rate | **1 of 5 documented-path commands exits non-zero (80%)**. The console-script surface is never executed in CI at all | MEASURED | Clean-room transcript + `ci.yml` |
| M9 Stale sample count | Not counted at baseline | UNMEASURED | — |
| M10 Senior hours per onboarding | `UNMEASURED` — no onboarding run has ever been instrumented | UNMEASURED | — |

## 3. Why M2 is `UNMEASURED` rather than zero

The 20-run window on `main` holds **zero failed runs**, so no run contributes a
time-to-first-failure sample. M2 is not zero — it has no sample.

Two historical failures exist outside the window (`41849510474`, `41712313936`,
both `release-please--branches--main`). Their job-level timings are not
retrievable through the API, so they cannot supply the sample either.

- Reason: no failed run with retrievable job timings inside the gate window.
- Owner: Analytics Reporter.
- Measurement date: first post-rewrite failure, expected within the 20-run gate window.

`ci_metrics.py` prints this as `UNMEASURED` and counts the missing samples, so an
empty window can never be mistaken for a perfect one.

## 4. The two defects that invalidate the documented path

Both are reproducible today on a clean machine, and both are the reason M1 has no
value.

### D1 (P0) — the console script is broken

`pyproject.toml` declares:

```toml
[project.scripts]
agency-agents = "agency_agents:main"
```

`agency_agents/__init__.py` exports only `__version__`. There is no `main`.

```text
$ agency-agents --help
ImportError: cannot import name 'main' from 'agency_agents'
```

Consequence: `python -m agency_agents` works, the installed `agency-agents`
command — the one a developer who installed the package reaches for — does not.
**222 tests pass because nothing tests the installed entry point.**

### D2 (P1) — the lint gate does not gate

`lint` prints tool-catalog and division-catalog errors and then exits **0**. Only
agent-frontmatter issues and runbook issues set a non-zero exit.

Verified by injecting a schema-valid tool whose `format` has no registered
renderer:

```text
❌ Tools Consistency Errors:
  - Tool 'bogus-tool' is per-agent but format 'no-such-format' has no renderer.
...
EXIT_CODE=0
```

This contradicts `CONTRIBUTING.md:240` and `:249` ("fails the build if any of the
pieces below disagree") and the `_note` in `tools.json`. A CI gate that reports a
failure and exits successfully is worse than no gate: it teaches reviewers to
ignore red text.

## 5. Undocumented steps a newcomer must guess

From `docs/dx/newcomer-reading-path.md`, verified against the two documents:

| Step | Where the docs omit it |
| --- | --- |
| Installing `uv` | README:44 says "requires ... uv"; no command anywhere |
| A Python 3.13 interpreter | README:44 says "Python 3.13+"; no command, and Ubuntu 24.04 ships 3.12 |
| `uv sync` before running anything | `uv run` does it implicitly; CONTRIBUTING never names it |
| Running from the repo root | `CatalogManager` resolves `tools.json` from `Path.cwd()`; from `docs/` it raises `FileNotFoundError` |
| The CI-equivalent gate | `mise run ci` exists and mirrors CI exactly; zero mentions in README or CONTRIBUTING |
| `pre-commit install` | Not mentioned in either document |

Two of the five measured steps (`install-uv`, `uv-sync`) are therefore not
documented steps at all — they are folk knowledge. That is M6's real problem: the
documented path is shorter than the executable path, and the gap is filled by
whoever is on call.

## 6. Honest limit of the Phase 4 evidence

The runbook defines first success as being measured **by timing a real person on a
clean machine**, with a recorded, consented session. No human subject was
available for this run.

The clean-room harness therefore produces `ENGINEER-EXECUTED` evidence: a real
disposable container, proven clean by an empty work-directory listing and an empty
`which` transcript, running only the documented commands. It is genuinely
reproducible and genuinely timed.

It is **not** a human subject. Consequently, G4 clauses 4.1, 4.3, 4.4 and 4.7
cannot pass on this evidence and are reported `UNMEASURED`. See
`docs/dx/scorecard.md`.

## 7. G1 verdict

```text
G1.1  Every metric in M1-M10 measured with its source named, or UNMEASURED
      with a reason, an owner and a date.                  PASS
G1.2  The M1 baseline entry is present and is not blank.  PASS (present, as a
                                                          measured failure)
```

**G1: PASS** — the before-state is frozen and every claim in it has a re-runnable
source behind it.
