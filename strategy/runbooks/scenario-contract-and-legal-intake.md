# Runbook: Contract & Legal Intake

> **Mode**: NEXUS-Micro | **Duration**: 5 business days per batch, recurring, 3 documents per batch | **Agents**: 10

## Scenario

Contracts arrive by email, get read by whoever is least busy, and are signed because the renewal date is tomorrow. Non-standard indemnity clauses pass unnoticed, data-processing terms contradict the published privacy policy, and nobody can name which vendor agreements auto-renew next quarter. The organization is not ungoverned — it is unintakeable: no queue, no classification, no baseline, no one accountable for the signature.

This runbook classifies what arrives, extracts the clauses carrying actual risk, and routes a decision to a human with authority to make it.

**Hard boundary.** It extracts, classifies, compares against a cited baseline, and routes. It does not advise, approve, negotiate, or execute. Approval exists here only as a record against a named human in the authority matrix; an agent that writes "approved" is a defect, not a shortcut, and G4 fails the batch for it. An agent producing a cited, structured brief removes work; an agent issuing a conclusion creates liability. A clause nobody quoted was never reviewed.

The same boundary applies to the standard itself. The clause baseline that defines "material" is an approved input with a named approving human and an approval date — not something the reviewing agent writes for itself and then tests against.

## Applicability

| Use this runbook when | Use a different runbook when |
| --- | --- |
| Inbound agreements need intake, classification, disposition | You must implement audit-ready controls — use `compliance-certification-program` |
| Contracts need clause-level risk extraction against a playbook | A vulnerability is reported or exploited — use `security-vulnerability-response` |
| Data-processing terms must reconcile with the privacy policy | You must choose a license for your own code — use `repository-hardening-program` |
| Renewal and obligation dates must move out of an inbox | The agreement is signed, in dispute, or in negotiation |

## Required Inputs

Every input below is produced outside this runbook: access, a human decision, a chosen standard, or an external artifact. Nothing this runbook produces — the classified register, the clause summary, the exceptions list — may appear in this table, and a batch missing any row is held, not started. The Owner column names a provider, not an approver.

| Input | Type | Why it blocks | Owner |
| --- | --- | --- | --- |
| Read access to the intake mailbox, shared drive, and agreement repository | Access | An agreement nobody can open cannot be classified, hashed, or measured | Agents Orchestrator |
| Approved clause baseline `BL-3.1`: version id, per-family standard / negotiable / unacceptable positions, `BL-LIAB` liability multiple, `BL-PAY` payment days, `BL-NOTICE` notice window, approving human, approval date | Chosen standard | Without a cited, human-approved version, "non-standard" is an opinion and no deviation can be tested as material | General Counsel, as approving human; the Legal Compliance Checker drafts it and may not approve it |
| Authority matrix `AM-2`: value bands A1-A4 with the named human signer and co-signer per tier and per category | Human decision | A brief routed to nobody authoritative is a delay, not a review, and a band with no number cannot be applied at G1 | Chief Financial Officer |
| Approved forum list `FORUM-1` v1: the courts and arbitration seats of record | Chosen standard | "Off the approved list" is unusable until the list exists as a version | General Counsel |
| Entity and tax assumption sheet: contracting entity, residence, treaty position, and reporting basis per counterparty jurisdiction | External artifact | VAT, withholding, and gross-up cannot be cited without the entity assumption each position depends on | Chief Financial Officer |
| Privacy policy, DPA template, approved sub-processor list, approved transfer mechanism | External artifact | DPA, sub-processor, and transfer gaps are undetectable without reference text | Data Protection Lead |
| Named decision owner per document category and `AM-2` tier, recorded in the register | Human decision | A brief routed to nobody authoritative is a delay, not a review | Chief Financial Officer, from `AM-2` |
| Renewal calendar keyed to notice windows, seeded from vendor and finance records | External artifact | Auto-renewal is missed inside the notice window, not at the end date | Chief of Staff |
| Counsel of record and escalation path | External artifact | Otherwise the reviewer's inference becomes the record | General Counsel |
| Review staffing commitment: the five review limits in Batch Capacity held for the batch at the stated hours | Access | A batch staffed below the derivation can review only its derived capacity; anything more is reported as queued, not reviewed | Agents Orchestrator |

Register rows, clause summaries, and exception lists are Phase 1-3 output. They are never a precondition for Phase 1-3.

## Defined Thresholds

Gates fail against these numbers, so they are fixed before the batch opens and cited by version. An undefined threshold cannot be failed and therefore does not exist.

| Threshold | Definition | Set by |
| --- | --- | --- |
| Material deviation | A quoted position differing from cited baseline version `BL-3.1` in any one of: labeled "unacceptable" in that baseline; liability cap below the `BL-LIAB` multiple, or unlimited; indemnity or cap carve-out excluding the organization's own data, IP, or confidentiality; personal data leaving the approved transfer mechanism or an unlisted sub-processor; unilateral amendment, audit, or termination right added; notice window shorter than `BL-NOTICE`; payment terms beyond `BL-PAY` days, net of withholding, or missing gross-up; a forum outside `FORUM-1`. One hit is material. The test is mechanical and applied by the Legal Compliance Checker; the confirmation is a human decision. | General Counsel, in baseline `BL-3.1` |
| `BL-LIAB` liability multiple | Aggregate liability cap of at least 1× the fees paid or payable in the 12 months preceding the claim, applying to both parties. Below that multiple, unlimited on our side only, or capped as a fixed sum small enough to fall below it, is a material deviation. | General Counsel, in baseline `BL-3.1` |
| `BL-PAY` payment days | Net 30 from a valid invoice. A term beyond net 45, payment conditioned on counterparty acceptance, a unilateral set-off right, or any withholding without a gross-up clause is a material deviation. | Chief Financial Officer, in baseline `BL-3.1` |
| `BL-NOTICE` notice-window minimum | 30 calendar days before the end date, or the longer period the agreement or the renewal calendar states. Shorter is a material deviation. | Chief Financial Officer, in baseline `BL-3.1` |
| Authority value bands `AM-2` | A1 under USD 50,000; A2 USD 50,000 to 250,000; A3 above USD 250,000 to 1,000,000; A4 above USD 1,000,000 or any unlimited exposure. Annual contract value = total fees payable over the initial term ÷ term years; the band and its tier are cited in the register row at G1. | Chief Financial Officer, authority matrix `AM-2` |
| Approved forum list `FORUM-1` | Exclusive courts: Delaware, New York (SDNY or New York Supreme), England & Wales. Arbitration seats with their rules: New York (AAA/ICDR), London (LCIA), Stockholm (SCC). Any other forum, or a forum whose judgments are not enforceable where the counterparty holds assets, is off-list and a material deviation. | General Counsel, list `FORUM-1` v1 |
| Batch capacity | 3 documents per batch, derived in Batch Capacity. A document above capacity holds a queue position and is reported as queued, never as late. | Agents Orchestrator, from the Batch Capacity derivation |
| Receipt-to-routed clock | 5 business days from batch open to brief routed; stops at routing. The clock starts when a document is admitted to a batch slot, not when it arrives. Documents held at Phase 1 for a missing required input, and documents above batch capacity waiting in queue, are excluded and reported as held or queued, not late. | Agents Orchestrator |
| Phase boundary | Day 1 intake; Days 2-3 clause review; Days 3-4 control review; Day 5 routing. A document crossing a boundary is escalated in the batch report, never silently carried. | Agents Orchestrator |
| Decision turnaround | 5 business days from routed brief to a recorded human decision. At 6 business days, the Chief of Staff records an escalation naming the signer. Measured across batches, never inside the batch that routed the brief — see Post-runbook. | Chief of Staff |
| DPA coverage | A personal-data flow is covered only by an executed DPA naming the current sub-processor list and transfer mechanism. A draft, an intent, or a link to the public policy is not coverage. | Data Protection Lead |

## Batch Capacity

The 5-day duration is a promise only against a document count. That count is derived from the review time each document consumes and the review time the batch actually has, so a batch that admits more than it can review cannot convert the clock into a lie.

| Quantity | Value | Where it comes from |
| --- | --- | --- |
| Review hours per agent per batch | 12 h | Two clause-review days (Days 2-3) at 6 effective hours per day; the other hours absorb decisions, queue, and escalation |
| Nine-family quotation per document | 4.0 h | Legal Document Review, one document end to end |
| Baseline comparison and materiality test per document | 3.0 h | Legal Compliance Checker |
| Flow map per document carrying personal data | 2.0 h | Privacy Engineer, inside the Days 3-4 window that also holds 12 h |
| Control artifact verification per document | 1.5 h | Compliance Auditor, same window |
| Brief authoring per document | 1.5 h | Document Generator, Day 5 at 6 h |
| Routing and obligation booking per document | 0.5 h | Chief of Staff, Day 5 at 6 h |
| Binding constraint | 3 documents | Lowest of: Legal Document Review 12 ÷ 4.0 = 3, Legal Compliance Checker 12 ÷ 3.0 = 4, Privacy Engineer 12 ÷ 2.0 = 6, Compliance Auditor 12 ÷ 1.5 = 8, Document Generator 6 ÷ 1.5 = 4, Chief of Staff 6 ÷ 0.5 = 12 |

**Capacity = 3 documents per batch.** Documents 4 and beyond hold a queue position, an arrival date, and the batch they will be admitted to. A queued document is never reported as late, never starts the receipt-to-routed clock, and is reported as queued in every batch close until admitted. Admitting a fourth document without a written change to this derivation is a G5 failure, not a review.

## Authority Matrix

No agent appears in this matrix, and no agent may. Every row names a human office; the individual's legal name is recorded in the register at G1 and in the decision line as `decision: <human name>, authority: <basis>, date: <date>`. **Business Sponsor of record: the Chief Commercial Officer** — the accountable commercial owner below A3 and the recommender at A3 and above, not an unnamed role.

| Tier | Annual contract value (USD) | Signer of record (human) | Co-signer required (human) | Authority basis |
| --- | --- | --- | --- | --- |
| A1 | under 50,000 | Business Sponsor — Chief Commercial Officer | none | Delegation of authority `AM-2`, Tier A1 |
| A2 | 50,000 to 250,000 | Business Sponsor — Chief Commercial Officer | Chief Financial Officer for price, payment, liability, or renewal terms | Delegation of authority `AM-2`, Tier A2 |
| A3 | above 250,000 to 1,000,000 | Chief Financial Officer | General Counsel | Delegation of authority `AM-2`, Tier A3 |
| A4 | above 1,000,000 or unlimited exposure | Chief Executive Officer | Chief Financial Officer and General Counsel | Board delegation, Tier A4 |

| Decision domain | Named human owner (and co-signer) |
| --- | --- |
| Indemnity direction and scope | Business Sponsor — Chief Commercial Officer at A1-A2; General Counsel at A3 and above |
| Liability cap multiple | General Counsel; Chief Financial Officer co-signs above A2 |
| IP assignment and licence-back | General Counsel |
| Personal data in scope, DPA mandatory, deviation from the template | Data Protection Lead; General Counsel where the transfer mechanism changes |
| Exclusivity | Business Sponsor — Chief Commercial Officer; Chief Executive Officer above A3 |
| Renewal inside the notice window — a budget commitment | Business Sponsor — Chief Commercial Officer as budget owner; Chief Financial Officer above A2 |
| Termination triggers and cure period | General Counsel |
| Governing law, forum, arbitration seat | General Counsel |
| Payment terms, withholding, gross-up, VAT | Chief Financial Officer |
| Materiality confirmation against the cited baseline | General Counsel, as the baseline's approving human |
| Control gap acceptance | General Counsel; Data Protection Lead where the gap touches personal data |

The Data Protection Lead is a named human office, deliberately distinct from the privacy agent on the roster: that agent records the scope finding, and records it only. Where a row above and a roster row share a subject, the roster row produces evidence and the matrix row decides.

## Tax and Cross-Border Boundary

This runbook does not assert a tax treatment. VAT, withholding, gross-up, and cross-border characterisation depend on the jurisdiction of each party, the entity assumption the document supports — which legal entity contracts, where it is resident, whether a treaty position applies — and the invoice mechanics the agreement creates. The Tax Strategist cites the governing rule, its jurisdiction, and the entity assumption it depends on, one row per position. The Chief Financial Officer, as a named human, decides, and the decision date is recorded against the citation. A position with no recorded decision stays flagged pending in the brief and is listed in the batch close; it is never filled in by inference.

## Agent Roster

Every row is answerable to a gate or a metric; a role with neither is not on this roster. No row is answerable to a decision: agents on this roster produce findings, flags, and cited evidence.

### Intake & Classification (Always Active)

| Agent | Role | Gate / metric it is answerable to |
| --- | --- | --- |
| Agents Orchestrator | Intake queue, one category per document, register row, batch and phase clock, capacity and queue position, carry-over list | G1 and the receipt-to-routed clock metric |
| Legal Client Intake | Counterparty legal name, sender authority, document lineage, deadline, sponsor, commercial intent in one sentence | G1: counterparty and lineage present before review opens |
| Data Privacy Officer | Scope finding only: whether personal data is in scope, whose, which jurisdictions, which DPA obligation follows; the determination is the Data Protection Lead's | G1 recorded personal-data finding; G3 DPA coverage; post-runbook DPA metric |

### Review (Per Document)

| Agent | Role | Gate / metric it is answerable to |
| --- | --- | --- |
| Legal Document Review | Quotes clause text per family, records baseline position and the delta | G2: nine families quoted or recorded absent |
| Legal Compliance Checker | Applies the `BL-3.1` material-deviation test and records a flag with its test result; it confirms no materiality and clears no document | G2 materiality flag with test result; baseline-version drift metric |
| Tax Strategist | One row per tax position: governing rule, jurisdiction, entity assumption, payment timing, withholding, gross-up, VAT, late-payment, invoice mechanics | G2 payment-terms row |

### Technical Control Review

| Agent | Role | Gate / metric it is answerable to |
| --- | --- | --- |
| Privacy Engineer | Data flows, retention, sub-processors, transfers, described versus implemented measures | G3: every flow mapped and covered |
| Compliance Auditor | Claimed controls verified against dated, scoped artifacts | G3: every claimed control has a covering artifact |

### Output & Sign Off

| Agent | Role | Gate / metric it is answerable to |
| --- | --- | --- |
| Document Generator | One structured brief per document: quotes, baseline deltas, control findings, open questions, the decision requested | G5: brief complete and routable |
| Chief of Staff | Owns the authority matrix, routes to the named human, records the human decision with its authority basis and date, books obligations, chases decision turnaround | G4 boundary, G5 routing, decision-turnaround and missed-notice-window metrics |

## Day 1: Intake & Classification

```text
├── Legal Client Intake → counterparty legal name, sender authority, document lineage as
│   a hash of the received file, deadline, sponsor, commercial intent in one sentence
├── Agents Orchestrator → admit to a batch slot if capacity remains, else record a queue
│   position and the arrival date; a queued document is reported as queued, never late
├── Data Privacy Officer → scope finding only: personal data in scope? whose, which
│   jurisdictions? recorded before review opens, because the answer selects the checklist
├── Agents Orchestrator → cite the `BL-3.1` version id with its approving human and approval
│   date, the `AM-2` tier and band, the named decision owner, and the `FORUM-1` version in the
│   register row; a missing baseline, an unapproved baseline, an unassigned owner, or an
│   unbanded value holds the document here, it does not open
├── Legal Document Review → hash and freeze the file; a re-sent file is a new version,
│   never an overwrite of the frozen one
├── Agents Orchestrator → one category, one register row, one named decision owner, clock started
└── Quality Gate (G1) fails if any admitted document lacks a category, a register row, a named
    decision owner with its `AM-2` tier and band, a frozen checksum, a cited baseline version
    with its approving human and approval date, or a recorded personal-data finding; and fails
    if any document above batch capacity lacks a queue position
```

| Document category | What it triggers |
| --- | --- |
| MSA | Full baseline review; governs every later order form |
| SOW | Scope, acceptance, change control, deliverable IP; must cite an MSA or open one |
| NDA | Direction, confidential-information scope, term, residuals |
| DPA | Sub-processors, breach window, audit rights, transfers, deletion |
| Vendor order form | Consumption floors, price escalation, incorporated terms by reference |
| License | Scope of use, seats, redistribution, audit clause |
| Renewal | Notice window and method, price change, termination rights |

## Day 2-3: Clause-Level Review

Nine families, quoted exactly or recorded as absent. Silence is absent, never acceptance. Every row names the agent that carries the evidence and the human who decides; an agent in the decision column is a G4 failure.

| Clause family | Risk it carries | Agent that carries the evidence | Evidence it must carry into the brief | What the human decides | Decision owner (named human from the authority matrix) |
| --- | --- | --- | --- | --- | --- |
| Indemnity | One-way defence cost, uncapped exposure | Legal Compliance Checker, on Legal Document Review's quotation | Direction, any carve-out for our data or IP, cited baseline position, delta | Whether the direction and scope are acceptable at this value, or the document is negotiated or declined | Business Sponsor — Chief Commercial Officer at A1-A2; General Counsel at A3 and above |
| Liability cap | Capping the loss that actually occurs: data, IP, confidentiality | Legal Compliance Checker | Quoted cap and every carve-out, the `BL-LIAB` multiple applied, the delta | Accept the multiple, negotiate it, or decline | General Counsel; Chief Financial Officer co-signs above A2 |
| IP assignment | Deliverables, improvements, or pre-existing IP vesting in the counterparty | Legal Compliance Checker | Quoted assignment, licence-back, pre-existing IP register match | Which pre-existing IP is excluded and whether a licence-back is enough | General Counsel |
| Data processing | Unlawful processing, unlisted sub-processors, undefined breach duty | Data Privacy Officer for the scope finding; Privacy Engineer for flows | Scope finding, flow map, retention, sub-processor and transfer coverage against the DPA template | Whether processing proceeds on the template or a named deviation is accepted | Data Protection Lead; General Counsel where the transfer mechanism changes |
| Exclusivity | Lost ability to serve others, given away unpriced | Legal Compliance Checker | Quoted scope, duration, territory, recorded commercial cost | Whether exclusivity is granted, and at what term or minimum | Business Sponsor — Chief Commercial Officer; Chief Executive Officer above A3 |
| Auto-renewal | An unbooked obligation renewing for a further term | Chief of Staff, on Legal Document Review's quotation | Quoted term, notice window, method; the booked window against the renewal calendar; renewal cost | Whether to renew at all and which notice method is used — a budget commitment | Business Sponsor — Chief Commercial Officer as budget owner; Chief Financial Officer above A2 |
| Termination | No exit for breach, or exit only at a penalty | Legal Compliance Checker | Quoted triggers, cure period, exit fees, baseline test | Whether exit terms stand or a cure period must be amended | General Counsel |
| Governing law and forum | Disputes decided in an unfamiliar forum at prohibitive cost | Legal Compliance Checker | Quoted law, forum, arbitration seat, `FORUM-1` comparison | Whether the venue is acceptable or counsel of record must be engaged | General Counsel |
| Payment terms | Withholding leakage, FX loss, cash exposure, gross-up disputes | Tax Strategist | Quoted timing, withholding, gross-up, VAT, late-payment and cross-border terms; per position the governing rule, its jurisdiction, and the entity assumption | Whether terms are accepted or amended before signature | Chief Financial Officer |

```text
├── Legal Document Review → every family above either quoted verbatim or recorded "absent";
│   an absent family keeps its row and is compared to the baseline default
├── Legal Document Review → baseline position and delta per family; a delta matching the
│   Material deviation definition is flagged, not weighed
├── Legal Compliance Checker → apply the `BL-3.1` test to each flag against the version cited at
│   G1 and record the test result; it issues no confirmation and no clearance
├── General Counsel (human) → confirm or reject each materiality flag; record
│   `decision: <human name>, authority: BL-3.1 approving human, date: <date>`; an unconfirmed
│   flag is routed as an open question naming the confirmation as outstanding, never dropped
├── Tax Strategist → one row per tax position: governing rule, jurisdiction, entity assumption,
│   payment timing, withholding, gross-up, VAT, late-payment, cross-border, invoice mechanics
├── Chief Financial Officer (human) → payment terms and every tax position decided, each with
│   its citation and decision date; an undecided position is marked pending, never assumed
└── Quality Gate (G2) fails if any of the nine families has neither a quotation nor an explicit
    "absent", any row lacks a baseline delta and a recorded test result, any materiality flag
    lacks a recorded human confirmation or a recorded open-question row naming that confirmation
    as outstanding, or any payment-terms row lacks a governing rule, a jurisdiction, or an
    entity assumption
```

## Day 3-4: Control & Data Review

```text
├── Privacy Engineer → collection, retention, sub-processors, cross-border transfer, and
│   whether the DPA matches what the terms say will happen
├── Privacy Engineer → security measures as described versus as implemented, gap by gap
├── Compliance Auditor → certificate scope, report period, exceptions, test dates;
│   unobtainable evidence is a finding, never compliance
├── Compliance Auditor → each claimed control tied to a dated, scoped artifact whose period
│   covers the term claimed in the agreement; the finding names the human owner from the
│   authority matrix who must decide whether the gap blocks signature
└── Quality Gate (G3) fails if any claimed control has no dated scoped artifact covering the
    term, any personal-data flow has neither an executed DPA nor a recorded escalation, or any
    control is asserted without an artifact id
```

## Day 5: Output & Routing

```text
├── Document Generator → one brief per document: category, quoted non-standard clauses with
│   baseline deltas, control findings, open questions for counsel, the decision requested,
│   the named decision owner and tier from the authority matrix
├── Document Generator → observed text separated from inference; no risk score presented as a
│   legal conclusion; an open question is written as a question, never as a verdict; a pending
│   human decision is listed as pending, never pre-filled
├── Chief of Staff → route to the named human in the authority matrix for that category and
│   tier; record `decision: <human name>, authority: <basis>, date: <date>`; start the
│   decision-turnaround clock for cross-batch measurement
├── Chief of Staff → book obligations: notice windows, reporting and audit duties, each with
│   an owner and a date
├── Agents Orchestrator → close the batch: documents routed, held, queued with position,
│   carried over, escalated
├── Quality Gate (G4) fails if any brief, register field, obligation row, or status value
│   records a contract as approved, executed, or legally cleared by an agent — or names any
│   approver, signer, or decision owner who is not a human listed in the authority matrix,
│   including any decision cell of the clause-family table above
└── Quality Gate (G5) fails if any brief is unrouted, any routed brief lacks a named owner and
    a route date, any obligation lacks an owner and a date, or any document above batch capacity
    is reported as late rather than queued with a queue position
```

### Boundary Enforcement

G4 is the reason this runbook can exist inside a process that signs things. It is decided by an observation, not a claim: read every produced artifact and search for a status or sentence attributing a contract decision to an agent, a model, or a pipeline, then read the clause-family table and confirm every decision cell names a human from the authority matrix. Decisions are recorded only as `decision: <human name>, authority: <basis>, date: <date>`. An agent-authored "approved" is a defect even when the underlying analysis was correct, because the record is what an auditor, a counterparty, and a court read.

## Key Decisions

Agents produce findings and flags. The decision, its authority, and its date are recorded against a named human; a decision attributed to an agent is a G4 failure, not a review.

| Decision Point | When | Finding produced by (agent) | Decision owner (named human) | Recorded as |
| --- | --- | --- | --- | --- |
| Intake category and named decision owner | Day 1 | Agents Orchestrator classifies from the category table and cites the `AM-2` tier | Whoever the tier names: Business Sponsor — Chief Commercial Officer at A1-A2, Chief Financial Officer at A3, Chief Executive Officer at A4 | register row: category, tier, named decision owner |
| Personal data in scope, DPA mandatory | Day 1 | Data Privacy Officer records the scope finding: which data, whose, which jurisdictions, which obligation follows | Data Protection Lead; General Counsel joins where the transfer mechanism changes | `decision: <human name>, authority: AM-2 Tier <tier>, date:`, citing the scope finding |
| Whether a deviation is material | Day 2-3 | Legal Document Review flags the delta; Legal Compliance Checker applies the `BL-3.1` test and records the result | General Counsel, as the baseline's approving human, confirms or rejects each flag | `decision:` line per flag, citing the test result and the baseline version |
| Whether a material deviation is business-acceptable | Day 2-3 | Legal Compliance Checker states the exposure and the delta in the brief | Business Sponsor — Chief Commercial Officer; General Counsel above A2 | `decision:` line with the tier and band cited |
| Control evidence sufficient or a gap | Day 3-4 | Compliance Auditor records findings with artifact ids, periods, and test dates | General Counsel decides whether a gap blocks signature; Data Protection Lead where the gap touches personal data | `decision:` line citing the artifact ids it rests on |
| Sign, negotiate, or decline | Day 5 | Document Generator writes the decision request with the options and the cited evidence | The signer of record for the tier and category: Business Sponsor — Chief Commercial Officer at A1-A2, Chief Financial Officer at A3, Chief Executive Officer at A4, with the co-signer `AM-2` requires | `decision: <human name>, authority: AM-2 Tier <tier>, date:` |
| Whether to renew inside the notice window | Day 5 | Chief of Staff books the window and states renewal cost, notice date, and method | The budget owner: Business Sponsor — Chief Commercial Officer; Chief Financial Officer above A2. A renewal is a budget commitment, so the Chief of Staff records it and never decides it | `decision:` line naming the budget owner and the booked window |
| Recording a contract as approved, executed, or legally cleared | Never by an agent | No finding: it is not a decision this runbook has | It is a G4 failure and a defect report to the Chief of Staff | defect report row naming the artifact and the agent |
| Baseline version changes mid-batch | Any day | Legal Compliance Checker reports the newer version and the families it moves | General Counsel, as the baseline's approving human, decides which version governs; the batch finishes on the version cited at G1 and the newer version opens a new batch | `decision:` line citing both version ids and the approval dates |

## Success Criteria

In-batch metrics only; anything with a longer window is in Post-runbook.

| Metric | Target |
| --- | --- |
| Documents with category, register row, named decision owner with tier, frozen checksum, cited baseline version with approving human and approval date, at G1 | 100% |
| Documents above batch capacity reported as queued with a queue position, none reported as late | 100% |
| Clause families quoted or explicitly recorded absent, with a baseline delta and a test result, per document | 9 of 9, 100% of documents |
| Material deviations with a recorded human confirmation or a recorded open-question row naming that confirmation as outstanding | 100% |
| Payment-terms rows citing a governing rule, a jurisdiction, an entity assumption, and a recorded human decision or a pending flag | 100% |
| Receipt to routed brief (held and queued documents excluded, reported separately) | ≤ 5 business days; ≥ 90% of routed documents; median ≤ 3 |
| Routed briefs with a named decision owner, a route date, and a written decision request | 100% |
| Clause-table decision cells naming a human in the authority matrix | 9 of 9; an agent in a decision cell fails the batch |
| Outputs recording a contract as approved, executed, or legally cleared by an agent | 0 |
| Obligations with an owner and a date | 100% |
| Claimed controls with a dated, scoped artifact covering the term | 100% |
| Documents held at intake for a missing required input, with the missing input named | 100% named |

## Post-runbook

These cannot be measured inside a 5-day batch. They are not batch gates; each has one owner and one measurement event, and a miss is reported to the same authority that signs contracts.

| Metric | Why the window exceeds the batch | Owner | Measured |
| --- | --- | --- | --- |
| Decision turnaround: routed briefs reaching a recorded human decision inside 5 business days, with escalations at 6 | A brief routed on Day 5 of a batch cannot have a decision observed by that same batch; the clock ends after the batch closes | Chief of Staff | Day 1 of the next batch, for every brief routed by the batch that closed 5 business days earlier; escalations listed by signer |
| Routed briefs still undecided with no escalation at 6 business days | Same clock, and it only exists once the batch that routed them has closed | Chief of Staff | Day 1 of the next batch, against the escalation log |
| Missed renewal or notice windows | The obligation ledger is only testable across a full quarter of dates | Chief of Staff | First business day after quarter close |
| Contracts with no named owner | Legacy agreements acquire owners by assignment, not by intake | Chief of Staff | Day 5 of each month |
| Personal-data agreements lacking an executed DPA | Execution follows the decision by weeks and cannot close in-batch | Data Protection Lead | Day 5 of each month |
| Renewal calendar coverage: active agreements with a booked notice window | Coverage grows as agreements execute, not as they arrive | Agents Orchestrator | Day 5 of each month |
| Register rows citing a superseded baseline version | Drift only appears after a baseline revision lands | Legal Compliance Checker | First business day after quarter close |
| Decisions recorded outside the signer's `AM-2` tier | The tiering error surfaces at signature, which follows the batch | Chief of Staff | Day 1 of the next batch, against the signed agreements list |

## Common Pitfalls

| Pitfall | Mitigation |
| --- | --- |
| A summary that hides the one clause that matters | The brief carries quoted text per family; the summary never replaces it |
| Silence on a clause treated as acceptance | Absent families recorded as absent and compared to the baseline default |
| An agent listed where a human decides | The clause table has a decision-owner column restricted to authority-matrix humans, and G4 fails any other name |
| Auto-renewal missed because the date lived in an inbox | Book notice windows, not end dates, each with an owner and a date |
| Renewal treated as an administrative note | A renewal is a budget commitment decided by the budget owner; the Chief of Staff books it and records the decision |
| DPA waived to unblock a purchase | The Day 1 data finding gates review; a waiver is a named-human decision on the record |
| Agent restating a legal conclusion as counsel's | Observed text, inference, and open questions stay separate; G4 fails an agent-recorded approval |
| Reviewing without the company's own baseline | G1 holds any document with no cited baseline version; Phase 2 cannot open |
| A baseline certified by the agent that later tests against it | The baseline arrives as an input with an approving human and an approval date, and G1 records both |
| Tax treatment carried over from the last similar contract | One row per position citing the governing rule, jurisdiction, and entity assumption; the Chief Financial Officer decides and the date is recorded |
| A batch sized by hope, not by arithmetic | Capacity is derived from review hours (3 documents per batch); everything above it is queued with a position and never reported as late |
| Register or clause summary treated as a prerequisite | Required Inputs admits only access, human decisions, chosen standards, and external artifacts |
| "Material" argued case by case until nothing is material | Materiality is the written definition; the flag is mechanical, the confirmation is a human decision with a date |
| A threshold nobody wrote down | Every gate number lives in Defined Thresholds, carries an artifact id, and is cited by version |
| A batch metric reported quarterly to look successful | Quarter-window and post-batch metrics live in Post-runbook with an owner and a measurement event, never in Success Criteria |
