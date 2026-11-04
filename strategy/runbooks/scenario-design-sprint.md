# Runbook: One-Week Design Sprint

> **Mode**: NEXUS-Micro | **Duration**: 5 days | **Agents**: 10

## Scenario

You have one week to answer one product question with evidence. The week compresses research, sketching, decision-making, prototyping, and user testing into five days. The product of the week is a **validated decision**, not a prototype: a prototype nobody tested is a demo with a deadline.

The roster does the work and the week produces two artifacts — a prototype that has been in front of real users, and a decision record naming what happens next and who owns it. Neither is an input; both are outputs. Gates are agent verdicts on artifacts, and the build / iterate / stop call belongs to the named human decision owner, not to the room and not to an agent.

Doctrine: **a sprint question that cannot fail is not a question.** "Should we improve onboarding?" cannot fail. "Does a 3-step onboarding with no email verification get more people to the first project than the current 7-step flow?" can — a week of work either supports it, contradicts it, or is inconclusive, and all three answers are usable.

## Applicability

| Use this runbook when | Use a different runbook when |
| --- | --- |
| One product question needs an evidence-backed answer in five days | The answer is not needed this week — `feature-discovery-to-spec` contracts what to build |
| The decision is between directions, and a clickable approximation can test the directions | No product exists yet and the whole venture is the question — `startup-mvp` |
| The team will argue from opinion until someone watches a user try it | The flow is agreed and the code is the problem — `codebase-modernization-program` |
| A named human with authority will accept the verdict and fund the next step | The question is whether a finished surface is consistent — `design-system-and-ui-quality` |
| Existing analytics or funnel data can narrow the question before Day 1 | The question is a price, plan, or packaging change — `pricing-and-monetization-review` |
| Real users from the target cohort can be recruited and compensated this week | You cannot reach five real users — a week of internal testing answers nothing |

## Required Inputs

Nothing this runbook produces appears below. The prototype, the test script, the decision record, and the one-pager are outputs of Days 3–5; listing them as blockers would make the week circular. Every input exists before Day 1 and is owned outside the run.

| Input | Why it blocks | Owner |
| --- | --- | --- |
| The sprint question in one sentence, and the named human who decides build / iterate / stop from the verdict, with the authority that lets them commit the next step | A week that ends with a recommendation nobody can act on has produced an opinion with slides | Decision owner |
| Access to real users in the target cohort, with a route to five sessions on Day 5 (customer list, panel, or support-sourced introductions) | Colleague testing is the default failure mode; access decided on Day 4 is access you do not have | UX Researcher, arranged with the decision owner |
| Existing analytics, funnel, or session data for the behaviour the question is about, with dataset names and read access | Without a baseline the week cannot say whether the prototype changed anything | Analytics Reporter |
| A prototype tool the team can actually use on Day 4 — licensed, installed, with accounts that work, or a code stack the team already ships in | A tool discovered as unavailable on Day 4 turns prototype day into procurement day | Rapid Prototyper |
| Written consent from each participant, and a paid retainer or incentive committed per session | Unconsented testing is unusable evidence and a real liability; unpaid recruitment selects for enthusiasm, not for the cohort | UX Researcher, budget approved by the decision owner |

## Agent Roster

Ten agents, three activation windows. Each role below is load-bearing: the gate named in its Role cell is the point at which the week can fail, and G1–G5 are defined in the day sections.

### Sprint Core (Always Active)

| Agent | Role |
| --- | --- |
| Agents Orchestrator | Facilitation and timeboxing; runs every gate call, records the verdict and its timestamp, and refuses a gate that has no artifact to judge (G1–G5) |
| UX Researcher | Expert interviews, Day 5 recruitment from the target cohort, consent, and the five test sessions (G1, G5) |
| UI Designer | Screen design, visual direction, independent solution sketches, and visual issue notes from the sessions (G2, G5) |
| UX Architect | Current-state journey map, solution principles, flow sketches, and the storyboard the test script runs against (G1, G3) |
| Sprint Prioritizer | Sprint question and decision criteria, dot-vote, target user and moment, and the build / iterate / stop recommendation (G1, G5) |

### Prototype & Validate (Day 3+)

| Agent | Role |
| --- | --- |
| Rapid Prototyper | Prototype plan on Day 3, then the high-fidelity build including the functional interactions the test needs — the work this runbook used to split with a separate Frontend Developer (G3, G4) |
| Reality Checker | Feasibility and testability check on Day 3, prototype readiness on Day 4, observation on Day 5, and the evidence verdict (G3, G4, G5) |
| Inclusive Visuals Specialist | Accessibility considerations at sketch stage, then contrast, focus, target-size and non-text alternatives on the prototype (G2, G4) |
| Analytics Reporter | Existing data and funnel baseline on Day 1, task success and friction captured in session (G1, G5) |

### Handoff (Day 5)

| Agent | Role |
| --- | --- |
| Senior Project Manager | Decision record with evidence, next-step owner and date, plus the brand alignment review and the stakeholder one-pager — the two duties this runbook used to list as separate Brand Guardian and Executive Summary Generator roles (G5) |

Two roles left the registry when the mode was sized to ten agents, and their work did not leave with them. Functional interactions are the Rapid Prototyper's on Day 4; brand alignment review and the stakeholder one-pager are the Senior Project Manager's on Day 5. Both are gate items, not courtesies: G4 fails on a click-through with dead controls, and G5 fails on a decision record with no brand review and no one-pager on file.

## Day 1: Understand

```text
Morning:
├── Sprint Prioritizer → Sprint question in one sentence, plus the decision criteria the evidence must meet
├── UX Researcher → Expert interviews on current behaviour, not on the feature someone requested
├── Analytics Reporter → Existing data and funnel baseline; every number carries query, cohort, window and n
└── Agents Orchestrator → Problem-space map and the day's timeboxes

Afternoon:
├── UX Researcher → Recruitment of five or more participants from the target cohort for Day 5
├── UX Architect → Current-state journey map
├── Sprint Prioritizer → Target user and the exact moment the question is about
└── Quality Gate G1: sprint question locked
```

**G1 fails** when the question names more than one decision, when the decision owner is unnamed or cannot commit the next step, or when the evidence that would settle the question is not written down before the week starts. A question that is really three questions is the standard failure: split it, ship one, and record the other two as out of scope for the week. A question locked on Day 1 is not reopened on Day 3 to fit a prototype that already exists.

**Baseline rule.** The Analytics Reporter's Day 1 numbers are the comparison the week reports against. A funnel claim with no dataset, cohort, window, or n is anecdote and cannot be the reason the sprint question was chosen.

## Day 2: Sketch

```text
Morning:
├── UX Researcher → Lightning demos of adjacent solutions, each with what it does differently and why
├── UI Designer → Inspiration and pattern review against the existing product surface
├── UX Architect → Solution principles the sketches must satisfy
└── Agents Orchestrator → Four-step sketch briefing: notes, ideas, crazy 8s, solution sketch

Afternoon:
├── UI Designer → Independent solution sketches, one per participant, no group whiteboard
├── UX Architect → Flow sketches covering the whole tested journey, including entry and exit
├── Inclusive Visuals Specialist → Accessibility considerations carried into the sketches, not retrofitted later
└── Quality Gate G2: sketches ready for critique
```

**G2 fails** when solutions were drawn together rather than independently, when a sketch cannot be read by someone who did not draw it, or when the accessibility pass is a note to do later. Sketches that differ only in colour or copy are one sketch and are recorded as one.

## Day 3: Decide

```text
Morning:
├── Sprint Prioritizer → Critique and dot-vote, with the criteria from G1 on the wall
├── UX Researcher → User-impact assessment per candidate, stated as an observable behaviour
├── Reality Checker → Feasibility and testability check per candidate
└── Agents Orchestrator → Decision on prototype scope: what the prototype must show and what it must omit

Afternoon:
├── UX Architect → Storyboard of the test flow, screen by screen
├── UI Designer → Key screen direction for the chosen flow
├── Rapid Prototyper → Prototype plan: build steps, the interactions that must be functional, and the fidelity that is enough
└── Quality Gate G3: prototype scope and test script approved
```

**G3 fails** when the prototype plan cannot answer the G1 question, when a candidate is carried forward because a senior person favoured it, or when the test script has no task that could produce a failing observation. The Reality Checker's testability verdict defaults to NEEDS WORK: the question asked is "what would we see that kills this direction?", and a plan with no answer to it is not scoped.

## Day 4: Prototype

```text
├── Rapid Prototyper → High-fidelity prototype, plus the functional interactions the test depends on
├── UI Designer → Visual polish and consistency across every screen in the flow
├── Inclusive Visuals Specialist → Contrast, focus order, target size and non-text alternatives
├── UX Researcher → Test script, consent capture, and the session schedule for Day 5
├── Reality Checker → Prototype readiness check: does it test the G1 question on a real device
└── Quality Gate G4: prototype ready for testing
```

**G4 fails** on a prototype that requires narration to be understood, on dead controls where the script asks for a decision, on content that is placeholder in the exact place the question lives, on a missing accessibility pass, or on any session booked without recorded consent. A beautiful prototype that answers a different question than G1 fails here, which is the cheapest place in the week to find that out.

The Rapid Prototyper owns the functional half of this day. A separate frontend role is not on the roster, and "the interactions are not ready" is not a schedule note on Day 4 — it is a G4 failure, because a prototype the participant cannot use measures the participant's patience.

## Day 5: Validate

```text
Morning:
├── UX Researcher → Five user test sessions from the target cohort, one observer per session
├── Reality Checker → Observe and validate findings against what was actually seen and heard
├── Analytics Reporter → Capture task success, time, dead ends and friction points per participant
├── UI Designer → Note visual issues as observed, not as inferred
└── Agents Orchestrator → Synthesize observations, keeping observation separate from interpretation

Afternoon:
├── Reality Checker → Evidence verdict: supported, contradicted, or inconclusive
├── Sprint Prioritizer → Build / iterate / stop recommendation against the G1 criteria
├── Senior Project Manager → Decision record, next-step owner and dated next step, brand alignment review, stakeholder one-pager
├── Agents Orchestrator → Confirm the decision owner has accepted the record in writing
└── Quality Gate G5: decision documented with evidence
```

**G5 fails** on a decision record with no named next-step owner and date, on a verdict that quotes opinion instead of observed behaviour, on a build call that contradicts the evidence the sessions produced, or on a missing brand review or one-pager. INCONCLUSIVE is a legitimate G5 outcome — it is recorded with what would settle the question and what the next step is, and it is not rewritten as a win in the one-pager.

**Recording, consent, retention.** Sessions may be recorded only when the participant signed the written consent in Required Inputs, and the consent record names the purpose, the medium (audio or video), and the retention period. The default retention is 30 days from the G5 verdict, after which recordings and any session notes containing identifying detail are deleted by the UX Researcher, who confirms the deletion in the decision record. Access is limited to the sprint roster plus the named decision owner; nobody outside that list opens a recording, and a participant may withdraw a quote or a recording before the record is finalized. The decision record carries verdicts, observed behaviours, task outcomes, and counts — never names, faces, email addresses, account identifiers, or verbatim quotes that identify a person. Evidence that needs identifying detail lives in the restricted evidence folder and is referenced by session ID only.

## Key Decisions

| Decision Point | When | Who Decides |
| --- | --- | --- |
| Sprint question and the criteria that would settle it | Day 1 | Sprint Prioritizer proposes; Agents Orchestrator locks it at G1; the decision owner countersigns the question it will answer |
| Whether a participant is in the target cohort | Day 1 | UX Researcher, against the cohort defined in the sprint question |
| Which direction the prototype tests | Day 3 | Agents Orchestrator on the G2 dot-vote and the Reality Checker's testability verdict — the loudest room does not decide this |
| Prototype scope and what it deliberately omits | Day 3 | Agents Orchestrator + Reality Checker at G3 |
| Whether sessions are recorded, and for how long | Day 4, before the first session | The decision owner, with UX Researcher; recorded in the consent and in the decision record |
| Whether the evidence is sufficient to conclude | Day 5 | Reality Checker; defaults to NEEDS WORK, and INCONCLUSIVE is recorded as an outcome rather than resolved by discussion |
| Build / iterate / stop, and who owns the next step | Day 5 | Sprint Prioritizer recommends; the named decision owner from Required Inputs decides and accepts the record in writing — no agent holds this decision |

## Success Criteria

Everything here is observable when the week closes on Day 5.

| Metric | Target | Measured by |
| --- | --- | --- |
| User test sessions completed with participants from the target cohort | ≥ 5, and 0 sessions run with colleagues or internal staff | UX Researcher, checked by Reality Checker |
| Prototype tests the sprint question locked at G1 | Confirmed by Reality Checker at G4 and again at G5 | Reality Checker |
| Sessions with written consent on file | 100%, 0 sessions without | UX Researcher |
| Decision documented with evidence, verdict and rationale | Yes, verdict labelled supported / contradicted / inconclusive | Senior Project Manager |
| Next-step owner and dated next step assigned | Yes, named person and calendar date | Senior Project Manager, accepted by the decision owner |
| Accessibility pass on prototype | Completed at G4, findings listed | Inclusive Visuals Specialist |
| Brand alignment review and stakeholder one-pager | Both on file at G5 | Senior Project Manager |
| User data in the decision record | 0 names, faces, identifiers, or identifying quotes | Senior Project Manager, checked by Reality Checker |

## Common Pitfalls

| Pitfall | Mitigation |
| --- | --- |
| The sprint question is really three questions, so the week answers none of them | G1 requires one sentence, one decision and one evidence test; the extra questions are written down as out of scope and scheduled separately |
| The prototype is tested with colleagues instead of users | Sessions are booked from the target cohort on Day 1, not Day 4; the Success Criteria count internal sessions as zero, and G5 fails on a single colleague-only session |
| The prototype answers the wrong question and looks good enough to be accepted anyway | Reality Checker checks the prototype against the G1 question at G4 and again at G5, and its verdict defaults to NEEDS WORK |
| The decision is taken by seniority in the room rather than by the evidence | The verdict is recorded before the discussion, and the build / iterate / stop call belongs to the named decision owner who countersigned the question and accepts the record in writing |
| Participants are recruited for enthusiasm rather than fit | The cohort is defined inside the sprint question and the UX Researcher screens against it; a participant who cannot be placed in the cohort is not evidence |
| The decision record has no owner for the next step, so the week ends in a document | G5 fails without a named next-step owner and a calendar date, and the decision owner accepts the record in writing before the room empties |
