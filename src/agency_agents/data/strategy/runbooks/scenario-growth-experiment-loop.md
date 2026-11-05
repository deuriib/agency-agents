# Runbook: Growth Experiment Loop

Mode: NEXUS-Micro | Duration: 5 agent-days of work across a ≥14-day calendar window | Agents: 10

Five agent-days of scheduled work — Day 1, Day 2, Day 3, the readout session, the decision session — inside a calendar window that is at least 14 days wide, because 14 days is the minimum runtime of exposure. The readout session is scheduled at data lock, not on calendar day 4-5: data lock is the calendar day on which n per arm is reached and the minimum runtime has elapsed, and it is written into the register at launch.

## Scenario

Experiments are run, results are argued about, and nothing compounds. The sample size was never computed, so every result is "directionally positive" and nobody can say what would have counted as a win. The metric was chosen after the data arrived, because the metric that moved is more interesting than the metric that was registered. Three experiments ran in the same week on the same funnel step and confounded each other, so the lift belongs to none of them. The one "win" everyone remembers was never rolled out: the flag is still serving 5% of traffic a year later, because no one owned the follow-through.

The doctrine is one sentence: **an experiment whose metric was chosen after the data is an anecdote with a dashboard. Pre-registration is the whole value.** One experiment at a time, with a frozen hypothesis, a computed sample size, a stopping rule, and a decision recorded before the data is seen.

Scope is one controlled comparison on a product or funnel surface, carried to a decision in both directions. Deciding *what* deserves a test is `feature-discovery-to-spec`; buying the traffic to test it on is `paid-media-launch`.

## Applicability

| Use this runbook when | Use a different runbook when |
| --- | --- |
| One product or funnel change can be run as a controlled comparison with a variant and a control | There is nothing to vary yet and the constraint is traffic — use `paid-media-launch` |
| An existing baseline rate and the instrumentation to measure it are already in place | The question is reach, positioning, and content across channels — use `marketing-campaign` |
| A flat result is an acceptable, recordable outcome | The change must be decided with no traffic at all — use `feature-discovery-to-spec` |
| A losing variant can be removed and a winning one rolled out to all traffic | The change under test is a price, a tier, or a discount policy — use `pricing-and-monetization-review` |
| The metric is a conversion, activation, or retention rate on a defined population | The metric is service quality on a live queue — use `customer-support-operations` |

Boundary: one run covers one experiment with one primary metric. A change that cannot produce a losing result is a launch, not an experiment, and does not belong here.

## Required Inputs

Raw sources only. The hypothesis record, the sample-size calculation, the frozen pre-registration, the readout, and the decision are outputs of the run — listing them as blocking inputs would make the runbook its own prerequisite.

| Input | Why it blocks | Owner |
| --- | --- | --- |
| Read access to the analytics system, with the dataset, table, and event names written down | The baseline and the readout come from queries, not from a dashboard someone remembers | Analytics Reporter |
| Access to the flag system, with permission to split traffic, log exposure, and kill a variant | A variant that cannot be switched off cannot be evaluated or removed | Frontend Developer |
| The current baseline rate for the target metric, with its window, its n, and the query that produced it | A sample size computed from a guessed baseline is a guessed sample size | Analytics Reporter |
| A traffic estimate: eligible weekly exposure per arm at the intended split | n per arm divided by weekly exposure is the only honest runtime; traffic that "feels" sufficient is not an estimate | Experiment Tracker |
| The guardrail's last 8 weekly control-allocation readings, with their dates | The control-chart bound is fixed at design from history; it cannot be reconstructed after a breach | Analytics Reporter |
| The experiment register from previous cycles: surface, audience, metric, duration, result, whether it shipped | Overlap and confounding are only detectable against history | Experiment Tracker |
| A named decision owner with written authority to ship, kill, or roll back | An experiment with no owner produces a result, not a decision | Product Manager |

## Agent Roster

Traceability: `G1`–`G4` are the gates closing the phase sections, `S1`–`S5` the Success Criteria rows, `P1`–`P6` the post-runbook measures.

### Command (Always Active)

| Agent | Role | Proven by |
| --- | --- | --- |
| Agents Orchestrator | Gatekeeper: holds exposure until the record is frozen, releases the launch, is the only agent who may pause it, calls the readout session on the data-lock date, and closes the register | G2, G3, G4 |
| Experiment Tracker | Owns the register, the pre-registration record, the sample-size arithmetic, the data lock, the readout, and the running false-positive count | G1, G2, S2, S5, P6 |

### Hypothesis & Design (Day 1-2 Agent-Days)

| Agent | Role | Proven by |
| --- | --- | --- |
| Growth Hacker | Falsifiable hypothesis, the single change under test, the primary metric, the MDE | G1 |
| Product Manager | The decision the experiment serves, and the pre-committed action for WIN, FLAT, and LOSS | G1, P5 |
| UX Researcher | The observed behaviour the hypothesis rests on: one named observation with its source, and variant distinctness | G1 |

### Instrumentation (Day 3 Agent-Day)

| Agent | Role | Proven by |
| --- | --- | --- |
| Frontend Developer | Flag wiring, one assignment unit, exposure and guardrail events, a tested kill switch; later, the ramp to 100% traffic and its reported share | G3, P5 |
| Analytics Reporter | Baseline recomputation, n per arm, one pipeline for primary and guardrail, end-to-end trace, and the control-chart bound fixed at G2 | G3, S5 |

### Readout & Proof (Readout at Data Lock)

| Agent | Role | Proven by |
| --- | --- | --- |
| Evidence Collector | Evidence pack: frozen hash, exposure counts, readout query, dashboard captures | G4 |
| Reality Checker | Verdict PASS / FLAT / FAIL / INVALID, default NEEDS WORK | G4, S2 |
| Content Creator | Turns a verdict into shipped surface: production copy, in-app message, changelog entry, or the written "no" — the surface P5 measures live | P5 |

## Thresholds

Every number a gate or metric cites is defined here once. A threshold that is not defined is an unfailable criterion.

| Threshold | Definition | Default value | Owner |
| --- | --- | --- | --- |
| Minimum detectable effect (MDE) | The smallest relative lift on the primary metric the experiment is powered to detect; it is the effect that must also be worth shipping. Relative: 5% means 5% of the control rate, not 5 points | 5% relative on a conversion or activation rate; a smaller MDE requires the computed n, not a smaller MDE | Growth Hacker |
| Significance level (α) | Two-sided false-positive rate fixed at design time, never revisited in the readout | 0.05 | Experiment Tracker |
| False-positive budget | The number of certified wins that may later fail durability (P1) or the reversal check (P4) before the loop is treated as uncalibrated. With α = 0.05 applied to wins that are shipped, about one certified win in twenty is expected to be spurious; the register carries the running count and reports it against this budget | 1 spurious certified win per 20 certified wins | Experiment Tracker |
| Power (1−β) | Probability of detecting the MDE when the MDE is real | 0.80 | Experiment Tracker |
| Sample size, proportions | n per arm = 2(z₁₋α/₂ + z₁₋β)²·p(1−p)/δ² , with z₁₋α/₂ = 1.96, z₁₋β = 0.84, p the baseline rate, δ the absolute effect = p × MDE | Recorded as `n = 15.7·p(1−p)/δ²`, rounded up | Analytics Reporter |
| Sample size, continuous | n per arm = 16σ²/Δ², with σ the per-unit standard deviation from the baseline window and Δ the MDE in metric units | Same five inputs recorded: p or σ, δ or Δ, α, power, allocation | Analytics Reporter |
| Reproducible n | A second person recomputes the same n per arm from the recorded inputs and the recorded formula, to the same round-up | 0 disagreements | Reality Checker |
| Minimum runtime | Calendar days of exposure, fixed at design; it must cover at least two full weekly cycles so weekday and weekend behaviour both appear, and one full billing or renewal cycle when the primary metric is revenue | 14 days, regardless of how early n is reached | Experiment Tracker |
| Experiment window | One calendar window as long as the minimum runtime. At most one experiment is exposed inside a window; the next experiment is designed — hypothesis, sample size, pre-registration, no traffic — while the current one is exposed | 14 days per window: at least 1 experiment carried to a recorded decision per window, at least 2 per 28-day cycle | Experiment Tracker |
| Data lock | The calendar day on which n per arm is reached and the minimum runtime has elapsed, whichever is later. The readout session is called on that date; it is a date computed and registered at launch, never a fixed day count | The later of n reached and minimum runtime elapsed | Agents Orchestrator |
| Stopping rule | The run stops only when n per arm is reached **and** the minimum runtime has elapsed, or at the registered end date. The single exception is a guardrail breach | Any other stop is recorded as an invalid readout, not a win | Agents Orchestrator |
| Guardrail tolerance | Degradation allowed on a metric the experiment must not harm, evaluated with the same sample, the same window, and the same test as the primary | No more than 2% relative degradation, or the guardrail's own control-chart bound, whichever is tighter | Product Manager |
| Control-chart bound | The guardrail's own historical band: the 5th and 95th percentile (p5/p95) of the guardrail rate over the trailing 8 weekly control-allocation readings. The band, the 8 dates used, and the weekly values are written into the pre-registration record at G2, so the bound is fixed before exposure; it can only tighten the 2% rule, never loosen it | Trailing 8 weekly readings, p5/p95, recorded at G2 | Analytics Reporter |
| Flat band | The result band inside which the outcome is FLAT rather than a directional win or loss, computed in relative units around the control rate: control × (1 ± MDE), which at the default 5% relative MDE is control × [0.95, 1.05] | control × [0.95, 1.05] at 5% relative MDE | Experiment Tracker |
| Absolute reporting | The readout states every result in absolute percentage points beside the relative lift, so the unit is never ambiguous: control 4.0% and variant 4.4% is +0.4 points and +10% relative. The flat band is computed in relative units and reported in both | Both units on every readout | Analytics Reporter |
| Analysis plan | The named test and the decision rule per outcome, fixed at design; segments are exploratory and are reported as exploratory | One frequentist two-sided test, or one Bayesian rule with its threshold stated | Analytics Reporter |
| Decision latency | Working days from data lock to a recorded decision in the register | ≤2 | Product Manager |
| Post-ramp guardrail recheck | The guardrail re-read 7 days after the ramp reaches 100% of traffic, at or inside its pre-experiment band. It is a condition of certification, not a post-runbook score: a win is not certified until it passes | 7 days after the ramp reaches 100% | Analytics Reporter |
| Certified win | A G4 PASS verdict whose rollout reached 100% of traffic — the variant serves all eligible traffic on that surface, control at zero — and whose guardrail passed the post-ramp recheck. A certified win that later fails P1 or P4 is counted against the false-positive budget | Verdict PASS + recheck inside band + 100% of traffic | Reality Checker |

## Day 1-2: Hypothesis & Design

```text
Day 1 — Hypothesis
├── Growth Hacker → hypothesis in falsifiable form: "because <observed behaviour>, changing
│   <X> for <audience> will move <primary metric> by ≥<MDE> relative within <runtime>"
├── UX Researcher → the observation the hypothesis rests on: exactly one named observation with
│   its source — a funnel step with its date range, a session-recording identifier, or a ticket
│   cluster identifier. The observation is quoted, not paraphrased
├── Product Manager → the decision this serves: what WIN, FLAT and LOSS each change in the
│   roadmap. Three identical answers means the experiment is a status update
├── Experiment Tracker → conflict check against the register: no live experiment on the same
│   funnel step, the same audience, or the same primary metric
├── Experiment Tracker → window check: the previous experiment reached its decision in the
│   current 14-day window, so this one is designed now and exposed only after that decision
└── Quality Gate (G1): the hypothesis is falsifiable and names one primary metric, one
    audience, one change and one MDE; it cites exactly one named observation with its source,
    and a hypothesis with no cited source is a preference and fails here; and WIN / FLAT / LOSS
    each lead to a different written action. Two outcomes that produce the same action fail
    the gate.
```

```text
Day 2 — Design and Pre-registration
├── Growth Hacker → exactly one change per variant, so the result is attributable; a variant
│   that differs from control in two ways is two experiments wearing one flag
├── Analytics Reporter → baseline rate recomputed from the frozen query on a stated window,
│   with its n; n per arm computed from baseline rate, absolute effect, α, power, allocation,
│   with the formula and all five inputs written into the record
├── Analytics Reporter → control-chart bound computed from the trailing 8 weekly
│   control-allocation readings of the guardrail, with those 8 dates written into the record
├── Frontend Developer → instrumentation plan: assignment unit, exposure event, guardrail
│   event, and confirmation that every registered metric is actually measurable
├── Experiment Tracker → pre-registration record, ten fields: hypothesis with its cited
│   observation and source, audience, variant, primary metric with frozen query, guardrail with
│   tolerance and its control-chart bound plus the 8 weekly readings used, MDE, α and power,
│   n per arm with formula inputs, runtime and stopping rule, analysis plan plus decision owner
│   with the pre-committed action per outcome
├── Agents Orchestrator → freeze: commit the record, write its hash into the experiment
│   register, and confirm the flag cannot serve traffic before the hash exists
└── Quality Gate (G2): the record is frozen before the first exposed user — hash present in
    the register, freeze timestamp earlier than the first exposure event — n per arm
    recomputes from its own five inputs, and the control-chart bound is present with the 8
    weekly readings that produced it. An unfrozen record, a missing hash, a guardrail with no
    bound, or arithmetic that does not reproduce fails.
```

## Day 3: Instrument & Launch

```text
├── Frontend Developer → flag wired: variant and control served from one assignment unit, the
│   same unit the baseline was computed on; exposure emitted once per unit per experiment; no
│   client-side re-randomisation; kill switch flipped once in staging and observed to stop
│   exposure
├── Analytics Reporter → one exposed user and one control user traced end to end: assignment
│   → exposure → metric event → readout query, with payloads captured
├── Frontend Developer → guardrail event instrumented on the same pipeline as the primary, not
│   a separate dashboard nobody opens
├── Experiment Tracker → register updated with launch timestamp, current n per arm, registered
│   end date, the data-lock date (the later of n reached and minimum runtime elapsed), and the
│   stopping rule as it was frozen
├── Growth Hacker → launch at the registered allocation only; no mid-flight edits to the
│   variant, the copy, or the targeting — a mid-flight fix restarts the clock and is recorded
│   as a new experiment
├── Agents Orchestrator → releases exposure, remains the only agent who may pause it, and is
│   the only agent who calls the readout session, on the registered data-lock date
└── Quality Gate (G3): one exposed user appears exactly once, in exactly one arm, with a
    payload that matches the frozen record; the guardrail query returns a number for both
    arms; and the kill switch has been observed to stop exposure. A user in both arms, a null
    guardrail, or an untested kill switch fails.
```

## Readout & Proof: Readout at Data Lock (Agent-Days 4-5)

Wait state: no agent session is scheduled between the launch call and data lock. The calendar
window is at least 14 days (Minimum runtime), and the readout session is called on the data-lock
date written into the register at launch, not on calendar day 4-5. The gap is not idle: the next
experiment is designed in it — hypothesis, sample size, pre-registration — but not exposed.

```text
├── Agents Orchestrator → calls the readout session on the registered data-lock date; not
│   earlier, and not later than the registered end date
├── Experiment Tracker → data lock at the registered runtime: n per arm reached and minimum
│   runtime elapsed, no further exposure counted, readout computed from the frozen query and
│   not from a rebuilt one
├── Analytics Reporter → primary result with interval and p-value under the registered test,
│   reported in absolute points beside the relative lift and compared to the flat band
│   control × [0.95, 1.05]; guardrail evaluated with the same sample, window, and test, against
│   the tighter of the 2% relative rule and the p5/p95 control-chart bound frozen at G2 — a
│   guardrail read on a different cut is not a guardrail
├── Evidence Collector → evidence pack: frozen record hash, exposure counts per arm, the
│   readout query, dashboard capture, and the pre-launch capture of the same dashboard
├── Reality Checker → verdict PASS / FLAT / FAIL / INVALID, default NEEDS WORK; INVALID when
│   the record changed after launch, when the sample was cut short without a guardrail
│   breach, or when the analysis test differs from the frozen one
├── Content Creator → on a win: the shipped surface — production copy, in-app message,
│   changelog entry — so the win exists outside the dashboard; on a loss: the written "no"
│   with the result attached, filed where the next cycle will read it. The surface is what P5
│   measures at 100% traffic
├── Product Manager → the decision executed against the action pre-committed on Day 1, with
│   the rollout owner and the ramp date named
├── Experiment Tracker → register records the certification state of each win (recheck
│   pending, passed, failed) and the running count of certified wins that later failed P1 or
│   P4, against the false-positive budget of 1 per 20
├── Agents Orchestrator → experiment closed in the register, outcome and decision timestamped
└── Quality Gate (G4): the readout recomputes from the frozen record, its hash matches the
    pre-launch hash, and the verdict plus decision are recorded within 2 working days of data
    lock. Any change to the primary metric, the stopping rule, or the analysis plan after
    launch fails this gate and relabels the run as an observational study — a changed plan is
    a different study, not a footnote, and any result quoted from it carries that label.
```

Certification is not complete at G4. A PASS verdict is certified only once the guardrail passes
the post-ramp recheck at 100% traffic, and the register keeps that state per win. When the count
of certified wins that later failed P1 or P4 exceeds the false-positive budget, the loop is
reported as uncalibrated and the next α or MDE is set before the next experiment is exposed.

## Key Decisions

| Decision Point | When | Who Decides |
| --- | --- | --- |
| One experiment at a time versus overlap: default is one live experiment per funnel step; overlap is allowed only when two experiments share no audience, no primary metric and no triggering surface, and the isolation argument is written into the register | Day 1 | Experiment Tracker proposes, Agents Orchestrator approves |
| Ship threshold: a win requires the primary metric at or beyond MDE, the registered test at α, the guardrail inside tolerance, and the full runtime; it is certified only after the post-ramp recheck passes at 100% traffic | Day 2, pre-committed | Experiment Tracker computes, Reality Checker certifies |
| Who may stop an experiment early: only the named decision owner, and only for a guardrail breach or a user-harm event; "it looks great" is not a stop reason | Launch onward | Decision owner acts, Agents Orchestrator records the stop as a stop |
| When the readout is called: on the registered data-lock date, never on a fixed day count and never on an interim peek | Day 3, pre-registered | Agents Orchestrator |
| What happens on FLAT: the pre-registered default action runs — usually keep control, archive the variant, and do not re-run the same hypothesis for one full cycle | Day 2 pre-committed, executed at data lock | Product Manager |
| Whether a losing variant is removed: yes — the code path is deleted within 5 working days, or left behind a default-off flag with a removal ticket naming an owner | At data lock | Product Manager on the Reality Checker verdict |
| Whether a win is rolled out: ramp to 100% traffic with the guardrail re-read 7 days after the ramp; the ramp owner and the date are named in the register, and a failed recheck un-certifies the win | At data lock | Decision owner, executed by Frontend Developer |

## Success Criteria

| Metric | Target |
| --- | --- |
| S1 — Experiments carried to a recorded decision per 14-day window | ≥1 per window and ≥2 per 28-day cycle; exactly one exposed at a time, the next designed but not exposed while the current one runs |
| S2 — Pre-registration compliance: records frozen before first exposure, zero post-launch changes to metric, stopping rule, or analysis plan | 100%, 0 changes |
| S3 — Decision latency from data lock to recorded decision | ≤2 working days |
| S4 — Guardrail coverage: experiments evaluating at least one non-degradable metric with the primary's rigour | 100% |
| S5 — Sample-size provenance: experiments carrying a reproducible n per arm; early stops without a guardrail breach | 100% reproducible; 0 early stops |

## Common Pitfalls

| Pitfall | Mitigation |
| --- | --- |
| The metric chosen after the data arrives, because another one moved | The primary metric and its query are frozen at G2 with a hash; the readout must recompute from that query, and a swapped metric fails G4 |
| A hypothesis that is a preference in disguise, with no observation behind it | G1 requires exactly one named observation with its source; a hypothesis with no cited source fails the gate before any traffic is spent |
| Peeking and stopping when the result looks good | The stopping rule is frozen at design and permits one exception, a guardrail breach; agents report current n, never an interim p-value, and anything else is recorded as invalid |
| Reading the flat band as an absolute interval, so 4.0% control against 4.4% variant is argued to be FLAT | The band is computed as control × (1 ± MDE) in relative units — control × [0.95, 1.05] at 5% — and every readout prints absolute points beside the relative lift |
| Waiting for the readout on the calendar day the plan was written rather than the day the data locked | The data-lock date is computed and registered at launch, and Agents Orchestrator calls the readout session on that date |
| Overlapping experiments that confound each other | The register conflict check at G1 blocks a second experiment on the same funnel step, audience, or metric unless the isolation argument is written down |
| Sample size skipped because traffic "felt" sufficient | n per arm must recompute from five recorded inputs at G3 before exposure; a missing baseline blocks the launch rather than shrinking the requirement |
| A certified win that never ships | The decision owner, ramp owner and ramp date are named at data lock, P5 tracks the share live at 100%, and the register cannot close the experiment without a rollout owner |
| Guardrail metrics measured loosely or not at all | One guardrail minimum per record, same pipeline, same sample, same test as the primary; a null guardrail reading fails G3 and an out-of-tolerance one overrides a primary win |
| A win certified at α = 0.05 and later quietly reversed, with nobody counting | The post-ramp recheck is part of certification and P6 reports the running count of certified wins that later failed P1 or P4 against the budget of 1 per 20 |

## Post-runbook

These windows close after the run. They are not scored at G4 and must not be reported as in-run results; the owner named here measures them on the date written into the G4 record. The post-ramp guardrail recheck is the exception: it is a certification condition defined in Thresholds, recorded by the register before a win is called certified, not a P-row.

| Metric | Owner | Measured on |
| --- | --- | --- |
| P1 — Durability of the win: primary metric lift still present at the registered effect, same cohort definition, same query | Experiment Tracker | 30 days after full rollout |
| P2 — Guardrail drift after the rollout: guardrail back at or inside its pre-experiment band | Analytics Reporter | 30 days after full rollout |
| P3 — Cumulative lift: sum of shipped, guardrail-clean wins measured against the pre-cycle control baseline | Analytics Reporter | Last day of each quarter |
| P4 — Reversal rate of shipped wins: share of rolled-out wins rolled back or downgraded | Product Manager | 60 days after each rollout |
| P5 — Certified wins live at 100% traffic: share of certified wins serving all eligible traffic on their surface | Product Manager accounts; Frontend Developer executes the ramp and reports the share | Verdict recorded in the register + 10 working days |
| P6 — False-positive count: certified wins that later failed P1 or P4, as a running count against the false-positive budget | Experiment Tracker | Reported at every P1 and P4 check |
