# Runbook: Customer Support Operations

Mode: NEXUS-Sprint | Duration: 4-6 weeks | Agents: 15

## Scenario

Support works and nobody can prove it. Ticket volume grows with the customer base, the same five questions consume most of the queue, every reply is written from scratch, and the product team learns about recurring breakage from a frustrated customer instead of from the ticket data it already had.

This runbook installs the operating system of a support function: triage, macros and knowledge that actually deflect, a measurement that is not "time to first reply", and a feedback loop that turns repeat tickets into product work. The doctrine is one sentence: **a support metric that can be improved by closing tickets faster is measuring the wrong thing.** Every speed number produced here is reported beside an outcome number — repeat-contact rate or graded resolution quality — and a desk that improves its speed while those two stand still has changed nothing except how quickly it disappoints people.

Scope is the support surface and its feedback loop. It is not a product redesign, a live outage, or a defect backlog.

## Applicability

| Use this runbook when | Use a different runbook when |
| --- | --- |
| Support volume, response times, and repeat questions are unowned and unmeasured | Production is broken right now — use `incident-response` |
| Every reply is written from scratch and nothing is documented | The complaint is a defect backlog with disputed priority — use `bug-triage-and-defect-elimination` |
| The help center exists but nobody can show it prevents tickets | Product work must be turned into a spec before anyone builds it — use `feature-discovery-to-spec` |
| Recurring tickets never reach the product team as evidence | The customer of support is another engineering team — use `developer-experience-platform` |
| Support is being built or rebuilt from zero operating rules | A program is failing and needs delivery triage, not queue triage — use `delivery-recovery` |

A ticket that matches P0 on the severity mapping below — service completely down, data loss, or a security breach — leaves this runbook immediately and runs as an incident; the queue work resumes once the incident is contained.

## Required Inputs

Five inputs, and nothing else. Every other artifact this runbook relies on is produced by the roster and passes a gate.

| Input | Why it blocks | Owner |
| --- | --- | --- |
| Export access to the ticket system with at least 90 days of history: threads, tags, close timestamps, account identifiers, channel | Cluster counts, the repeat-contact baseline, and recontact pairs are computed from one retained extract; a 30-day window cannot show a repeat cycle or a seasonal cluster | Studio Operations |
| The response-time commitments as currently published to customers: first response, resolution, support hours, supported channels | The desk is measured against the promise customers already have in writing, not against a target invented in week 1 | Studio Operations |
| The product's known-issue list, with dates and affected surfaces | Reconciling clusters against this list is how a stale known-issue entry is caught; without it, week 2 compares tickets against memory | Product Manager |
| Brand and tone guidance: voice, banned phrases, escalation language, and what may not be promised | Macro and article text is machine-written; without the guidance it either reads like a robot or promises something the product cannot keep | Support Responder |
| A named owner of the help center with publish rights | Articles, redirects, and the "did this solve it" control cannot ship by proxy; an unnamed owner means the surface decays the week after handoff | Technical Writer |

Triage rules, the intent taxonomy, the macro library, the self-serve surface, and the feedback digest are **outputs** of this run, not inputs. If a predecessor already produced one, it is graded by the same gates as everything built here — inherited artifacts get no exemption for age.

## Thresholds

Every number this runbook references, defined once. A gate or metric that cites a term below uses this definition, not a local reading.

| Term | Definition | Where checked |
| --- | --- | --- |
| Measurement window | The 90 calendar days ending on day 0, the run's start date. Every cluster count prints its query, its window, and its ticket count beside it. A count without all three is not a count. It ends before the run builds anything, so it never measures an artifact this run produced: it is the clustering, scoping, and baseline window, and the only metric that reports against it is M6. | G1, M6 |
| Cluster | A set of tickets sharing one symptom, expressed as what the customer could not do. Two clusters that share a word but not a symptom stay separate. | G1 |
| In-scope cluster | A cluster meeting either test: ≥ 25 tickets in the measurement window, or ≥ 3% of the window's total volume. The in-scope set is the five highest-volume clusters among them: the run scopes five, G1 prints all five with their ticket count, query, and window, and every cluster outside the five is named as out of scope at G1 rather than left implied. | G1, G3, M4, M5 |
| Article set | The five clusters of the in-scope set plus every cluster at or above the handoff threshold that is not among them, evaluated once on the measurement window. G1 prints the set, its members, and its count **N**, and week 3 writes exactly N articles and N macros in volume order. The size is N, printed before the work starts, not a fixed ambition: the five in-scope clusters come first and a burst cluster joins the queue behind them. A cluster inside the set that ships no article fails M5. | G1, G2, G3, M5 |
| Support severity | The P0-P3 classification from `incident-response`, applied unchanged to a ticket, with that runbook's wording and response times quoted rather than paraphrased. P0 — Critical: "Service completely down, data loss, security breach", response "Immediate (all hands)". P1 — High: "Major feature broken, significant performance degradation", response "< 1 hour". P2 — Medium: "Minor feature broken, workaround available", response "< 4 hours". P3 — Low: "Cosmetic issue, minor inconvenience", response "Next sprint". This runbook defines no severity scale of its own, drops nothing from that scale, and adds nothing to it. | G1, escalation trigger |
| Repeat contact (recontact) | A new ticket from the same account about the same cluster within 14 days of a ticket on that cluster being marked resolved, on a different thread. Same account writing about a different cluster is not a recontact. Repeat-contact rate = recontacts ÷ tickets resolved on that cluster inside the same window, both terms counted on the final cohort. | G1, M2, M3 |
| Resolution graded `2` | The closing reply states what changed, what the customer does next, and what is happening about the cause, and the customer would not have to write back. `1` = correct but the customer has to write back for a step. `0` = wrong, partial, or a link that does not contain the answer it is cited for. Quality score = share of the sample graded `2`. | G2, G5, M3 |
| First response | The first reply written by a person, inside the published support hours of the channel the ticket arrived on. An auto-acknowledgement is not a first response. | M1 |
| Fast-and-right | A ticket answered inside the published first-response commitment that produces no recontact within the 14-day lookback. A close that comes back scores zero in this measure, which is the point of the measure. | M1 |
| Run exit | The last day of the run: day 28 of a four-week run, day 42 of a six-week run. Every window below ends at run exit unless it says otherwise. | M1, M2, M3, M4, M5, M6 |
| Final cohort (the M1/M2 cohort) | The tickets closed on the last 14 days of the run — days 15-28 of a four-week run, days 29-42 of a six-week one — read at run exit + 14 days, when every ticket in the cohort has carried its full 14-day recontact lookback. M1 and M2 are computed on this identical cohort. A closing ticket whose lookback has not expired is not in the cohort and appears in no ratio, so a ticket closed on the last day never inflates M1 or deflates M2; the cohort is read 14 days late for exactly that reason. | M1, M2 |
| Readout date | The day a metric is read: run exit + 14 days for M1 and M2, run exit for M3, M4, M5, and M6. A metric read on any other date is a draft and does not pass its gate. The exit + 14 days read is owned by the Analytics Reporter, who publishes M1 and M2 together and hands the pair to the run's owner; a run that ends without that readout has not closed its success criteria. | M1, M2, M3, M4, M5, M6 |
| Week 1 baseline | The repeat-contact rate measured with the same arithmetic as M2, not a number pulled from a different denominator: tickets resolved in the 14 days ending on day 0, each carrying its full 14-day recontact lookback, read on the same readout date as M2. Baseline and M2 therefore differ only in which 14 days they cover. | M2 |
| Deflection (self-serve resolution without a ticket) | A session on the help center or in-app self-serve surface that reaches an article or guided flow for its cluster, records a **positive completion signal** — an explicit "this solved it" or an instrumented task completion — and produces no ticket in that cluster from the same account within 7 days. Deflection rate = deflected sessions ÷ (deflected sessions + tickets) for that cluster, both terms counted inside the deflection window. | G4, M4 |
| Deflection window | The 7 days ending on the readout date, per cluster, starting no earlier than that cluster's instrumented launch date in week 4. A 7-day window that begins before the cluster was instrumented is not a window; a cluster instrumented fewer than 7 days before the readout date has no M4 number for that readout instead of a partial one. Deflected sessions and the tickets they are compared against are counted from this one window: no numerator is taken over 90 days against a denominator taken over 7. | G4, M4 |
| Give-up | A self-serve session with no positive completion signal that also produced no ticket. It counts as a failure, never as a deflection, and it is excluded from the deflection numerator. A deflection number that can be raised by excluding signals rather than by resolving sessions is a broken number. | G4, M4 |
| Escalation trigger | Any of: a ticket matching P0 — which includes a security breach, per the support severity row — → `incident-response` at its published P0 response time, "Immediate (all hands)"; ≥ 3 distinct accounts in one cluster within 24 hours on a P1 function, P1 being `incident-response`'s "Major feature broken, significant performance degradation" with its "< 1 hour" response time → candidate incident, escalated the same day; a cluster growing > 50% week over week → product and engineering review, not a support decision. | G1, G5 |
| Handoff threshold | A cluster becomes a product candidate at ≥ 25 tickets in the measurement window, or at ≥ 10 tickets from ≥ 5 distinct accounts inside any 7-day stretch of the measurement window. Below it, the cluster stays a documentation problem. | G5, M6 |
| Article walk | A person who did not write the article starts from a quoted ticket in the cluster, follows the published path, and reaches resolution without opening a ticket. The path is recorded. A walk that ends at a contact form or a second search is a failed walk. | G3, M5 |
| Macro retirement | A macro is retired when two consecutive grades on tickets whose wording it was not written from both fall short of `2`, the two grades coming from two different weekly samples under the G2 grading. This is the only retirement criterion: usage, age, edit count, and ticket volume retire nothing. An edit does not buy a fresh count — the next weekly grade is still a grade — so a macro that keeps scoring below `2` stays retired until a graded `2` on an unseen ticket brings it back, deliberately and on the record. | G2 |
| Recontact watchlist | Every account with three or more recontacts inside the final cohort's 14 days. Each account on it carries a named human owner and a recorded cause — the cause written down, not inferred from the cluster name — and a named human means an assignment, not a queue. A rate that passes while the accounts behind it have nobody assigned has measured the ratio, not the support. | G5 |
| Support hour | A working hour inside the hours published for the channel. A clock that starts outside support hours starts at the next support hour, and the metric says so. | M1 |

## Agent Roster

15 agents. `Proven by` names the gate (G1-G5) or Success Criteria metric (M1-M6) that fails without that agent; every row is cited at least once, and a row cited by neither is removed from the roster.

### Command (Always Active)

| Agent | Slug | Role | Proven by |
| --- | --- | --- | --- |
| Agents Orchestrator | `agents-orchestrator` | Freezes intake to one queue and one taxonomy; calls every gate and records the verdict, its author, and its date | G1, G5 |
| Support Responder | `support-support-responder` | Writes the reply standard and the grading rubric; makes the escalation call a macro cannot make | G2 |
| Product Manager | `product-manager` | One verdict per recurring cluster — defect, spec candidate, documentation fix, or dated no-action | M6 |

### Triage & Knowledge (Week 1-2)

| Agent | Slug | Role | Proven by |
| --- | --- | --- | --- |
| Customer Service | `customer-service` | Intent taxonomy with one definition and two quoted tickets per cluster; triage rules in the order a responder reads them; severity assignment | G1 |
| Technical Writer | `engineering-technical-writer` | Task-first articles and macro text in the customer's words; the article owner named on every page | M5 |
| Studio Operations | `project-management-studio-operations` | Queue structure, routing rules, staffed windows against the published commitments, macro review cadence | M1 |

### Deflection & Channels (Week 3-4)

| Agent | Slug | Role | Proven by |
| --- | --- | --- | --- |
| Email Marketing Strategist | `marketing-email-strategist` | Proactive known-issue notices and the macro-guided email reply set; one tone across notice, article, and reply | M4 |
| Platform Engineer | `engineering-platform-engineer` | Self-serve surface, search tuned to ticket vocabulary, session instrumentation and the completion signal | G4 |
| Workflow Optimizer | `testing-workflow-optimizer` | The non-author article walk, ticket-to-macro routing, and the retirement path for a macro that stops resolving | G2, G3 |

### Voice of Customer (Week 3-5)

| Agent | Slug | Role | Proven by |
| --- | --- | --- | --- |
| Feedback Synthesizer | `product-feedback-synthesizer` | Digest entry per handoff cluster: volume, affected accounts, verbatim quotes, the workaround customers invented | G5 |
| Analytics Reporter | `support-analytics-reporter` | Cluster volumes, the repeat-contact rate, deflection arithmetic, and every rate printed with its query, cohort, and window | M2, M4 |
| Customer Success Manager | `customer-success-manager` | Recontact watchlist; accounts recontacting three or more times get a named human and a recorded cause, not a faster macro | G5 |

### Proof (Week 5-6)

| Agent | Slug | Role | Proven by |
| --- | --- | --- | --- |
| Infrastructure Maintainer | `support-infrastructure-maintainer` | Queue-volume and error-rate signal per cluster, so an outage surfaces from instrumentation before a customer report | G5 |
| Evidence Collector | `testing-evidence-collector` | Dated captures: walk paths and dead ends, graded closes, article revisions, signal firing | M5 |
| Reality Checker | `testing-reality-checker` | Audits the graded sample, the deflection arithmetic, and every metric claim; verdict defaults to NEEDS WORK | M3 |

## Week 1-2: Measure & Triage

Nothing is changed in week 1. The desk is measured as it is, because a baseline taken after the improvements is a story, not a baseline.

### Week 1: Baseline what exists

```text
├── Agents Orchestrator → freeze intake to one queue and one taxonomy file; no new label
│   may be created until the taxonomy is published
├── Analytics Reporter → cluster the 90-day export by symptom: tickets per cluster, the
│   query that produced the count, and the window it covers
├── Customer Service → publish one definition and two real quoted tickets per cluster;
│   a cluster with no definition is merged or dropped, not left ambiguous
├── Analytics Reporter → baseline the outcome numbers before anything changes: the
│   repeat-contact rate on the 14 days ending on day 0, computed with the same arithmetic
│   and the same lookback as M2, and the grade distribution on a 30-ticket sample of closes
├── Studio Operations → current routing and staffed windows, compared line by line with
│   the response-time commitments customers were given
├── Support Responder → grade 30 closing replies from the window against a written
│   standard: what changed, what the customer does next, what is happening about the cause
└── Quality Gate (G1): every ticket in the window carries exactly one cluster from the
    published taxonomy and one severity from the support severity mapping; the five
    highest-volume clusters are printed with ticket count, query, and window; the article
    set — those five plus every cluster at or above the handoff threshold — is printed with
    its member count N; the repeat-contact baseline exists as a number. Fails on one
    untagged ticket, one ticket carrying two cluster tags, an article set printed without
    its count, or a baseline recorded as "unknown".
```

A cluster that cannot be named in the customer's words is not a cluster yet — it is a label. The taxonomy is published when a responder who did not write it can assign a new ticket correctly without asking.

### Week 2: Triage rules and a reply standard

```text
├── Customer Service → triage rules in reading order: intent → cluster → severity → owner,
│   with the escalation ask printed beside each severity
├── Support Responder → reply standard graded 0-2, with one real good reply and one real
│   bad reply quoted beside each grade definition so the rubric is not a matter of taste
├── Technical Writer → macros for the article set, one per cluster, triggered by conditions
│   a responder reads off the ticket, written in the customer's words rather than in
│   product nouns
├── Workflow Optimizer → macro review loop: who may edit, who approves, and how one
│   retires on the single threshold criterion — two consecutive grades below `2` on
│   tickets its wording was not written from — with no second rule based on usage or age
├── Studio Operations → severity routing: P0 and P1 tickets hand to `incident-response`
│   within the hour with the ticket links attached
├── Product Manager → known-issue list reconciled against the clusters: which entries
│   nobody has asked about in 90 days, and which in-scope clusters have no entry at all
└── Quality Gate (G2): every macro in the library — N macros, one per cluster in the
    article set — closed a sampled ticket whose wording was not used to write it, and no
    graded reply in the sample sends a customer to an article that does not contain the
    answer it is cited for. Fails on one macro that only closes when a human escalation
    sits behind it, or on a macro retired by any criterion other than the one above.
```

**Non-negotiable:** a reply standard that the desk's best responders fail is a standard problem and gets rewritten, not enforced. The rubric quotes real replies for exactly this reason.

## Week 3-4: Deflect & Document

Deflection work is scoped by evidence, not by what looks easy to write. The article set printed at G1 — the five in-scope clusters plus every cluster at or above the handoff threshold, N clusters with a count — is the only content that gets built in week 3; a cluster smaller than the in-scope test waits, however annoying it is. The set is copied from G1, not rebuilt, and each in-scope row keeps the query that produced its count.

**Caption — illustrative only: replace these numbers with G1 output; they must never appear in a report.**

| Cluster, in the customer's words | Tickets in the 90-day window | Distinct accounts | Self-serve path today | Week 3 artifact |
| --- | --- | --- | --- | --- |
| "my integration token stopped working" | 412 | 187 | None — a ticket is the only answer | Article, in-app entry point on the token screen, macro |
| "invite a teammate with the right role" | 268 | 154 | A page that explains roles but not the invite flow | Rewritten article, guided flow, macro |
| "why was I billed twice this month" | 231 | 96 | A pricing page that answers annual plans only | Article, notice template, escalation path for real double charges |
| "export is empty after I run it" | 149 | 71 | An article whose walk ends at a contact form | Rewritten article, known-issue notice |
| "connect the integration to our SSO" | 104 | 31 | Three pages that disagree about the same setup | Article rewritten from one source of truth, plus a spec candidate |

The rows above are the shapes a run meets, written in the words customers use; the counts in them are placeholders for the G1 printout and are replaced, not copied. The artifact column is decided per cluster at the G3 gate, and volume ordering decides what gets written first, so a cluster the team finds interesting but small is deferred rather than promoted.

### Week 3: Deflect on the clusters that carry the volume

```text
├── Technical Writer → one task-first article per cluster in the article set, titled in the
│   words the tickets use, with steps in the order the customer performs them
├── Customer Service → harvest the vocabulary from ticket subjects and first sentences;
│   internal nouns and code names are banned as article titles
├── Platform Engineer → self-serve surface: search tuned to that vocabulary, entry points
│   on the product screen where the question appears, and no login wall in front of an answer
├── Email Marketing Strategist → proactive known-issue notices and the macro-guided email
│   reply set, in one tone across notice, article, and reply
├── Workflow Optimizer → the non-author walk: someone who did not write the article starts
│   from a quoted ticket and must resolve without opening a ticket
├── Evidence Collector → dated capture per walk: path taken, dead end hit, text changed
└── Quality Gate (G3): every article in the article set resolved its quoted ticket wording
    in a walk performed by someone who did not write it, and every article carries at least
    one revision made from a recorded dead end. Fails on one walk that ends at a contact
    form or at a second search, or on one cluster in the set with no article to walk.
```

### Week 4: Measure deflection honestly

```text
├── Platform Engineer → instrument the surface: article reached, explicit "this solved it",
│   instrumented task completion, and whether a ticket in that cluster follows within
│   24 hours and within 7 days
├── Analytics Reporter → deflection arithmetic per the Thresholds table, per cluster, with
│   deflected sessions and tickets both counted inside the deflection window, and cluster
│   demand stated as sessions plus tickets rather than as tickets alone
├── Analytics Reporter → demonstrate the give-up exclusion on one named session that ended
│   with no completion signal and no ticket, and was not counted as deflected
├── Studio Operations → supported channel set published; a channel the roster cannot staff
│   is announced as unsupported instead of being silently dropped from the queue
├── Email Marketing Strategist → channel map: which channels the in-scope clusters actually
│   arrive on, and what the notice and the reply look like on each
├── Customer Success Manager → recontact watchlist live: accounts recontacting three or more
│   times inside the final cohort's 14 days get a named human and a recorded cause, not a
│   faster macro
└── Quality Gate (G4): the deflection number in the report recomputes from retained session
    records, excludes every session without a positive completion signal, breaks out per
    cluster, and uses one deflection window ending on the readout date that starts no
    earlier than each cluster's instrumented launch. Fails on one session counted as
    deflected that carried no positive signal, or on a rate whose numerator and denominator
    come from two different windows.
```

Where a ticketing or analytics platform cannot retain the session-to-ticket link, the link is recorded by a landing parameter or an account-level lookup before any deflection number is published. A deflection figure that cannot be recomputed from retained records is a claim, not a measurement, and it does not survive this gate.

## Week 5-6: Close the Loop

A digest forwarded by email is not a loop. The loop closes when a named product owner has accepted or refused a specific cluster on a specific date, and that decision is attached to the cluster's ticket evidence.

```text
├── Feedback Synthesizer → digest entry per handoff cluster: ticket count, distinct accounts,
│   verbatim quotes, the workaround customers invented, and when the cluster started
├── Analytics Reporter → cost per cluster: tickets times median handle time, plus the
│   recontact share inside that cluster
├── Product Manager → one verdict per entry: defect, spec candidate, documentation fix, or
│   no action with a written reason and a dated re-review
├── Support Responder → re-grade the standard against the final sample; a rubric the best
│   replies fail is rewritten before it is enforced
├── Infrastructure Maintainer → queue-volume and error-rate signal per cluster; inject a
│   synthetic spike and require the signal to fire before a customer report would arrive
├── Workflow Optimizer → handoff of the macro library, the routing rules, and the review
│   cadence to the named queue owners
├── Customer Success Manager → the recontact watchlist is read at the gate: every account
│   with three or more recontacts in the final cohort's 14 days has a named human owner and
│   a cause written down beside it
├── Evidence Collector → evidence pack: cluster counts with queries, walk captures, graded
│   closes, article revisions, signal firing
├── Reality Checker → audit the sample, the deflection arithmetic, and every metric claim;
│   verdict defaults to NEEDS WORK
├── Agents Orchestrator → record the verdict, the residual gaps, and the owner of each
└── Quality Gate (G5): every cluster at or above the handoff threshold carries a filed
    product record with a named owner and a dated decision; every account on the recontact
    watchlist carries a named human and a recorded cause; and the queue-volume signal was
    observed firing on the injected spike. Fails on one digest entry without an owner or a
    date, on one watchlist account with neither a named human nor a cause, or on one
    customer-reported outage that reached the queue before the signal.
```

**Reporting rule:** no speed number leaves this runbook alone. First response and time to close may be published only in the same artifact as M1, M2, and M3, because each of those three can move in the wrong direction while speed improves. M1 and M2 are published at their readout date, run exit + 14 days, on the final cohort; a speed number published before that date has no outcome beside it and is a draft.

## Key Decisions

| Decision Point | When | Who Decides |
| --- | --- | --- |
| What is answered by a macro versus a human | Week 2, per cluster: a macro must be graded `2` on a sample it was not written from, and the cluster must be in the article set; everything else gets a human | Support Responder + Technical Writer |
| Whether to publish an SLA | Week 1, before any routing change: publish only a number the staffed windows can hit, and state the support hours and channels with it | Studio Operations + Product Manager |
| Which channels are supported | Week 4: a channel that cannot be staffed and measured is published as unsupported rather than absorbed | Studio Operations + Support Responder |
| When a recurring ticket becomes a product defect | Week 5, against the handoff threshold; below it the answer is documentation, not engineering | Product Manager + Feedback Synthesizer |
| How a "solved" signal is defined and who may change it | Week 4: the definition changes only with a dated note in the metric's own record, never silently mid-run | Platform Engineer + Analytics Reporter |
| Who owns the help center, the macro library, and the digest after week 6 | Week 6 | Agents Orchestrator + Technical Writer |

## Success Criteria

| Metric | Target |
| --- | --- |
| M1 Fast-and-right rate: tickets answered inside the published first-response commitment with no recontact inside the 14-day lookback, computed on the final cohort and read at run exit + 14 days | ≥ 85% of the cohort's tickets |
| M2 Repeat-contact rate: recontacts ÷ tickets resolved on the same cluster, both counted on that same final cohort and read on the same readout date | ≤ min(8%, the Week 1 baseline) |
| M3 Resolution quality: closing replies graded `2` on a 30-ticket sample drawn from the last 14 days of the run, read at run exit | ≥ 90% of the sample |
| M4 Deflection rate on the in-scope set, computed per the Thresholds definition as deflected sessions ÷ (deflected sessions + tickets), both counted inside the deflection window — the 7 days ending on the readout date, per cluster, starting no earlier than that cluster's instrumented launch date | ≥ 20% of cluster demand in that same deflection window, demand being deflected sessions plus tickets |
| M5 Coverage of the article set: 100% of the G1 in-scope set plus every cluster at or above the handoff threshold outside it — N clusters, N printed by G1 in week 1 — each carrying a published article, the working "this solved it" control defined under Deflection, and a named article owner | N of N, N stated by G1 |
| M6 Recurring clusters carried to product with cited ticket evidence, a named owner, and a dated decision | ≥ 5 clusters, each citing ≥ 15 tickets from the measurement window |

M1 is the only row that contains speed, and it cannot be improved by closing faster: a fast close that comes back scores zero. M2 and M3 are the outcome rows that make M1 readable — a run that hits M1 while M2 or M3 sits at baseline has learned that its queue moves faster, not that its customers are served.

Every row in the table declares two things the numbers depend on: its cohort and its window. M1 and M2 share one cohort read 14 days after exit, so no ticket in either ratio is missing its lookback. M4 counts one 7-day window that begins after instrumentation exists, so no pre-instrumentation session is compared against post-instrumentation tickets. M5 counts its clusters against the G1 printout, so the denominator is fixed before week 3 starts; M6 counts them against the filed product records. A rate printed without its cohort and its window is not this metric.

## Common Pitfalls

| Pitfall | Mitigation |
| --- | --- |
| Speed is gamed by fast wrong answers: first response drops, replies get shorter, tickets come back | M1 scores a close as zero when it recontacts; M2 and M3 are reported in the same artifact as any speed number and cannot be omitted |
| Macros sound like a robot, so responders stop using them and quality splits by who answered | Macros are graded `2` on tickets they were not written from, quoted beside real replies in the rubric, and retired on the single threshold criterion — two consecutive grades below `2` on unseen tickets — with no second rule to argue about |
| Knowledge articles are written for the writer: internal nouns, prerequisites, and the fix described from the codebase | Titles and steps come from ticket vocabulary; every article must pass a non-author walk starting at the customer's quoted words |
| Feedback digests are produced weekly and read by nobody | The loop closes only with a named product owner and a dated decision per cluster; an entry without both fails G5 |
| Deflection is counted when the customer simply gave up | Only sessions with a positive completion signal count; a signal-free session with no ticket is a give-up and is demonstrated as excluded at G4 |
| A rate is read on a window that cannot contain its own evidence: a repeat-contact rate read before the lookback expired, or a deflection rate counted over 90 days when the surface was instrumented in week 4 | Every metric prints its cohort and its window. M1 and M2 are read on the final cohort at exit + 14 days; M4 counts one 7-day window that starts no earlier than the cluster's instrumented launch. A row that cannot print both is not a measurement |
| Support instruments catch outages after customers do | Queue-volume and error-rate signals per cluster are proven by injecting a synthetic spike at G5, and customer-first detections in the window fail the gate |

## Post-runbook

These measurements outlive the run, so they are recorded here rather than in Success Criteria.

| Metric | Owner | Measured on |
| --- | --- | --- |
| CSAT/NPS trend for the support-touch cohort against the untouched cohort, 7-day rolling | Analytics Reporter | Day 90 and day 180 from day 0 |
| Retention — logo and revenue — of accounts that recontacted two or more times | Customer Success Manager | Day 180 from day 0 |
| Tickets per account per month, normalized for active accounts | Analytics Reporter | Day 90 and day 180 from day 0 |
| Repeat-contact rate on the in-scope clusters, sustained without weekly intervention | Support Responder | Day 90 from day 0 |
