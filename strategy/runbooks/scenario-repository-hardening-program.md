# Runbook: Repository Modernization & Hardening

Mode: NEXUS-Sprint | Duration: 2-4 weeks | Agents: 20

## Scenario

A repository works but does not look or behave like a professional one. There is no license, no security policy, no contribution path, no issue or PR templates, no owners, CI that only runs on push, actions pinned to floating tags, `write-all` permissions, and no branch protection. Contributors cannot tell where to start, and maintainers cannot prove any of the rules are enforced.

This runbook turns a working repository into a **governed, enforceable, evidence-backed** repository. The doctrine is one sentence: **every policy must be backed by a gate that has been observed failing.** A `SECURITY.md` nobody monitors, a `CODEOWNERS` naming users who left, or a workflow that never runs on pull requests is worse than nothing, because it manufactures false confidence.

Scope is the repository surface and its enforcement — not product architecture. For architecture and code modernization, use `codebase-modernization-program`.

## Applicability

| Use this runbook when | Use a different runbook when |
| --- | --- |
| The repo must meet a professional or open-source baseline (license, security, community, ownership, templates) | The code itself must be restructured — use `codebase-modernization-program` |
| CI/CD is inconsistent, over-privileged, or unpinned | You must ship one feature into a healthy product — use `enterprise-feature` |
| You cannot prove branch protection, reviews, or checks actually block a merge | The repo has suffered a specific reported vulnerability — use `security-vulnerability-response` |
| Preparing for public release, an audit, or external contributors | You need SOC 2 / ISO 27001 organizational controls — use `compliance-certification-program` |
| Standardizing many repositories onto one hardened template | A whole product and process portfolio must change — use `digital-transformation-program` |

## Required Inputs

| Input | Why it blocks | Owner |
| --- | --- | --- |
| Admin rights on the repository and, for rulesets and org-wide settings, the organization | Enforcement cannot be applied read-only | Platform Engineer |
| Confirmation of which plan features are available (rulesets, secret scanning, push protection, CodeQL) | Plan gaps change the gate design; assuming a feature exists wastes a phase | Platform Engineer |
| A monitored security contact channel and its response window | A disclosure policy without a real inbox is a liability | Security Owner |
| Legal sign-off on license choice and third-party notice obligations | Re-licensing after publication is painful and sometimes impossible | Legal Compliance Checker |
| A decision on DCO vs CLA | Contributor friction and provenance depend on it | Maintainer + Legal |
| A named maintainer accountable for the outcome | Hardening without an owner decays in one quarter | Project Manager |

## Agent Roster

### Command (Always Active)

| Agent | Role |
| --- | --- |
| Agents Orchestrator | Pipeline controller, phase gating |
| Senior Project Manager | Spec-to-task conversion, gap matrix ownership |
| Git Workflow Master | Branch model, protection and rulesets, CODEOWNERS, contribution model, release and versioning strategy |
| Platform Engineer | Organization settings, plan-feature verification, enforcement rollout |

### Repository Foundation (Phase 1-2)

| Agent | Role |
| --- | --- |
| Technical Writer | README, CONTRIBUTING, SUPPORT, CHANGELOG, governance docs, and the CI job that executes their commands so docs are tested, not trusted |
| Legal Compliance Checker | License, third-party notices, DCO/CLA, export and terms review |
| Developer Community Builder | Contribution path a newcomer can actually follow |
| DevOps Automator | Workflow scaffolding, reusable actions, pinned SHAs; from Phase 3 on, CI/CD pipelines with least-privilege permissions, concurrency, and caching |

### Governance & Automation (Phase 3)

| Agent | Role |
| --- | --- |
| Developer Tooling Engineer | Composite actions, local parity with CI, pre-commit hooks |
| Studio Operations | Triage process, label taxonomy, stale and escalation policy |

### Security & Supply Chain (Phase 4)

| Agent | Role |
| --- | --- |
| Security Reviewer | Workflow trust boundaries, fork-PR secret exposure, permissions audit |
| Application Security Engineer | SAST/CodeQL configuration, dependency review, severity thresholds |
| Secrets & Credential Hygiene Engineer | Secret scanning, push protection, rotation guidance |
| Compliance Auditor | Evidence collection, policy-to-gate traceability |

### Quality & Enforcement Proof (Phase 5)

| Agent | Role |
| --- | --- |
| Test Automation Engineer | Deliberately failing PRs that prove each gate blocks |
| Evidence Collector | Screenshots and run logs for every gate |
| Reality Checker | Final verdict (default: NEEDS WORK) |
| Code Reviewer | Review standards, required-review configuration |

### Developer Experience (As Needed)

| Agent | Role |
| --- | --- |
| DX Engineer | Time-to-first-green-CI for a new contributor |
| Developer Advocate | Public-facing contribution and support narrative |

## Execution Plan

### Phase 1: Baseline Audit & Gap Matrix (Day 1-3)

```text
├── Senior Project Manager → gap matrix: required surface vs what exists
├── Platform Engineer → plan-feature verification, org-level setting inventory
├── Git Workflow Master → current branch model, protection state, merge strategy
├── Security Reviewer → workflow permission and secret-exposure audit
├── Compliance Auditor → existing policy docs and whether any gate backs them
└── Quality Gate: gap matrix signed, every item classified as
    present / present-but-unenforced / missing / not-applicable
```

### Phase 2: Legal & Community Foundation (Week 1)

```text
├── Legal Compliance Checker → LICENSE, THIRD-PARTY-NOTICES, DCO or CLA, terms review
├── Technical Writer → README (what it is, install, first run, where to get help),
│   CONTRIBUTING (setup, tests, PR expectations, commit convention),
│   SUPPORT, CHANGELOG, GOVERNANCE
├── Developer Community Builder → CODE_OF_CONDUCT with a real enforcement contact
│   and a stated response window; contribution path verified by walking it
├── Studio Operations → issue triage policy: label taxonomy, response targets, stale policy
└── Quality Gate: every doc names a real, monitored channel; every command in README
    and CONTRIBUTING is verified to run in CI (docs are tested, not trusted)
```

### Phase 3: GitHub Surface & Templates (Week 1-2)

```text
├── DevOps Automator → .github/ISSUE_TEMPLATE/*.yml (issue forms, not blank markdown)
│   + config.yml chooser that routes questions to Discussions
├── Technical Writer → PULL_REQUEST_TEMPLATE.md with a real self-review checklist
├── Git Workflow Master → .github/CODEOWNERS covering the actual tree;
│   every entry validated against live users and teams
├── Studio Operations → .github/labels.yml as the source of truth + sync workflow
├── Platform Engineer → .github/FUNDING.yml (valid sponsor target) and
│   .github/dependabot.yml (ecosystems, schedule, grouping, reviewers)
└── Quality Gate: no template is blank; no CODEOWNERS entry points at a dead
    user or team; labels are declarative and drift-free
```

### Phase 4: CI/CD & Supply Chain (Week 2-3)

```text
├── DevOps Automator → workflows that run on pull_request, with explicit
│   top-level permissions (default contents: read), concurrency groups, and caching
├── DevOps Automator → every action pinned to a full commit SHA, not a tag
├── Developer Tooling Engineer → composite/reusable action so local and CI run
│   the same commands (one way to do things)
├── Application Security Engineer → CodeQL/SAST on a schedule and on PRs, dependency review,
│   severity threshold that actually fails the build
├── Secrets & Credential Hygiene Engineer → secret scanning + push protection enabled,
│   rotation guidance documented
├── Security Reviewer → fork-PR trust boundary: publish and secret-consuming steps
│   gated to base-repo refs only
├── Compliance Auditor → SBOM, build provenance, OpenSSF Scorecard baseline recorded
└── Quality Gate: zero unpinned actions, zero write-all permissions, secret scanning
    and push protection on, and the Scorecard baseline is recorded for comparison
```

### Phase 5: Enforcement & Proof (Week 4)

```text
├── Git Workflow Master → ruleset on the default branch: required status checks,
│   required reviews, CODEOWNERS review, linear history, no force-push,
│   no deletion, signed commits where the project demands it
├── Platform Engineer → staged rollout: warn-only first, then enforce
├── Test Automation Engineer → open one throwaway PR per gate, each deliberately
│   violating exactly one rule, and confirm each goes red for the right reason
├── Evidence Collector → capture run logs and screenshots for every red PR
├── DX Engineer → measure clean-clone to first green CI for a new contributor
├── Reality Checker → final verdict (default: NEEDS WORK)
└── Quality Gate: every policy has an observed failing gate, and the rollout
    moved from warn to enforce with no unreviewed exception
```

## Required Repository Surface

This table is the deterministic checklist. "Enforced by" is mandatory: an item with no gate is not done.

| Surface | Required artifact | Enforced by |
| --- | --- | --- |
| Legal | `LICENSE`, `THIRD-PARTY-NOTICES` | GitHub license detection + legal sign-off |
| Contribution terms | `DCO` check or `CLA` workflow | Required status check |
| Security policy | `SECURITY.md` with private reporting path and response window | GitHub private vulnerability reporting enabled |
| Community | `CODE_OF_CONDUCT.md` with enforcement contact and response window | Maintainer acknowledgement recorded |
| Contribution path | `CONTRIBUTING.md` with setup, test, and PR expectations | Docs executed in CI |
| Orientation | `README.md` (what, install, first run, help) | Docs executed in CI |
| Help routing | `SUPPORT.md`, Discussions enabled | Issue chooser `config.yml` links to it |
| History | `CHANGELOG.md` | Release workflow requires an entry |
| Ownership | `.github/CODEOWNERS` | Required review from code owners |
| Intake | `.github/ISSUE_TEMPLATE/*.yml` + `config.yml` | Forms validate required fields |
| Review | `PULL_REQUEST_TEMPLATE.md` | Checklist referenced in required review guidance |
| Triage | `.github/labels.yml` + sync workflow | Drift check in CI |
| Funding | `.github/FUNDING.yml` | Valid sponsor target or file removed |
| Dependencies | `.github/dependabot.yml` | Dependabot alerts + review |
| CI | workflows triggered on `pull_request` | Required status checks |
| Release | Release workflow with tags, notes, provenance | Tag-triggered, reproducible |
| SAST | CodeQL or equivalent | Schedule + PR gate |
| Secrets | Secret scanning + push protection | Organization security settings |
| Supply chain | SBOM, build provenance, OpenSSF Scorecard | Recorded baseline, trend reviewed |
| Default branch | Ruleset: checks, reviews, CODEOWNERS, no force-push, no deletion | Proven by a deliberately red PR |

## Key Decisions

| Decision Point | When | Who Decides |
| --- | --- | --- |
| License choice | Phase 1 | Legal Compliance Checker + maintainer |
| DCO vs CLA | Phase 1 | Maintainer + Legal Compliance Checker |
| Disclosure response window and security contact | Phase 1 | Security Owner |
| Issue form set and Discussions routing | Phase 2 | Studio Operations + Technical Writer |
| Workflow permission model | Phase 3 | Security Reviewer + DevOps Automator |
| Warn-then-enforce rollout schedule | Phase 4 | Platform Engineer + Git Workflow Master |
| Which checks become required | Phase 5 | Git Workflow Master + maintainer |
| Exception policy for emergencies | Phase 5 | Maintainer + Risk Reviewer |

## Success Criteria

| Metric | Target |
| --- | --- |
| Required surface complete | 100% of the matrix, or explicitly marked not-applicable with a reason |
| Policy-to-gate traceability | 100% of documented policies have an observed failing gate |
| Actions pinned | 100% pinned to full commit SHAs |
| Workflow permissions | Every workflow declares top-level permissions; zero `write-all` |
| Secret scanning and push protection | Enabled and verified by a blocked test commit |
| Branch protection | Ruleset live on the default branch, proven by a red PR |
| CODEOWNERS validity | 100% of entries resolve to live users or teams |
| Docs truth | Every command in README and CONTRIBUTING executes green in CI |
| Disclosure SLA | Acknowledged within 2 business days, triaged within 5 |
| Time to first green CI | New contributor, clean clone, under 1 hour |
| Enforcement evidence | At least one deliberately failing PR captured per gate |

## Deliverables

| Deliverable | Produced by | Phase |
| --- | --- | --- |
| Gap matrix with present / unenforced / missing classification | Senior Project Manager | 1 |
| Legal and community documents | Legal Compliance Checker + Technical Writer | 2 |
| GitHub surface: templates, CODEOWNERS, labels, Dependabot, Funding | DevOps Automator + Git Workflow Master + Studio Operations | 3 |
| Hardened workflows with pinned actions and least privilege | DevOps Automator + Security Reviewer | 4 |
| Supply chain baseline: SBOM, provenance, Scorecard record | Compliance Auditor | 4 |
| Enforcement ruleset with staged rollout | Git Workflow Master + Platform Engineer | 5 |
| Red-PR evidence pack, one per gate | Test Automation Engineer + Evidence Collector | 5 |
| Final verdict and residual risk note | Reality Checker | 5 |

## Common Pitfalls

| Pitfall | Mitigation |
| --- | --- |
| A policy file nobody monitors — `SECURITY.md` or `CODE_OF_CONDUCT.md` naming an inbox that no human reads. Written policy without enforcement is false confidence, which is worse than having no policy | No surface row ships without its "Enforced by" entry, Phase 2 requires a real monitored channel with a stated response window, and the disclosure SLA is measured (acknowledge in 2 business days, triage in 5) |
| Actions re-pinned to floating tags after the hardening wave, because pinning was treated as a one-time sweep | Phase 4 gate holds at zero unpinned actions, `dependabot.yml` owns pin updates, and the result ships as an organization-wide template so new repositories inherit the pin instead of re-earning it |
| `permissions: write-all` copy-pasted into every workflow | Default to `contents: read` and elevate per job, per need |
| `CODEOWNERS` naming people who left, so required reviews are requested from nobody | Phase 3 validates every entry against live users and teams and the build fails on a dead entry; success requires 100% of entries to resolve |
| CI that only runs on push, so pull requests merge unverified | Required checks must be defined on `pull_request` |
| Release or publish steps reachable from fork pull requests — secret exposure | Gate publish and secret-consuming steps to base-repository refs |
| Chasing an OpenSSF Scorecard number instead of the behaviour it measures | Gate on the specific checks and treat the score as a trend, never a target |
| Turning on strict protection on a busy branch in one step — contributor revolt | Staged rollout: warn-only, then enforce, with a documented exception path |
| Docs that drift from reality, so contributors follow broken instructions | Execute README and CONTRIBUTING commands in CI; a broken command fails the build |
| A `CONTRIBUTING.md` no newcomer ever followed — plausible prose, an untested path | The Developer Community Builder walks the contribution path end to end, and the DX Engineer measures clean clone to first green CI under one hour |
| The hardening wave decays after handoff because no owner was named | A named maintainer is a blocking Required Input before Phase 1, the exception policy names who grants and reviews exceptions, and the Reality Checker's residual risk note assigns an owner to every open item |
