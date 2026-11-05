# Runbook: Open-Source Maintainer Operations

> **Mode**: NEXUS-Sprint | **Duration**: 2-4 weeks to install, then a permanent weekly cadence | **Agents**: 18

## Scenario

The repository is hardened — license, `SECURITY.md`, issue forms, `CODEOWNERS`, labels as code, a release workflow, required status checks — and then nothing runs. Issues arrive unlabeled. Pull requests wait for a review that never comes, so the author stops waiting. Release notes contradict the diff. Contributors land one patch and vanish. The maintainer alone knows why anything is the way it is.

A ruleset blocks bad merges; it does not prove a good PR was read. Hardening built the enforcement; this runbook staffs it, exercises it, and records who operates it on which day.

**Non-negotiable gate**: an item that arrives with no label and no owner is visible inside 48 hours — either labeled, owned and clocked, or on a declared exception queue with a reason, an owner and a review date. The gate counts arrivals, not the whole backlog: a sweep that must be fully green before launch measures history, not operation.

## Applicability

| Use this runbook when | Use a different runbook when |
| --- | --- |
| Enforcement exists; the gap is who operates it | No policies or enforcement — use `repository-hardening-program` |
| Issues and PRs arrive unlabeled and unowned | The code must be restructured — use `codebase-modernization-program` |
| Release notes are hand-written and untraceable to merged PRs | A vulnerability must be handled — use `security-vulnerability-response` |
| Bus factor is one | An incident is live — use `incident-response` |

Boundary: `repository-hardening-program` builds enforcement; this runbook staffs it.

## Required Inputs

| Input | Why it blocks | Owner |
| --- | --- | --- |
| Repository settings access: labels, issue and PR queues, release settings, required-check configuration | Every triage, sync and release action writes there; read-only access can describe the gap and fix nothing | Maintainer |
| The label inventory as it exists today, exported on day one | You cannot verify a sync, a rename or a removal without the before-state to compare against | Studio Operations |
| Triage rights for two people | One triager is an outage during their vacation | Maintainer |
| A response window per intake class, agreed by the maintainer | The roster can propose a number; only the maintainer can commit the project to it | Maintainer |
| A release credential the maintainer controls and can rotate | A release gated on a former employer's token is not a cadence | Maintainer |
| A named backup maintainer holding merge and release rights | Rights are granted by an administrator, not documented by a runbook | Maintainer |

The labels file is not an input either: it is a Phase 1 deliverable, reconciled against the inventory above. The release workflow and the required checks come from hardening and are exercised, not authored, in Phases 2 and 3.

## Agent Roster

Each row names the gate or metric that proves the agent did its job. No row is on this roster without one.

### Maintainer Command (Always Active)

| Agent | Role | Gate or metric |
| --- | --- | --- |
| Agents Orchestrator (`agents-orchestrator`) | Arrival clock, escalation, exception-queue review | Gate 1.2, Gate 2.2 |
| Senior Project Manager (`project-manager-senior`) | Owner assignment rule, backup maintainer, calendar | Gate 1.2, Gate 4.2 |
| Git Workflow Master (`engineering-git-workflow-master`) | Merge rights, semver intent, deprecation window | Gate 2.1, Gate 3.1 |
| Studio Operations (`project-management-studio-operations`) | Labels, intake classes and stale policy — not assignment | Gate 1.1, Gate 1.2 |

### Triage & Review (Always Active)

| Agent | Role | Gate or metric |
| --- | --- | --- |
| Code Reviewer (`engineering-code-reviewer`) | Blocking-versus-optional standard, rotation, first response | Gate 2.2 |
| Security Reviewer (`engineering-review-security`) | Second reviewer on auth, crypto, CI and dependency paths | Gate 2.2 |
| Reliability Reviewer (`engineering-review-reliability`) | Failure-mode checklist: what fails, what the user sees, rollback | Success: failure-mode checklist applied |
| Test Automation Engineer (`testing-test-automation-engineer`) | Proves the existing required test check actually blocks | Gate 2.1 |
| Developer Community Builder (`marketing-developer-community-builder`) | Acknowledgement, first-timer lane, greeter | Gate 1.2, Gate 4.1 |

### Release & Comms (Weekly)

| Agent | Role | Gate or metric |
| --- | --- | --- |
| DevOps Automator (`engineering-devops-automator`) | Dry-run release: merged PRs to notes to tag to artifact | Gate 3.1, Gate 4.2 |
| Technical Writer (`engineering-technical-writer`) | Actionable notes, `CONTRIBUTING` commands green in CI | Gate 3.1, Gate 4.1 |
| Developer Advocate (`specialized-developer-advocate`) | Announcement naming the tag, breaking changes, upgrade command | Gate 3.2 |

### Trust & Safety (As Needed)

| Agent | Role | Gate or metric |
| --- | --- | --- |
| Application Security Engineer (`security-appsec-engineer`) | Inbound security reports: severity stated per report | Gate 1.2, Post-runbook severity metric |
| Secrets & Credential Hygiene Engineer (`security-secrets-credential-engineer`) | Release credential custody, scoped and rotated | Gate 3.1, Post-runbook rotation metric |
| Compliance Auditor (`security-compliance-auditor`) | SBOM, build provenance and supply-chain evidence per artifact | Gate 3.1, Post-runbook SBOM metric |
| Legal Compliance Checker (`support-legal-compliance-checker`) | License, NOTICE and third-party terms | Success: license and NOTICE review |

### Proof (Monthly)

| Agent | Role | Gate or metric |
| --- | --- | --- |
| Evidence Collector (`testing-evidence-collector`) | Evidence pack: sync runs, timestamps, release links, gate results | Gate 4.3 |
| Reality Checker (`testing-reality-checker`) | Running-or-documented verdict per cadence element | Gate 4.3, Post-runbook verdict metric |

## Phase 1: Triage Install

The label taxonomy exists, as code, with a sync workflow and a drift check. Phase 1 operates it and looks for a defect — it does not author it again.

```text
Week 1-2: Take the existing gate into operation
├── Studio Operations → export today's label inventory and diff it against the
│   documented set: synonyms, labels no queue uses, labels an issue form cannot
│   produce; every removal carries an owner and a date
├── Studio Operations → deliver the labels file and exercise the sync: add one
│   label and rename another through it, let the sync run, then look at the labels
│   page and the drift check; both changes visible, check clean afterwards, and no
│   label created by hand in the UI that day
├── Studio Operations → intake classes, stale policy (what closes, what reopens,
│   after how long) and the label-to-class map; assignment is not decided here
├── Agents Orchestrator → arrival timestamp per item, response window per class,
│   overdue queue, and the exception queue: item, reason, owner, review date
├── Senior Project Manager → owner assignment: one named human per arriving item,
│   not the reporter, written on the item inside the window
├── Developer Community Builder → acknowledgement text, who posts it, in which
│   window, and what an outside contributor reads first
├── Quality Gate 1.1 (label sync): the create and the rename both appear on the
│   labels page from the labels file alone, the drift check reports clean after,
│   and both run links are recorded. A renamed label that reappears under its old
│   name fails this gate.
└── Quality Gate 1.2 (arrivals, last 48 hours): every item carries a label, a
    named owner and an SLA clock, or sits on the exception queue with a reason, an
    owner and a review date; the queue holds at most 10 items and none past its
    review date. Items older than 48 hours are backlog: judged by the post-runbook
    staleness metric, not by this gate.
```

## Phase 2: Review Pathway

The required status checks exist on the default branch. Phase 2 proves one of them refuses a merge, then puts humans behind the rest.

```text
Week 2-3: Prove the block, then staff the reading
├── Code Reviewer → one page of blocking versus optional feedback, linked from
│   PULL_REQUEST_TEMPLATE; a comment is blocking or it is not, decided by that page
├── Code Reviewer → rotation with a named reviewer per day, 2-business-day first
│   response, escalation to the maintainer on the day the clock breaks
├── Security Reviewer → auth, crypto, CI config and dependency additions wait for
│   a second reviewer; the path list is written down, not inferred per PR
├── Reliability Reviewer → failure-mode checklist on changes touching retries,
│   timeouts, queues or stored data: what fails, what the user sees, how it rolls
│   back, one quoted line per answer
├── Test Automation Engineer → break the existing required check on purpose: open
│   a throwaway PR with a behavior change and no test, confirm it goes red and the
│   merge stays unavailable, record the check name that did it
├── Developer Community Builder → first-time PRs get a named greeter, a priority
│   lane and the labels that mark them
├── Quality Gate 2.1 (the check blocks): one throwaway PR shows the required test
│   check red on a behavior change with no test, with merge unavailable; the
│   required-check list is recorded with an owner per check.
└── Quality Gate 2.2 (review clock, last 5 business days): every PR opened in that
    window has a named reviewer and a first human response inside 2 business days,
    or a recorded escalation; the median comes from the timestamps, not from memory.
```

## Phase 3: Release Cadence

The release workflow exists: tag-triggered, notes from merged PRs, provenance attached. Phase 3 runs it from a clean clone and finds where it still needs a human.

```text
Week 2-4: Run the release train once, by the book
├── DevOps Automator → dry-run release from a clean clone: merged PRs to notes to
│   tag to artifact, writing down every step that needed someone's memory
├── Technical Writer → notes a user acts on: breaking, added, fixed, deprecated,
│   with an upgrade command per breaking entry; a line no merged PR explains is
│   either traced to that PR or deleted
├── Git Workflow Master → semver intent against the merged diff, the compatibility
│   promise, and the deprecation window written on the item being deprecated
├── Secrets & Credential Hygiene Engineer → the release credential is held by the
│   maintainer, scoped to the release job, and one rotation rehearsal completes
│   without breaking a release
├── Compliance Auditor → SBOM and build provenance on the dry-run artifact: does
│   the SBOM list what the artifact ships, and which dependencies does it omit?
│   Each gap gets an owner and a date
├── Legal Compliance Checker → license, NOTICE and third-party terms for the
│   dependencies added since the last release; a license contradicting the
│   project's declared license is a recorded conflict, resolved before the tag
├── Developer Advocate → announcement and upgrade path published with the tag
├── Quality Gate 3.1 (dry run): a clean clone cuts the dry-run release with notes
│   generated from merged PRs, zero unexplained hand-written lines, a signed tag,
│   the artifact and its SBOM attached, and every memory step on the fix list.
└── Quality Gate 3.2 (release comms): the announcement names the tag, the breaking
    changes and the upgrade command; a reader outside the maintainer team runs that
    command from the previous version and reports the result before the release is
    marked announced.
```

## Phase 4: Contributor Pipeline and the Second Human

```text
Week 3-4, plus the first cycle after it where noted
├── Developer Community Builder → good-first issues with an owner, done criteria,
│   the files involved, and the response window written on the issue itself
├── Technical Writer → CONTRIBUTING kept true: its commands run in CI, so a stale
│   command fails the build instead of the newcomer
├── Senior Project Manager → backup maintainer trained, then observed cutting a
│   release; the date is recorded, inside the install window or the first cycle
│   after it
├── Evidence Collector → evidence pack: sync runs, review timestamps, release run
│   links, SBOM and license records, gate results per phase
├── Reality Checker → running-or-documented verdict per cadence element, default
│   NEEDS WORK, using the definitions below
├── Quality Gate 4.1 (contributor lane): every good-first issue carries an owner,
│   done criteria and a reply inside the response window, and the CONTRIBUTING
│   commands are green in CI on the day of the gate.
├── Quality Gate 4.2 (second human): two different humans have cut a release
│   end-to-end with both names and the date recorded, inside the install window or
│   the first cycle after it. If the second human's release has not happened, the
│   gate reports NOT MET and names the calendar date it is scheduled for; a
│   rehearsal reported as a release fails this gate.
└── Quality Gate 4.3 (verdict): every cadence element is running or documented
    under the definitions below and the evidence pack exists. One element marked
    not installed means the runbook is not installed.
```

### Verdict Definitions

- **Running** — a dated observation from inside the last cadence window, produced by someone other than the person who wrote the policy: a sync run, a review answered inside the clock, a release with generated notes, a rotation rehearsal. Installing the tool twice is not an observation.
- **Documented** — the policy exists and one dated exercise shows it executing as written, but the cadence window has not closed, so there is no second observation. Documented is provisional and carries an expiry: the date of the next scheduled observation.
- **Not installed** — neither. No dated execution, or an exercise that passed only because someone did it by hand outside the workflow.

The Reality Checker reports one verdict per cadence element, quotes the observation behind every running verdict, and states the expiry date behind every documented one.

### Recurring Cadence After Install

| Group | Weekly | Monthly | Quarterly |
| --- | --- | --- | --- |
| Maintainer Command | Agents Orchestrator clears the overdue queue on a fixed weekday and names a decision per item; Senior Project Manager confirms the backup maintainer still holds merge and release rights | Senior Project Manager runs one live release decision with the backup maintainer, not a walkthrough | Maintainer with Git Workflow Master reviews who holds merge rights and revokes the ones nobody used |
| Studio Operations | Review the labels added in the past week against the intake classes; each new label joins the labels file or is removed | Diff the live labels against the labels file and record the drift count, including a recorded zero | Re-read the stale policy against what was actually closed and reopened; amend or confirm in writing |
| Triage & Review | Code Reviewer checks rotation coverage for the coming week and fills gaps by name; Reliability Reviewer confirms the failure-mode checklist still names real failure paths | Review the response-time spread per reviewer; a reviewer outside the clock takes fewer assignments next month | Re-read the blocking-versus-optional page against a sample of the quarter's review comments and delete a rule nobody applied |
| Release & Comms | DevOps Automator confirms the coming release is cuttable: notes preview, artifact, SBOM, valid credential; Developer Advocate drafts the announcement skeleton | Compare generated notes line by line with merged PRs; every unexplained line becomes a follow-up item | Git Workflow Master restates the compatibility and deprecation window against what actually shipped |
| Trust & Safety | Application Security Engineer clears inbound security-classified reports and states severity per report | Secrets engineer audits credential TTLs and completed rotations; Compliance Auditor confirms SBOM and provenance on that month's releases | Legal Compliance Checker re-reviews license, NOTICE and third-party terms for the quarter's added dependencies |
| Proof | Evidence Collector appends this week's dated observation per cadence element, so the monthly verdict is read from a log and not reconstructed | Reality Checker issues the running-or-documented verdict per element; Evidence Collector files the month's evidence pack | Evidence Collector and Reality Checker re-run Gates 1.1 through 4.3 as an audit and report what regressed |

## Key Decisions

| Decision Point | When | Who Decides |
| --- | --- | --- |
| Intake classes, and the response window each carries | Phase 1 | Studio Operations + Maintainer |
| Stale policy: what closes, what reopens, after how long | Phase 1 | Studio Operations + Senior Project Manager |
| Who is exempt from assignment: bots, drafts, embargoed security reports | Phase 1 | Senior Project Manager + Application Security Engineer |
| Who may merge where, and which paths need a second reviewer | Phase 2 | Git Workflow Master + Security Reviewer |
| First-timer priority: which labels, in what order | Phase 2 | Code Reviewer + Developer Community Builder |
| Cut now or wait; patch versus minor | Phase 3 | Maintainer + DevOps Automator |
| A dependency whose license contradicts the project's | Phase 3 | Legal Compliance Checker + Maintainer |
| Backup maintainer, and the date of their first release | Phase 4 | Maintainer + Senior Project Manager |

## Success Criteria

Windows here close inside the runbook. Anything that needs a month or a quarter is in Post-runbook with a named owner.

| Metric | Target | Window |
| --- | --- | --- |
| Label sync exercised: create and rename applied from the labels file, drift check clean afterwards | 2 of 2 changes applied, 1 clean drift run recorded | Phase 1 |
| Arrivals in the last 48 hours carrying a label, a named owner and a clock, or an exception entry with reason and review date | ≥ 95% of arrivals, exception queue ≤ 10 items, none overdue | Gate 1.2 |
| Throwaway PR with a behavior change and no test blocked by the existing required check | 1 of 1 red, merge unavailable, check name recorded | Gate 2.1 |
| PRs opened in the last 5 business days with a named reviewer and a first response inside 2 business days, or a recorded escalation | ≥ 90% of those PRs, median ≤ 2 business days | Gate 2.2 |
| Changes touching retries, timeouts, queues or stored data carrying a quoted failure-mode checklist line | every such change opened during the install | Phase 2-3 |
| Dry-run release from a clean clone with notes generated from merged PRs | 1 of 1, zero unexplained hand-written lines | Gate 3.1 |
| SBOM attached to the dry-run artifact, with the dependencies it omits named | 1 of 1, gap list with an owner per gap | Gate 3.1 |
| Dependencies added since the last release with license, NOTICE and third-party terms reviewed | every added dependency, dated record each | Phase 3 |
| Credential rotation rehearsal completed without breaking a release | 1 of 1, with the rotation timestamp | Phase 3 |
| Upgrade command from the announcement executed from the previous version by an outside reader | 1 of 1, result recorded before "announced" | Gate 3.2 |
| Good-first issues carrying an owner, done criteria and a reply inside the response window | every good-first issue open on the gate day | Gate 4.1 |
| Releases cut end-to-end by two different humans, names and date recorded | 2 humans, by the install window or the first cycle after it | Gate 4.2 |
| Cadence elements with a running or documented verdict | every element, default NEEDS WORK | Gate 4.3 |

## Post-runbook

Windows longer than the install, measured from the Go-Live date. Each row has one owner who reports the number to the maintainer.

| Metric | Target | Window | Owner |
| --- | --- | --- | --- |
| Open issues and PRs stale past 90 days | ≤ 5% of open items | Quarterly | Studio Operations |
| Releases cut end-to-end by a non-primary maintainer | ≥ 1 per quarter | Quarterly | Senior Project Manager |
| Median time to first human response, pull requests | ≤ 2 business days | Monthly | Code Reviewer |
| Median time to first human response, issues | ≤ 3 business days | Monthly | Agents Orchestrator |
| Releases whose notes were generated from merged PRs, no unexplained hand-written lines | every release in the month | Monthly | DevOps Automator |
| Releases with SBOM and build provenance attached to the published artifact | every release in the month | Monthly | Compliance Auditor |
| Added dependencies with license, NOTICE and third-party terms reviewed | every added dependency | Monthly | Legal Compliance Checker |
| Security-classified inbound reports with a stated severity inside the response window | every report in the month | Monthly | Application Security Engineer |
| Scheduled credential rotations completed against their stated TTL | every scheduled rotation, per quarter | Quarterly | Secrets & Credential Hygiene Engineer |
| Cadence elements still running under the verdict definitions | every element, re-verdicted each month | Monthly | Reality Checker |
| Evidence packs filed: monthly pack, quarterly audit pack | 1 per month, 1 per quarter | Monthly / Quarterly | Evidence Collector |

## Common Pitfalls

| Pitfall | Mitigation |
| --- | --- |
| Rebuilding the label taxonomy, the release workflow or the required checks that hardening delivered | Phases 1-3 exercise what exists and record the run; a defect in the existing gate becomes an issue against hardening, not a rewrite here |
| Triage labels but never assigns — a storage bin | Senior Project Manager owns assignment; Studio Operations owns labels and stale policy; neither owns both |
| A gate that sweeps the whole backlog and can never be green | Gate 1.2 counts arrivals in the last 48 hours; backlog is a post-runbook trend with an owner |
| Exceptions hidden because they look like failure | The exception queue is a required artifact — reason, owner, review date — capped at 10 and reviewed weekly |
| Release notes written from memory | Generated notes are diffed against merged PRs; an unexplained line is traced or deleted |
| Backup maintainer who never cut a release | Gate 4.2 needs a real release with a name and a date, or reports NOT MET |
| "Documented" reported as "running" | Documented verdicts expire at the next observation date; running verdicts quote their observation |
| Supply-chain evidence parked with whoever mentions licensing | SBOM and provenance belong to the Compliance Auditor; license, NOTICE and third-party terms to Legal Compliance Checker |
| Cadence abandoned after week four | Monthly verdict and quarterly gate re-run, both owned in the Post-runbook table |
