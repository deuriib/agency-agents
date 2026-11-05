# Toolchain Standardization

Mode: NEXUS-Micro | Duration: 1-5 days | Agents: 9

## Scenario

There are five ways to run the tests and nobody can say which one is authoritative. The README says `pytest`. CI says `uv run pytest`. One engineer has Python 3.11 in their shell, CI has 3.12, and the lockfile says 3.13. A formatter runs on save for some people, in CI for everyone, and nowhere in the pre-commit hook that half the team installed by hand. A `Makefile` target calls a script that calls a tool nobody pinned.

None of it is broken enough to stop work, which is exactly why it survives. The drift is invisible until a version-sensitive failure reproduces on one machine and not another, and by then the investigation costs more than the pin would have.

This runbook installs one toolchain with a committed lockfile, one task graph that mirrors CI step for step, and one documented way in. The doctrine is one sentence: **a version nobody pinned is a version nobody can reproduce, and a task graph that does not mirror CI is a claim about CI that nobody has tested.**

Scope is the toolchain and the task contract of a single repository — the interpreter, the tools, the lockfile, the task names, and the commands the documentation prints. It is not repository governance: licence, security policy, contribution surface, branch protection and ownership belong to `repository-hardening-program`. It is not the measurement of onboarding throughput across teams: that is `developer-experience-platform`. `mise` is the instrument this runbook uses, and that choice is recorded in Key Decisions as reversible — the gates below are about pinning, parity and single entry point, which any mechanism must satisfy.

## Applicability

| Use this runbook when | Use a different runbook when |
| --- | --- |
| More than one way exists to build, test or lint the repository, and no one can name the authoritative one | The repository lacks a licence, security policy, contribution path, ownership or enforced branch protection — use `repository-hardening-program` |
| Runtimes arrive by hand, by `.tool-versions`, by `nvm`, `pyenv` or `asdf`, or by prose in the README | Onboarding time across teams must be measured and shortened — use `developer-experience-platform` |
| Local and CI results disagree on the same commit | The code itself must be restructured — use `codebase-modernization-program` |
| CI installs its tools its own way and reimplements the local build | The pipeline is the problem: it is slow, flaky, or cannot fail — use `developer-experience-platform` |
| Documentation prints raw interpreter and package-manager commands that sidestep the toolchain | A specific reported vulnerability must be remediated — use `security-vulnerability-response` |
| A new or inherited repository needs a toolchain it can be handed over with | You are moving a fleet of repositories onto one config — no runbook covers that yet; this one is single-repository by design |

## Required Inputs

Only what the roster cannot produce: access, a human decision, a chosen standard, or an external constraint. The pinned config, the lockfile, the task graph and the evidence pack are **outputs** of this run, never inputs.

| Input | Why it blocks | Owner |
| --- | --- | --- |
| The declared support matrix: which operating systems and architectures the repository claims to support | A toolchain can only be proven on platforms someone named; "it works on my machine" is the defect this runbook removes, and an undeclared platform cannot be failed | Platform owner |
| Write access to the CI configuration and permission to change the pipeline | G2 changes CI; a read-only roster can only document the divergence it was hired to remove | Repository admin |
| A named toolchain owner, with authority to approve a version bump, for the day after handover | An unowned pin rots silently, and a bump with no approver becomes a drive-by change inside a feature diff | Engineering lead |
| A decision on which package managers and tool sources are permitted, plus any registry mirror or proxy the environment requires | Pinning a source the network cannot reach produces a config that cannot install, which is a pin that fails at the worst moment | Platform owner |
| The runtime version the application is expected to run on in production, or a written statement that none is defined | Pinning the developer's convenience version instead of the deployed one moves the defect to production, where it is expensive | Backend owner |
| The minimum `mise` version the organisation supports, if one is mandated | `min_version` is a gate; inventing a floor the team does not run makes the config unusable on real machines | Platform owner |

## Definitions

Every threshold and gate below reads these definitions, and a gate fails on the observation named here.

| Term | Definition used by every gate |
| --- | --- |
| Pinned | A `[tools]` entry that resolves to exactly one version. A range, a partial version such as `3.13`, `latest`, or a version supplied by an untracked file is not pinned. |
| Lockfile | The committed `mise.lock` for the config root, carrying the resolved version, checksum and download URL of every tool. |
| Task | A named entry under `[tasks]` or a file in `mise-tasks/`, invoked as `mise run <task>`. |
| Gating task | A task that CI runs, or that another task depends on. |
| Orphan task | A task that is not gating, is not named in tracked documentation, and is not the `default` task. |
| Second entry point | Any documented command that reaches a build, test, lint or run step without `mise run` — a `Makefile` target, an `npm` script, a shell script, or a raw interpreter invocation. |
| Task parity | A one-to-one mapping between every gating task and the CI step that runs it, in both directions. Parity is 100% or it is a fail; there is no partial parity. |
| Doc-to-task resolution | The share of commands printed in tracked documentation that resolve to an existing task. |
| `DRIFT` | A detected difference: an unpinned tool, a stale lockfile, a gating task with no CI step, a CI step with no task, an orphan task, a second entry point, or an unresolvable documented command. `DRIFT` counts. It is never a warning. |
| Trust-free config | A `mise.toml` holding only `min_version`, plain-string `[tools]` entries, and `[tasks]` that declare no `secrets`. By `mise trust`'s own rules such a file needs no trust, so no contributor is prompted and CI never grants trust. |
| Cold run | An install and a full `mise run check` on a runner with no `mise` cache and no previously installed tools for this repository. |
| Divergence ticket window | Five business days from a `DRIFT` finding to repair, or to a recorded owner and date on a repair ticket. |

## Agent Roster

### Command (Always Active)

| Agent | Role | Proven by |
| --- | --- | --- |
| Agents Orchestrator | Owns the five-day sequence, convenes each quality gate, stops the run when one fails, and records the verdict, the owner and the repair clock at handover | G4 |
| Platform Engineer | Owns the toolchain as a platform artifact — version floor, pinning policy, lockfile, trust model and the CI install path — and signs G1 and G2 | G1, G2 |

### Pinning (Day 1)

| Agent | Role | Proven by |
| --- | --- | --- |
| DevOps Automator | Inventories every runtime and binary the repository actually invokes, pins each to an exact version, mints and commits the lockfile, and rewires the CI install through the committed config | G1 |

### Task Contract (Day 2)

| Agent | Role | Proven by |
| --- | --- | --- |
| Developer Tooling Engineer | Designs the task graph — names, descriptions, dependencies, one aggregate `check` — and removes every second entry point | G2, G3 |
| Git Workflow Master | Routes hooks and review discipline through the same entry point, and keeps the lockfile diff reviewable instead of buried or conflicted | M5 |
| Technical Writer | Rewrites every documented command as `mise run <task>`, publishes the one-way-in contract, and owns doc-to-task resolution | M4 |

### Drift & Proof (Day 3-5)

| Agent | Role | Proven by |
| --- | --- | --- |
| Codebase Onboarding Engineer | Reads the repository as a stranger and proves every documented command resolves to a real task, reporting the first failure by file and line rather than as a summary | M4 |
| Evidence Collector | Assembles the evidence pack: command inventory, pin table, lockfile digest, parity table, doc-to-task map, the gate's red and green runs, and one cold run per supported platform | M1, M2, M3, M6 |
| Reality Checker | Holds the verdict, re-runs the lockfile and drift checks independently, and defaults to NEEDS WORK | G4 |

## Thresholds

Every number below is decided before the phase that reads it, and each is defined once in Definitions. A threshold negotiated while a build is red is not a threshold.

| Threshold | Value | Why that number |
| --- | --- | --- |
| Pinned coverage | 100% of invoked tools; 0 entries resolving to a range, a partial version or `latest` | One floating tool makes the lockfile decorative, because its resolution then changes with the calendar rather than with a commit |
| Lockfile staleness | `mise lock --dry-run` reports zero changes on the default branch, on every run | A stale lockfile is worse than none: it reads as a pin and resolves as a request |
| Task parity | 100% in both directions — every gating task has a CI step, every CI step has a task | The gate's only job is to keep the local and remote definitions of "verified" identical; 90% parity means one verification in ten is a local opinion |
| Orphan tasks | 0 | An orphan is either an undocumented capability or dead config; both make `mise tasks` a worse index than no index |
| Second entry points | 0 | A second way in is a second way to be wrong, and it is the one a new contributor finds first |
| Doc-to-task resolution | 100% of commands printed in tracked documentation | A documented command that does not exist costs a contributor more than missing documentation, because it is trusted |
| Cold install budget | `mise install` from the committed lockfile plus a green `mise run check` in 8 minutes or less, per platform in the declared support matrix, on a cold runner | The budget is what makes the documented path worth taking; a 40-minute bootstrap gets bypassed, and a bypassed path is a path nobody maintains |
| Divergence ticket window | 5 business days, from finding to repair or to a recorded owner and date | A drift gate with no repair clock becomes a permanently red job, and a permanently red job is the same as no job |
| Verdict default | NEEDS WORK | A toolchain is proven by an install on a cold runner, not by a reading of the config |

## Day 1: Inventory & Pin (G1)

Pinning starts from commands, not from products. The inventory is a list of what the repository actually executes, because a tool that is pinned and never invoked is decoration, and a tool that is invoked and never pinned is the defect.

```text
├── DevOps Automator → inventory every runtime and binary the repository invokes: read CI,
│   hooks, Dockerfiles, scripts, task files and documentation, and list each by the command
│   that calls it — interpreter, package manager, formatter, linter, test runner, code
│   generator, and any binary a script shells out to
├── Platform Engineer → for each entry write the source backend explicitly, so resolution does
│   not depend on whichever registry answers first
├── DevOps Automator → pin each tool to an exact version; a partial version, a range or
│   `latest` is recorded as DRIFT rather than annotated as a temporary convenience
├── Platform Engineer → set `min_version` to the floor the team actually runs, and confirm the
│   config is trust-free by construction: plain-string versions, no template syntax, no
│   `env._.file` or `env._.source`, and no task-level `secrets`. If trust is genuinely
│   required, record why, and enable paranoid mode so trust is tied to file contents
├── DevOps Automator → run `mise lock` and commit `mise.lock`; `mise lock --dry-run` must then
│   report no changes, and the digest goes into the evidence pack
├── DevOps Automator → install from the lockfile on each platform in the support matrix and
│   capture `mise ls`; a platform that cannot install is DRIFT with a named blocker, not a
│   footnote
├── Evidence Collector → pack: the command inventory, the pin table with resolved versions, the
│   lockfile digest, per-platform `mise ls` transcripts, and the list of failing platforms
└── Quality Gate (G1): every command in the inventory resolves to a pinned tool; the lockfile
    is committed and `mise lock --dry-run` is clean; the config needs no trust, or records why
    it does and runs paranoid. A single entry resolving to a range, or a lockfile that changes
    when nothing changed, fails G1 — the pin is the artifact everything downstream rests on, and
    a pin that re-resolves has already drifted.
```

## Day 2: Task Contract & CI Parity (G2)

The task graph is the repository's definition of "verified". CI stops being a parallel implementation of it and becomes a caller of it.

```text
├── Developer Tooling Engineer → design the task graph around what both a contributor and CI
│   need — install, format, lint, types, test, coverage, build, verify — give every task a
│   description, and keep `mise tasks validate` clean
├── Developer Tooling Engineer → make one aggregate `check` the definition of verified, failing
│   on the first failing leg rather than collecting results; an alias `ci` is allowed only if
│   the repository wants the ceremony, and it must call the same legs
├── Developer Tooling Engineer → remove every second entry point: a `Makefile` target, an `npm`
│   script, a shell script, or a CI-only invocation that reaches a gating step by another route
├── Developer Tooling Engineer → where a legacy entry point cannot be deleted this week, reduce
│   it to a one-line call to `mise run`, record it as a shim with a removal date, and count it
│   as an open divergence rather than as a path
├── DevOps Automator → rewrite CI to install tools from the committed config and lockfile,
│   cache on the lockfile digest, and invoke the same tasks the contributor runs
├── Git Workflow Master → wire hooks through the entry point, and set the review rule for
│   `mise.toml` and `mise.lock`: a bump is its own commit with its own reviewer, so a tool change
│   never hides inside a feature diff
├── Technical Writer → publish the contract in one place: the task list, what each task does,
│   and the statement that `mise run <task>` is the only supported entry point
├── Evidence Collector → the parity table: each gating task, the CI step that runs it, and the
│   CI run URL that proves it, plus the removed entry points and every surviving shim
└── Quality Gate (G2): task parity is 100% in both directions, `mise tasks validate` is clean,
    and CI installs and runs from the same config the contributor does. One gating task with no
    CI step, one CI step with no task, or a CI step that installs a tool by its own path fails
    G2 — parity is the entire claim, and a 90% parity claim is a local opinion about CI.
```

## Day 3: Documentation Read-Back & Drift Gate (G3)

A command printed in prose is still a command, and the contributor has no way to tell that it stopped working.

```text
├── Codebase Onboarding Engineer → extract every command from tracked documentation: README,
│   CONTRIBUTING, AGENTS.md, docs, instructive code comments, and the issue and pull-request
│   templates
├── Codebase Onboarding Engineer → resolve each one against the task definitions, and check the
│   command does what the surrounding text claims; record the first failure by file and line
├── Developer Tooling Engineer → generate the task reference from the config rather than typing
│   it, so the published index cannot drift from the task definitions
├── Developer Tooling Engineer → commit the drift gate as a script in the repository and call it
│   from `check` and from CI: unpinned tool, stale lockfile, orphan task, second entry point,
│   unformatted config, unresolvable documented command — each reported by name
├── DevOps Automator → prove the gate can fail: on a scratch branch introduce one unpinned tool
│   and one dead documented command, confirm the gate goes red and names both, then revert
├── Technical Writer → fix or delete every command that does not resolve; a paragraph that only
│   works if the reader already knows the toolchain is rewritten, not annotated
├── Evidence Collector → the doc-to-task map, the gate's red run and its green run, and the
│   scratch-branch transcript proving it failed on both injected defects
└── Quality Gate (G3): doc-to-task resolution is 100%; the drift gate is committed, wired into
    `check` and CI, and has been observed failing on an injected defect. A gate that has never
    been red is a claim, not a control — and every removed entry point is either deleted or a
    one-line shim with a date.
```

## Day 4-5: Evidence, Verdict & Handover (G4)

```text
├── Evidence Collector → cold-run the documented path on each platform in the support matrix:
│   `mise install` from the lockfile, then `mise run check`, capturing elapsed time per platform
│   against the cold install budget
├── Evidence Collector → assemble one pack: command inventory, pin table, lockfile digest,
│   parity table, doc-to-task map, the drift gate's red and green runs, cold-run timings, the
│   surviving shims, and the named toolchain owner
├── Reality Checker → read the pack rather than the summary, re-run `mise lock --dry-run` and
│   the drift gate independently, and default to NEEDS WORK
├── Reality Checker → NEEDS WORK if any platform in the matrix was never cold-run, if the gate
│   was never seen red, if a shim survives with no recorded reason or date, or if the owner is
│   unnamed
├── Agents Orchestrator → on PASS, hand over with the owner named, the bump rule written down and
│   the repair clock agreed; on NEEDS WORK, one work item per failing gate with an owner and a
│   date, and the run closes as NEEDS WORK rather than as partial
└── Quality Gate (G4): the Reality Checker's verdict is recorded with the evidence behind it, and
    the run closes as PASS or NEEDS WORK — never as "done with follow-ups". A toolchain nobody
    owns and a gate nobody repairs are the two ways this work disappears within a quarter.
```

## Key Decisions

| Decision Point | When | Who Decides | Default if undecided |
| --- | --- | --- | --- |
| Adopt `mise` as the toolchain manager, or pin the existing mechanism first | Day 1, before pinning starts | Platform Engineer with the toolchain owner | Adopt it when the repository already has three or more ad-hoc install paths; otherwise pin what exists and revisit — the gates are mechanism-neutral except where a command is named |
| Exact pins versus ranges in `[tools]` | Day 1 | Platform Engineer | Exact pin plus a committed lockfile; a range is DRIFT, because it moves without a commit |
| Whether the lockfile is committed | Day 1 | Platform Engineer | Committed. An uncommitted lockfile is a cache, not a pin |
| Trust-free config versus paranoid trust | Day 1, when a tool or task needs template syntax or secrets | Platform Engineer | Trust-free by construction; where trust is unavoidable, paranoid mode with content-tied trust and a recorded reason, and CI never blankets trust |
| One aggregate `check` versus per-leg tasks only | Day 2 | Developer Tooling Engineer | One aggregate that fails fast, plus the individual legs it calls |
| Whether a legacy `Makefile` or `npm` script survives | Day 2 | Developer Tooling Engineer with the repository owner | Deleted; a surviving shim is a one-line call to `mise run` with a removal date |
| When a tool version bump ships | Handover, then recurring | Named toolchain owner | Its own commit with its own reviewer, never inside a feature diff |
| What happens to a `DRIFT` finding that cannot be fixed now | Day 3, at G3 | Agents Orchestrator with the owner | Recorded with an owner and a date inside the divergence ticket window; past the window it escalates rather than being silently re-baselined |

## Success Criteria

| Metric | Target |
| --- | --- |
| M1 Pinned coverage | 100% of invoked tools pinned; 0 range, partial or `latest` entries; 0 tools installed outside the committed config |
| M2 Lockfile integrity | `mise.lock` committed; `mise lock --dry-run` reports zero changes on the default branch on every run |
| M3 Task parity | 100% in both directions; the parity table sits in the evidence pack and every row names a CI run |
| M4 Doc-to-task resolution | 100% of commands in tracked documentation resolve to an existing task; 0 unresolved |
| M5 Entry points and orphans | 0 second entry points and 0 orphan tasks; every surviving shim is a one-line call to `mise run` with a recorded removal date |
| M6 Cold install budget | `mise install` from the lockfile plus a green `mise run check` in 8 minutes or less per platform in the support matrix, measured on a cold runner and recorded per platform |
| M7 Drift gate liveness | The gate is committed, wired into `check` and CI, and was observed failing on an injected unpinned tool and an injected dead documented command within this run |
| M8 Ownership and repair clock | The toolchain owner is named, the bump rule is written down, and the divergence ticket window is agreed before handover |

## Common Pitfalls

| Pitfall | Mitigation |
| --- | --- |
| The config is pinned but the README still tells people to `pip install` or `npm install` | Doc-to-task resolution is a gate and the task reference is generated from the config; an unresolvable documented command is DRIFT and is fixed or deleted before G3 |
| The lockfile is committed and then never checked | `mise lock --dry-run` runs on every CI run and the drift gate names the stale entry; a lockfile that re-resolves silently is a pin in appearance only |
| CI keeps its own install path "for speed" | G2 compares install paths as well as steps; any CI step installing a tool by another route is DRIFT, and the cache is keyed on the lockfile digest instead |
| Two tasks run the same suite, one of them not wired to CI | Every gating task maps to a CI step and every CI step to a task; a duplicate leg is either used by `check` or it is an orphan, never a third thing |
| A trust prompt trains everyone to answer yes | The config stays trust-free by construction; where trust is unavoidable, paranoid mode ties it to file contents with a recorded reason and CI grants nothing |
| The drift gate is red from day one and everyone learns to ignore it | The gate is proven to fail on an injected defect, repaired on a clock, and re-baselined only by a recorded act — a permanently red job is the same as no job |
| Version bumps land inside feature diffs and nobody reviews them | The Git Workflow Master sets the rule: a bump is its own commit with its own reviewer, and the lockfile diff belongs to the bump |
| "It works on my machine" survives because only the developer's platform was installed | Every platform in the declared support matrix is cold-run; a platform that was never run is NEEDS WORK at G4, not an untested assumption |

## Post-runbook

Measured after handover, reviewed at the next monthly check so the numbers change the next run.

| Metric | Owner | Measured on |
| --- | --- | --- |
| Unpinned additions: tools introduced outside the committed config | Named toolchain owner | Weekly drift gate run, trailing 30 days |
| Lockfile staleness incidents: runs where `mise lock --dry-run` reported changes | DevOps Automator | Every default-branch CI run |
| Parity regressions: a CI step added or edited without a task, or the reverse | Developer Tooling Engineer | Every pull request touching CI, reviewed monthly |
| Cold install time trend per platform | Platform Engineer | Monthly, on the same runner class |
| Documented-command failures reported by contributors | Codebase Onboarding Engineer | Issue intake, trailing quarter |
| Time from a `DRIFT` finding to repair | Agents Orchestrator | Every finding, against the divergence ticket window |
