# Runbook: Game Launch

Mode: NEXUS-Sprint | Duration: 6 weeks | Agents: 16

## Scenario

The game is fun in the editor and broken on the target hardware. An artist's asset imports differently on a colleague's machine, because the import settings live in a conversation rather than in the project. The economy curve was tuned by feel and collapses at hour three, once the second currency unlocks and one faucet compounds with no sink. Audio clips in the busiest scene, where the voice count was never bounded. The localisation string table overflows every button, because the keys were written at English length and the longest locale was never loaded. And the platform certification requirements are being read for the first time inside the submission form.

None of that is polish. Each one is a gate that was never installed, and each one is discovered at the most expensive moment to fix it. This runbook takes a game to a store release with three gates: the content pipeline reproduced from a clean machine by someone who is not the artist who authored the asset, every performance and quality budget measured on the minimum specification in a packaged build rather than in the editor, and certification evidence collected per published checklist item before the submission form is opened.

Doctrine: **a content pipeline that has only ever been run by its author is not a pipeline; a frame rate measured in the editor is not a frame rate; certification requirements are inputs read from the platform's current published rules, never assumptions.** An assumption about certification is a schedule risk, and this runbook does not invent platform policy.

Scope is one store release: content pipeline, build, tuning evidence, localisation set, accessibility surface and submission package. It is not live-service operations after launch, not a storefront growth programme, and not engine architecture.

## Applicability

| Use this runbook when | Use a different runbook when |
| --- | --- |
| A game is going to a store release and platform certification is in scope | The product is a utility app rather than a game — use `mobile-app-launch` |
| The content pipeline must be reproduced from a clean machine by someone who is not the asset's author | The product is an XR title whose comfort, latency and occlusion budgets are the release risk — use `spatial-app-launch` |
| Frame rate, load time, crash-free sessions and localisation are release gates, not polish | The work is interface consistency inside an already-shipping product — use `design-system-and-ui-quality` |
| An economy curve and a difficulty curve must survive real play at hour three, not one afternoon of testing | The game is live and the work is a routine update cycle — use `release-train` |
| The age rating and the certification checklist are inputs that constrain content before the schedule is committed | You are still deciding what the game should be — use `feature-discovery-to-spec` first, which decides and does not ship |

## Required Inputs

Only what the roster cannot produce. The build, the tuning report, the localisation set and the submission package are **outputs** of this runbook, never inputs to it.

| Input | Why it blocks | Owner (supplied from outside the roster) |
| --- | --- | --- |
| The target platform or platforms, and each platform's current published certification requirements, quoted with the checklist version and its publication date | The checklist is a binding input; a version that is not quoted cannot be evidenced against, and a checklist memory is a schedule risk | Publisher or platform-relations owner |
| The target hardware and a declared minimum specification: exact CPU, GPU, memory, storage and target display, plus at least one physical device at that floor | Frame, load and memory budgets are meaningless without a floor, and a floor discovered in Week 3 invalidates every measurement taken before it | Technical director |
| The content pipeline's source assets: art source files, audio source sessions and tracks, and the engine project with the asset tree | The pipeline gate rebuilds from source; an asset that exists only as an imported binary cannot be reproduced from a clean machine | Art and audio leads |
| The localisation string set as it exists now, plus the languages committed for launch and any contractual or legal language obligation | The committed locale count sets the UI length budget and the certification surface; adding a locale after Week 4 is out of scope by construction | Product owner + localisation vendor |
| An age-rating determination from the relevant rating board for the launch content | The rating constrains content and storefront metadata, and a rating pending at submission blocks the release for reasons no agent can resolve | Publisher or legal |
| A named sign-off authority with written power to cut scope, hold a gate and move a launch window | A gate with nobody to fail to is a status report; the day a budget misses is the day that authority must already exist | Studio leadership |

Content decisions that the roster can make — what to cut when the frame budget fails, which locales ship complete, what a day-one patch may contain — are decisions, not inputs. They are recorded in Key Decisions with a default that holds while unresolved.

**Domain boundary.** Certification requirements are inputs read from the platform's current published rules. They are never assumptions, never inferred from a similar game, and never reconstructed from a forum thread or a previous project. This runbook does not invent platform policy: where a published checklist item is ambiguous, the item is quoted verbatim, the interpretation question is raised through the platform's stated developer support channel, and the answer is recorded with a date and a link. An assumption about certification is a schedule risk carried by the whole release, and it is the single most common way a finished game misses its window while remaining technically correct.

## Thresholds

Every number a gate uses is defined here. A gate that cites a number not in this table is void.

A **capture** is a recorded run of a named scene on a named device with a named build id, from which frame-time percentiles, load timings, memory and audio events are read. Editor statistics, a stationary camera, and a developer workstation are not captures and cannot satisfy a gate.

A **clean machine** is a machine that has never opened the project: no cached imports, no local override files, no editor preferences inherited from an artist's workstation. The pinned toolchain and importer version are installed from the repository, not from a colleague's drive.

| ID | Threshold | Value | Enforced at |
| --- | --- | --- | --- |
| T1 | Clean-machine pipeline reproduction | Every asset in the manifest imports, builds and packages on a clean machine operated by someone who is not the asset's author, and the result matches the recorded manifest hash. Zero assets that need a manual step, a locally edited setting, or the author present | G1 |
| T2 | Sustained frame rate on minimum specification | 10-minute capture in each of the three busiest scenes: average ≥ 30 fps, 1% low ≥ 24 fps, and 0 frames longer than 100 ms anywhere in the capture | G2 |
| T3 | Load time budget | Cold boot to first interactive menu ≤ 25 s; any level load ≤ 12 s; 0 loads beyond 30 s on the minimum specification | G2 |
| T4 | Crash-free session rate | ≥ 99.5% of sessions complete without a crash, over ≥ 500 sessions of the certification-candidate build on the device matrix, of which ≥ 100 are on minimum specification; and 0 crashes in the 30-minute soak per scene | G3 |
| T5 | String overflow tolerance | 0 clipped, truncated or silently ellipsised strings in any committed locale, evaluated per key at the longest value that locale produces. One clipped glyph in one locale is one failure | G2, G3 |
| T6 | Certification checklist pass requirement | 100% of items in the current published checklist carry a recorded observation taken from the certification-candidate build. 0 items recorded as assumed, untested, not applicable without the platform's own written statement, or deferred to a day-one patch | G3 |
| T7 | Audio stability and true peak | 10-minute capture in the busiest scene: 0 dropped voices, 0 buffer underruns, 0 click artefacts at scene transitions, and mixed true peak ≤ −1 dBFS on the master bus | G2 |
| T8 | Economy behaviour at hour three | The simulated hour-three balance sits within ±10% of the designed curve target, every source has at least one sink, and 0 compounding loops survive across the 10-hour simulation | G2 |

T5 is measured from a UI capture set, not from a spreadsheet: every screen that renders text is captured in every committed locale at the longest value per key, and the images are the evidence. T6 is measured per item, so a checklist with 40 items and 39 observations fails by one row.

## Agent Roster

Every row carries the gate or threshold that fails when that agent's work is missing.

### Command (Always Active)

| Agent | Role | Proven by |
| --- | --- | --- |
| Agents Orchestrator | Phase gating, gate re-runs, the decision to hold the window instead of weakening a gate | G1, G2, G3 |
| Senior Project Manager | Certification checklist decomposed into owned tasks with evidence fields, cut list, decision log, submission calendar | G1, G3, T6 |
| Game Designer | Core loop and fun hypothesis, difficulty curve, the ordered cut list that applies when a budget misses | G2, T8 |

### Content & Systems (Week 1-2)

| Agent | Role | Proven by |
| --- | --- | --- |
| Level Designer | Three busiest scenes rebuilt from source assets only; pacing and difficulty read at hour three | G1, G2, T8 |
| Narrative Designer | Every line of copy authored as a string key from the first commit; locale context notes for translators | G1, T5 |
| Economy Designer | Sources, sinks, curve targets in 1-hour, 3-hour and 10-hour form; 10-hour simulation; exploit enumeration | G2, T8 |

### Build & Art (Week 2-4)

| Agent | Role | Proven by |
| --- | --- | --- |
| Technical Artist | Import settings per asset class committed into the project, pinned importer version, asset hash manifest, per-platform compression and memory budget | G1, T2 |
| Game Audio Engineer | Bus layout with a hard voice limit, priority and virtualisation rules, streaming, master true-peak discipline | G2, T7 |
| Backend Architect | Save integrity across a build swap, offline behaviour, entitlement checks where the published rules require them; or an explicit recorded "no online services" | G2, T4 |

### Certification & Quality (Week 4-6)

| Agent | Role | Proven by |
| --- | --- | --- |
| Performance Benchmarker | Capture rig on the floor device, frame-time percentiles, load timings, memory, soak runs | G2, T2, T3, T4 |
| Evidence Collector | One evidence record per checklist item, each traceable to a build id and a device, plus the gate log and package index | G1, G2, G3 |
| Reality Checker | Clean-install pass on a store-like build, adversarial pass on the candidate, final verdict (default: NEEDS WORK) | G3, T4 |
| Accessibility Auditor | Remapping, subtitle presentation with speaker identity and size options, colour-independent gameplay cues, store-claim accuracy | G2, G3 |

### Launch (Week 5-6)

| Agent | Role | Proven by |
| --- | --- | --- |
| App Store Optimizer | Store page, screenshots and metadata rendered from the candidate build in every committed locale | G3, T5 |
| DevOps Automator | Reproducible build CI, versioning and build numbering, candidate promotion, rollback, patch pipeline | G1, G3 |
| Mobile Release Engineer | Signing, store package, submission form, rating certificate attachment, rejection triage and response | G3, T6 |

## Week 1-2: Content Pipeline & Systems

No budget is measured in this phase. A frame rate measured before the pipeline is closed is a measurement of whichever workstation happened to build the scene.

```text
Week 1: One pipeline, one truth
├── Technical Artist → import settings per asset class committed into the project:
│   texture compression per platform, mesh scale and axis convention, LOD and collider
│   policy, audio import rates, with the importer version pinned in the repository
├── Technical Artist → asset hash manifest: every imported asset records source path,
│   importer version, settings hash and per-platform variant
├── Level Designer → the three busiest scenes rebuilt from source assets only; no
│   hand-edited binary, no asset that exists on exactly one workstation
├── Narrative Designer → every line of copy becomes a string key in the table in the
│   same commit that introduces it; hard-coded text in a scene fails the gate
├── Game Designer → core loop, fun hypothesis, difficulty curve, and an ordered cut
│   list with the date on which the cut decision is taken
├── Senior Project Manager → the current published certification checklist imported as
│   tasks, one owner and one evidence field per item, plus its version and date
├── Backend Architect → online scope recorded as named services or as an explicit
│   "none", with save integrity and offline behaviour decided where services exist
├── Evidence Collector → manifest hash, build ids, toolchain lockfile and the commit
│   that froze them

Week 2: Reproduce it somewhere else
├── DevOps Automator → CI job that installs the pinned toolchain from the repository
│   and runs import, build and package with no manual step
├── Technical Artist → a second workstation and the build agent both produce a build
│   whose content hash matches the manifest
├── Economy Designer → sources, sinks and curve targets at hour one, hour three and
│   hour ten, with the simulation that reads them committed alongside
├── Level Designer → onboarding and first ten minutes playable end to end on the floor
│   device, using only pipeline-built assets
├── Narrative Designer → string table loaded with a placeholder locale to prove the
│   table, not the code, owns every visible glyph
└── Quality Gate (G1): the pipeline reproduces on a clean machine that has never
    opened the project, operated by an engineer who is not the artist who authored
    the asset (T1). It fails on (1) one asset that rebuilds only on the author's
    machine, (2) one import setting that lives outside the repository, (3) one scene
    referencing an asset with no source path in the manifest, (4) one line of copy in
    a scene that is not a string key, and (5) a build on the build agent whose
    content hash differs from the same commit on the second workstation.
```

The G1 operator is chosen in Week 1 and is never the artist who authored the assets under test. When the only person who can build the game is the person who made its art, the pipeline does not exist yet — it is a person.

## Week 3-4: Build, Tune & Localise

Every number in this phase comes from a capture on the declared floor device, from a packaged build, with the recording retained.

```text
Week 3: Measure on the floor, not in the editor
├── Performance Benchmarker → capture rig on minimum specification: frame-time
│   percentiles per scene, load timings, peak and steady memory, thermal behaviour over
│   the full capture
├── Technical Artist → per-platform compression applied to the whole asset set, with a
│   memory report per scene against the floor's declared budget
├── Game Audio Engineer → hard voice limit with priority and virtualisation rules,
│   music and ambience streaming, master bus true-peak discipline under load
├── Level Designer → pacing and difficulty read from a real hour-three playthrough, not
│   from the design document
├── Accessibility Auditor → remappable controls, subtitle presentation, colour-
│   independent gameplay cues, and readable text at the smallest supported size
├── Backend Architect → save integrity across a candidate build swap, offline path, and
│   entitlement checks where the published rules require them

Week 4: Tune, localise, enumerate what can be exploited
├── Economy Designer → 10-hour simulation: every source has a sink, the second
│   currency does not compound, hour-three balance sits on its designed target
├── Economy Designer → exploit enumeration: dupe, offline-time, save edit, bot loop,
│   store refund path; each recorded as fixed, gated, or accepted with an owner and a
│   fix date
├── Narrative Designer → full string table in every committed locale with context
│   notes for gender, plural and case
├── App Store Optimizer → store metadata and screenshots in every committed locale
├── Level Designer → UI capture set: every text-bearing screen, every locale, longest
│   value per key
├── Game Audio Engineer → busiest-scene capture with the voice limit under real load
├── Performance Benchmarker → second capture pass after tuning, on the same rig, so
│   the delta is comparable
├── Evidence Collector → evidence record per item: build id, device, capture, date
└── Quality Gate (G2): the packaged build holds every budget on minimum-specification
    hardware, measured by capture and not by editor statistics — T2 sustained frame
    rate, T3 load times, T5 zero clipped strings in every committed locale, T7 audio
    stability and true peak, T8 economy at hour three. It fails on (1) one scene below
    T2 at any point in the capture, (2) one load past T3, (3) one clipped or
    ellipsised string in one locale on one screen, (4) one dropped voice, underrun or
    a mixed peak above T7, and (5) one hour-three simulation outside T8 or one
    compounding loop surviving it.
```

When G2 fails on frame rate, the cut list from Week 1 applies in its written order. Re-tuning the scene until the capture passes, without cutting, is how a game ships at the edge of its budget and then misses it on the second device model.

## Week 5-6: Certification & Launch

Certification work starts in Week 1 as a checklist with owners. This phase is where the observations are made and attached, not where the checklist is discovered.

```text
Week 5: Candidate build and certification evidence
├── Mobile Release Engineer → signing, store package, store-side configuration, and the
│   submission form filled from the published checklist rather than from memory
├── Performance Benchmarker → 30-minute soak per scene with memory and thermal trace
├── Evidence Collector → one evidence record per checklist item, each with a build id,
│   a device model and a date; the package index maps item to record
├── Reality Checker → clean-install pass on a store-like build on the floor device, and
│   an adversarial pass on save corruption, resume from suspend and storage-full states
├── Accessibility Auditor → the store page's accessibility claims checked against what
│   the candidate build actually does
├── App Store Optimizer → listing, screenshots and metadata frozen from the candidate
├── Economy Designer → exploit register reviewed against the candidate build

Week 6: Prove it, then submit
├── Reality Checker → closed beta on the certification candidate, crash-free
│   sessions read by device model with the floor devices reported separately
├── DevOps Automator → candidate promotion and rollback in one command; the exact
│   submitted binary is rebuildable from a tagged commit
├── Mobile Release Engineer → age-rating certificate attached, locale set submitted,
│   submission evidence pack attached per published requirements
├── Senior Project Manager → rejection triage plan assigned before submission, with a
│   named responder and a response window
├── Agents Orchestrator → hold-or-submit decision recorded against T6, never against
│   the calendar
├── Evidence Collector → final package: gate log, per-item certification evidence,
│   crash-free ledger, locale capture set, exploit register
└── Quality Gate (G3): every item in the current published certification checklist
    carries a recorded observation from the certification-candidate build (T6), the
    candidate meets T4 crash-free sessions, and the submission package index is
    complete. It fails on (1) one item recorded as assumed, untested or deferred to a
    day-one patch, (2) one evidence record not traceable to a build id and a device
    model, (3) crash-free sessions below T4, (4) one committed locale with no UI
    capture set or no store metadata, and (5) one T5 failure reintroduced by a
    late string change after the last capture set.
```

A rejection after submission is answered from the evidence pack, item by item, against the same checklist version the submission was built to. Re-submitting a candidate whose checklist version has changed means the changed items are re-evaluated before the next submission, not after.

## Key Decisions

| Decision Point | When | Who Decides | Default while unresolved |
| --- | --- | --- | --- |
| The minimum specification: exact CPU, GPU, memory, storage and display floor, and which physical device represents it | Week 1 | Senior Project Manager + Performance Benchmarker | The slowest device the studio physically owns, declared in writing and used for every capture; no lower device is promised to players or to the store page |
| What gets cut when the frame budget fails on the floor device | Decided by Week 4, applied on failure | Game Designer + Technical Artist | Cut in the written order — VFX density, then shadow and post-process quality, then resolution scale, then scene content — cheapest to reverse first, content last |
| Whether to ship with a known economy exploit | Week 4, reviewed Week 5 | Economy Designer + Senior Project Manager | Not shipped. An accepted exploit carries an owner, a detection signal and a fix date inside the first patch window; "players will not find it" is not an acceptance |
| Localisation scope: which locales ship at launch and which follow | Week 1, from the committed language requirement | Senior Project Manager + Narrative Designer | Fewer locales complete rather than more locales partial; a locale ships only with a full string table and a UI capture set meeting T5 |
| The launch window relative to certification lead time | Week 2, before the submission slot is booked | Senior Project Manager + Mobile Release Engineer | Window = the platform's current published review time + one full rejection-response cycle, counted from G3 evidence complete; if the window cannot hold that, the window moves and the gate does not |
| What a day-one patch may contain | Week 5 | Mobile Release Engineer + Senior Project Manager | Only items that are not certification-relevant and were already verified in the candidate; no checklist item is ever deferred into it |

## Success Criteria

| Metric | Target |
| --- | --- |
| T1 Clean-machine pipeline reproduction | 3 of 3 named assets imported, built and packaged on a machine that has never opened the project, by an engineer who is not their author, matching the recorded manifest hash |
| T2 Sustained frame rate on minimum specification | Average ≥ 30 fps and 1% low ≥ 24 fps across 10-minute captures in the three busiest scenes, with 0 frames longer than 100 ms |
| T3 Load time budget | Cold boot to first interactive menu ≤ 25 s, any level load ≤ 12 s, 0 loads beyond 30 s on the floor device |
| T4 Crash-free session rate | ≥ 99.5% over ≥ 500 sessions of the certification candidate, ≥ 100 of them on minimum specification, 0 crashes in the 30-minute soak |
| T5 String overflow tolerance | 0 clipped, truncated or ellipsised strings in every committed locale at the longest value per key |
| T6 Certification checklist | 100% of current published checklist items pass with a recorded observation from the candidate build, 0 items assumed |

Every row is measured inside the 6 weeks from evidence retained by the Evidence Collector. A row with no capture, no build id or no device model is not measured, and an unmeasured row cannot be reported as met.

## Common Pitfalls

| Pitfall | Mitigation |
| --- | --- |
| A content pipeline that works only on the artist's machine, because import settings were edited locally and the build depends on a cache nobody committed | Settings per asset class live in the repository with the importer version pinned, G1 runs on a clean machine that has never opened the project, and the operator is deliberately not the artist who authored the asset (T1) |
| Frame rate measured in the editor, on a workstation, with the profiler attached and a camera pointed at an empty corridor | T2 is read from a packaged build on the declared floor device by the Performance Benchmarker's capture rig, and G2 fails on a single frame longer than 100 ms anywhere in a 10-minute capture |
| An economy tuned by feel and untested at hour three, where the second currency unlocks and one faucet compounds with no sink | The Economy Designer commits a 10-hour simulation with hour-one, hour-three and hour-ten targets, and G2 fails on any hour-three balance outside ±10% or any surviving compounding loop (T8) |
| Certification read at submission, in the form, by whoever is filling the form, against a checklist version that is not the one the build was made for | The current published checklist is a Required Input quoted with its version and date, decomposed into owned tasks in Week 1, and G3 fails on one item without a recorded observation from the candidate build (T6) |
| Localisation strings that overflow the UI, because keys were written at English length and the longest locale was only loaded after the layout was frozen | Copy is authored as string keys from the first commit, the UI capture set covers every text-bearing screen in every committed locale, and G2 and G3 both fail on one clipped or silently ellipsised string (T5) |
| A day-one patch used as a substitute for a certification pass, so the submitted binary was never the verified binary | G3 fails on any checklist item deferred to a day-one patch, and DevOps Automator makes the exact submitted binary rebuildable from a tagged commit; the patch pipeline carries only non-certification-relevant work |

## Post-runbook

Metrics whose window is longer than 6 weeks are owned commitments with a date, never closed results above.

| Metric | Owner | Measured on |
| --- | --- | --- |
| Retention at day 7 and day 28 by cohort, read against the designed progression curve from T8 and segmented by minimum-specification devices | Economy Designer | Handover + 28 days, then monthly |
| Refund rate by platform, device model and locale, investigated when one device or one locale dominates the population | Mobile Release Engineer | Handover + 30 days, then monthly |
| Crash-free sessions by device model, with minimum-specification and low-memory devices reported separately from the rest of the matrix | Performance Benchmarker | Weekly from launch, handover + 90 days |
| Review score by locale and store, read alongside store metadata and screenshot changes so a score move is attributable | App Store Optimizer | Handover + 30 days, then monthly |
| Patch cadence and the certification lead time actually observed on the first post-launch patch, against the lead time assumed in the Key Decisions window | DevOps Automator | First patch after launch, then per patch |
