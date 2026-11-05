# Runbook: Academic Research Program

Mode: NEXUS-Sprint | Duration: 6 weeks | Agents: 15

## Scenario

A funded programme has a question, a deadline, and a repository that cannot regenerate a single figure. Two researchers produce different numbers from the same dataset. A citation turns out to have been quoted from another paper's summary rather than from the paper itself. The analysis notebook runs on one laptop, in one directory, with one researcher's home directory baked into a path.

The output of this run is not a draft. It is an output that survives scrutiny: **every claim traceable to a source that was read, every figure regenerable from the repository, and every method decision recorded before the result was known.** A programme that produces an interesting number nobody can rebuild has produced an anecdote with a bibliography.

**Domain boundary.** Reproducibility is a gate, not an aspiration. An artefact that cannot be regenerated from the repository by someone who did not produce it is not a result. A citation verified against another citation is not verified. This runbook stops at the boundary of the evidence: it organises, verifies, and records; it does not produce knowledge that the sources do not support, and it does not grant ethics approval to anyone.

Scope is one funded question carried to one submission-ready output. Building the data substrate a longer programme will stand on is `data-platform-foundation`; deciding what to study in the first place is `feature-discovery-to-spec`.

## Applicability

| Use this runbook when | Use a different runbook when |
| --- | --- |
| A funded programme has one question, a deadline, and an output that must be publishable | The question is still being chosen and the audience is still unclear — use `feature-discovery-to-spec` |
| The result will be read by people who will try to reproduce it | The unit of work is a controlled comparison on a live product surface with a metric and a decision — use `growth-experiment-loop` |
| The repository must rebuild every figure from the raw sources on demand | The data substrate itself does not exist yet and ingestion, governance, and lineage are the work — use `data-platform-foundation` |
| An institution, funder, or ethics committee will audit the programme against its own conditions | The audit is an institutional control certification with external auditors and a control framework — use `compliance-certification-program` |
| The corpus, coding scheme, or survey data already has an access right and a custodian | The corpus is customer records and the constraint is privacy law rather than scholarly evidence — use `contract-and-legal-intake` |

Boundary: one run covers one question. A programme with two questions is two runs, or the second question is declared a separate output with its own freeze.

## Required Inputs

Only what the roster cannot produce. The dataset, the analysis, the manuscript, the source register, the method record, and the reproducibility pack are outputs of the run — listing them here would make the runbook its own prerequisite.

| Input | Why it blocks | Owner |
| --- | --- | --- |
| The funded question and its constraints: funder, deliverable, deadline, reporting obligations, and what the funder has already published about the award | A question invented in Week 1 is a different project with the same money | Principal Investigator |
| Ethics approval and its conditions, where any human subject, their data, or their materials are involved — with the committee reference, the approved protocol version, and every condition in the approval letter | Conditions in an approval are obligations, not advice; a run that discovers them at submission has already breached them | Named ethics committee (outside this roster) |
| Primary sources with access rights: archive or library permissions, database licences, data-use agreements, and the terms that govern quotation and redistribution | A source that cannot be read in full cannot be verified; a source whose licence forbids redistribution cannot be shipped in the repository | Principal Investigator with the custodian |
| The target venue's requirements: length, structure, style, reference format, data and code availability policy, reproducibility statement expectations, and the submission deadline with its timezone | Every verification target in Weeks 5-6 is defined by the venue, not by the team | Principal Investigator |
| A named principal investigator who signs the output and holds accountability for it | No agent may sign a scholarly claim or an ethics position; without a signature holder there is no output, only a draft | Principal Investigator |

## Agent Roster

15 agents. `Proven by` names the gate (G1-G3), Success Criteria row (S1-S6), or post-runbook measure (P1-P5) that fails without that agent.

### Command (Always Active)

| Agent | Role | Proven by |
| --- | --- | --- |
| Agents Orchestrator | Phase gating, the freeze at G1, the clean-room rerun at G2, and the signature-bound handover at G3; the only agent who declares a phase closed | G1, G2, G3 |
| Research Synthesist | Search protocol with boundaries written before screening, the source register, passage-level citation verification, and the honest statement of what the search did not find | G1, G3, S1, P3 |
| Senior Project Manager | Decision log, method-record freeze discipline, open-item ownership, authorship and contribution record | G1, S3 |

### Evidence & Method (Week 1-2)

| Agent | Role | Proven by |
| --- | --- | --- |
| Statistician | The method record: design, primary outcome, analysis plan, α, power, n, declared effect size, multiplicity handling, and the exploratory label on every post-freeze decision | G1, G3, S3, S6 |
| Psychologist | Construct validity per measure: instrument or coding scheme, its validity evidence, its known limits, and the claims it cannot carry | G1, S1 |
| Anthropologist | Contextual frame: what the source base can bear about the setting it describes, and which claims would need evidence the base does not hold | G1, S1 |

### Domain & Narrative (Week 3-5)

| Agent | Role | Proven by |
| --- | --- | --- |
| Historian | Passage-level source reading in period: consensus separated from active debate, and a secondary summary never cited in place of the work it summarises | G3, S1 |
| Geographer | Consistency of spatial and environmental variables: units, extent, period, and whether what the source claims about them holds together | G2, S1 |
| Narratologist | Manuscript argument map: the controlling claim, the claims supporting it, and the numbered result or citation behind each one | G3, S1, P1 |

### Production (Week 3-5)

| Agent | Role | Proven by |
| --- | --- | --- |
| Data Engineer | One-command pipeline from immutable raw copies to figures, pinned environment and lockfile, per-figure provenance and output hashes | G2, S2, P2 |
| Technical Writer | Manuscript assembled against the venue's requirements, with a data and code availability statement and reproduction instructions a stranger can run | G3, S2 |
| Analytics Reporter | Number table: every number in the draft resolves to a query and a script at a commit; second-analyst reconciliation of the primary result | G2, S4 |

### Proof (Week 5-6)

| Agent | Role | Proven by |
| --- | --- | --- |
| Evidence Collector | Clean-room rerun log, per-figure hash comparison, claim-to-source map, and the verification pack | G2, G3, P4 |
| Reality Checker | Per-criterion verdict PASS or NEEDS WORK, default NEEDS WORK, and the residual risk note | G3, S1 |
| Legal Compliance Checker | Prepares the ethics and data-handling position — consent conditions, anonymisation, retention and deletion, raw-data location, agreement obligations — for a named human to sign; **approves nothing and signs nothing** | G3, S5 |

## Thresholds

Every number a gate, criterion, or phase step cites is defined here once. A threshold that is not defined is an unfailable criterion.

| Threshold | Definition | Default value | Enforced at |
| --- | --- | --- | --- |
| Pre-registration deadline | The frozen method record is committed to the repository before the first outcome variable is computed over the primary dataset, and its commit hash is written into the decision log at that moment. A record committed after that run is a plan, not a pre-registration | Freeze at G1; the freeze commit timestamp precedes the repository's earliest analysis run over the primary dataset | G1, S3 |
| Reproducibility bar | A person who did not produce the analysis clones the tagged commit into a fresh environment built from the lockfile, on a machine that never held the working directory, runs one documented command, and every in-scope figure is byte-identical by hash | 100% of in-scope figures, 0 hash mismatches | G2, S2 |
| Citation verification coverage | A citation is verified when the full text of the cited work was read and the relied-upon passage located by page, section, or line range. A citation read only in another work's summary, abstract, or quotation is unverified, and the claim resting on it is unsupported | 100% of citations in the submitted manuscript; 0 verified against a summary | G3, S1 |
| Sample size and power | n per group computed and recorded before data collection from α, power, and the smallest effect worth caring about, all three declared in the method record. Where the sample is fixed by design or availability, achieved power at the declared effect is computed and reported instead | α = 0.05 two-sided, power = 0.80, declared effect recorded no later than the freeze | G1, G3 |
| Inconclusive rule | A confirmatory test whose achieved power to detect the declared effect is below the power threshold is reported as inconclusive at that effect size. It is not reported as a null result | Achieved power below 0.80 at the declared effect → inconclusive, never null | G3, S6 |
| Uncertainty reporting | Every reported estimate carries a 95% interval and its unit. A p-value alone is not a reported result | 100% of reported estimates carry an interval and a unit | G3, S6 |
| Method change classification | Any analysis decision taken after the first look at outcome data is written into the decision log with its date, its reason, and the label exploratory, and it cannot carry a confirmatory claim | 0 confirmatory claims resting on a post-freeze decision | G1, G3, S3 |
| Two-analyst agreement | A second analyst recomputes the primary result from the frozen inputs and the recorded analysis plan. A disagreement is resolved on the record with a reason, never by keeping the more convenient number | 0 unresolved disagreements at handover | G2, S4 |
| Source retrievability | Every source in the register has an identifier that resolves outside the project's own files — a DOI, ISBN, archive reference, or accession number — and a recorded access right permitting the read | 100% of registered sources; 1 unresolvable identifier fails G1 | G1, S1 |
| Retention and deletion | Human-subjects data is held for exactly the period written in the ethics approval and deleted on the date in that approval, with the deletion recorded | Deletion date from the approval; 0 records past it | G3, P5 |

### Ethics and privacy

No agent grants ethics approval. The Legal Compliance Checker assembles the position and the conditions evidence; a named human on the ethics committee or its delegated authority signs, and the signature is an input the roster cannot produce.

- **Consent.** Every participant's consent record names the study, the data collected, the uses permitted, the withdrawal route, and the date. A conditional consent is a row in the register with its evidence, not a footnote.
- **Anonymisation.** Direct identifiers are removed at ingest and replaced with study ids; the re-identification key lives in the approved location, never in the repository. Any human-subjects material quoted in the manuscript is checked for re-identification before submission.
- **Retention.** Raw human-subjects data is held for the approved period only and deleted on the approved date, with the deletion recorded.
- **Location.** Raw human-subjects data never leaves its approved location. Analysis runs against it in place or against a copy inside the approved environment; no raw record enters the repository, a shared drive, a chat tool, or a model prompt.

## Week 1-2: Question, Method & Source Base

```text
├── Week 1 — Question, method record, and the measurement frame
│   ├── Agents Orchestrator → run charter: the funded question in one sentence, the deadline,
│   │   the target venue, the named principal investigator, and the signature holder
│   ├── Statistician → method record: design, primary outcome, secondary outcomes, analysis
│   │   plan, α, power, the declared effect worth caring about, n, multiplicity handling, and
│   │   the pre-committed action for a positive, a null, and an inconclusive result
│   ├── Psychologist → measurement validity per construct: instrument or coding scheme, its
│   │   validity evidence, its known limits, and the claims it cannot carry
│   ├── Anthropologist → contextual frame: what the source base can bear about the setting it
│   │   describes, and which claims need evidence the base does not hold
│   └── Senior Project Manager → decision log opened; every method decision dated as it is made
├── Week 2 — Source base, access rights, and the freeze
│   ├── Research Synthesist → search executed against the written protocol: databases and
│   │   archives, date range, languages, inclusion and exclusion criteria; every exclusion
│   │   recorded with its reason
│   ├── Research Synthesist → source register: resolvable identifier, access right permitting
│   │   the read, the passage read, and whether the full text was read or only a summary
│   ├── Historian → first-pass source dating and provenance: who produced each source, for
│   │   whom, and in what frame
│   ├── Data Engineer → immutable copies of every readable source, checksummed, with a manifest
│   │   mapping identifier to path and a refusal to store anything the access right forbids
│   ├── Agents Orchestrator → freeze: commit the method record, write its hash into the decision
│   │   log, and confirm no outcome variable has been computed on the primary dataset
└── Quality Gate (G1): the freeze commit precedes the repository's earliest analysis run over
    the primary dataset, and every source in the register carries an identifier that resolves.
    One source whose identifier does not resolve fails the gate, and a method record committed
    after the first outcome computation is not a pre-registration.
```

## Week 3-4: Analysis & Reproducibility

```text
├── Week 3 — The analysis as a script, not a session
│   ├── Data Engineer → pipeline from immutable raw copies to derived tables to figures, run by
│   │   one documented command, with a pinned environment and a lockfile; no step that only
│   │   runs inside one notebook session or one home directory
│   ├── Data Engineer → per-figure provenance: input manifest, script path, environment hash,
│   │   and the figure's own output hash written beside it
│   ├── Statistician → analysis executed against the frozen record; every deviation written into
│   │   the decision log with its reason and its exploratory label at the moment it happens
│   ├── Historian → passage-level reading of each cited source in period, with consensus,
│   │   active debate, and speculation kept apart, and no secondary summary standing in for the
│   │   work it summarises
│   ├── Geographer → consistency of the spatial and environmental variables: units, extent,
│   │   period, and whether the claims made about them hold together
│   └── Analytics Reporter → number table: every number in the draft resolves to a query and a
│       script at a commit, not to a value typed from a console
├── Week 4 — Reproduction by someone who did not produce it
│   ├── Evidence Collector → clean-room rerun: clone at the tag, build the environment from the
│   │   lockfile on a machine that never held the working directory, run the one command
│   ├── Evidence Collector → hash comparison per figure, pass or fail per figure; an aggregate
│   │   "mostly reproduces" is not a result
│   ├── Analytics Reporter → two-analyst reconciliation: the second analyst recomputes the
│   │   primary result from the frozen inputs and the recorded plan
│   └── Statistician → ambiguity list: every point where the record needed an interpretation it
│       did not contain, returned to the decision log as exploratory
└── Quality Gate (G2): a person who did not produce the analysis regenerates every in-scope
    figure from a clean clone and every output hash matches. One figure that differs fails the
    gate; a rerun performed by the person who wrote the pipeline does not satisfy it.
```

## Week 5-6: Writing, Verification & Handover

```text
├── Week 5 — Argument, citations, uncertainty, and the ethics position
│   ├── Narratologist → manuscript argument map: the controlling claim, the claims supporting
│   │   it, and the numbered result or citation behind each; a claim with neither is cut
│   ├── Research Synthesist → citation verification: full text read, passage located by page,
│   │   section, or line range, and quoted from the work that contains it
│   ├── Research Synthesist → literature position: where the result agrees with, disagrees with,
│   │   or is silent against the evidence, each stated at its own weight
│   ├── Technical Writer → manuscript against the venue's requirements, plus the data and code
│   │   availability statement and reproduction instructions a stranger can execute
│   ├── Statistician → uncertainty pass: every estimate carries an interval and a unit, the
│   │   inconclusive rule is applied to underpowered tests, and exploratory findings are labelled
│   └── Legal Compliance Checker → ethics and data-handling position for signature: consent
│       conditions and their evidence, anonymisation applied, retention window, deletion date,
│       raw-data location, agreement obligations — prepared for a human, signed by none of us
├── Week 6 — Proof and handover
│   ├── Evidence Collector → verification pack: claim-to-source map, per-figure hashes, clean-room
│   │   log, ethics evidence, and the decision log
│   ├── Reality Checker → verdict PASS or NEEDS WORK per criterion, default NEEDS WORK, plus the
│   │   residual risk note with an owner on every open item
│   ├── Senior Project Manager → handover: tagged release, archived artefact with an identifier,
│   │   authorship and contribution record, and open items assigned by name
│   └── Agents Orchestrator → the named principal investigator signs the output; an unsigned
│       output is not delivered, whatever the verdict says
└── Quality Gate (G3): every claim in the submitted manuscript resolves to a numbered result
    regenerable at the tagged commit or to a citation verified against that work's own full text,
    and the ethics position carries a human signature. One claim that resolves to neither fails
    the gate, and a citation traced to another work's summary fails it as unverified.
```

## Key Decisions

| Decision point | When | Who decides | Recorded in |
| --- | --- | --- | --- |
| Confirmatory versus exploratory framing of the question | Week 1, before the freeze | Statistician with the principal investigator | Method record |
| The primary outcome and the design that can carry it | Week 1 | Statistician with the principal investigator | Method record |
| What a null, an inconclusive, and a positive result each mean for the programme | Week 1, before any result exists — the three actions written in advance, not after the number arrives | Principal investigator with the Statistician | Method record and decision log |
| Whether a source is citable, and at what weight | Continuously, closed at Week 5 | Research Synthesist, with the Historian or Anthropologist reading the domain claim | Source register |
| Authorship, contribution order, and who is accountable for which claim | Before submission; never renegotiated after a reviewer responds | Principal investigator | Contribution record |
| Where raw data lives and what may be published from it | Week 2, rechecked at handover | Legal Compliance Checker with the principal investigator | Data-handling position |

## Success Criteria

Rows are read top to bottom as S1-S6, and the roster's `Proven by` column cites them by that number.

| Metric | Target |
| --- | --- |
| Claims with a verified source | 100% of claims in the submitted manuscript resolve to a repository result or to a citation whose full text was read; 0 resolve to a summary-only source |
| Figures regenerable from the repository | 100% of in-scope figures reproduce byte-identical on a clean-environment rerun by a non-producer; 0 exceptions |
| Method decisions frozen before analysis | 100% of confirmatory decisions sit in the frozen record with a preceding hash; 0 confirmatory claims rest on a post-freeze decision |
| Peer reproductions succeeded | At least 2 of 2 independent attempts by people who did not produce the analysis, each inside the reproducibility bar |
| Ethics conditions met | 100% of the approval's conditions evidenced at handover; 0 open, 0 deferred to post-publication |
| Reported estimates carrying an interval | 100% of reported estimates, each with its unit and its interval |

## Common Pitfalls

| Pitfall | Mitigation |
| --- | --- |
| A citation quoted from another paper's summary — plausible, quotable, and about a claim the original never made | The Research Synthesist verifies against the cited work's own full text, locating the passage by page or section, and the source register records whether a full text or only a summary was read; G3 fails on a citation traced to a summary, against a 100% coverage target |
| A notebook that runs only on one machine, so "it works" means "it worked in that directory once" | The Data Engineer ships one documented command with a pinned environment and a lockfile in Week 3, and G2 requires a non-producer to rebuild every figure from a clean clone on a machine that never held the working directory |
| Hypotheses adjusted after seeing the data, then described as if they had been there from the start | The method record is committed and hashed at the G1 freeze before any outcome variable is computed, and the Statistician labels every post-freeze decision exploratory in the decision log at the moment it is made, against a target of zero confirmatory claims resting on one |
| A figure that cannot be regenerated, because the number was typed from a console or produced by an untracked step | The Analytics Reporter requires every number in the draft to resolve to a query and a script at a commit, the Data Engineer writes a hash beside each figure, and the Evidence Collector compares hashes per figure rather than in aggregate |
| Two researchers publishing different numbers from the same dataset, each certain the other made an error | The Analytics Reporter runs the second-analyst reconciliation from the frozen inputs and the recorded plan in Week 4, and a disagreement is resolved on the record with a reason rather than by keeping the convenient value |
| A result reported without its uncertainty, so a point estimate travels and the interval does not | The Statistician's Week 5 uncertainty pass requires an interval and a unit on every reported estimate, the inconclusive rule refuses a null claim from an underpowered test, and S6 measures it at 100% |

## Post-runbook

These measures close after the six weeks and are not scored at G3. Rows are read top to bottom as P1-P5, and the roster's `Proven by` column cites them by that number. The owner named here measures them on the date written, and the numbers change the next run's method record.

| Metric | Owner | Measured on |
| --- | --- | --- |
| First peer-review outcome: the decision and the claims reviewers challenged | Principal investigator | The venue's first decision letter |
| Third-party reproduction attempts: attempts recorded and attempts that succeeded | Data Engineer | 12 months after the archived artefact's identifier is issued |
| Citation uptake: independent works citing the archived output | Research Synthesist | 24 months after publication |
| Corrections issued: errata, expressions of concern, retractions, and data corrections traced to this output | Evidence Collector | 24 months, on each notice received |
| Retention and deletion executed: raw human-subjects data deleted on the approved date, with the confirmation recorded | Legal Compliance Checker | The deletion date written in the ethics approval |
