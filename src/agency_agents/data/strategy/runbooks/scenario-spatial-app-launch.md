# Runbook: Spatial App Launch

Mode: NEXUS-Sprint | Duration: 6 weeks | Agents: 15

## Scenario

The spatial demo is convincing on the developer's headset and unusable for anyone else. Windows are placed at a height that assumes one person's room. The frame rate holds in the simulator and drops in a real space, where passthrough, glass materials, and a real room's geometry all cost what the simulator did not charge. A grab interaction requires a reach nobody has. And the app has never been through spatial store review, so the requirements it will be judged against exist only as a recollection of what someone read once.

None of those failures is visible in a video of the demo, which is why they survive to the week before submission. They are comfort and interaction failures, and they are measurable before release.

This runbook ships a spatial product whose comfort, latency, and interaction budgets are release gates, verified in a real space by someone who did not build it. The doctrine is one sentence: **a spatial build is done when a first-time participant completes the core tasks, in a room the team did not choose, inside the frame, latency, and reach budgets, without a comfort stop** — on the same build that is filed for review.

**Domain boundary — comfort and safety budgets are release gates, not polish.** A spatial app that makes people ill, or requires a reach outside a normal range of motion, is broken regardless of how it looks. There is no visual quality argument that outranks a participant stopping a session because of discomfort, and no schedule argument that converts a comfort stop into a known issue. A build that fails a comfort or reach budget is not "almost there": it is unshippable until the failing observation is gone, and the fix is re-observed in a real space, not reasoned about.

Platform and store requirements are inputs, read and cited at run start. This runbook asserts no platform behaviour on a vendor's behalf and names no review requirement it has not read.

## Applicability

| Use this runbook when | Use a different runbook when |
| --- | --- |
| A visionOS, XR, or spatial product is going to a spatial store review, and comfort, latency, and interaction budgets must hold in a real space | The release is a 2D mobile app for iOS or Android — `mobile-app-launch` |
| The spatial interaction model is part of what ships: windows, volumes, immersive scenes, and the space they assume | The interface is flat screens that need to become a system — `design-system-and-ui-quality` |
| Comfort, latency, and reach are release gates with numbers attached | Accessibility conformance on a shipped surface needs a retrofit — `accessibility-remediation-sprint` |
| A second device family is in scope and the degradation ladder must be decided before it is discovered | A frame-rate or memory problem with no spatial dimension: `bug-triage-and-defect-elimination` when it is a regression, `mobile-app-launch` when it ships with a 2D release |
| A convincing demo must be proven on people who did not build it, in rooms the team did not pick | What to build is still undecided — `design-sprint` |

## Required Inputs

Only artifacts the roster cannot produce. The app, the comfort report, and the evidence pack are outputs of Weeks 2-6; listing them here would make the run circular.

| Input | Why it blocks | Owner (outside the roster) |
| --- | --- | --- |
| Physical test devices: at least one device at the target spec with developer provisioning, plus one device from the second family if that decision is still open | Budgets are measured on hardware. A simulator cannot fail a comfort gate, so a run without devices has no gate | Engineering leadership or device owner |
| A real room of known dimensions — clear floor area, ceiling height, lighting — measured and recorded, plus a second room the team did not choose, available in Week 5 | Placement and reach cannot be validated against an assumed room; the second room is what proves the app is not tuned to one apartment | Product owner |
| The store's current spatial review requirements as published at run start, downloaded, dated, and cited item by item | Requirements change without notice; a checklist recalled from a previous submission fails at review | Sign-off authority |
| A named test group of at least eight first-time participants who did not build the app, recruited with consent and compensation | Builders' muscle memory hides every interaction defect, and comfort data from people who already know the gestures is not comfort data | Product owner with research operations |
| An accessibility baseline for motion and interaction: the standard, the severity scale findings cite, and the non-hand input paths that must exist for every core task | Motion and reach failures found after submission are design changes, not fixes | Compliance or legal owner |
| A named sign-off authority with the power to stop the release, and their written waiver rule for a comfort or reach failure | Without a named authority, comfort and reach failures ship with whoever is most tired of the build | Executive sponsor |

## Agent Roster

Fifteen agents, five activation windows. Every row is load-bearing: the Proven by column names the gate or metric that fails when the agent's work is missing.

### Command (Always Active)

| Agent | Role | Proven by |
| --- | --- | --- |
| Agents Orchestrator | Pipeline control, gate calls with a timestamp, decision log, and refusal of any gate that has no artifact to judge | G1, G2, G3 |
| Senior Project Manager | Scope ceiling, traceability matrix, device-family decision, budget amendment log, submission schedule | G1, M5 |
| XR Interface Architect | Interaction contract ownership: modality per task, space assumption, reach envelope, mismatch behaviour, degradation ladder | G1, M6 |

### Spatial Build (Week 2-4)

| Agent | Role | Proven by |
| --- | --- | --- |
| visionOS Spatial Engineer | Window, volume, and scene architecture; placement read from the measured room rather than a constant; glass material cost kept inside the frame budget | G2, M1 |
| XR Immersive Developer | Input pipeline behind the contract's interface so the input model can be swapped without touching task logic; degradation ladder implementation | G2, M2 |
| macOS Spatial/Metal Engineer | Render path and GPU work per frame profiled on the target device; overdraw, material count, and pass structure measured rather than assumed | G2, M1 |
| Terminal Integration Specialist | Text and console surfaces render inside the frame budget at both reading distances, with no per-frame layout work | G2, M1 |

### Interaction & Comfort (Week 2-4)

| Agent | Role | Proven by |
| --- | --- | --- |
| XR Cockpit Interaction Specialist | Seated anchoring, constraint-driven grab volumes, and the reach sweep that measures every interactive target against the envelope | G2, M6 |
| UX Researcher | First-time participant protocol, comfort instrument and its stopping rule, recruitment outside the team, and the Week 5 sessions | G3, M3, M4 |
| Accessibility Auditor | Motion and interaction baseline, reduced-motion path, non-hand input path per core task, and findings on the printed severity scale | G1, M4 |

### Design (Week 1-3)

| Agent | Role | Proven by |
| --- | --- | --- |
| UI Designer | Spatial layout grid: depth bands, eye-level band, reach-shell overlay at true scale, legible type at 2 m and at 60 cm | G1, M6 |
| UI Finish-Gate Reviewer | Legibility, contrast, occlusion, and glass-material findings closed or dated before submission; store captures taken from the validated build | G3, M4 |

### Quality & Proof (Week 5-6)

| Agent | Role | Proven by |
| --- | --- | --- |
| Performance Benchmarker | Measurement harness, the 20-minute sustained session, frame-time percentiles, drop-frame rate, motion-to-photon sampling, thermal curve | G2, M1, M2 |
| Evidence Collector | Evidence pack: session logs, comfort records, reach measurements, frame captures, each tied to a metric ID and to the submitted build | G3, M5 |
| Reality Checker | Real-space verdict on the validated build, default NEEDS WORK, plus the residual risk note that assigns an owner to every open item | G3, M3 |

## Week 1-2: Spatial Interaction Contract

The contract is the artifact this phase exists to produce, and it is written before the build is tuned. It states the space the app assumes, the reach it requires, what it does when the room does not match, and what it drops first when the frame budget is exceeded. A build without a frozen contract is a demo whose behaviour depends on whose apartment it is running in.

| Contract field | What it must state | Failure it prevents |
| --- | --- | --- |
| Space assumption | Seated, standing, or room scale, per core task, with the clear floor area and ceiling height assumed | Content placed for one person's room |
| Reach envelope | The 30-60 cm shell from the shoulder origin, the vertical band, and the azimuth limit every target must sit inside | A grab interaction nobody can perform |
| Mismatch behaviour | What the app does when the measured space is smaller than assumed: recenter, fall back to window modality, or decline to enter immersive with a stated reason | An app that is broken in a normal room |
| Input model and fallback | Primary input per task, and a non-hand path (voice, controller, accessibility feature) for every core task | An interaction that works for one body only |
| Degradation ladder | The ordered list of what drops first when thermal or frame budget is exceeded, decided before it happens | Random frame loss during a session |
| Session limits | Break prompt at 20 minutes, hard cap on validation session length, comfort check interval | Comfort failures discovered by users |

```text
Week 1: Space Assumption & Contract
├── Agents Orchestrator → phase plan, gate calendar, decision log opened, budget sheet started
├── XR Interface Architect → interaction contract v1: modality per core task, space assumption
│   per task, reach envelope, input model, mismatch behaviour, degradation ladder
├── UI Designer → spatial layout grid: depth bands, eye-level band, reach-shell overlay drawn
│   at true scale, type legible at 2 m and at 60 cm
├── UX Researcher → first-time participant protocol, three core tasks, comfort instrument and
│   its stopping rule, recruitment from outside the team
├── Accessibility Auditor → motion and interaction baseline: reduced-motion path, non-hand
│   input path per task, and the severity scale every later finding cites
├── Senior Project Manager → scope ceiling, traceability matrix scaffold, device-family question
│   raised with the sign-off authority
Week 2: Contract Freeze & Instrumentation
├── XR Interface Architect → contract v2 frozen: space assumption signed, mismatch behaviour
│   implemented for every core task
├── visionOS Spatial Engineer → window and scene scaffolding placed from the measured room, with
│   no hard-coded world positions
├── XR Immersive Developer → input pipeline behind the contract interface, so the input model can
│   be swapped without touching task logic
├── XR Cockpit Interaction Specialist → seated anchoring and constraint-driven grab volumes sized
│   inside the envelope, not inside the model
├── Accessibility Auditor → baseline applied to the first vertical slice, findings on the printed
│   severity scale
├── UX Researcher → three participants from outside the team run the contract in the team's room;
│   failure notes, not opinions
├── Senior Project Manager → second device family decided and recorded, or declined with a reason
└── Quality Gate (G1): One seated first-time participant in the smallest declared space completes
    the primary task with every interactive target inside the reach envelope and no verbal
    instruction.
```

## Week 3-4: Build & Comfort Budgets

Budgets are instrumented in Week 3 and exercised in Week 4. Instrumentation comes first because a budget measured with the wrong tool is a number nobody can defend: frame time at the percentiles in Thresholds, motion-to-photon latency from real head motion, thermal state across a session, and the reach of every target measured in the room rather than in the scene graph.

```text
Week 3: Budgets Instrumented
├── Performance Benchmarker → measurement harness: frame time at p50, p95 and p99, dropped-frame
│   count, motion-to-photon sampling, thermal state, all logged against a session ID
├── macOS Spatial/Metal Engineer → render path profiled on the target device: overdraw, material
│   and pass count, glass cost per window measured rather than estimated
├── visionOS Spatial Engineer → window and volume count under budget; placement logic reads the
│   measured room dimensions instead of a constant
├── XR Immersive Developer → degradation ladder implemented in the decided order: fidelity, then
│   window count, then refresh, then immersive exit
├── Terminal Integration Specialist → text and console surfaces inside the frame budget at both
│   reading distances, with layout cached rather than recomputed per frame
├── UI Designer → depth, occlusion and contrast pass at true scale; legibility measured in the room
├── UI Finish-Gate Reviewer → glass, occlusion and contrast findings closed or dated, with an owner
├── Senior Project Manager → budget amendment log opened: any budget change is written, dated and
│   re-signed, never agreed in a standup
Week 4: Comfort Budgets & First Real-Space Run
├── Performance Benchmarker → 20-minute sustained session on the target device in the measured
│   room: frame rate, p99 frame time, drop-frame rate, stalls, thermal curve
├── XR Cockpit Interaction Specialist → reach sweep: every interactive target measured against the
│   envelope in the smallest declared space, with the measurement recorded per target
├── Accessibility Auditor → reduced-motion and non-hand input paths exercised end to end on the
│   slice, not reviewed on paper
├── UX Researcher → first full comfort protocol with participants who did not build the app,
│   comfort instrument every 5 minutes, no prompting during tasks
├── Reality Checker → interim verdict on the slice; any comfort stop is a finding, not an anecdote
└── Quality Gate (G2): One continuous 20-minute session in the measured room holds the sustained
    frame rate, the p99 frame time and the drop-frame tolerance at the same time, with the thermal
    curve flat after warm-up.
```

## Week 5-6: Real-Space Validation & Review

Validation happens in two rooms, one of them chosen by someone other than the team, with participants who did not build the app and were not told how the gestures work. Review runs in parallel from the validated build, against requirements read at run start rather than remembered.

```text
Week 5: Real-Space Validation
├── UX Researcher → eight first-time participants across two rooms: the measured room and one the
│   team did not choose; comfort instrument every 5 minutes; no instruction during tasks
├── XR Interface Architect → mismatch behaviour exercised: smallest space, seated participant,
│   lighting change, recenter mid-task, immersive entry refused with a stated reason
├── Accessibility Auditor → baseline verified against the shipped build, findings on the printed
│   severity scale, non-hand path exercised per core task
├── Performance Benchmarker → per-session frame and latency capture, on both device families when
│   a second family is in scope
├── Evidence Collector → evidence pack: session logs, comfort records, reach measurements, frame
│   captures, each tied to a metric ID and to the build hash that was filed
├── Reality Checker → real-space verdict on the validated build; default NEEDS WORK
Week 6: Review & Submission
├── Senior Project Manager → store spatial review requirements read at run start, dated, mapped to
│   a checklist with one owner per item and evidence named for each
├── Evidence Collector → submission pack assembled from the validated build, never from mockups
├── UI Finish-Gate Reviewer → store screenshots and preview captures taken from the validated build
├── Agents Orchestrator → hold rule enforced: no comfort stop and no reach violation ships with a
│   waiver, and no gate is closed on a verbal report
├── Reality Checker → release verdict and residual risk note with an owner per open item
└── Quality Gate (G3): One first-time participant who did not build the app completes all three
    core tasks with no instruction, in a 20-minute session in a room the team did not choose, with
    zero comfort stops, on the same build that is filed for review.
```

## Thresholds

Defined once here and cited by every gate and metric. Budgets are set at G1 and are not renegotiated mid-run; a change is a written amendment with a date and a re-signed approval, recorded by the Senior Project Manager. Frame budgets are expressed as frame time at the target device's display refresh — if that refresh differs from the reference used below, the budget is the frame time at the real refresh, never a lower number.

| ID | Budget | Definition and measurement |
| --- | --- | --- |
| M1 | Sustained frame rate | At least 90 frames per second averaged across a continuous 20-minute session on the target device in the measured room, with the 99th-percentile frame time at or below 13.9 ms. The reference frame budget is 11.1 ms at a 90 Hz refresh; 13.9 ms is 1.25 times that budget. A p50 figure, a 10-second burst, or a simulator run does not satisfy it |
| M1b | Drop-frame tolerance | At most 1 percent of frames in any rolling 60-second window exceed twice the frame budget, and no single stall exceeds 100 ms after the first 5 seconds of the session. Warm-up is excluded and the exclusion is stated in the log |
| M2 | Motion-to-photon latency | At most 20 ms at the 95th percentile, from tracked head movement to the corresponding change in the rendered image, over at least 200 samples across a session. Interaction acknowledgement for gaze and pinch selection is at most 100 ms at the 95th percentile |
| M3 | Comfort duration | A break is recommended at 20 minutes of continuous use, prompted in the app and logged. Validation sessions are capped at 30 minutes, with a 5-minute break before any second session. The comfort instrument runs every 5 minutes, and one comfort stop voids the session as evidence |
| M4 | Interaction success without instruction | At least 80 percent of first-time participants complete all three core tasks on the first attempt with no verbal or written instruction, no gesture demonstration, and no team member in the room |
| M5 | Review basis and outcome | Requirements read from the store's published spatial review material at run start, dated in the log, mapped one-to-one to a checklist item with a named owner and named evidence. No requirement is asserted from memory or from a previous submission, and the outcome is counted in unresolved rejections at exit |
| M6 | Reach envelope | Every interactive target sits between 30 cm and 60 cm from the shoulder origin, between 20 cm below and 30 cm above eye level, within 45 degrees of forward azimuth. A target outside the envelope in the smallest declared space is a design defect, not a stretch |

## Key Decisions

| Decision | Options | When | Who decides |
| --- | --- | --- | --- |
| Spatial modality per core task | Window, volume, or fully immersive | Week 1 | XR Interface Architect with UI Designer |
| Space assumption | Seated, standing, or room scale, and the minimum room that assumption implies | Week 1 | XR Interface Architect with UX Researcher |
| What degrades first when thermal or frame budget is exceeded | Material fidelity, window count, refresh rate, or immersive exit, in a fixed order | Week 3 | Spatial engineers with Performance Benchmarker |
| Second device family | Ship on one family, ship on two, or declare a universal build | Week 2 | Senior Project Manager with sign-off authority |
| Input model and its non-hand fallback | Gaze and pinch, direct touch, controller, voice, or a stated combination per task | Week 2 | XR Cockpit Interaction Specialist with Accessibility Auditor |
| Waiver for a comfort stop or reach violation | None inside the run, or a written waiver with a dated re-test before submission | Week 5 | Sign-off authority only |

## Success Criteria

| Metric | Target |
| --- | --- |
| Sustained frame rate (M1) | At least 90 fps over a continuous 20-minute session, p99 frame time at or below 13.9 ms, drop-frame tolerance held |
| Motion-to-photon latency (M2) | At most 20 ms at p95 for head motion, at most 100 ms at p95 for gaze and pinch acknowledgement |
| Comfort completion rate (M3) | At least 90 percent of first-time participants complete the 20-minute protocol with zero comfort stops |
| Interaction success without instruction (M4) | At least 80 percent of first-time participants complete all three core tasks on the first attempt |
| Reach envelope compliance (M6) | 100 percent of interactive targets inside the envelope in the smallest declared space |
| Spatial review outcome (M5) | Submission filed against the requirements read at run start, with zero unresolved rejections citing comfort, motion, or interaction at the Week 6 exit |

## Common Pitfalls

| Pitfall | Mitigation |
| --- | --- |
| Validating in the simulator, where passthrough, glass materials and real room geometry cost nothing, so the build looks comfortable and fast until it is on a head | G2 is a 20-minute session on the target device in the measured room with the measurement harness attached, and the simulator is never accepted as evidence for a frame, latency, or comfort metric |
| Placing content for one person's room: window height, depth and scale tuned to the builder's apartment, which is the only room the layout has ever been observed in | The interaction contract names a space assumption and a mismatch behaviour per task at G1, the reach sweep measures every target in the smallest declared space, and Week 5 runs in a room the team did not choose |
| An interaction that requires an unnatural reach — a grab at arm's length above the shoulder, or a two-handed gesture at full extension — because the builder could do it | The reach envelope is printed in Thresholds, the XR Cockpit Interaction Specialist measures every target against it, and M6 requires 100 percent compliance rather than an average |
| Frame rate measured over a short burst, on a cool device, before thermal throttling and before the session's real content mix, so the number is a best case | M1 and M1b are defined over a continuous 20-minute session with the thermal curve recorded, warm-up excluded and stated, and G2 requires frame rate, p99 frame time and drop-frame tolerance to hold in the same log |
| Review requirements assumed rather than read: a checklist recalled from a previous submission, a different platform, or a forum post, and discovered wrong at submission | The store's published spatial review requirements are a blocking Required Input, read and dated at run start, mapped one-to-one to checklist items with owners and evidence, and M5 measures the mapping rather than the intention |
| Testing with the team instead of first-time users, because colleagues are available and already know the gestures, so every interaction appears discoverable | The named first-time test group is a blocking Required Input, M4 forbids instruction and demonstration, and G3 is observed on a participant who did not build the app with no team member in the room |

## Post-runbook

Everything below is measured after the six weeks end and has an owner, because these are the failures that only appear in a population the run could not recruit.

| Metric | Owner | Measured on |
| --- | --- | --- |
| Crash-free sessions by device family | Performance Benchmarker | Store telemetry, segmented by device family and by session length, reviewed weekly for the first month |
| Comfort complaints reported through the store or support | UX Researcher | Support and review channels, classified against the comfort instrument's symptoms, with any comfort-stop-equivalent report escalated as a defect |
| Thermal throttling on long sessions | macOS Spatial/Metal Engineer | Sessions longer than 20 minutes in production telemetry, comparing frame-time percentiles against the M1 budget after throttling begins |
| Interaction discovery rate in the shipped build | UX Researcher | First-session task completion without instruction, from instrumentation, compared against M4 measured in the run |
| Reach and placement complaints | XR Interface Architect | Support reports naming height, distance or placement, mapped to the envelope in Thresholds before any fix is designed |
