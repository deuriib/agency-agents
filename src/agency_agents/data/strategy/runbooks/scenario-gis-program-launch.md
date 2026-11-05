# Runbook: GIS Program Launch

> **Mode**: NEXUS-Sprint | **Duration**: 6 weeks | **Agents**: 17

**Domain boundary.** A spatial deliverable is done when its coordinate reference system, geometry validity and topological consistency are verified with evidence — not when the map renders. A layer that looks right on screen and fails a topology check is a defective deliverable, not a near-miss, and it does not ship behind a cartographic apology.

## Scenario

The programme has maps, data and a deadline, and nobody can say whether any of it is correct. Layers arrive from three suppliers in three different coordinate systems, none of them announced: whoever loads a layer discovers its CRS from how it lands. A boundary that should close does not — the ring comes within a few centimetres of itself and stops, so the polygon is open at a scale nobody zooms to. The drone capture is georeferenced against a control point that was never surveyed, which makes its accuracy statement an opinion. And the map renders beautifully, because styling was the only step anybody could inspect, on top of geometry that fails a topology check.

This runbook delivers a spatial product whose correctness is verified before it is styled. Work runs in one direction — intake and spatial contract, then geoprocessing and analysis, then delivery and verification — and each phase ends at a gate that a single observation can fail. Styling, tiles and 3D scenes consume layers that already passed; they never become the place where a geometry problem is discovered.

Doctrine: one governing CRS for the whole product, no on-the-fly reprojection anywhere downstream of intake, and no accuracy number in a deliverable that was not measured against surveyed control.

## Applicability

| Use this runbook when | Use a different runbook when |
| --- | --- |
| A programme delivers a spatial product: field capture, supplier layers, geoprocessing, web maps, and a client who must accept the geometry | The platform beneath the spatial product does not exist yet — use `data-platform-foundation` |
| The acceptance question is "is this correct" — CRS, geometry, topology, positional accuracy | The repository and its governance need hardening, not the geometry — use `repository-hardening-program` |
| Layers come from more than one supplier and must be reconciled into one CRS and one data model | The map exists and must become visually systematic and accessible — use `design-system-and-ui-quality` |
| A wrong boundary, a wrong position or a leaked layer carries contractual or regulatory exposure | The platform must be secured, audited or pen-tested before delivery — use `security-posture-review` |
| An existing GIS is being replaced and its data must survive the move intact | An incumbent GIS is being retired — use `legacy-platform-migration` |

## Required Inputs

Only artifacts the roster cannot produce. The spatial contract, the intake register, the topology report, the accuracy statement, the delivered tiles and the sign-off pack are phase outputs; a runbook that lists its own outputs as inputs is asking to be blocked by itself.

| Input | Why it blocks | Owner (supplied from outside the roster) |
| --- | --- | --- |
| The authoritative source of each layer, with its lineage: origin survey or capture, capture date, processing history, licence | A layer without lineage cannot be assessed for accuracy, cannot be re-verified after a supplier refresh, and cannot be defended at sign-off | Client data owner |
| The mandated CRS and units: EPSG code, horizontal and vertical datum, linear unit, and whether the mandate is negotiable | Choosing the CRS is a client decision with legal weight; a CRS chosen by the team mid-sprint is a decision nobody authorized | Client survey authority |
| Surveyed control points for any captured imagery: ground control points and independent checkpoints with their coordinate values in the mandated CRS, plus the survey method and its accuracy | Without surveyed control, drone and photogrammetric output is georeferenced against assumption and its accuracy claim is unusable | Licensed surveyor |
| The positional accuracy tolerance the client will accept, as a number with its measurement method and confidence | Every accuracy gate compares against this number; a tolerance agreed after delivery is a renegotiation, not an acceptance | Client sign-off authority |
| One named sign-off authority with the delegation to accept the spatial product | Acceptance requires an observation by a person with the authority to make it; a committee cannot draw the G3 sample | Client executive sponsor |

## Agent Roster

Seventeen agents. Every row traces to a gate line or a Success Criteria metric; a row that traces to nothing is a passenger.

### Command (Always Active)

| Agent | Role | Proven by |
| --- | --- | --- |
| Agents Orchestrator | Gate sequencing, phase control, resolution of conflicting verdicts | G3 |
| Senior Project Manager | Spatial contract ownership, intake register, decision records, sign-off pack | G1 |
| Technical Consultant | Turns the client's decision questions into one governing CRS and a delivery specification | G1 |
| Solution Engineer | Builds the throwaway proof-of-concept that proves a candidate reprojection path before it enters the pipeline | G2 |

### Spatial Foundation (Week 1-2)

| Agent | Role | Proven by |
| --- | --- | --- |
| Spatial Data Engineer | Intake ETL, documented reprojection, attribute normalization, lineage register | G1, M1 |
| Geoprocessing Specialist | Automated validity and topology reporting, batch repair under a recorded decision, re-runnable process scripts | G1 |
| BIM/GIS Specialist | Supplied Revit/IFC assets converted to GIS features with explicit CRS and level mapping, or excluded with a written reason | G1, M2 |
| Drone/Reality Mapping Specialist | Photogrammetric processing under surveyed control only; GCP and independent checkpoint residuals reported | G1, M4 |

### Data & Analysis (Week 3-4)

| Agent | Role | Proven by |
| --- | --- | --- |
| Spatial Data Scientist | Spatial statistics and predictive analysis restricted to layers that passed G1 | G2, M4 |
| GeoAI/ML Engineer | Feature extraction and classification with a held-out validation set from surveyed or photo-interpreted truth | G2, M4 |
| GIS Analyst | Layer maintenance, spatial queries, attribute and metadata audits on every modified layer | G2, M5 |

### Delivery (Week 4-5)

| Agent | Role | Proven by |
| --- | --- | --- |
| Web GIS Developer | Map application on validated services; simplification bounded by the budget, not by how fast it feels | G3, M6 |
| 3D & Scene Developer | 3D scene, terrain and point cloud from the same validated geometry, with the vertical datum stated | G3 |
| Cartography Designer | Classification, labels, legend, scale ranges and the accuracy caveat list, applied after G2 | G3, M6 |

### Quality & Proof (Week 4-6)

| Agent | Role | Proven by |
| --- | --- | --- |
| GIS QA Engineer | Topology sweep, CRS consistency, metadata audit, accuracy assessment, evidence pack | G3, M3 |
| Evidence Collector | Records the observation behind each gate: check logs, CRS reports, RMSE tables, delivered-product screenshots | G3 |
| Reality Checker | Independent blind re-run of a sample of G3 passes; default verdict NEEDS WORK | G3 |

## Week 1-2: Data Intake & Spatial Contract

Intake freezes once. Every raw layer is copied read-only into an intake snapshot with an ID, and every later product cites that ID, so an analysis defect can be traced to the layer that caused it rather than to the analyst who ran it.

```text
├── Spatial Data Engineer → intake register per layer: authoritative source, lineage,
│   declared CRS as supplied, feature count, units, licence
├── Spatial Data Engineer → freeze the raw layers read-only as the intake snapshot;
│   the snapshot ID goes on every downstream artifact
├── Spatial Data Engineer → reproject the snapshot into the governing CRS with the
│   documented transformation and its parameters; 0 on-the-fly reprojection downstream
├── Spatial Data Engineer → attribute normalization against the data dictionary;
│   unmapped attributes are recorded as gaps, not dropped silently
├── Geoprocessing Specialist → validity and topology report over the reprojected set:
│   ring closure, self-intersection, overlap, gap, dangle, sliver, duplicate vertex
├── Geoprocessing Specialist → supplier defect report per layer with counts and feature
│   IDs, returned for re-acquisition or repaired under a recorded Key Decision
├── BIM/GIS Specialist → supplied BIM/IFC converted with explicit CRS and level mapping,
│   or excluded from the product with a written reason and a named owner
├── Drone/Reality Mapping Specialist → photogrammetric run against surveyed control only;
│   GCP and independent checkpoint residuals reported per axis
├── Technical Consultant → delivery specification: governing CRS, accuracy statement
│   format, topology definition, layers in scope, layers excluded
├── Senior Project Manager → spatial contract v1.0 dated and signed by the sign-off authority
└── Quality Gate (G1): replay the intake check on the frozen snapshot and read three
    counts — layers whose declared CRS differs from the governing CRS, layers below the
    intake validity rate, layers with no accuracy statement and no written exception.
    A single unexcused layer in any of the three fails G1.
```

## Week 3-4: Geoprocessing & Analysis

Analysis is where a bad intake decision becomes an invisible defect: a buffer computed on an unprojected layer, a spatial join across two datums, a classification trained on unverified labels. Every analysis product therefore carries the CRS, the units and the snapshot ID it derives from, and one product is re-run independently from the snapshot before anything is styled.

```text
├── Geoprocessing Specialist → versioned, re-runnable process per analysis product, with
│   parameters pinned to the spatial contract rather than to session state
├── GIS Analyst → layer edits and maintenance inside the governing CRS; attribute and
│   metadata audit on every modified layer, not on a sample of layers
├── Spatial Data Scientist → statistics and predictive models on G1-passed layers only;
│   excluded layers named in the output note, never quietly substituted
├── GeoAI/ML Engineer → extraction and classification against a held-out validation set
│   from surveyed or photo-interpreted truth; confusion matrix and sample size reported
├── Spatial Data Scientist → every output written with CRS, units, provenance and the
│   intake snapshot ID it derives from
├── Solution Engineer → independent re-run of one analysis product from the frozen
│   snapshot on a clean environment, compared feature by feature with the release
├── GIS Analyst → change log: what geometry moved, by how much, under which decision
├── Senior Project Manager → decision record for every layer that could not meet the
│   tolerance, including whether it ships and under what caveat
└── Quality Gate (G2): diff the independent re-run of one analysis product against the
    release and read the mismatch count across feature identity, geometry, attribute
    value, CRS and units. A single unexplained mismatch fails G2.
```

## Week 5-6: Delivery & Verification

The delivery track opens in Week 4 on layers that already passed G1; the verification track runs through Week 6. Nothing is styled before G2 — a design decision made over unverified geometry is a decision that will be made twice.

```text
├── Web GIS Developer → map application served from the validated layer set; tile and
│   feature simplification bounded by the simplification budget
├── 3D & Scene Developer → 3D scene, terrain and point cloud from the same validated
│   geometry; vertical datum stated in the scene metadata
├── Cartography Designer → classification, labels, legend, scale ranges and the accuracy
│   caveat list applied after G2
├── GIS QA Engineer → accuracy assessment against surveyed control: horizontal and
│   vertical RMSE on a blind sample drawn from the delivered set
├── GIS QA Engineer → final topology and CRS sweep on the delivered artifacts, including
│   the tiled and exported form, not only the working source
├── GIS QA Engineer → metadata audit: CRS, lineage, accuracy statement and licence on
│   100% of delivered layers
├── Evidence Collector → evidence pack per gate: check logs, CRS reports, RMSE tables,
│   delivered-product screenshots, caveat list
├── Cartography Designer + Web GIS Developer → known-gap layers rendered behind the
│   documented warning, or withheld per Key Decisions
├── Reality Checker → independent blind re-run of a sample of delivered layers; verdict
│   PASS or NEEDS WORK, default NEEDS WORK
└── Quality Gate (G3): the sign-off authority draws one feature blind from the delivered
    set and compares its delivered position with the surveyed position and with the
    stated accuracy number. A miss beyond tolerance, or an accuracy claim with no
    measurement behind it, fails G3.
```

## Thresholds

Every number a gate can fail on lives here once; the gates cite this table. Scenario counts (three suppliers, three CRSs) and the 6-week window are intake facts and schedule, not tolerances. A new number in a gate is added here first.

| Threshold | Value | Bound by |
| --- | --- | --- |
| Governing CRS | Exactly 1 CRS, mandated in Required Inputs, carried by every stored geometry | 0 layers stored in any other CRS |
| Projection mismatch policy | A layer is in mismatch when its declared CRS differs from the governing CRS, when the declaration is absent, or when a reprojection round trip returns a residual above 0.001 m | Blocked from the product until resolved; 0 tolerated |
| Minimum geometry validity rate | 100% of features in the delivered set pass an OGC validity check | Intake rejection threshold: a supplier layer below 98% valid goes back to the supplier instead of entering the repair queue |
| Positional accuracy tolerance | Client-declared. Absent a declaration, 0.50 m horizontal RMSE for accuracy-carrying layers and 2.00 m for context layers; a stricter declared value governs | Reported as RMSE plus sample size plus method |
| Sliver tolerance | A polygon fragment with area below 1.0 m² and mean width below 0.10 m | 0 slivers in the delivered set |
| Topology failure | Any of: unclosed ring, self-intersection, gap above 0.01 m² where coverage is declared, overlap above 0.01 m² within one planar layer, line endpoint not coincident within 0.001 m with the feature it joins, duplicate vertex, zero-length segment | 0 in the delivered set, counted on delivered artifacts |
| Drone capture control | Ground control points at least 5; independent checkpoints at least 3 not used in the bundle adjustment; checkpoint residual at most 0.03 m horizontal and 0.05 m vertical | Below this the capture is labeled unverified and carries no accuracy claim |
| Simplification budget | Vertex deviation introduced by any simplification at most 0.50 × the positional accuracy tolerance at the maximum delivery scale | 0 features and 0 tiles outside the budget |
| Map performance | First map paint at most 3.0 s and p95 interaction frame at most 100 ms on the declared reference device and connection | Measured on the delivered build with real geometry, never on a sample-free mockup |
| Accuracy sample size | At least 30 features or 5% of the layer, whichever is larger, drawn blind | Reported alongside the RMSE |
| Metadata completeness | CRS, lineage, accuracy statement, licence and capture date on every delivered layer | 100%; a layer missing one field is not delivered |
| Sign-off authority | Exactly 1 named person | G3 requires that person's own observation |

## Key Decisions

| Decision point | When | Who decides |
| --- | --- | --- |
| Which CRS governs the product, and whether the mandate is accepted or renegotiated | Week 1, before G1 | Technical Consultant + sign-off authority |
| Reproject a mismatched supplier layer or re-acquire it at source | Week 1-2, per layer | Spatial Data Engineer + Senior Project Manager, with re-acquisition treated as a schedule decision |
| What to do when a supplier layer cannot meet the accuracy tolerance: reject, repair, or accept with a recorded exception and a stated caveat | Week 2, per layer | GIS QA Engineer on measurement + sign-off authority |
| Whether a known-gap layer ships behind a warning or is withheld from the product | Week 5, before G3 | Sign-off authority on the QA evidence |
| The delivery scale, the reference device and the simplification budget they imply | Week 3, before delivery starts | Cartography Designer + Web GIS Developer |
| A layer whose accuracy cannot be measured before the deadline: ship it unclaimed, or not at all | Week 6 | Sign-off authority |

## Success Criteria

Measured inside the 6-week window, so every target is countable before handover.

| Metric | Target |
| --- | --- |
| M1 · Delivered layers in the governing CRS, declared and verified | 100%, with 0 reprojection at read time |
| M2 · Features passing geometry validity in the delivered set | 100% |
| M3 · Topology failures in the delivered artifacts | 0, counted on the delivered and tiled form |
| M4 · Accuracy-carrying layers measured against surveyed control | 100%, sample at least 30 features or 5% |
| M5 · Delivered layers with complete metadata | 100% of CRS, lineage, accuracy statement, licence, capture date |
| M6 · Delivered map inside the simplification and performance budgets | 0 features outside deviation; first paint at most 3.0 s on the reference device |

## Common Pitfalls

| Pitfall | Mitigation |
| --- | --- |
| Styling before validation: the legend is designed, the client is pleased, and the geometry underneath was never checked | G2 blocks delivery work; Cartography Designer starts in Week 4 on G1-passed layers only, and the map spec records the accuracy caveat per layer |
| Silent on-the-fly reprojection: a service, a tile cache or a desktop session reprojects at read time, so the delivered position differs from the verified position | One reprojection happens at intake with a documented transformation; M1 requires 0 reprojection at read time and G3 re-checks position on the delivered artifact, not the source |
| A boundary that closes visually but not topologically: the ring comes within centimetres of itself, the fill looks solid, and every area, containment and adjacency query is wrong | G1 counts unclosed rings on the frozen snapshot and the topology sweep runs again on the tiled output, so a renderer that hides the defect does not hide the count |
| Drone imagery georeferenced without surveyed control, producing an orthomosaic whose accuracy statement nobody can defend | Required Inputs make surveyed control blocking; the Drone/Reality Mapping Specialist reports checkpoint residuals, and a capture below the control threshold is labeled unverified and carries no accuracy claim |
| A web map that feels fast because the geometry was simplified past the accuracy tolerance — the speed is the defect | Simplification is bounded at 0.50 × the accuracy tolerance at the maximum delivery scale, and performance is measured on the delivered build with real geometry |
| An accuracy claim nobody measured: a number in the metadata inherited from a supplier's brochure | G3 makes the sign-off authority draw one feature blind and compare it with surveyed control; an unmeasured claim fails the gate, and M4 requires the sample size to be reported |

## Post-runbook

Metrics whose measurement window exceeds the runbook.

| Metric | Owner | Measured on |
| --- | --- | --- |
| Data currency: share of delivered layers whose capture date is inside the programme's stated currency window | Spatial Data Engineer | Quarterly, from the lineage register |
| Drift after supplier refresh: features changed plus new validity and topology failures after a supplier re-delivery | GIS QA Engineer | Every supplier refresh, within 5 business days |
| User adoption of the delivered product: active users against the target agreed at handover | Senior Project Manager | Monthly for the first 6 months |
| Accuracy drift: re-measured RMSE against surveyed control on a blind sample | GIS QA Engineer | Annually, and after any re-acquisition |
| Known-gap layers still shipping behind a warning | Senior Project Manager | Quarterly until each one is closed or withdrawn |
