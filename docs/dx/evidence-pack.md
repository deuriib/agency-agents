# Evidence pack — Developer Experience Platform handover

**Runbook:** `strategy/runbooks/scenario-developer-experience-platform.md`
**Assembles:** G4 clause 4.6 (consent, retention, viewer list, redaction) and G5 clause 5.4 (deletion date and viewer list)
**Prepared by:** Evidence Collector
**Date:** 2026-11-05

---

## 0. Status of this document

This pack **organises proof. It does not approve anything.** Every verdict in the
runbook is the Reality Checker's default-to-`NEEDS WORK` call; nothing here
pre-empts it. Where this pack finds no artifact behind a documented number, it
says so and leaves the claim standing as unsupported rather than quietly
repairing it.

Three things this pack establishes, and one thing it cannot:

1. Which claims in `docs/dx/baseline.md` and `docs/dx/golden-path.md` an artifact
   actually proves, with file and line (§2).
2. That the two transcripts are in the repository, byte-identical to the
   originals, and clean of secrets (§3).
3. That the retention window, the deletion date and the viewer list are written
   down (§4) — which is what G5 clause 5.4 asks for.

What it cannot establish: **G4 clause 4.6's consent requirement.** There is no
recorded session of a human subject, so there is no consent to be on file. §4
states this plainly instead of producing a consent record for a subject who does
not exist.

### Verification method

Every number below was re-read from the artifact on 2026-11-05, not copied from
the summary that commissioned this pack. Commands actually executed:

```bash
uv run python scripts/ci/ci_metrics.py --limit 20
git show 1452c6d:README.md | sed -n '44p'
git show 1452c6d:CONTRIBUTING.md | sed -n '240p;249p'
git show 1452c6d:pyproject.toml | sed -n '10,20p'
git show 1452c6d:.github/workflows/ci.yml | grep -E '^  [a-z-]+:$'
gh run view 41849510474 --json databaseId,name,headBranch,conclusion,jobs
gh run view 41712313936 --json databaseId,name,headBranch,conclusion,jobs
grep -n ... (per-claim greps, cited inline)
git archive 1452c6d | tar -x -C /tmp/qa-baseline-1452c6d
  cd /tmp/qa-baseline-1452c6d && uv sync --frozen && uv run pytest -q
```

---

## 1. Instrument register

The five instruments that produce the numbers, and what each is entitled to
prove.

| Artifact | Purpose | Notes that limit it |
| --- | --- | --- |
| `scripts/ci/ci_metrics.py` | Stored query behind M2, M3, M4. Reads `gh` run history. | Live query, not a snapshot: the same command run next week returns a different window. Its output was not committed as a log. |
| `scripts/ci/cleanroom_onboarding.sh` | M1, M5, M6 clean-machine harness. Writes the transcript. | Evidence is `ENGINEER-EXECUTED` by its own header (`:28-29`): "It is not a recorded session of a human subject and never satisfies G4 clause 4.1 on its own." |
| `scripts/ci/cleanroom.Dockerfile` | The "clean machine" definition (`FROM ubuntu:24.04`, `:12`). | Installs `git curl ca-certificates` only (`:14-16`); no credential check is performed anywhere. |
| `scripts/ci/paths/baseline.sh` | The documented path as it stood before Phase 3, executed literally (`:20-45`). | Marks its own guessed steps `(undocumented)` (`:27`, `:34`). |
| `scripts/ci/paths/golden-path.sh` | The golden path executed literally, 5 `run_step` calls (`:14`, `:22`, `:26`, `:32`, `:39`). | `expected=298` is hard-coded at `:43`, so the manifest check proves agreement with the instrument, not an independent count. |

Repository copies of the two transcripts live at
`docs/dx/evidence/baseline-transcript.log` and
`docs/dx/evidence/golden-path-transcript.log`. All line citations in §2 point at
those copies.

---

## 2. Evidence inventory

### 2.1 `docs/dx/baseline.md` — claims backed by an artifact

| # | Claim in baseline.md | Artifact | Exact line(s) that prove it |
| --- | --- | --- | --- |
| B1 | M1: "the console script fails at step 5 of 5" | `evidence/baseline-transcript.log` | `:132` `step_5_label: console-script --help`; `:133` `step_5_exit: 1`; `:131` `ImportError: cannot import name 'main' from 'agency_agents'` |
| B2 | M2 `UNMEASURED` — no failed run in the window | `ci_metrics.py` output, 2026-11-05 | `CI \| 19 \| UNMEASURED \| UNMEASURED \| ... \| 0 \| 0 \| 0.0%` and the `Project Quality Check` row; both `Failures` columns `0` |
| B3 | M3: CI p50 33s / p90 51s; Project Quality Check p50 42s / p90 58s | `ci_metrics.py` output | `\| CI \| 19 \| ... \| 33s \| 51s \| 0 \| 0 \| 0.0% \|` and `\| Project Quality Check \| 20 \| ... \| 42s \| 58s \| 0 \| 0 \| 0.0% \|` |
| B4 | M4: 0.0% — 0 flakes across 39 completed gating runs | `ci_metrics.py` output | `Runs` column 19 + 20 = 39; `Flakes` 0 for both workflows. (Doc says "20 runs/workflow"; CI contributed 19 — the window is 20, the supply is 19.) |
| B5 | M5: 100% — 1 of 1 clean-machine attempts exited non-zero | `evidence/baseline-transcript.log` | `:138` `steps_total: 5`; `:139` `steps_failed: 1`; `:144` `harness_exit: 1` |
| B6 | M6: 5 steps, of which 2 undocumented | `scripts/ci/paths/baseline.sh` | 5 `run_step` calls at `:20`, `:27`, `:34`, `:37`, `:44`; two labelled `(undocumented)` at `:27` and `:34`. Confirmed by transcript `:29` and `:117`. |
| B7 | M8: 1 of 5 documented-path commands exits non-zero (80%) | `evidence/baseline-transcript.log` | `:139` `steps_failed: 1` over `:138` `steps_total: 5`; the failing step is `:133` |
| B8 | M8: "the console-script surface is never executed in CI at all" | `.github/workflows/ci.yml` @ `1452c6d` | Job list is `lint, types, test, verify-manifest, security, required`; `grep -n 'agency-agents --help'` returns nothing. The `documented-commands` job exists only at HEAD (`ci.yml:86`). |
| B9 | §3: two historical failures outside the window, `41849510474` and `41712313936`, both release-please | `gh run view` | Both return `"conclusion":"failure"`, `"headBranch":"release-please--branches--main--components--agency-agents"` |
| B10 | §3: "their job-level timings are not retrievable through the API" | `gh run view` | Both return `"jobs":[]` — no job data available, so no M2 sample can be derived |
| B11 | D1: `pyproject.toml` declares `agency-agents = "agency_agents:main"` | `pyproject.toml` @ `1452c6d` | `:15` `[project.scripts]`; `:16` `agency-agents = "agency_agents:main"` |
| B12 | D1: `agency_agents/__init__.py` exports only `__version__` | `src/agency_agents/__init__.py` @ `1452c6d` | `:4` `__version__ = "1.8.0"` and no other symbol |
| B13 | D1: `$ agency-agents --help` raises ImportError | `evidence/baseline-transcript.log` | `:130-131` traceback ending `from agency_agents import main` / `ImportError` |
| B14 | D1: "`python -m agency_agents` works" | `evidence/baseline-transcript.log` | `:123-125` `step_4_label: cli-install-agents`, `step_4_exit: 0` |
| B15 | D2: contradicts `CONTRIBUTING.md:240` and `:249` | `CONTRIBUTING.md` @ `1452c6d` | `:240` "…`python -m agency_agents lint` (CI) fails the build if any of the pieces below disagree." `:249` "6. **Run `uv run python -m agency_agents lint`** - it must pass." Both quotations are verbatim at the baseline commit. |
| B16 | D2: contradicts the `_note` in `tools.json` | `tools.json` | `_note`: "…`uv run python -m agency_agents lint` (job `lint` in .github/workflows/ci.yml) fails the build when this fi…" |
| B17 | §5: README:44 says "requires … uv"; no command anywhere | `README.md` @ `1452c6d` | `:44` "…(requires Python 3.13+ and [uv](https://docs.astral.sh/uv/); inside the repo run with `uv run python -m agency_agents`)." `grep 'astral\|uv install\|curl -LsSf'` over README + CONTRIBUTING returns only that line — no install command exists. |
| B18 | §5: `uv sync` is never named in CONTRIBUTING | `CONTRIBUTING.md` @ `1452c6d` | `grep -n 'uv sync'` returns nothing in README or CONTRIBUTING at that commit |
| B19 | §5: `tools.json` is resolved from the invocation directory | `src/agency_agents/cli/main.py`, `src/agency_agents/infrastructure/catalog.py` | `main.py:41` `root_dir = Path(".").absolute()`; `catalog.py:56` `class CatalogManager`; `catalog.py:65` `path = self.root_dir / "tools.json"` |
| B20 | §5: `mise run ci` exists; zero mentions in README or CONTRIBUTING | `mise.toml`; `README.md`/`CONTRIBUTING.md` @ `1452c6d` | `mise.toml:46` `[tasks.ci]`; `grep -n 'mise'` at the baseline commit hits only README `:403` inside the word "premises" — i.e. no real mention |
| B21 | §5: `pre-commit install` is not mentioned in either document | `README.md`/`CONTRIBUTING.md` @ `1452c6d` | `grep -n 'pre-commit'` returns nothing at that commit |
| B22 | §5: `install-uv` and `uv-sync` are undocumented steps | `scripts/ci/paths/baseline.sh` | Comments at `:25-26` and `:32-33` state "NOT documented"/"GUESSED"; labels at `:27`, `:34` |
| B23 | §6: the machine is "proven clean by an empty work-directory listing and an empty `which` transcript" | `evidence/baseline-transcript.log` and `evidence/golden-path-transcript.log` | baseline `:13-17` (`workdir listing (expect empty): / [end of listing]`, `which uv/python3/agency-agents: <absent>`), `:18` `clean: true`; golden `:11-18` identical. **Scope: this proves no prior repo copy and no project runtime. It does not prove "no cached credential".** |
| B24 | §6: G4 4.1, 4.3, 4.4, 4.7 "cannot pass on this evidence and are reported UNMEASURED" | The runbook's own Definitions + both transcripts | Both transcripts record `executor: ENGINEER-EXECUTED (not a human subject)` (baseline `:6`, golden `:6`); the harness states the same limit at `cleanroom_onboarding.sh:28-29`. The self-limitation is honest and matches the artifact. |

### 2.2 `docs/dx/golden-path.md` — claims backed by an artifact

| # | Claim in golden-path.md | Artifact | Exact line(s) that prove it |
| --- | --- | --- | --- |
| G1 | Five steps, each with a named owner | `scripts/ci/paths/golden-path.sh` | 5 `run_step` calls: `:14` get-the-code, `:22` bootstrap, `:26` gate, `:32` install-your-work, `:39` prove-it-landed. Confirmed by transcript `:374` `steps_total: 5`. |
| G2 | "Five steps against a ceiling of six (G2 clause 2.1)" | Runbook | `:142` "2.1 Six or fewer steps (M6), each with a named owner." |
| G3 | `scripts/bootstrap.sh` refuses to run outside a git working tree and names the clone as the fix (handoff note H1) | `scripts/bootstrap.sh` | `:80` `fail "not a git working tree: ${ROOT_DIR}"`; `:82` "that is a network or credential problem, not a toolchain problem … bootstrap needs a clone, not a downloaded ZIP." |
| G4 | "The five phases it runs" | `evidence/golden-path-transcript.log` | `:29` `[1/5]`, `:32` `[2/5]`, `:41` `[3/5]`, `:49` `[4/5]`, `:134` `[5/5]` |
| G5 | `docs/dx/bootstrap.md` documents the phases and failure text | `docs/dx/bootstrap.md` | File exists; cited as the reference, not as a measurement |
| G6 | M6 before/after 5 → 5, guessed steps 2 → 0 | `baseline.sh` + `golden-path.sh` + transcripts | baseline has 5 steps with 2 marked `(undocumented)` (`baseline.sh:27,34`; transcript `:29`, `:117`); `golden-path.sh` has 5 steps and zero undocumented markers; golden transcript `:374-375` `steps_total: 5`, `steps_failed: 0` |
| G7 | Step 1 friction: 2 s | `evidence/baseline-transcript.log` | `:25` `step_1_seconds: 2` (golden path `:25` also `2`) |
| G8 | Step 2 friction: its two constituent steps measured 6 s + 18 s | `evidence/baseline-transcript.log` | `:31` `step_2_seconds: 6`; `:119` `step_3_seconds: 18` |
| G9 | Step 3 friction `UNMEASURED` — no one-command gate existed at baseline | `scripts/ci/paths/baseline.sh` | No gate invocation anywhere in `:20-45`; the golden transcript's gate step (`:341-343`, 80 s) has no baseline counterpart |
| G10 | Step 4 friction: 8 s | `evidence/baseline-transcript.log` | `:125` `step_4_seconds: 8`. **Caveat:** that step ran `uv run python -m agency_agents install` (`baseline.sh:38`), while golden-path step 4 runs the console script and took 1 s (golden `:349`). The number measures a different command than the step describes. |
| G11 | Step 5 friction `UNMEASURED` — the command surface did not work | `evidence/baseline-transcript.log` | `:133` `step_5_exit: 1` against `:132` `step_5_label: console-script --help` |
| G12 | Removed: `agency_agents:main`, "replaced by a real `main()`; the import no longer fails" | `pyproject.toml`, `src/agency_agents/cli/main.py`, golden transcript | `pyproject.toml:16` now `agency-agents = "agency_agents.cli.main:main"`; `cli/main.py:775` `def main() -> None`; golden `:138` `ok: console script answered (exit 0)` |
| G13 | Removed: manual copying replaced by `install --runbook <slug>` / `--list runbooks` | `src/agency_agents/cli/main.py` | `:254` `--runbook` option; `:236` message naming ``install --list runbooks`` |
| G14 | Removed: manual `cp` instructions replaced by `--division` / `--agent` | `src/agency_agents/cli/main.py` | `:252` `--division`; `:253` `--agent` |
| G15 | "which of the 5 CI jobs to run" (baseline friction) | `.github/workflows/ci.yml` @ `1452c6d` | Exactly 5 gating jobs at that commit: `lint`, `types`, `test`, `verify-manifest`, `security` (`required` is an aggregator) |
| G16 | Step 3 target: "cheapest check first" | `scripts/gate.sh` | `CHECK_COSTS` (`:55-64`) ascends 0.1-1.2s → 0.8-0.9s → 0.8-1.3s → 2-3.2s → 0.9-24s → 8-15s → 14-27s → 50-57s, and the loop runs in `CHECK_IDS` order (`:244-247`); the transcript shows `[1/8]`…`[8/8]` in the same order (golden `:155-340`) |
| G17 | G2.2 verdict: steps sharing an owner carry handoff note H1 | `docs/dx/golden-path.md` §Handoff note H1 + `scripts/bootstrap.sh` | Steps 1 and 2 both name the Platform Engineer; H1 is written out and closed in code at `bootstrap.sh:80-82` |
| G18 | G2.3 verdict: friction measured or `UNMEASURED` with an owner and a date | The friction table plus G7-G11 | Every row carries either a measured number with a transcript line or `UNMEASURED` with an owner and "Phase 4 run" |

### 2.3 UNSUPPORTED — no artifact behind the claim

This is the part of the pack that matters most. Each row is a number or a
judgement that exists in the document but has nothing stored behind it. Nothing
here says the number is wrong; it says **nobody can check it**, which is exactly
what the runbook's Required Inputs forbid ("a number with no stored source behind
it").

| # | Unsupported claim | Why no artifact supports it |
| --- | --- | --- |
| U1 | `baseline.md:97` "**222 tests pass** because nothing tests the installed entry point." | No test log for the baseline tree is stored anywhere. `grep -rn 222` finds only this sentence and a comment at `.github/workflows/ci.yml:90` — two statements of the same remembered number. **Re-measured by this pack** (see §2.5): the baseline commit collects 222 tests, of which 221 pass and 1 fails as a path-length artefact. So the count is right and the "because" clause is right (`grep` finds no test touching `project.scripts` at `1452c6d`) — but the document's assertion still rests on a memory, not a stored run. |
| U2 | `baseline.md` D2 "Verified by injecting a schema-valid tool … `EXIT_CODE=0`" | The pre-fix behaviour has no stored log. The only related artifact, `scripts/ci/assert_lint_fails.sh:4-11`, was written *after* the fix and asserts the opposite of the claim. The quoted `❌ Tools Consistency Errors` / `EXIT_CODE=0` block cannot be traced to a file. |
| U3 | `baseline.md:126` "A Python 3.13 interpreter … Ubuntu 24.04 ships 3.12" | No artifact establishes what the image ships. The harness's own image shows `which python3: <absent>` (baseline transcript `:17`, golden `:18`) — the clean-room image has no Python at all, so the 3.12 detail is neither confirmed nor relevant to the measured run. |
| U4 | `baseline.md:128` "from `docs/` it raises `FileNotFoundError`" | The resolution mechanism is proven (B19); the *failure* was never recorded. No transcript, test, or log shows it. |
| U5 | `baseline.md:129` "`mise run ci` … mirrors CI exactly" | No artifact compares the two. The existence half is supported (B20). The "mirrors CI exactly" half is contradicted in spirit by C3 below, where the local gate omits one `ci.yml` job. |
| U6 | `baseline.md:12` "Branch measured: `feat/cli-runbooks-tui` (identical tree to `main` at `1452c6d`)" | **Neither transcript records a commit SHA or tree hash.** Both record only `clone_source: git bundle of ref feat/cli-runbooks-tui` (baseline `:4`, golden `:4`). Nothing in the pack pins which tree produced the numbers, so "identical to `main` at `1452c6d`" rests on the author's word. |
| U7 | `baseline.md:13` "Signed by DX Engineer, Analytics Reporter" | A signature line with no signature artifact and no signature file. |
| U8 | `baseline.md:53` M7 "**0 decisions recorded** → 0%", cited to `docs/dx/m7-tool-decisions.md` | The cited artifact records **2** decisions (`:562`: "Decisions recorded \| 2 (D-001, D-002)"). It contains no baseline count and no dated statement that zero existed before. The citation points at the file that holds the opposite fact, with no before/after marker to disambiguate. |
| U9 | `golden-path.md` senior hours: 4.0 h, 2.5 h, 0.5 h, 6.0 h, "Total measured senior time removable per onboarding: **13.0 hours**" | No artifact. The arithmetic is internally consistent (4.0 + 2.5 + 0.5 + 6.0 = 13.0), which is precisely the trap: a sum of remembered inputs looks like a measurement. The word "measured" is unsupported. |
| U10 | `golden-path.md` "baseline M10 target was 24 hours from the last 5 hires" | No artifact. There are no onboarding-channel tickets in this repository, which the runbook names as M10's source. |
| U11 | `golden-path.md` G2.4 verdict `PASS` — "every mandated-versus-optional decision is recorded with the senior hours it saves" | The verdict rests entirely on U9. The runbook also requires the **Product Manager** to supply this record (`strategy/runbooks/scenario-developer-experience-platform.md:138`); no Product Manager record exists anywhere in the pack. |
| U12 | `golden-path.md` step 5 target: "names the files written" | Golden transcript `:352-367` lists 16 tool names with "all hashes match" and `:368` prints a count (`298`). No file paths are printed. The step names tools, not files. |
| U13 | `golden-path.md` "Removed paths and their removal commits" — column headed "Removed in" | The column holds phase names ("Phase 3"), not commits. No SHA identifies any removal, so the removals cannot be audited. |
| U14 | `golden-path.md` M6 narrative: "the two steps that did not exist (the gate, the proof) are added" with the count staying at 5 | The golden instrument was edited from 6 steps to 5 at `163d2c2` ("measure five steps, matching the documented path"), and the earlier 6-step run is `/tmp/goldenpath-proof.log` (`122`s, `step_6` present). The published transcript (`116`s) postdates that edit and does not record which version of the path file it ran. The 5-vs-6 difference is a documented, defensible fix — but the pack must show it, because the number that proves "5" was changed two minutes before the run that reports it. |

### 2.4 CONTRADICTED — the artifact says the opposite

Kept separate from UNSUPPORTED because these are not gaps in evidence; the
evidence exists and disagrees.

| # | Claim | What the artifact shows |
| --- | --- | --- |
| C1 | `golden-path.md`: "`TUIWizard` as the only interactive surface … **deleted in the same change** per D-001" | `src/agency_agents/infrastructure/tui.py:33` still defines `class TUIWizard`; `src/agency_agents/cli/main.py:25` still imports it (`from agency_agents.infrastructure.tui import TUIWizard, WizardCancelled`) and `:318` still calls `TUIWizard(root_dir, catalog).run(...)`. `src/agency_agents/tests/unit/test_tui_wizard.py` still tests it. Nothing was deleted. A new browser surface was added (`infrastructure/browser.py`), which is compatible with "superseded" — but not with "deleted". |
| C2 | `baseline.md:149-150` "… See `docs/dx/scorecard.md`" | `docs/dx/scorecard.md` does not exist. The reference is dangling, which also means G5 clause 5.1 ("the scorecard is published … and linked from the README") cannot be verified from this pack. |
| C3 | `golden-path.md` step 3: "Same checks as CI, cheapest check first" / `mise … scripts/gate.sh` "calls the same tasks" | `scripts/gate.sh:45-54` maps its 8 checks onto 5 `ci.yml` jobs (`lint`, `types`, `verify-manifest`, `test`, `security`). The `documented-commands` job (`.github/workflows/ci.yml:86`, the M8 instrument) is **not mapped**: `grep -n documented scripts/gate.sh` returns nothing. Green locally therefore does not imply green in CI. |
| C4 | `golden-path.md` "`mise run ci` as an alternative gate — **Removed**" | `mise.toml:46` still defines `[tasks.ci]`. What was removed is the *documented recommendation*, not the task. The decision record reads as if the path were gone; a developer can still run it. |

### 2.5 Re-measurements performed by this pack

Recorded separately from the artifacts above, because a re-measurement is new
evidence and must never be presented as the original run.

| Re-measurement | Command | Result |
| --- | --- | --- |
| Test count at the baseline commit (U1) | `git archive 1452c6d \| tar -x -C /tmp/qa-baseline-1452c6d && uv sync --frozen && uv run pytest -q` | **222 tests collected: 221 passed, 1 failed.** The failure is `test_install_rejects_unparsable_agent_file` (`tests/integration/test_cli_commands.py:303`): `rich` hard-wraps the message, and in a relocated checkout the long tmp path pushes `engineering/br` / `oken.md` across a line break, so `assert "engineering/bro" in result.output` fails. The test comments this itself ("console hard-wraps the long path"). Verdict: the 222 figure is genuine; one test is path-length dependent and would fail on any checkout whose temp path is long. |
| CI history (B2-B4) | `uv run python scripts/ci/ci_metrics.py --limit 20` | Returns exactly the two rows quoted in B2-B4, `Failures 0` and `Flakes 0` for both workflows |
| Historical failures (B9, B10) | `gh run view <id> --json …` | Both runs exist, both failed, both carry `"jobs":[]` |

---

## 3. The transcripts, and what was redacted

| Repository file | Source | Bytes / lines | SHA-256 (identical in both) |
| --- | --- | --- | --- |
| `docs/dx/evidence/baseline-transcript.log` | `/tmp/cleanroom-20261105T145724Z.log` | 3,643 B / 144 lines | `aeb5f0ca26ed99807efc44f6a2084971ba49b8ea14ab41e0722d5814eef5ce73` |
| `docs/dx/evidence/golden-path-transcript.log` | `/tmp/goldenpath-proof-final.log` | 14,105 B / 380 lines | `a9788df875db9c71f1048cac9e81068c5faf04cec2e571e6c308d9c4f6b9ad2a` |

The copies are byte-identical to their sources: the hashes match pairwise, so no
silent editing happened during the move. That is deliberate — a transcript that
was "tidied up" while being filed is no longer evidence.

One file was added so the copies can exist at all: `docs/dx/evidence/.gitignore`
containing `!*.log`. The repository's root `.gitignore:44` ignores `*.log`, which
would have dropped both transcripts from the commit while leaving §2 citing paths
that do not exist in the tree. Verified: `git check-ignore -v` reports the
negation as the winning rule, and `git ls-files --others --exclude-standard`
lists all three files as addable.

### What was checked

The scan ran over the **copied** files, case-insensitively, one pattern per
class. Every pattern below returned **zero matches in both files**:

```
(ghp_|gho_|ghs_|ghu_|github_pat_)          GitHub token shapes
(xox[baprs]-)                              Slack token shapes
(AKIA[0-9A-Z]{16})                         AWS access key id
(sk-[A-Za-z0-9]{16,})                      generic sk- secret keys
(Bearer|Authorization:|Basic [A-Za-z0-9+/=]{10,})   auth headers
(-----BEGIN [A-Z ]*PRIVATE KEY-----)       private keys
(token|secret|passw(or)?d|api[_-]?key|credential)   credential vocabulary
([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,})    email addresses
(\b([0-9]{1,3}\.){3}[0-9]{1,3}\b)          IPv4 addresses
(/home/[^ ]*)                              Linux home directories
(/Users/[^ ]*)                             macOS home directories
([A-Za-z]:\\Users)                         Windows user profiles
(deuriib|HPALLINONE)                       this machine's username and hostname
(customer|acct[_-]?id|account[_-]?id)      customer identifiers
```

### What was redacted

**Nothing.** No credential, token, key, email address, IP address, hostname,
username, home directory or customer identifier appears in either transcript, so
the copies carry no edits at all. This is stated explicitly rather than left
implied, because "we redacted" and "there was nothing to redact" are different
facts and a reviewer is entitled to know which one applies.

### What was deliberately left in, and why

| Content | Where | Judgement |
| --- | --- | --- |
| `/root/.local/bin`, `/root/.local/share/uv/...` | golden `:35`, `:39`, `:47`, `:142`, `:265` | Container root home. Contains no username, so it identifies nobody. Removing it would destroy the record of where the toolchain landed. |
| `/work/agency-agents`, `/src/repo.bundle` | both transcripts | Paths inside the disposable container, recreated identically on every run. |
| `/tmp/agency-agents-requirements.03ikut` | golden `:299` | Temp filename generated inside the container by `uv export`. |
| `uv 0.13.7`, `cpython-3.13.18`, package versions | both transcripts | The pinned toolchain is the point of the record. |
| `https://docs.pytest.org/...` | golden `:268` | Public documentation URL printed by `pytest`. |
| `clone_source: git bundle of ref feat/cli-runbooks-tui` | both `:4` | Internal branch name; no remote URL and no credential in it. |

One artifact in this pack does contain a username and is redacted: the
re-measurement output quoted in §2.5 originally printed
`/tmp/pytest-of-<username>/pytest-116/...`. It appears here as
`/tmp/qa-baseline-1452c6d`, with the pytest temp path left out. The unstripped
output was never copied into the repository.

### Selection disclosure

`/tmp` holds more runs than the pack publishes:

| File | Outcome | In the pack? |
| --- | --- | --- |
| `/tmp/cleanroom-20261105T145250Z.log` | `harness_exit: 125` — docker rejected a relative volume name | no |
| `/tmp/cleanroom-20261105T145258Z.log` | `harness_exit: 1` — pre-run check ran at `/` and saw the whole root filesystem | no |
| `/tmp/cleanroom-20261105T145331Z.log` | clone exited `128` under `harness_exit: 1` | no |
| `/tmp/cleanroom-20261105T145712Z.log` | clone exited `128` under `harness_exit: 1` | no |
| `/tmp/cleanroom-20261105T145724Z.log` | 5 steps, 1 failed — **published** | yes |
| `/tmp/goldenpath-proof.log` | 6 steps, 0 failed, 122 s | no |
| `/tmp/goldenpath-proof-final.log` | 5 steps, 0 failed, 116 s — **published** | yes |

The four unpublished clean-room logs are instrument-debugging failures, not
subject runs, and the 6-step golden run is superseded by `163d2c2`. Publishing
only the final run of each path is defensible. Recording it here is mandatory,
because a reader who assumes one attempt took place is being misled by omission,
and the runbook's own pitfall list treats a curated happy path as a defect.

---

## 4. Consent and retention record

### 4.1 The honest statement about consent

**These two runs are ENGINEER-EXECUTED. They are not recorded sessions of human
subjects, and they do not satisfy G4 clause 4.6's consent requirement.**

Clause `4.6` (`:226-228`) asks for three things: written consent on file for
every recorded session; the retention window and the viewer list recorded with
the evidence pack; and no secret, token or customer record visible in it. §3
satisfies the third and §4.2 records the second. The first is not satisfied, and
cannot be: there is no recorded session and therefore no subject from whom
consent could be taken. Filing a consent form for an engineer who ran a
container against their own script would be a fabricated record.

The harness says the same thing in its own header
(`scripts/ci/cleanroom_onboarding.sh:28-29`): *"The transcript this writes is
ENGINEER-EXECUTED evidence. It is not a recorded session of a human subject and
never satisfies G4 clause 4.1 on its own."*

Two further consequences, stated here so they cannot be discovered later as
surprises:

- The runbook's "Recorded session" definition requires **video plus terminal
  transcript**. These are terminal transcripts only. No video exists.
- The runbook's Required Inputs make a first-time test subject a blocking input,
  with the reason *"The DX Engineer's own run is not evidence."* That is exactly
  what this pack contains, so the pack is not evidence for G4 — it is the
  instrument's output, filed so the eventual evidence run has a baseline of
  procedure.

### 4.2 Retention and deletion date

Per the runbook's Definition of Recorded session, evidence is *"retained 90 days
past handover and then deleted"*.

The 90-day clock has **no start date**: the G5 acceptance date is not recorded
anywhere in the pack, so the deletion date cannot be fixed from an artifact.

| Field | Recorded-session variant (the definition as written) | **Engineer-executed variant (what applies here)** |
| --- | --- | --- |
| Retention window | 90 days past handover, then deleted | 90 days past handover, then deleted — inherited unchanged, because the rule is a hygiene floor and there is no reason to hold engineer-executed logs longer than consented ones |
| Deletion date | handover date + 90 days — **not determinable yet**, no handover date on file | **2027-02-03**, computed as 2026-11-05 + 90 days, i.e. the latest possible date if handover is accepted on the date this pack was prepared. If handover lands later, the date moves with it and must be recomputed on the day. |
| Deletion must also cover | the video and the transcript on restricted storage | `docs/dx/evidence/baseline-transcript.log`, `docs/dx/evidence/golden-path-transcript.log`, **and their `/tmp` originals** (`/tmp/cleanroom-20261105T145724Z.log`, `/tmp/goldenpath-proof-final.log`). Deleting the repository copy and leaving `/tmp` behind defeats the rule. |
| Personal data | yes — video and voice of a named person | **none.** The scan in §3 found no name, email, hostname, username, address or credential. Retention here is hygiene and reproducibility, not privacy compliance. |
| Viewer list | DX Engineer, Evidence Collector, Reality Checker, subject | DX Engineer, Evidence Collector, Reality Checker — **and no subject, because there is none.** See the enforcement note below. |
| Access control | restricted storage; "viewable only by" the named viewers | **The viewer list cannot be enforced.** The transcripts are committed to a tracked directory, so they are readable by anyone with read access to the repository. The names above are the people accountable for the pack, not an access-control list. This is the one place where the engineer-executed variant is *weaker* than the definition, and it is a property of the storage choice, not of the content. |

### 4.3 Deletion record (to be completed on the deletion date)

| Field | Value |
| --- | --- |
| Scheduled deletion date | 2027-02-03 (provisional — recompute on the handover date actually recorded) |
| Files in scope | `docs/dx/evidence/baseline-transcript.log`, `docs/dx/evidence/golden-path-transcript.log`, `/tmp/cleanroom-20261105T145724Z.log`, `/tmp/goldenpath-proof-final.log` |
| Executed on | _not yet — before the scheduled date_ |
| Executed by | _to be recorded_ |
| Replacement evidence | The two transcripts are regenerable from §5 at any time. Deleting them costs reproducibility of *these* numbers and nothing else, which is why the date is enforceable rather than aspirational. |

---

## 5. Reproduction commands

The image is built once; each path then runs in a fresh container from that
image.

**Step 0 — build the clean-room image** (`from scripts/ci/cleanroom.Dockerfile`):

```bash
docker build -f scripts/ci/cleanroom.Dockerfile -t agency-agents-cleanroom:1 .
```

**Command 1 — regenerate the baseline transcript** (this is the command published
in `docs/dx/baseline.md` §1):

```bash
bash scripts/ci/cleanroom_onboarding.sh \
  --path scripts/ci/paths/baseline.sh \
  --ref feat/cli-runbooks-tui \
  --build-image
```

**Command 2 — regenerate the golden-path transcript:**

```bash
bash scripts/ci/cleanroom_onboarding.sh \
  --path scripts/ci/paths/golden-path.sh \
  --ref feat/cli-runbooks-tui \
  --out /tmp/goldenpath-proof-final.log
```

Both write a transcript whose default path is `/tmp/cleanroom-<stamp>.log`
(`cleanroom_onboarding.sh:24`), print every step's label, exit code and seconds,
and exit `0` only when every step exited `0` (`:26`).

Two honest caveats about Command 2:

- It is **reconstructed** from the harness's documented flags
  (`cleanroom_onboarding.sh:13-24`), not copied from a stored record. No
  document in the repository publishes the invocation that produced
  `/tmp/goldenpath-proof-final.log`, and the transcript does not record its own
  argv.
- Running it today would not reproduce these numbers bit-for-bit: `--ref
  feat/cli-runbooks-tui` now points at a later commit than the one measured
  (§2.3 U6), and the image is referenced by the mutable tag
  `agency-agents-cleanroom:1` with no digest recorded anywhere.

Neither command was re-executed for this pack: both require Docker plus network
access to download the interpreter and the 60 packages. The transcripts in
`docs/dx/evidence/` are therefore the only evidence of these two runs, which is
another reason §4 fixes a deletion date rather than letting them rot.

---

## 6. Gap list — what G4 requires and this pack cannot prove

Ordered by clause. Each entry names what G4 asks for, what exists, and what is
missing.

### G4.1 — Three consecutive subjects reach first success on clean machines

- **Requires:** three different first-time subjects, three clean machines, three
  first successes.
- **Exists:** zero subjects. Two engineer-executed runs (one per path), one
  image, no repeat of either run.
- **Missing — four separate things:**
  1. **No subject at all.** Required Inputs say it plainly: "The DX Engineer's own
     run is not evidence."
  2. **First success is never reached, even by the engineer.** The runbook defines
     first success as the subject's own change *deployed by the documented path*
     **and** an observability query returning data for it (`:44`). Golden-path
     step 5 (`golden-path.sh:39-46`) verifies a manifest and counts files in
     `~/.claude/agents`. Nothing is deployed. No observability query runs. So
     the 116 s run is a *local install proof*, not first success, and M1 has no
     value for either run — only M5/M6-style observations.
  3. **No "three consecutive."** One run per path, no repetitions, so no
     consecutiveness and no variance.
  4. **No proof the same clean machine was used three times.** The image is a
     mutable tag with no recorded digest (`baseline-transcript.log:3`,
     `golden-path-transcript.log:3`: `image: agency-agents-cleanroom:1`).

### G4.2 — Zero interventions across all three runs

- **Requires:** an intervention log showing zero senior-engineer actions.
- **Exists:** no intervention log of any kind. The harness has no concept of one.
- **Missing:**
  1. **A log, not an absence.** "No interventions were recorded" and "no
     intervention occurred" are indistinguishable here, which the runbook treats
     as a fail.
  2. **The strongest kind of intervention is built in.** The runbook defines an
     intervention as any senior action that "names a command for the subject"
     (`:47`). In these runs the operator wrote the very file that names every
     command (`scripts/ci/paths/golden-path.sh`), then executed it. Executed
     against a real subject, that would void the run by definition.
  3. **Undisclosed instrument churn between attempts.** Four earlier clean-room
     attempts and one earlier golden run exist (§3, Selection disclosure), and
     `golden-path.sh` itself changed at `163d2c2` between the two golden runs.
     Each of those is an environment action taken by a senior engineer during the
     measurement period, none of them logged as such.

### G4.3 — Median time to first success at or under 4 hours (M1)

- **Exists:** no M1 value at all, for either run — see G4.1 point 2. The 116 s and
  34 s totals are per-step sums of install commands, not time to first success.
- **Missing:** any M1 measurement; any median; any subject population to take a
  median over.

### G4.4 — All three subjects at or under 8 hours (M1)

- **Exists:** nothing. The clause is judged subject by subject, and there are no
  subjects.
- **Missing:** three per-subject totals. Not derivable from a single
  engineer-executed run, by construction.

### G4.5 — Every stall is logged with its step and duration

- **Exists:** per-step durations (`step_N_seconds`) for every step that ran, in
  both transcripts. That is step timing, not stalling.
- **Missing:**
  1. **No stall instrument.** A stall is a subject stopping to work something out;
     the harness times commands, so it cannot see a stall.
  2. **No stall log file, empty or otherwise.** No `stalls.md`, no timestamped
     stall rows, nothing an observer could have written.
  3. **A related signal is unrecorded:** in the golden run `bootstrap` took 27 s
     (`golden-path-transcript.log:151`) against 6 s + 18 s = 24 s for the two
     baseline steps it absorbs (`baseline-transcript.log:31`, `:119`). The
     wrapper therefore costs ~3 s. Nothing has adjudicated that, and it shows how
     sensitive these numbers are to instrument shape.

### G4.6 — Consent on file; retention window and viewer list recorded; no secret visible

- **Exists:** retention window and viewer list are recorded in §4 of this pack;
  redaction was performed and its null result recorded in §3; the artifacts
  contain no secret, token or customer record.
- **Missing:**
  1. **Consent — not satisfied and not satisfiable.** No recorded session, no
     subject, no consent form. This is the blocking clause and it is stated, not
     papered over.
  2. **No video.** The definition asks for video plus transcript; these are
     transcripts only.
  3. **The viewer list is not enforceable** while the artifacts live in a tracked
     repository (§4.2, Access control). G5's "viewable only by the named viewers"
     is a promise the storage cannot keep.

### G4.7 — M10 at or under 2 hours of senior time per onboarding run

- **Requires:** senior-engineer time from the intervention log plus
  onboarding-channel tickets.
- **Exists:** neither source. There is no intervention log and no
  onboarding-channel ticket in this repository.
- **Missing:**
  1. **No M10 value.** `baseline.md:56` records `UNMEASURED` with no owner and no
     measurement date, which G1 requires and which the row does not carry.
  2. **The honest floor is higher than zero.** Zero senior actions happen *inside*
     the container, but the harness, the path file and the bootstrap script were
     all authored and debugged by a senior engineer during the measurement
     window. M10 counts senior time touching a subject's environment; charging
     instrument maintenance is exactly the accounting the clause exists to force.

### G5.4 — The evidence pack records its deletion date and its viewer list

- **Satisfied, with one limit worth carrying into the verdict:** §4.2 records the
  window, the deletion date (2027-02-03, provisional until a handover date
  exists) and the viewer list, in both the recorded-session form the runbook
  names and the engineer-executed form that actually applies.
- **Limit:** the deletion date has no anchor. Nothing in the pack records a G5
  acceptance date, so the date is computed from the day the pack was prepared
  rather than from the event the rule points at. Recording the handover date at
  acceptance turns this into a fixed commitment.

### Beyond G4 — noted here, decided elsewhere

These are outside the two clauses this pack assembles, but a Reality Checker will
meet them and should not have to find them alone.

1. **`docs/dx/scorecard.md` does not exist** though `baseline.md:150` cites it.
   G5.1 ("published where engineers look and linked from the README") and the
   Phase 5 scorecard therefore cannot be checked from this pack.
2. **No handover acceptance record** (G5.2) exists in the repository.
3. **Neither transcript records the commit SHA it measured, nor its own command
   line.** Both are cheap to add to the harness and both close a chain-of-custody
   hole that no amount of re-reading can close afterwards.
4. **`298` is the instrument's own expectation** (`golden-path.sh:43`). It is
   asserted with `test "${written}" -ge "${expected}"`, a `>=` against a
   hard-coded literal, so the check proves "at least as many files as the script
   already believed" and not an independently derived count.
5. **The local gate is not CI** (C3). `documented-commands` — the job built to
   catch the exact class of defect the baseline found — runs nowhere locally.
6. **`ci_metrics.py` output is not stored.** M2/M3/M4 are reproducible only while
   the 20-run window still exists on GitHub. Past that, the numbers become
   memory again. A committed snapshot per gate would fix it.

---

## 7. What the Reality Checker is being handed

- 42 claims in the two documents verified against an artifact, with file and line
  (24 in `baseline.md`, 18 in `golden-path.md`).
- 14 claims with no artifact behind them (U1-U14), of which one (U1, "222 tests
  pass") was independently re-measured and found substantially correct, and one
  (U9, the 13.0 senior-hours total) is an arithmetic sum of unsourced inputs.
- 4 claims the artifact contradicts (C1-C4), the sharpest being a "deleted" class
  that is still in the tree and still on the call path.
- Two transcripts in the repository, byte-identical to their sources, with a
  documented null redaction result and a full disclosure of the runs that were
  not published.
- A retention and viewer record that satisfies G5.4's letter and honestly names
  the one clause it cannot satisfy: 4.6's consent, because there is no subject.

**Verdict: none. This pack does not approve.** The default stands — `NEEDS WORK` —
because G4.1 through G4.5 and G4.7 have no subject behind them, and G4.6's
consent requirement is not met by engineer-executed evidence.
