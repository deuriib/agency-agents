# Runbook: Clinical Evidence Review

> **Mode**: NEXUS-Micro | **Duration**: 5 days per review batch, recurring | **Agents**: 10

## Scenario

A clinical claim needs support, and the evidence assembled to support it is a slide deck nobody can trace. One study is quoted from its abstract, so the figure in the deck never appeared in the paper. Another was retracted eleven months ago and is still on slide six. A third is a preprint presented as peer-reviewed, and the trial's population — age band, line of therapy, exclusion profile, care setting — is not the population in the claim. The claim may still be true. Nobody in the room can say what it rests on, which is a different and more expensive problem.

This runbook assembles a cited evidence brief, states the strength of what it found, and routes every clinical judgement to a named clinician. It produces no recommendation of its own.

**Domain boundary. The agents on this roster assemble and cite evidence, classify it, and state its limits. They never issue a clinical recommendation, never diagnose, never advise a treatment, and never assert that a claim is clinically supported. A named clinician with authority makes every clinical determination and signs it. Nothing produced here is medical advice.**

The boundary is not modesty, it is the mechanism. An agent producing a cited, tiered, limit-stating brief removes work from a clinician. An agent issuing a determination creates a record that a regulator, a journal, a payer, and a patient will read as clinical advice, with no licence, no examination, and no accountability behind it. The determination exists in this runbook only as a `determination:` line against a named human — `<result>, clinician: <name>, credential: <credential>, authority: <basis>, date: <date>` — and an agent-written one is a defect, not a shortcut.

Two consequences run through the whole batch. First, **"insufficient evidence" is a valid result.** It is recorded, routed, and reported like any other, and it is frequently the honest answer. It is never a failure to be repaired by admitting a weaker source, widening a date window, or lowering a tier. Second, a source nobody read is not evidence. An abstract is a summary of a paper's claims, not a report of its findings, and treating it as the paper is the defect this runbook exists to catch.

## Applicability

| Use this runbook when | Use a different runbook when |
| --- | --- |
| A clinical or health claim needs a cited evidence base before it is published, submitted, or repeated | The agreement that carries the claim needs clause review — use `contract-and-legal-intake` |
| The evidence behind a deck, abstract, label, dossier, or product page exists but cannot be traced to a source | The subject is institutional controls and audit evidence rather than clinical literature — use `compliance-certification-program` |
| A regulator, journal, payer, or partner has challenged what the evidence actually shows | You are producing research rather than assessing published evidence — use `academic-research-program` |
| The strength of the support and the limits of it must be stated once, in writing, for a named clinician to rule on | The question is technical exposure in a system rather than in a claim — use `security-posture-review` |

## Required Inputs

Only what the roster cannot produce. The evidence brief, its appraisal, the evidence tiers, the population-mismatch flags, and the claim determinations are outputs — if they existed, this runbook would not be needed. A batch missing any row is held, not started.

| Input | Why it blocks | Owner |
| --- | --- | --- |
| The exact claim to be assessed, written verbatim, in the wording it is intended to carry, with the audience it targets | "Supports" and "contradicts" are answerable only against a fixed sentence; a paraphrased claim quietly becomes a different, easier claim and the appraisal then answers the wrong question | Claim owner (named human, recorded in the brief) |
| The population and indication the claim refers to, as a list of dimensions: indication, age band, line of therapy or disease stage, comorbidity and exclusion profile, care setting, geography | Population mismatch is undetectable unless the claim's own population is written down before retrieval opens; discovered afterwards, it is an argument | Claim owner |
| The jurisdiction whose regulatory standard governs, with the standard's name, version, and effective date | Evidence expectations differ by regulator; a comparison against an unnamed standard is an opinion and G2 cannot be attempted | Regulatory owner accountable to that regulator |
| A named clinician with authority to make the clinical determination: name, credential, scope of authority, and the determination being asked of them | A brief routed to nobody authoritative is a delay, not a review, and a determination attributed to a role without a name is not a determination | Medical Director or clinical governance owner |
| Read access to the source databases: biomedical literature index, trial registry, retraction and correction register, and the publisher records behind the full texts | A source that cannot be opened cannot be read at the primary source, and a source that cannot be read cannot be admitted to the batch | Agents Orchestrator, from the library or access owner |

Nothing this runbook produces may appear in this table. The brief, the tiers, the flags, and the determinations are Phase 1-3 output and are never a precondition for Phase 1-3.

## Agent Roster

10 agents. `Proven by` names the gate (G1-G3) or metric (M1-M6, Success Criteria) that fails without that row — a role answerable to nothing is not on this roster. No row is answerable to a determination: this roster produces findings, citations, tiers, and flags.

### Command (Always Active)

| Agent | Slug | Role | Proven by |
| --- | --- | --- | --- |
| Agents Orchestrator | agents-orchestrator | Batch admission against the derived capacity, claim freeze and claim id, screening-log reconciliation, route date, batch close | G1, M5 |
| Clinical Evidence Agent | healthcare-clinical-evidence-agent | Primary-source registration and retrieval, peer-review status, retraction and correction checks with their dates, integrity sweep | G1, G2, M2 |

### Evidence & Appraisal (Day 1-4)

| Agent | Slug | Role | Proven by |
| --- | --- | --- | --- |
| Healthcare Innovation Strategist | healthcare-innovation-strategist | The claim restated as testable sub-claims, population reconciliation per dimension, and the wording options handed to the clinician and claim owner | G1, G2, M3 |
| Research Synthesist | research-synthesist | Search protocol, extraction from the full text only, evidence tier with its reason, limits section, conflicting-study resolution proposal | G2, M1 |
| Data Privacy Officer | data-privacy-officer | Scope finding only: whether a source carries patient-level or supplementary data, whose, under which jurisdiction; the determination follows | G1 |

### Governance (Day 2-5)

| Agent | Slug | Role | Proven by |
| --- | --- | --- | --- |
| Legal Compliance Checker | support-legal-compliance-checker | Admissibility determination against Thresholds, preprint-versus-peer-review classification, citation-traceability audit | G1, G2 |
| Sovereign Health Systems Agent | healthcare-sovereign-health-systems-agent | The governing regulatory standard's evidence expectation, cited by document and version, compared with what the batch actually holds | G2 |
| Privacy Engineer | engineering-privacy-engineer | Linkage and re-identification exposure of any patient-level or supplementary dataset the claim relies on, recorded as a limit | G2 |

### Proof (Day 5)

| Agent | Slug | Role | Proven by |
| --- | --- | --- | --- |
| Evidence Collector | testing-evidence-collector | Brief assembly, one dated artifact per quoted passage with its location at the primary source | G3, M1 |
| Reality Checker | testing-reality-checker | Verdict on the brief (default: NEEDS WORK), sampled readback of quoted figures at the primary source | G3, M4 |

## Thresholds

Every number and classification a gate cites is defined here once. A gate citing an undefined threshold cannot fail.

| Threshold | Definition | Set by |
| --- | --- | --- |
| Frozen claim | The claim text as supplied, recorded character-for-character at G1 with a claim id, its population dimensions, and its intended audience. A later wording change is a new claim and a new admission; it is never an edit to a frozen one | Claim owner; recorded by Agents Orchestrator at G1 |
| Admissible source | All of: peer-review status confirmed on the publisher's own record (not on an aggregator's badge); a retraction and correction check recorded with its date; publication inside the date window; a population reported in enough detail to compare; and the full text obtained and read. One missing element makes the source inadmissible, and an inadmissible source is never cited as support | Legal Compliance Checker, applying this table |
| Peer-review status | Exactly one of: `peer reviewed`; `peer reviewed with expression of concern, erratum, or correction` (with the notice cited); `not peer reviewed` — covering preprints, conference abstracts, theses, internal reports, and company materials. A `not peer reviewed` source may appear in the brief only with that label attached and may not be the sole support for a claim | Legal Compliance Checker |
| Retraction check | A query of the retraction and correction register plus the publisher's record for that specific source, recorded as `checked: <date>` plus one of `none`, `retracted`, `corrected`, `expression of concern`. A check older than 30 calendar days at the moment the brief is routed is re-run before routing, and the re-run date is the one recorded | Clinical Evidence Agent |
| Publication date window | Interventional support: published within 10 years of batch open. A claim about current practice, prevalence, or standard of care: within 5 years. Older work is admissible only where the claim explicitly concerns historical evidence, or where the source is the pivotal study the governing regulatory standard names — either way the reason is recorded next to the source row | Research Synthesist; Legal Compliance Checker confirms admissibility |
| Primary-source reading rule | Every citation is read at the primary source, and every quoted figure is located in that source's own text, with the page or section recorded. Quoting a study from its abstract is a defect. Quoting it from another review's summary is a defect. Neither is a lesser form of reading; both fail G2 on one observation | Research Synthesist; audited by Legal Compliance Checker |
| Evidence tier (E1-E4) | `E1`: systematic review or meta-analysis of randomised trials, or a single adequately powered randomised trial, assessed at primary source. `E2`: controlled trial without randomisation, or a prospective cohort with a stated comparator. `E3`: observational study, registry analysis, case series, or modelling study. `E4`: narrative review, expert opinion, conference abstract, preprint, or regulatory narrative. Animal and in-vitro work is out of scope for a human clinical claim and is recorded as `not applicable`, never as a low tier. Each row carries the reason for its tier | Research Synthesist; the tier is a classification, never a recommendation |
| Population match dimensions | Six dimensions, each compared between the claim and the source's stated eligibility criteria: indication; age band; line of therapy or disease stage; comorbidity and exclusion profile; care setting; geography. A difference in any single dimension is a population mismatch and is flagged per dimension. Mismatches across several sources are never averaged into a general statement of applicability | Healthcare Innovation Strategist |
| Determination set | Per claim, exactly one of `supports`, `contradicts`, `does not address`, `insufficient evidence`. The first three require a quoted passage from an admissible source. `insufficient evidence` is recorded where no admissible source addresses the claim, or where admissible sources conflict and no resolution is defensible at the tier they hold. The agent records the determination of the evidence; the clinician makes the clinical determination | Agents Orchestrator records; the clinician signs |
| Conflicting evidence | Two admissible sources that point different ways are both carried, both tiered, and the conflict is stated in the brief with the reason it is unresolved — differing populations, differing endpoints, differing comparators, or publication bias. A conflict is never resolved by dropping the less convenient source, and never by citing the higher-tier one alone as if the other did not exist | Research Synthesist proposes; the clinician decides |
| Batch capacity | 8 studies per evidence brief, derived in Batch Capacity below. A batch that admits more cannot convert the 5-day duration into a promise, so studies above capacity hold a queue position and are reported as queued | Agents Orchestrator, from the derivation |
| Review-batch clock | 5 business days from batch open to brief routed, stopping at routing. The clock starts when a study is admitted to a batch slot, not when it is identified. Studies held at G1 for a missing required input, and studies above capacity in queue, are excluded and reported as held or queued — not late | Agents Orchestrator |
| Phase boundary | Day 1-2 question and retrieval; Day 3-4 appraisal and verification; Day 5 brief and routing. A study crossing a boundary is escalated in the batch close, never silently carried | Agents Orchestrator |
| Clinician turnaround | 5 business days from a routed brief to a signed determination. At 6 business days the Agents Orchestrator records an escalation naming the clinician and the determination outstanding. Measured across batches, never inside the batch that routed the brief — see Post-runbook | Medical Director; measured by Agents Orchestrator |

### Batch Capacity

The 5-day duration is a promise only against a study count. That count is derived from the appraisal time each study consumes and the appraisal time the batch actually has.

| Quantity | Value | Where it comes from |
| --- | --- | --- |
| Review hours per agent per batch | 12 h | Days 1-4 at 6 effective hours per day; Day 5 holds 6 h for brief work |
| Primary-source retrieval, registration, retraction check | 0.5 h/study | Clinical Evidence Agent, 12 ÷ 0.5 = 24 studies |
| Full-text appraisal, extraction, evidence tier | 1.5 h/study | Research Synthesist, 12 ÷ 1.5 = 8 studies |
| Claim decomposition and population reconciliation | 1.0 h/study | Healthcare Innovation Strategist, 12 ÷ 1.0 = 12 studies |
| Data-classification scope finding | 0.75 h/study | Data Privacy Officer, 12 ÷ 0.75 = 16 studies |
| Admissibility and integrity verification | 0.75 h/study | Legal Compliance Checker at 11 h (Day 2-5), 11 ÷ 0.75 = 14 studies |
| Regulatory-standard comparison | 1.0 h/study | Sovereign Health Systems Agent, 12 ÷ 1.0 = 12 studies |
| Linkage and re-identification exposure check | 0.5 h/study | Privacy Engineer, 12 ÷ 0.5 = 24 studies |
| Brief assembly and citation artifacts | 0.5 h/study | Evidence Collector at 6 h, 6 ÷ 0.5 = 12 studies |
| Batch verification pass | 4 h per batch, flat | Reality Checker at 6 h, 6 ÷ 4 = 1 batch; it constrains the batch, not the per-study arrival rate |
| Binding constraint | **8 studies** | Lowest per-study limit: Research Synthesist 12 ÷ 1.5 = 8 |

**Capacity = 8 studies per evidence brief.** Study 9 and beyond hold a queue position, an identification date, and the batch they will be admitted to. A queued study is never reported as late, never starts the review clock, and appears as queued in every batch close until admitted. Admitting a ninth study without a written change to this derivation is a G1 failure, not a review.

**Source-verification rule.** Every citation in the brief is read at the primary source, and a retraction check is recorded with its date. Quoting a study from its abstract, or from another review's summary, is a defect that fails G2 — as is a source row whose retraction check has no date, because undated is indistinguishable from not done.

## Day 1-2: Question & Source Retrieval

Retrieval is not search. Search returns hits; retrieval returns a frozen question, a reproducible protocol, and a register of sources that were actually opened.

```text
├── Agents Orchestrator → freeze the claim verbatim with a claim id, its six population
│   dimensions, the governing jurisdiction, and the named clinician; admit the batch if a
│   capacity slot remains, else record a queue position and the batch it will enter
├── Healthcare Innovation Strategist → restate what the claim asserts and what would have to
│   be true for it to hold, as testable sub-claims; wording that cannot be tested returns to
│   the claim owner before the first query, not after the appraisal
├── Research Synthesist → search protocol frozen before the first query: databases, exact
│   strings, date window, inclusion and exclusion criteria, recorded with the run date and
│   per-database hit counts; a search whose protocol is written afterwards is not reproducible
├── Clinical Evidence Agent → register every candidate source with an identifier (PMID, DOI,
│   trial registry number, or report number) and obtain the full text; a source whose full
│   text cannot be obtained stays on the register as unobtained, never as reviewed
├── Clinical Evidence Agent → retraction and correction check per source against the
│   retraction register and the publisher's record, recorded with its check date
├── Data Privacy Officer → scope finding only: does the source carry patient-level or
│   supplementary data, whose data, under which jurisdiction; the determination is the
│   clinician's, this row produces the finding
├── Legal Compliance Checker → admissibility determination per source against Thresholds:
│   peer-review status, dated retraction check, date window, population reported, full text
│   obtained; it records the result and decides nothing clinical
├── Agents Orchestrator → screening log reconciled against the hit counts: every screened
│   source, its inclusion or exclusion reason, and the arithmetic that closes the gap
└── Quality Gate (G1): fails if one source row in the batch lacks an identifier, an obtained
    full text, a recorded peer-review status, a dated retraction check, or a recorded
    admissibility result — if the frozen claim text differs from the claim as supplied — or if
    a ninth study was admitted without a written change to the Batch Capacity derivation
```

## Day 3-4: Appraisal & Verification

Appraisal is reading the paper, not the paper's own summary of itself. Every quoted figure has a location; every classification has a reason written next to it.

```text
├── Research Synthesist → extraction from the full text only: design, sample size, eligibility
│   criteria as stated, comparator, endpoints with their definitions, effect size with its
│   interval, and the limitations the authors themselves state; page or section recorded per
│   extracted figure
├── Research Synthesist → evidence tier per source against E1-E4, with the reason the tier was
│   assigned written in the row; a tier with no reason is an opinion with a label on it
├── Clinical Evidence Agent → second retraction check at appraisal, plus erratum, correction,
│   and expression-of-concern lookup on the publisher's record, each dated; a source that
│   changed status between G1 and appraisal is escalated in the batch close
├── Healthcare Innovation Strategist → population reconciliation across the six dimensions
│   against the claim population frozen at G1, flagged per dimension and per source; a source
│   whose eligibility criteria cannot be compared is recorded as not comparable, not as matching
├── Sovereign Health Systems Agent → what the governing standard, cited by document and
│   version, expects as evidence for this class of claim, compared line by line with what the
│   batch holds; it records the comparison and asserts no compliance and no approval
├── Privacy Engineer → linkage and re-identification exposure of any patient-level or
│   supplementary dataset the claim depends on, recorded as a limit on what the evidence can
│   carry rather than as a blocker on its own
├── Legal Compliance Checker → integrity sweep: a preprint, conference abstract, thesis, or
│   company report presented as peer reviewed; a quoted passage that does not appear at the
│   cited location; a citation that traces only to another review's summary; a source cited
│   for a claim its design cannot answer
├── Reality Checker → sampled readback: re-verify the quoted figure at the primary source on a
│   systematic sample of source rows; one miss returns the row to the Research Synthesist and
│   the sample is redrawn after correction
└── Quality Gate (G2): fails on a single observation of an abstract-only quotation, a quotation
    traced to another review's summary, a source with no dated retraction check, an unclassified
    preprint, an ungraded source, an unflagged population dimension, or a regulatory comparison
    with no document and version cited
```

## Day 5: Brief & Clinical Routing

The brief is the deliverable, and its job is to be read once by a clinician who can then decide. It states what the evidence does, what it does not, and what the batch could not determine.

| Determination | What it means in the brief | Who may write it |
| --- | --- | --- |
| `supports` | An admissible source, quoted at its location, addresses this claim and points in its direction | Agent, against the quoted passage |
| `contradicts` | An admissible source, quoted at its location, addresses this claim and points against it | Agent, against the quoted passage |
| `does not address` | The batch holds no admissible source whose design or population can answer this claim | Agent, naming what was searched |
| `insufficient evidence` | Admissible sources exist but do not settle the claim, or none exist; the brief says so, names the gap, and stops | Agent — a recorded result, not a failure |

```text
├── Evidence Collector → one brief per batch: per claim and sub-claim the determination, the
│   source identifier, the exact quoted text, the location at the primary source where it
│   sits, the evidence tier, the population mismatches, and the limits
├── Evidence Collector → one dated citation artifact per quoted passage, retained so a later
│   reader can re-read the passage without redoing the search
├── Research Synthesist → limits section: what the evidence does not cover, which populations
│   are unrepresented in it, where the tier is too low to carry weight, and which sub-claims
│   came back as insufficient evidence
├── Healthcare Innovation Strategist → the claim wording as assessed next to wording the
│   evidence could carry, presented as options for the clinician and the claim owner; an agent
│   never applies the edit
├── Reality Checker → verdict on the brief (default: NEEDS WORK): every citation resolves at
│   the primary source, every determination matches a quoted passage, every mismatch is
│   flagged, every brief names a clinician with authority
├── Agents Orchestrator → route the brief to the named clinician and record the route date;
│   close the batch as routed, held, queued with position, carried over, or escalated
└── Quality Gate (G3): fails if one artifact in the batch records a clinical recommendation, a
    diagnosis, a treatment suggestion, or a statement that a claim is clinically supported — if
    any approving or determining authority named is not the clinician of record — if any claim
    in the brief carries no determination — or if any brief lacks a named clinician and a route
    date
```

### Boundary Enforcement

G3 is decided by an observation, not by a claim. Read every produced artifact and search for recommendation verbs — recommend, should be used, indicated for, first-line, approved for, safe and effective, clinically supported — then confirm each of those sentences belongs to a clinician's signed determination and to nothing else. Read the determination column of the brief and confirm it describes the evidence, never the patient. Then read the routing block and confirm the named authority is the clinician recorded in Required Inputs.

An agent-authored determination is a defect even when the underlying appraisal is correct, because the artifact is what a regulator, a journal, a partner, and a court will read. The appraisal is the work; the determination is the signature; they are not the same act and must never share an author.

## Key Decisions

Agents produce citations, tiers, flags, and determinations of the evidence. Every clinical decision belongs to the named clinician, recorded with its authority and date.

| Decision Point | When | Finding produced by (agent) | Decision owner (named human) | Recorded as |
| --- | --- | --- | --- | --- |
| Whether a source is admissible | Day 1-2, re-checked Day 3-4 | Legal Compliance Checker applies the admissibility definition and records pass or fail with the element that failed | The named clinician, where admissibility is contested or where a source below E1 is proposed as sole support | source row: admissibility result, the element that failed, and where contested a `determination:` line naming the clinician |
| How conflicting studies are handled | Day 3-4 | Research Synthesist carries both sources, both tiers, and the stated reason the conflict is unresolved | The named clinician decides which side, if either, the clinical determination rests on; the conflict stays visible in the brief either way | `determination:` line naming both source identifiers and the clinician's basis |
| What to do when the populations do not match | Day 3-4 | Healthcare Innovation Strategist flags each dimension and states which direction the mismatch pushes the finding | The named clinician decides whether the claim's population is still addressed; the claim owner decides whether the claim is narrowed | `determination:` line citing the flagged dimensions |
| Whether the claim must be reworded before review | Day 1-2, revisited Day 5 | Healthcare Innovation Strategist states the wording as assessed and the wording the evidence could carry, as options with the gap named | The claim owner decides the wording; the clinician confirms the evidence answer holds for the new wording. A rewording that changes the population or the indication is a new claim and a new batch | `determination:` line naming the claim id and the wording version assessed |
| Whether the evidence supports the claim as a clinical matter | Day 5, after routing | No agent finding: the brief carries determinations of the evidence, tiers, mismatches, and limits, and stops there | The named clinician with authority, who signs | `determination: <result>, clinician: <name>, credential: <credential>, authority: <basis>, date: <date>`, where `<result>` is one of the four values in the determination set |
| What happens when a cited source is retracted after the brief shipped | Any time, outside the batch | Clinical Evidence Agent records the new status, its date, and the claims that relied on the source | The named clinician decides whether the signed determination still stands; Agents Orchestrator records the recall or the confirmation | `recall:` or `confirmation:` line naming the source, the affected claims, the clinician, and the date |

## Success Criteria

In-batch metrics only. Anything with a longer window sits in Post-runbook.

| Metric | Target |
| --- | --- |
| M1 — Claims carrying at least one primary-source citation read at the full text, with a recorded location for the quoted passage | 100%; a quotation located only in an abstract counts as zero |
| M2 — Studies with a recorded retraction check and its date, re-run where the check was older than 30 days at routing | 100% |
| M3 — Population mismatch dimensions flagged per source, against the six dimensions frozen at G1 | 100% of comparable sources; a source whose criteria cannot be compared is recorded as not comparable |
| M4 — Briefs routed to a named clinician with authority, with a route date and a written determination request | 100% |
| M5 — Studies above the derived capacity of 8 reported as queued with a queue position, none reported as late | 100% |
| M6 — Outputs recording a clinical recommendation, a diagnosis, a treatment suggestion, or a statement that a claim is clinically supported by an agent | 0 |

## Common Pitfalls

| Pitfall | Mitigation |
| --- | --- |
| Quoting an abstract instead of the study, so the figure in the brief never appears in the paper | Every quoted passage carries a page or section located in the full text; G2 fails on one abstract-only quotation, and the appraiser has no access path that returns only abstracts |
| Citing a retracted paper because nobody checked | A dated retraction check is a required field on every source row, re-run when older than 30 days at routing, and an undated check is treated as not done |
| A preprint presented as peer-reviewed, because an aggregator's listing looked like a journal record | Peer-review status is read on the publisher's own record and classified into exactly three values; a `not peer reviewed` source carries the label in the brief and cannot be sole support |
| A population mismatch glossed over because the study "broadly" covers the indication | Reconciliation runs across six named dimensions, flagged per dimension; "broadly" is not a comparison, and an incomparable source is recorded as not comparable rather than as matching |
| An agent writing a recommendation because the brief looked complete | G3 fails any artifact carrying a recommendation verb outside a clinician's signed determination; the brief's determination column describes the evidence and stops there |
| "Insufficient evidence" treated as a failure to be fixed by lowering the bar | It is a recorded, routable result with a named gap; the date window, admissibility definition, and tier definitions are fixed before the batch opens and are not adjustable inside it — a bar moved to reach an answer is a G2 failure with the moved threshold named |

## Post-runbook

These cannot be measured inside a 5-day batch. They are not batch gates; each has one owner and one measurement event, and a miss is reported to the same authority the brief routes to.

| Metric | Owner | Measured on |
| --- | --- | --- |
| Clinician turnaround: routed briefs reaching a signed determination inside 5 business days, with escalations recorded at 6 | Agents Orchestrator, escalating to the Medical Director | Day 1 of the next batch, for every brief routed by the batch that closed 5 business days earlier; escalations listed by clinician |
| Claims revised after review, by classification: narrowed, requalified, withdrawn, or retained unchanged | Claim owner, from the brief's wording options | Day 5 of each month, against the claim register |
| Later retractions, corrections, or expressions of concern affecting a shipped brief, and whether a recall or a confirmation was recorded for each | Clinical Evidence Agent | Day 1 of each month, re-checking every source cited in briefs shipped in the trailing 24 months |
| Signed determinations that contradict the evidence determinations in the brief they were routed with, and the stated basis for each | Medical Director | First business day after quarter close |
| Shipped claims whose governing regulatory standard has changed version since the brief was routed | Regulatory owner | First business day after quarter close |
