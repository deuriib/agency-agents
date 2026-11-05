# Developer experience documents

Everything produced by the Developer Experience Platform runbook
(`strategy/runbooks/scenario-developer-experience-platform.md`, NEXUS-Sprint).
Read them in this order.

| Document | What it answers |
| --- | --- |
| [`scorecard.md`](scorecard.md) | **Start here.** What was delivered, what was measured, which gate clauses hold, and what is still owed. Status: NEEDS WORK |
| [`baseline.md`](baseline.md) | The before-state, frozen with a re-runnable source behind every number |
| [`golden-path.md`](golden-path.md) | The single supported route: five documented commands, one owner each, plus what the path can and cannot prove |
| [`m7-tool-decisions.md`](m7-tool-decisions.md) | Build-vs-adopt records for the TUI toolkit and the runbook install surface, with weights, arithmetic and exit paths |
| [`bootstrap.md`](bootstrap.md) | What `./scripts/bootstrap.sh` does and how to read its failures |
| [`gate.md`](gate.md) | What `./scripts/gate.sh` runs, in what order, and the CI job each check mirrors |
| [`newcomer-reading-path.md`](newcomer-reading-path.md) | Ten files to read in order, the couplings that confuse newcomers, and the setup steps the docs used to omit |
| [`m9-stale-samples.md`](m9-stale-samples.md) | The M9 audit: why this repository has an empty sample population rather than a measured zero |
| [`cli-faq.md`](cli-faq.md) | The questions the new commands raise, answered with runnable commands |
| [`evidence-pack.md`](evidence-pack.md) | Claim-by-claim evidence inventory, redaction scan, retention window and viewer list |
| [`reality-check.md`](reality-check.md) | The adversarial verdict. Default NEEDS WORK, and it was upheld |
| [`evidence/`](evidence/) | Raw transcripts, each naming the commit SHA and image digest it measured |

## Re-running the proof

```bash
# CI metrics (M2, M3, M4) from real Actions history
uv run python scripts/ci/ci_metrics.py --limit 20

# The documented path, timed, in a disposable container proven clean first
bash scripts/ci/cleanroom_onboarding.sh \
  --path scripts/ci/paths/golden-path.sh \
  --ref "$(git rev-parse --abbrev-ref HEAD)" --build-image
```

The clean-room transcript is `ENGINEER-EXECUTED` evidence. It is not a recorded
session of a human subject and never satisfies G4 clause 4.1 on its own.
