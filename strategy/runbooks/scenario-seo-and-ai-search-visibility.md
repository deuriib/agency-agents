# Runbook: SEO & AI Search Visibility

Mode: NEXUS-Sprint | Duration: 6 weeks | Agents: 16

## Scenario

Buyers no longer start at a search box. They ask a model, and it answers with three brands it trusts — or none. The site is indexable but has no structured data, the content never answers the questions people type, and nobody can prove whether an AI cites the company or a competitor.

Two surfaces:

- **Classic SEO** optimizes a **ranked list of links**: a position on a SERP.
- **Answer-engine optimization (AEO/GEO)** optimizes to be the **cited source inside a generated answer**: a citation, brand named and linked.

Different surface, different evidence, same content foundation: an answer engine can only cite text it can fetch and parse, so what is never published in text is never available to it.

**Non-negotiable: no visibility claim ships without a dated capture set of the actual surface, sampled at least three times per prompt per surface.** Answer surfaces are non-deterministic; run-to-run citation churn is large enough that a single before-and-after pair cannot separate a real change from sampling noise. A ranking report is not evidence. One captured answer is not evidence either. A delta is a result only when it exceeds the noise band measured in Phase 1.

## Applicability

| Use this runbook when | Use a different runbook when |
| --- | --- |
| Discoverability and citation, not reach | Reach — use `marketing-campaign`; no visibility measurement |
| A model's answer should name the brand | Interface quality — use `design-system-and-ui-quality` |
| Content must become answerable, structured | Developer docs — use `api-platform-launch` |
| Organic and AI answers are the main surface | Paid budget split — use `paid-media-launch` |

## Required Inputs

Only what the roster cannot produce. The prompt allowlist is not an input; it is a Phase 1 output.

| Input | Why it blocks | Owner |
| --- | --- | --- |
| Access to the surfaces: SERP tooling plus each named answer surface, signed in where required | An unauthenticated or blocked session records a degraded surface, not the buyer's | SEO Specialist |
| Crawl and index access (Search Console or equivalent, sitemap, robots.txt) | Index health is the Phase 1 record; without it "indexed" is an assumption | SEO Specialist |
| Analytics and CRM export, 12 months, branded vs non-branded split | No dated before-state; "improved" is unfalsifiable | Analytics Reporter |
| Real customer-question corpus: support tickets, sales calls, site search logs | Invented keywords measure the team's assumptions, not buyer language | Trend Researcher |
| A named human with authority to approve external claims | No agent in the roster may approve a claim; without a name, nothing publishable ships | Business owner |
| A named site owner who signs the per-crawler allow/block policy | Crawler access is a licensing and reputation decision, not an agent default | Site owner |

## Agent Roster

16 agents. `Proven by` names the gate (G1-G4) or leading indicator (L1-L5, Success Criteria) that fails without that agent — every row is traceable.

### Strategy & Governance (Always Active)

| Agent | Slug | Role | Proven by |
| --- | --- | --- | --- |
| Agents Orchestrator | agents-orchestrator | Phase gating, evidence-pack assembly, one passing route per phase | G4 |
| SEO Specialist | marketing-seo-specialist | Query map, rank sampling, index health, monitoring handoff | L4 |
| AEO Foundations Architect | marketing-aeo-foundations | Crawler policy implementation, text-rendering path | G2 |
| AI Citation Strategist | marketing-ai-citation-strategist | Prompt freeze, sampling design, citation deltas against the noise band | L2 |
| Trend Researcher | product-trend-researcher | Question corpus to intent clusters with a source per cluster | L3 |
| Legal Compliance Checker | support-legal-compliance-checker | Prepares the cited claim package (claim text, source, jurisdiction, risk note) for the named human approver; advises on crawler licensing and jurisdiction; **approves nothing** | G3 |

### Technical Foundation (Phase 2)

| Agent | Slug | Role | Proven by |
| --- | --- | --- | --- |
| Frontend Developer | engineering-frontend-developer | Crawlable HTML, canonicals, hreflang, CWV on cluster pages | G2 |
| CMS Developer | engineering-cms-developer | Structured data emitted from typed fields, one validated emitter per type | L5 |
| Technical Writer | engineering-technical-writer | Entity definitions, glossary, technical docs — not the marketing answer-first page | G2 |

### Content & Authority (Phase 3)

| Agent | Slug | Role | Proven by |
| --- | --- | --- | --- |
| Content Creator | marketing-content-creator | The answer-first page itself: answer, evidence, next question | L1 |
| Agentic Search Optimizer | marketing-agentic-search-optimizer | WebMCP pass/fail per task an agent must complete | G3 |
| PR & Communications Manager | marketing-pr-communications-manager | Corroboration per cluster: reviews, directories, third-party mentions with URL and date | G3 |
| Visual Storyteller | design-visual-storyteller | One extractable artifact per cluster: comparison or pricing table as real HTML, annotated spec as image plus table | G3 |

### Measure & Prove (Phase 4)

| Agent | Slug | Role | Proven by |
| --- | --- | --- | --- |
| Analytics Reporter | support-analytics-reporter | Noise-band arithmetic, index health, session baseline | L4 |
| Evidence Collector | testing-evidence-collector | Dated capture sets, raw records retained per prompt and surface | L2 |
| Reality Checker | testing-reality-checker | Verdict on the evidence pack (default: NEEDS WORK) | G4 |

## Phase 1: Baseline, Corpus & Prompt Freeze

```text
Week 1-2
├── SEO Specialist → index health: indexed vs submitted, coverage, canonicals, dated
├── Analytics Reporter → baseline record frozen: 12 months, branded vs non-branded, exported
│   and dated; then the noise band: ≥3 same-day captures per prompt per surface, spread
│   of repeat runs recorded as the per-prompt measurement floor
├── Trend Researcher → real questions from the corpus, clustered by intent, each cluster
│   citing the source question verbatim
├── AI Citation Strategist → prompt allowlist FROZEN as an output: 20-40 prompts, exact
│   wording, per surface, with locale and signed-in state recorded
├── AEO Foundations Architect → crawl audit: robots, sitemap, JS-free text path,
│   llms.txt presence logged as hygiene only
└── Quality Gate 1 (G1): the frozen prompt list, the noise band and the dated index
    baseline are committed. Fails if any prompt holds fewer than 3 captures, any capture
    lacks model/version or timestamp, or the baseline carries no date.
```

## Phase 2: Technical Foundation

```text
Week 2-3
├── Frontend Developer → crawlable HTML, canonicals, hreflang, CWV green on cluster pages
├── CMS Developer → Organization, Product, BreadcrumbList, FAQPage from typed fields,
│   one validated emitter per type
├── AEO Foundations Architect → AI-aware robots.txt implementing the signed per-crawler
│   policy, complete text rendering without JavaScript, observed status per crawler UA
├── Technical Writer → entity definitions, glossary, and the technical doc fixing
│   name/category/differentiators; no answer-first marketing page here
├── SEO Specialist → internal linking: every cluster page ≤3 clicks from the hub
└── Quality Gate 2 (G2): zero structured-data errors on rendered pages, zero unintended
    noindex, every allowed crawler UA receives 200, every blocked UA does not, and the
    policy carries a named human signer. Fails on any UA whose observed status
    contradicts the signed policy, or any page whose rendered HTML fails validation.
```

Structured data note: **FAQPage is retained only for content structure and model parsing.** It is not a rich-result play — FAQ rich results were restricted years ago and Google has been removing that result. Never gate on FAQ eligibility, and never promise a rich result from any emitted type.

`llms.txt` note: **low-cost hygiene, unproven effect — not a success criterion and not part of any gate.** Measured evidence shows the large majority of published llms.txt files receive no requests, and no major provider documents consuming it. Ship it if it costs an hour; never report it as a result.

## Phase 3: Content & Authority

```text
Week 3-5
├── Content Creator → one answer-first page per cluster: the answer in two sentences,
│   then evidence, then the next question; one page, one cluster
├── Technical Writer → glossary entries and entity terms behind each answer block,
│   one definition per entity, linked rather than restated
├── Agentic Search Optimizer → WebMCP pass/fail per task an agent must complete
│   (buy, book, register) with the failure point recorded
├── PR & Communications Manager → corroboration per cluster: named reviews, directories,
│   third-party mentions captured with URL and date
├── Visual Storyteller → one extractable artifact per cluster: comparison or pricing table
│   as real HTML, annotated spec as image plus table
├── Legal Compliance Checker → each publishable claim assembled into a cited package:
│   claim text, source, jurisdiction, risk note; routed to the named human approver
├── Named human approver → signs or rejects each package with a date; no agent signs
└── Quality Gate 3 (G3): every prioritized cluster has a live answer-first page, ≥2
    independent corroborating sources with URL and date, one Visual Storyteller artifact
    in HTML, and a claim-approval record naming the human who signed. Fails on any page
    whose claims lack a signed record, any cluster without corroboration, or any artifact
    that exists only as text inside an image.
```

## Phase 4: Sampled Re-Measurement & Verdict

```text
Week 5-6
├── Evidence Collector → same protocol as Phase 1: ≥3 same-day captures per prompt per
│   surface, model/version and timestamp recorded, raw records retained
├── AI Citation Strategist → delta per prompt per surface compared with the Phase 1 noise
│   band; a delta inside the band is reported as no measurable change
├── Analytics Reporter → index health and non-brand session baseline refreshed, reported
│   as context, never as attribution
├── Reality Checker → verdict on the evidence pack (default: NEEDS WORK)
├── SEO Specialist → handoff: sampling cadence, prompt-list version, named owner
└── Quality Gate 4 (G4): every claimed improvement is a delta above the noise band backed
    by a complete capture set. Fails if any reported metric has fewer than 3 captures per
    prompt per surface, or if the report contains a before/after pair with no band reference.
    Claims that fail are deleted, not softened.
```

## Sampling & Measurement Protocol

| Prompt class | Surface | Counts as a citation | Capture record |
| --- | --- | --- | --- |
| "best `<category>` tool for `<job>`" | ChatGPT | Brand named, linked or attributed | Answer text, model version, timestamp, signed-in state |
| "how do I `<task>`" | Perplexity | Brand domain in the source list | Answer, source URLs, timestamp |
| "`<brand>` vs `<competitor>`" | Gemini | Brand named and an owned page linked | Answer, linked URLs, timestamp |
| "`<product>` pricing / docs" | Google AI Overview + SERP | Overview cites the page, or the page holds a rank | SERP screenshot, overview text, rank, timestamp |

- Minimum 3 captures per prompt per surface, same day, spaced across the day; the same rule applies to rank checks.
- A capture without model/version, timestamp and locale is not evidence and is excluded from the delta.
- The Phase 1 noise band is per prompt and per surface: it is the observed spread of repeat same-day captures, not a global constant.
- Citation share is computed from the full capture set, never from a single flattering run.

## Key Decisions

| Decision Point | When | Who Decides |
| --- | --- | --- |
| Which query clusters to own (cap 3-5) | Phase 1 | SEO Specialist + Trend Researcher |
| Publishing cadence, pages per week | Phase 3 | Content Creator + SEO Specialist |
| Per-crawler-class allow or block (retrieval UA, training UA, agent UA), per directory | Phase 2 | Named site owner signs; Legal Compliance Checker advises on licensing and jurisdiction; never defaulted open by an agent |
| Publish comparison pages at all | Phase 3 | Named human claim approver signs each package; PR & Communications Manager recommends; Legal Compliance Checker prepares the cited package and does not approve |
| Whether a measured delta counts as a result | Phase 4 | AI Citation Strategist + Analytics Reporter, and only above the Phase 1 noise band |
| Competitor outranking on branded terms | Phase 4 | SEO Specialist + brand owner |

## Success Criteria

### Leading indicators (controllable, measured inside this runbook)

| Metric | Target |
| --- | --- |
| L1 Answer-first pages published | One live page per prioritized cluster, each mapped to ≥1 corpus question |
| L2 Prompt sampling completeness | 100% of frozen prompts per surface with ≥3 same-day captures carrying model/version and timestamp |
| L3 Question coverage | ≥80% of prioritized questions answered on a live page |
| L4 Indexation health | ≥95% of cluster pages indexed, zero unintended noindex, zero canonical errors |
| L5 Structured-data validity | 100% of emitted types valid on rendered HTML |
| Claims with a signed approval record | 100% of publishable claims, signature dated and named |

### Post-runbook outcomes (outside this gate, no promise)

| Outcome | Window | Named owner | What is claimed |
| --- | --- | --- | --- |
| Citation share on the frozen allowlist | 90-180 days after handoff | AI Citation Strategist | Direction against the noise band on re-sample; no share is promised |
| Non-brand organic sessions | 90-180 days, read against a control set of comparable untouched queries | SEO Specialist | Association only; a same-period comparison measures seasonality, so the 6-week gate claims no sessions |
| Agent-task completion on the site | 90-180 days | Agentic Search Optimizer | Monitored, no target agreed |
| Third-party mention volume | 90-180 days | PR & Communications Manager | Counted with URL and date; no causal claim |

## Common Pitfalls

| Pitfall | Mitigation |
| --- | --- |
| One before/after capture per prompt read as a result | Generative surfaces churn run to run; ≥3 same-day captures and a per-prompt noise band, deltas inside the band are reported as no change |
| Asking an agent to approve a claim | An agent may prepare the cited package; only the named human with authority signs |
| Crawler policy defaulted open by whoever edits robots.txt | Per-crawler-class allow/block is a signed human decision; an agent serving 200 to everything is a defect |
| `llms.txt` treated as the deliverable | Low-cost hygiene, unproven effect; no gate depends on it |
| FAQPage emitted expecting a rich result | Retained for content structure and model parsing only; FAQ rich results are restricted and being removed |
| Sessions compared with last year and reported as attributable gain | Seasonality dominates a same-period comparison; sessions are a 90-180 day outcome with a control set |
| Structured data that validates but lies | Emit from typed fields, validate the rendered page, not the snippet |
| Two agents writing the same answer block | Technical Writer owns entities, glossary and technical docs; Content Creator owns the answer-first page |
| Pages published with no question to answer | A cluster without a corpus question is not prioritized |
| Measuring rankings once, declaring victory | Freeze the prompt list, re-run the same protocol, reference the band |
| Treating AI citations as unmeasurable, so unowned | Sampling runs and the handoff carry a named owner |
