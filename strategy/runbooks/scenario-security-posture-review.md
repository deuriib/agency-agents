# Runbook: Security Posture Review

Mode: NEXUS-Sprint | Duration: 4-6 weeks | Agents: 15

## Scenario

There are security controls, a scanner, and a policy document. Nobody can state the organization's real exposure on one page. Alerts fire and get closed; the ticket moves, the system does not change. Secrets live in CI variables that nobody has rotated since the day they were created. AI-assisted coding has doubled the volume of merged code, and review capacity did not double with it. The last penetration test report is eighteen months old, and its findings were never verified as fixed — the tracker says "closed," the code says otherwise.

This runbook measures the posture that exists, proves which controls actually work, and produces a remediation plan ordered by real exposure rather than by a scanner's own severity labels.

The doctrine is one sentence: **a control that has never been observed failing is a hope, not a control.** This runbook converts claimed controls into observed ones. Every claim on the claim list frozen at G2 exits with one of three states — observed working, observed failing, or retired as unobservable, in which case it stays in the one-pager as an exposure line rather than disappearing — and "claimed" is not an exit state. A scanner report is not a posture; a policy document is not a control; an alert that fires and is closed is not a detection.

**Authorization boundary.** The Penetration Tester operates only inside a written scope, with written authorization and a stated time window naming targets, accounts, environments, and a named authorizer. Anything outside that scope — another tenant, another region, another domain, a production data store, a third-party SaaS, a colocated system that merely looks related — is out of bounds. When a test suggests the boundary, the runbook halts and returns the question to the named authorizer; it never expands the scope inside the window to pursue an interesting adjacent finding. An out-of-scope request is an incident, not an assessment.

**Attribution and adversary presence.** Every observation is attributed before it is recorded. An observation is attributed to a control weakness only when it is reproduced from an authorized origin and the state is fully explained by configuration the team owns; anything unexplained — a session nobody opened, traffic nobody generated, a credential in use, an account nobody created — is attributed to an adversary, not to a gap in coverage. If any observation indicates adversary presence rather than a weakness, the assessment stops immediately: the run halts, the named authorizer and incident response are notified within the hour, and the run resumes only on written re-authorization that names the new conditions. A halted run records as **HALTED — neither PASS nor FAIL**, whatever evidence it had collected, and no test traffic of any kind is sent while the incident is open. Chasing the incident is the incident-response runbook's job, not this one's.

Containment is not deferred to remediation. Anything that trips the immediate-containment threshold in Thresholds is contained when it is found, in any week, and enters the backlog with a containment date attached.

## Applicability

| Use this runbook when | Use a different runbook when |
| --- | --- |
| You need a standing, point-in-time assessment of the whole posture: controls, detections, code, cloud, identity | A specific vulnerability has been reported or detected — use `security-vulnerability-response` |
| The claim list exists but its truth is unknown, and exposure cannot be stated in one page | Something is actively happening right now and containment is the only objective — use `incident-response` |
| Remediation must be ordered by real exposure across the whole surface, not by one tool's severity ordering | The goal is audit-ready controls for SOC 2 / ISO 27001 — use `compliance-certification-program` |
| Alerts, secrets, and AI-assisted code volume have accumulated faster than anyone could review them | The scope is supply-chain and CI hardening — use `repository-hardening-program` |
| You need to know which of the claimed controls would survive an adversary who is allowed to try | The asset is an agent product that must be secured through design — use `agentic-product-build` |

Running this assessment alongside a framework audit is normal — the observation artifacts feed it — but the gates here are about exposure, not about certification.

## Required Inputs

Only what the roster cannot produce. The exposure report, the posture one-pager, and the ordered remediation backlog are outputs, not inputs — if they existed, this runbook would not be needed.

| Input | Why it blocks | Owner |
| --- | --- | --- |
| Written authorization and written scope for active penetration testing: targets, accounts, environments, time window, named authorizer, prohibited actions | Without a signed scope there is no adversarial validation at all; the Penetration Tester does not start and G4 cannot be attempted | Named authorizer (CISO or delegate) |
| Written authorization for synthetic trigger injection into live detection: the named roles permitted to inject into production, the suppression window agreed with the SOC, and the SOC notification that precedes the first injection | Active testing is not only the Penetration Tester's traffic: injecting a synthetic trigger into a production rule is an authorized test or an incident, and without this authorization Phase 2 cannot run and M4, M5, and G5 cannot be measured | Named authorizer with the SOC lead; executed by the Threat Detection Engineer |
| Read access to cloud and identity configurations: account/tenant list, IAM and role definitions, network exposure, identity provider settings, CI system configuration | Exposure cannot be measured from the outside alone; without it the asset inventory is a guess and G1 is unfailable | Platform / Cloud owner |
| The current control inventory or claim list — what the organization says it has, in whatever form it currently exists | The claim is the unit of work; no claim list means no test plan, only another scan | Security Architect (custodian) |
| Previous assessment findings with their fix status, including the eighteen-month-old penetration test report and every item marked "closed" | Re-verifying old "fixed" items is the cheapest real signal available, and an unverified closure is a finding in its own right | Compliance Auditor / prior engagement owner |
| A named owner who can authorize remediation budget and reallocate engineering time | A remediation plan without budget authority is a document, not a plan; G5 cannot close and the backlog rots | Business owner |

## Agent Roster

15 agents. `Proven by` names the gate (G1-G5) or metric (M1-M8, Success Criteria) that fails without that agent — every row is traceable to something that can be observed.

### Command (Always Active)

| Agent | Slug | Role | Proven by |
| --- | --- | --- | --- |
| Agents Orchestrator | agents-orchestrator | Phase gating, gate evidence assembly, run log, halt-on-out-of-scope authority | G5 |
| Security Architect | security-architect | Claim list decomposed into atomic testable claims; severity banding; exposure-score ordering of the backlog | G2 |
| Senior SecOps Engineer | security-senior-secops | Immediate containment execution for threshold findings; control fixes in authentication, authorization, headers, rate limiting, secure logging | M2 |

### Detection & Exposure (Week 1-2)

| Agent | Slug | Role | Proven by |
| --- | --- | --- | --- |
| Threat Detection Engineer | security-threat-detection-engineer | Alert inventory, per-rule fidelity measurement, synthetic trigger per rule, tuning and retirements | M4 |
| Threat Intelligence Analyst | security-threat-intelligence-analyst | Named adversaries and named techniques for this business, and which of them sit on the critical attack path | M5 |
| Cloud Security Architect | security-cloud-security-architect | Cloud and identity exposure inventory, IAM and IaC findings, reconciliation against the asset export | G1 |

### Code & Supply Chain (Week 2-3)

| Agent | Slug | Role | Proven by |
| --- | --- | --- | --- |
| Application Security Engineer | security-appsec-engineer | SAST/DAST signal triaged against the claim matrix; trust-boundary review of the highest-exposure services; SDLC gaps | M1 |
| AI-Generated Code Security Auditor | security-ai-generated-code-auditor | The seeded AI-assisted merge sample: trust-boundary violations and insecure defaults, CWE-mapped, each verdict citing file and line | G3 |
| Secrets & Credential Hygiene Engineer | security-secrets-credential-engineer | Secret inventory across repos, CI variables, and vaults; liveness classification; rotation and verified revocation | M6 |

### Adversarial Validation (Week 3-4)

| Agent | Slug | Role | Proven by |
| --- | --- | --- | --- |
| Penetration Tester | security-penetration-tester | Active validation inside the written scope only; reproduced proof per finding | G4 |
| SRE (Site Reliability Engineer) | engineering-sre | Test-window safety: abort conditions written before the first request, rate limits, environment isolation, retained network log; executes containment changes without an availability regression | G4 |

### Governance & Proof (Week 5-6)

| Agent | Slug | Role | Proven by |
| --- | --- | --- | --- |
| Compliance Auditor | security-compliance-auditor | The G5 traceability index — claims to dated artifacts and artifacts back to claims, in both directions — and the mapping of observed controls to whatever framework the organization reports against | G5 |
| Executive Summary Generator | support-executive-summary-generator | The one-page exposure statement a non-technical owner can act on: what is exposed, what is proven working, what is carried as accepted risk and until when | M1 |
| Evidence Collector | testing-evidence-collector | One dated artifact per finding and per closure; custody of the failing-then-passing pairs | M3 |
| Reality Checker | testing-reality-checker | Final verdict on the evidence pack (default: NEEDS WORK) | G5 |

## Thresholds

Every number a gate cites is defined here once. A gate that cites an undefined number cannot fail.

| Threshold | Definition | Default value | Owner |
| --- | --- | --- | --- |
| Severity band | Assigned from reachability, exploitability preconditions, and blast radius — not from a scanner's own label. A finding is banded by the worst realistic chain it participates in, not by its individual score | S1 Critical / S2 High / S3 Medium / S4 Low | Security Architect + Penetration Tester |
| Immediate-containment trigger | Any finding that is internet-reachable, needs no authentication, and reaches customer data or production credentials; or any credential that is live, non-expiring, and exists outside the vault | Containment begins the same business day; the named authorizer is notified within 4 hours | Senior SecOps Engineer |
| Remediation SLA | Calendar days from the day the finding enters the verified backlog to the day its fix is verified — not to the day a ticket is created | S1: 7 days · S2: 30 days · S3: 90 days · S4: 180 days | Security Architect |
| Verified fixed | The identical test that produced the finding was observed failing before the fix and passing after it, from the same origin, with both artifacts dated and retained; or a control that fires on the specific bad state was observed failing and then passing. "Code merged," "ticket closed," and "owner confirmed" are not verification | Pre-fix failing observation plus post-fix passing observation, both dated | Evidence Collector |
| Risk acceptance | A written, time-boxed decision to carry a finding unfixed, signed by the risk-acceptance authority. Acceptance expires; on expiry the finding returns to the backlog at its original severity with its clock reset | Maximum 90 days, one renewal; after that, remediation or control retirement is mandatory | Risk-acceptance authority |
| Asset reconciliation tolerance | Largest difference tolerated between the posture asset inventory and the cloud/identity resource export | Zero unclassified assets; every unmatched row has a named owner | Cloud Security Architect |
| AI-assisted change sample | Review sample size and selection for merged AI-assisted changes in the trailing 6 months: the larger of 40 changes or 10% of them, stratified so at least one third touch an authentication, authorization, data-access, or prompt/LLM trust boundary; drawn by seeded random selection over the merge list, with the seed recorded before the draw | ≥40 changes or 10%, ≥1/3 trust-boundary | AI-Generated Code Security Auditor |
| Frozen claim list | The claim list exactly as it stands at G2, with its claim count recorded in a dated artifact at G2. It is the fixed denominator for M1 and for the retirement-without-exposure cap: a claim added after G2 does not dilute the metric, and a claim retired after G2 does not leave the denominator | Count fixed and recorded at G2; the same count is used at G5 | Security Architect |
| Retirement-without-exposure cap | Share of the frozen claim list that may exit the runbook as retired because the control cannot be observed. A retired claim is never deleted to improve a ratio: it stays in the one-pager as an exposure line carrying a named owner, the compensating control that covers it, and a review date | Maximum 20% of the frozen list; a larger share of retirements without exposure lines fails G5 | Security Architect |
| Abort condition | The SRE's stop rule for every active test window, written and signed before the first request is sent. Any one of these, whichever comes first: request error rate at 2x the same-hour trailing 14-day baseline; p95 latency up 50% over that same baseline sustained for 3 consecutive minutes; or any 5xx response on checkout or authentication | Stop test traffic within 60 seconds of the trigger; notify the named authorizer within 5 minutes | SRE |
| Signed abort-condition sheet | The dated artifact holding the abort condition, the agreed rate limits, the isolated environments, the network log retention window, and the SRE's signature. It exists before the first request of a test window and is never written afterwards | Required before G4 can be attempted; a window without a signed sheet is not a test window | SRE |
| Alert review window | The lookback used for every per-rule precision and coverage number: the trailing 90 days for each rule, with the exact window stated on that rule's line in the alert inventory | Trailing 90 days per rule, window recorded per rule | Threat Detection Engineer |
| Traceability index completeness | Two directions, counted from the G5 traceability index: share of frozen claims that resolve to at least one dated artifact, and share of retained artifacts that resolve back to a claim on the frozen list | 100% in both directions; an orphan claim or an orphan artifact fails G5 | Compliance Auditor |
| Detection fidelity | Alert precision per rule over the alert review window: confirmed incidents divided by alerts raised, for rules that fired at least once | ≥50% per rule; a rule below it is retuned or retired with a recorded reason | Threat Detection Engineer |
| Detection coverage | Share of the techniques the threat model actually names (not the full ATT&CK matrix) for which a rule exists and has been observed firing on a synthetic trigger | ≥80% of named techniques; 100% of those on the critical attack path | Threat Intelligence Analyst |
| Exposure score | Ordering key for the backlog: reachability × exploitability preconditions × blast radius, multiplied upward when the adjacent control is unobserved or observed failing | Reported 0-100 per finding; ties broken by SLA age | Security Architect |
| One-pager completeness | Share of the frozen claim list that exits the runbook in a documented state rather than "claimed": observed working, observed failing, or retired and carried as an exposure line with owner, compensating control, and review date | 100% of the frozen list at G5 | Security Architect |

## Week 1-2: Measure the Real Surface

Phase 1 inventories what exists. Phase 2 converts the claim list into work. Both phases produce artifacts, not impressions.

### Phase 1: Asset & Claim Inventory

```text
├── Agents Orchestrator → run log opened; the authorization scope and time window
│   recorded as the first artifact, before any test is run
├── Cloud Security Architect → resource export from every account and tenant: compute,
│   storage, network paths, managed services, CI-privileged identities; reconcile against
│   the posture asset inventory; every unmatched row gets a named owner
├── Security Architect → control inventory decomposed into atomic claims:
│   "MFA enforced on all console access" not "identity security";
│   "bucket denies anonymous read" not "storage is locked down"
├── Senior SecOps Engineer → identity and access surface: who and what can reach
│   production, standing privileges, token lifetimes, and the full CI variable inventory
│   with each variable's age since last rotation
├── Threat Intelligence Analyst → the adversaries that matter to this business, named,
│   with the reasoning; the techniques they use and which sit on the critical attack path
├── Threat Detection Engineer → alert inventory: rule → signal → owner → last observed
│   firing → the alert review window each precision number will be measured over,
│   including the count of rules that have never fired since deployment
└── Quality Gate (G1): the inventory and the cloud/identity resource export reconcile —
    one asset present in the export and absent from the inventory, or present with no
    named owner, fails the gate
```

### Phase 2: Claim Classification & Containment Queue

```text
├── Security Architect → every claim classified as observed-working / claimed-untested /
│   unobservable / not-applicable, each carrying a named test method and a named owner;
│   "unobservable" is a legitimate class and forces a retire-or-redesign decision, and a
│   retirement is capped by the retirement-without-exposure cap: the claim stays in the
│   one-pager as an exposure line with an owner, a compensating control, and a review date
│   rather than leaving the count
├── Compliance Auditor → claims mapped to the framework the organization reports against,
│   so the framework view later shows observations rather than assertions
├── Senior SecOps Engineer → containment queue from Phase 1: anything meeting the
│   immediate-containment trigger is contained now and backdated into the backlog;
│   nothing waits for Week 5
├── Threat Detection Engineer → one synthetic trigger per rule, injected only under the
│   authorization held in Required Inputs, with the SOC notified before the first injection
│   and the agreed suppression window in force so injected triggers are not triaged as real
│   incidents: the rules where the trigger produces no alert are the real detection
│   inventory, and the rest are unproven until they fire on something real
├── Executive Summary Generator → first cut of the one-pager, entirely in "claimed"
│   state, so the delta at G5 is visible to a non-technical reader
└── Quality Gate (G2): every claim carries a classification, a named test method, and a
    named owner — a single claim still marked "in place" with no test method and no owner
    fails the gate. The claim list is frozen here and its count is recorded as a dated G2
    artifact: that frozen count is the only denominator M1 and the retirement-without-
    exposure cap may use
```

## Week 3-4: Test What Is Claimed

Phase 3 tests the code and supply-chain surface at volume. Phase 4 tests what remains, adversarially and inside the scope.

### Phase 3: Code, AI-Assisted Changes & Supply Chain

```text
├── AI-Generated Code Security Auditor → the seeded sample from Thresholds; per change,
│   the verdict answers one question: did the author treat the trust boundary correctly?
│   Concretely — row-level security left off, keys inlined, user input concatenated into a
│   system prompt, permissive CORS, a route with auth disabled, an allow-all firewall
│   rule, a service-role client shipped to a browser bundle; CWE-mapped, each verdict
│   citing file and line
├── Application Security Engineer → SAST/DAST results triaged against the claim matrix;
│   a hit the team previously dismissed as a false positive is re-tested, not re-trusted
├── Secrets & Credential Engineer → repo history, CI variables, and vault contents
│   inventoried across every repository in scope; each hit classified live or dead;
│   live ones rotated first, removed from source second, and the removal confirmed
│   by re-scan third
├── Threat Detection Engineer → coverage measured against the named techniques; a rule
│   that exists but has never fired is recorded as unproven, not as coverage
├── SRE → the abort-condition sheet is written and signed before the first request: the
│   abort condition itself, rate limits agreed, environments isolated, log retention
│   confirmed, all recorded in that one dated artifact
└── Quality Gate (G3): every change in the seeded sample has a recorded verdict with a
    resolvable file-and-line citation — one change marked "reviewed" with no citation and
    no verdict fails the gate
```

### Phase 4: Adversarial Validation

```text
├── Penetration Tester → inside the written scope and window only: validate the highest
│   exposure-score candidates from Phases 2 and 3 — is the "disabled" row-level security
│   actually readable, is the "private" bucket actually private, does the "internal only"
│   endpoint answer from the internet, does the CORS policy actually restrict, can the
│   leaked-but-rotated credential still authenticate
├── Penetration Tester → every confirmed finding carries a reproduced request/response
│   pair or a dated capture; an unreproducible finding goes back to Phase 3, it does not
│   enter the backlog as an assumption
├── Agents Orchestrator → halt on any request outside the written scope; escalate to the
│   named authorizer; no scope change is granted inside the window
├── SRE → availability watched during every active test against the abort condition in
│   Thresholds; on the trigger, test traffic stops within 60 seconds and the named
│   authorizer is notified within 5 minutes, and the stop is recorded in the run log
├── Penetration Tester → every observation is attributed before it is written up: a
│   reproduced state explained by owned configuration is a weakness, an unexplained
│   session, beacon, credential use, or account is adversary presence and halts the run
├── Evidence Collector → dated artifact per finding, indexed by exposure score
└── Quality Gate (G4): no window opens without the signed abort-condition sheet, every
    finding has a reproduced proof and a severity band traceable to the Thresholds table,
    and the retained network log shows zero requests outside the authorized scope — a
    missing or unsigned abort-condition sheet, a single out-of-scope request, or one
    unproven finding carried into the backlog, fails the gate
```

## Week 5-6: Remediate & Prove

```text
├── Security Architect → the backlog ordered by exposure score, not by scanner severity;
│   ties broken by SLA age; every row carries an owner, an SLA date, and the test that
│   proves it closed
├── Senior SecOps Engineer → S1 and S2 fixes land with their test: the check that failed
│   before the fix is retained and re-run after it
├── Application Security Engineer → SDLC changes that stop the class from returning — a
│   build check that fails on the specific bad state, observed failing before it is trusted
├── AI-Generated Code Security Auditor → the sample re-scanned; the review gate is applied
│   to new AI-assisted merges, not only to this sample
├── Secrets & Credential Engineer → rotation completed: vaulted, short-lived, no long-lived
│   CI credential remains; each old credential's revocation proven by attempting to use it
├── Compliance Auditor → the G5 traceability index: one row per claim on the frozen list,
│   each resolving to at least one dated artifact, and one row per retained artifact,
│   each resolving back to a claim; the framework view is then read off the index, so it
│   shows observed controls with dates instead of asserted controls
├── Executive Summary Generator → the one-pager: what is exposed, what is proven working,
│   what is carried as accepted risk with an expiry date, what is scheduled with an SLA,
│   and every retired claim as an exposure line with owner, compensating control, and
│   review date — a retirement is visible on the page, not subtracted from it
├── Evidence Collector → the closure pack: one dated failing-then-passing pair per closed
│   finding, retained and indexed
├── Reality Checker → final verdict on the evidence pack (default: NEEDS WORK); an
│   unobserved claim, an unverified closure, or a finding past SLA without a signed
│   acceptance prevents a PASS
└── Quality Gate (G5): zero claims left in "claimed" state, zero findings closed without
    a dated failing-then-passing pair, and a traceability index at 100% in both directions
    over the frozen claim list — one claim still marked "in place" without an observation,
    one finding closed as "fixed" with no pre-fix failing observation, one claim or
    artifact orphaned in the index, or a share of retirements above the retirement-without-
    exposure cap, fails the gate
```

## Key Decisions

| Decision Point | When | Who Decides | Default if nobody decides |
| --- | --- | --- | --- |
| Contain now versus schedule | At triage for every finding, re-checked at G4 | Security Architect with the named authorizer; Senior SecOps Engineer executes | Containment applies whenever the immediate-containment trigger is met; everything else is scheduled into its SLA band |
| Public disclosure of findings | End of Week 5, once the fix is verified | Named authorizer with Legal | No disclosure; findings stay internal unless a regulatory or contractual obligation applies |
| Risk acceptance authority and its scope | Week 1, before the backlog exists | Business owner named in Required Inputs | Findings past SLA are reported in the one-pager as unaccepted and unmitigated, with the exposure score unchanged |
| Does a finding block a release | At each release gate, per finding | Security Architect with the release owner | S1 and S2 block; S3 and S4 do not |
| Fix, retire, or re-scope a control | At G2, revisited at G5 | Security Architect with the control owner | A control that cannot be observed is retired from the frozen claim list rather than left claimed, within the retirement-without-exposure cap, and stays in the one-pager as an exposure line with owner, compensating control, and review date |
| Change of test scope mid-engagement | On any out-of-scope signal during Phase 4 | Named authorizer only, in writing | The run halts; no scope expansion is granted inside the window |
| Adversary presence suspected at any point | The moment an observation is attributed to an adversary rather than to a weakness | Named authorizer with incident response | The run is HALTED — neither PASS nor FAIL — authorizer and incident response are notified within the hour, no test traffic is sent while the incident is open, and the run resumes only on written re-authorization |

## Success Criteria

| Metric | Target |
| --- | --- |
| M1 — Claims on the frozen G2 list carried in the one-pager in a documented state (observed working, observed failing, or retired with an exposure line) | 100% of the frozen list |
| M2 — Findings meeting the immediate-containment trigger contained the same business day | 100% |
| M3 — Findings closed as verified fixed with a dated failing-then-passing pair | 100% |
| M4 — Detection rules at or above the fidelity threshold over the alert review window, or retired with a recorded reason | 100% |
| M5 — Named critical-path techniques with a rule observed firing on a synthetic trigger injected under written authorization | 100% |
| M6 — Live secrets found and rotated, plus revocation proven by a failed use attempt | 100% |
| M7 — Frozen-list claims retired as unobservable while carried as exposure lines | At or below the retirement-without-exposure cap of 20%; above it the run fails |
| M8 — Traceability index completeness, in both directions, over the frozen claim list | 100% of claims and 100% of artifacts |

## Common Pitfalls

| Pitfall | Mitigation |
| --- | --- |
| A scanner report presented as posture: the report is delivered, nobody can say what the organization's exposure is, and the numbers are quoted for a quarter | The deliverable is the one-pager with observations, not the export; every claim in it traces to a dated artifact, and a scanner hit is only an input candidate until it is reproduced |
| Findings closed by exception rather than by fix: tickets close through triage boards, renewals, and "risk accepted" with no signature | Only the Thresholds definition of verified fixed closes a finding; an acceptance needs a named authority and an expiry date, and an expired acceptance returns the finding at its original severity |
| Secrets rotated only after exposure: the CI variable is deleted from the repository and the credential stays live | Rotation precedes removal; revocation is proven by attempting to use the old credential and observing failure; a secret that is removed but not rotated is recorded as still live |
| Penetration tests with no verification of remediation: last year's report is filed as an artifact, its findings assumed fixed | G4 requires reproduced proof and G5 requires a failing-then-passing pair per finding; the previous report's "closed" items are re-verified as part of Phase 1, not trusted |
| Alerts tuned until they stop firing: a noisy rule is muted, precision improves, and coverage quietly disappears | Tuning and retirement are recorded decisions with a reason and an owner; a muted rule counts as absent coverage, and M4 and M5 are measured against the named techniques, never against the alert count |
| Claims retired until the percentage looks complete: unobservable controls leave the denominator, M1 reaches 100%, and the one-pager claims a posture it never observed | M1 runs over the frozen G2 list, never over what survived; a retired claim stays in the one-pager as an exposure line with owner, compensating control, and review date, and retirements above the retirement-without-exposure cap fail G5 |
| Adversary evidence filed as a finding: an unexplained session or a live credential outside the scope is written up as "weak logging" and the assessment continues around it | Attribution comes before write-up; an unexplained observation halts the run to HALTED, notifies the authorizer and incident response within the hour, and resumes only on written re-authorization |
| Abort condition agreed in conversation and lost when the test starts: nobody can state the number that stops traffic, so the test runs until someone notices the graph | The abort condition is written and signed on the abort-condition sheet before the first request; without that sheet there is no window and G4 is not attempted |
| Scope expansion during an adversarial test: an interesting adjacent finding pulls the tester one hop further, and the engagement becomes an unauthorized test | The written scope names targets, accounts, and a time window; any out-of-scope signal halts the run to the named authorizer, and G4 fails on a single out-of-scope request in the retained network log |

## Post-runbook

Anything measured after the window. A runbook that ends at the report has produced a document; these keep the observed posture observable.

| Metric | Owner | Measured on |
| --- | --- | --- |
| Remediation SLA adherence per severity band, plus the count past SLA without a signed acceptance | Security Architect | Day 30 and day 90 after the window |
| Re-test results for every S1 and S2 finding, inside a renewed written scope | Penetration Tester | One re-test at day 30, one at day 90 |
| Detection coverage drift: named techniques whose rule has not fired in the trailing 30 days | Threat Detection Engineer | Monthly |
| Alert fidelity drift per rule, with retune or retire decisions recorded | Threat Detection Engineer | Monthly |
| Secrets rotation currency: share of credentials past their rotation interval | Secrets & Credential Hygiene Engineer | Monthly |
| AI-assisted review gate effectiveness: share of AI-assisted merges passing the gate, and findings per 100 reviewed changes | Application Security Engineer | Weekly |
| Risk acceptance near expiry, with the owning signer notified | Compliance Auditor | Monthly, 14 days before each expiry |
| Control regression: the G2 test methods re-run, any claim that no longer passes back in the backlog | Senior SecOps Engineer | Quarterly |
