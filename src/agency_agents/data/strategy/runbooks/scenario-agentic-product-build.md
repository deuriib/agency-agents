# Runbook: Agentic Product Build

Mode: NEXUS-Sprint | Duration: 6 weeks | Agents: 15

## Scenario

The demo works. An agent reads a request, calls two tools, and answers impressively in front of a stakeholder. Then it meets real users: it loops on the same tool call until the turn limit, it invents a result when retrieval comes back empty, it costs eleven dollars for one conversation, and nobody can say whether the last prompt change made it better or worse — because there is no evaluation set.

None of those are model problems. They are the symptoms of building the feature list before the measurement. This runbook builds the agent as a product in the opposite order: the evaluation harness first, then tools, retrieval and memory, then guardrails and cost ceilings, then the product surface — and a regression suite that runs on every change, so quality is a number that can go down and block a merge.

The doctrine is one sentence: **an agent without an evaluation set is a demo, and a demo that costs money per conversation is a liability. The evaluation harness ships before the feature list.** Inventing an answer is a defect, not a style choice, and an unmeasured prompt change is an unrequested behaviour change.

Scope is the agent itself — corpus, tools, retrieval, memory, guardrails, cost, surface. It is not the data platform underneath, not a public API, and not the security programme around it.

## Applicability

| Use this runbook when | Use a different runbook when |
| --- | --- |
| You are building a new agent or MCP-based product, and the demo exists but the measurement does not | You are adding an LLM feature to an existing product — use `ai-feature-integration` |
| The agent calls tools, reads documents, or keeps memory across turns | The substrate the agent reads is the problem — use `data-platform-foundation` |
| You must prove quality, latency and cost per conversation with stored evidence | External consumers need a versioned contract — use `api-platform-launch` |
| Tool loops, fabricated answers, or unbounded spend are live risks | You must harden the whole system afterwards — use `security-posture-review` |
| The product surface, abstention experience and release gate ship together | You are delivering one feature into a healthy product — use `enterprise-feature` |

## Required Inputs

Only what the roster cannot produce. Everything else — the evaluation set, its split, the prompts, the tool schemas, the guardrails, the harness — is an output of this runbook, never an input to it.

| Input | Why it blocks | Owner |
| --- | --- | --- |
| A representative task corpus, or real user requests from which the corpus is built, redacted under the rule below | A synthetic corpus scored against synthetic graders proves nothing; without it there is no pass bar | Product Manager |
| A written data-protection basis for the task corpus, signed by a named data-protection owner who is not on this roster: legal basis, data subjects, and the corpus retention period with its deletion date | Real user requests carry personal data; a corpus with no lawful basis and no retention period is an unowned dataset, and no roster agent may supply either | Data-protection owner (outside this roster) |
| A written PII redaction rule for corpus tasks, applied to every task before it enters the corpus | A corpus built in-run from real requests without a redaction rule is a personal-data store with no rule; no roster agent may author it | Data-protection owner (outside this roster) |
| At least 5 recruited users from outside the build team, booked for the G5 date, with a written consent basis and a data-handling rule for their session data | G5 needs a user who did not build the agent; the roster cannot produce one, so with fewer than 5 the smoke session and G5 record NOT VERIFIED, never PASS | Reality Checker (recruits and books outside the roster; the users are the input, never a roster output) |
| Access to the model providers in use, including their rate limits and per-token prices | Latency and cost cannot be measured on a quota you do not have; rate limits decide the retry design | AI Engineer |
| A per-conversation cost ceiling approved by finance | A ceiling invented by engineering is not a budget; spend control with no owner is reverted at the first complaint | FinOps Engineer |
| The list of data sources the agent may read, with permission to read them | Scope of retrieval is a permission question before it is a ranking question | Product Manager |
| A named owner for the safety policy, with authority to say no | Guardrails without an owner are prose; the injection and confirmation rules need an approver | AI-Generated Code Security Auditor |

## Thresholds

Every number a gate uses is defined here. A gate that cites a number not in this table is void.

A **run record** is one task executed once: prompt version, model id, retrieved document ids with scores, tool calls with arguments and results, token counts, cost, latency, and the final answer. Every metric below is computed from run records, never from application logs or from a human reading a transcript.

A **trace id** is the document id or the tool-result id written into that run record. An id the record does not contain is not a trace id: a claim citing it is an unresolved claim.

No task enters the corpus until the redaction rule in Required Inputs exists and has been applied to it. The corpus version records the rule version and the redaction run, and G1 fails on a task that skipped either.

| ID | Threshold | Value | Enforced at |
| --- | --- | --- | --- |
| M1 | Task success rate | ≥ 85% of held-out tasks pass every assertion: required facts present, forbidden facts absent, expected tool calls made, expected abstention taken. Partial credit does not exist. | G3, G5 |
| M2 | Groundedness | 100% of factual claims in an answer resolve to a trace id in that run record, and 0 claims cite an id absent from the record. There is no tolerance inside a gate: one unresolved claim is one failure | G3, G5 |
| M3 | Abstention — unanswerable | ≥ 95% of tasks tagged unanswerable end in an explicit abstention, never in an answer | G3 |
| M3b | Abstention — answerable | ≤ 5% of answerable tasks abstain; a false abstention is a failure with the same weight as an invented answer | G3 |
| M4 | Regression tolerance | No accepted change drops M1, M2 or M3 by more than 2 percentage points absolute against the last accepted run; any drop on M2, and any larger drop anywhere, blocks the merge | G5 |
| M5 | Latency budget | Retrieval p95 ≤ 800 ms, one tool call p95 ≤ 2.5 s, first streamed token p95 ≤ 1.5 s, whole answer p50 ≤ 5 s and p95 ≤ 15 s | G3, G4 |
| M6 | Cost per conversation | p50 ≤ $0.03, p95 ≤ $0.12, hard stop at $0.15 per conversation, and ≤ $2.00 per active user per month at a declared mean of 30 conversations per active user per month, that is mean cost ≤ $0.0667 per conversation | G4 |
| M7 | Tool-call bound | ≤ 6 tool calls per task, ≤ 2 retries of one failing tool, abort on the third identical call | G3 |
| M8 | Corpus size and split | ≥ 150 tasks; ≥ 40% held out and never shown to the Prompt Engineer; ≥ 25% adversarial or injection; ≥ 20% unanswerable | G1 |
| M9 | Guardrail overhead | Whole-answer p95 with guardrails enabled minus whole-answer p95 without them ≤ 10% of that p95, which is ≤ 1.5 s against the 15 s p95 of M5. Computed from run records | G4 |
| M10 | Real-user smoke session | ≥ 5 representative tasks completed by recruited users from outside the build team, drawn from the ≥ 5 booked users, with 0 operator interventions. This is a smoke check, not a quality proof: at a true 70% task success rate a clean 5/5 session happens about 17% of the time, so quality is proven only by M1 on the sealed held-out run | G5 |
| A1 | Abstention threshold | Abstain when the top reranked document scores below the relevance floor of 0.35, or no document clears the floor, or a required tool call failed with no alternate evidence, or the grounding validator rejects two consecutive drafts | G3 |

M6 is one distribution read three ways: p50 and p95 are quantiles of per-conversation cost over run records, the hard stop is a runtime check inside the loop, and the per-user bar is that distribution's arithmetic mean multiplied by the declared 30-conversations-per-active-user assumption. When the observed mean conversation count differs from 30, the per-user bar is reported at the observed mean and the assumption is restated, never silently re-derived.

The relevance floor in A1 is fitted once on the **tuning split only**, by the RAG Pipeline Engineer, and frozen with the corpus version before the held-out slice is opened. The held-out slice is then scored once, after the freeze. Fitting the floor against the whole corpus, or re-scoring the held-out slice after moving the floor, destroys the sealed estimate this runbook rests on. Changing the floor requires a new split, is recorded as a corpus version change, and takes a full scored run.

## Agent Roster

Every row carries the gate or metric that fails when its work is missing.

### Command (Always Active)

| Agent | Role | Proven by |
| --- | --- | --- |
| Agents Orchestrator | Phase gating, gate re-runs, kill decision when a phase cannot pass | G1, G2, G3, G4, G5 |
| Multi-Agent Systems Architect | Topology, context budget, bounded tool loop, memory write rules, human-confirmation gating | G3, G4, M7 |
| Product Manager | Quality bar as a number, task classes, who may accept a regression, the signed exception record | M1, M3b, M4, G5 |

### Agent Core (Week 2-3)

| Agent | Role | Proven by |
| --- | --- | --- |
| MCP Builder | Typed MCP tools, input schemas, timeouts, read/write classification, offline fixtures | G3, M5, M7 |
| Prompt Engineer | Prompt versions, tuning split only, abstention prompt path, prompt ownership | G3, M4 |
| RAG Pipeline Engineer | Chunking, hybrid retrieval, re-ranking, relevance-floor calibration | M2, M3, A1 |
| AI Engineer | Model integration, trace instrumentation, grounding validator, streaming | M1, M5, G3 |

### Evaluation & Safety (Week 1, 4)

| Agent | Role | Proven by |
| --- | --- | --- |
| Model QA Specialist | Corpus, sealed held-out split, harness, blind scoring, safety slice | G1, G2, M1, M2 |
| AI-Generated Code Security Auditor | Injection review of tools and retrieval, server-side authorisation, confirmation enforcement | G4 |

### Cost & Operations (Week 4)

| Agent | Role | Proven by |
| --- | --- | --- |
| FinOps Engineer | Cost per run record, budget enforced inside the loop, unit-economics dashboard | M6 |
| DevOps Automator | Harness in CI, independent prompt and model rollout with rollback, outage path | M4, G4, G5 |

### Product Surface & Proof (Week 5-6)

| Agent | Role | Proven by |
| --- | --- | --- |
| Backend Architect | Conversation boundary, idempotency, timeouts, backoff, per-tenant rate limits | M5, G5 |
| Frontend Developer | Streaming, sources panel, abstention and error states, feedback into the corpus | M5, G5 |
| Evidence Collector | Run records, gate records, cost ledger, release evidence pack | G1, G2, G5 |
| Reality Checker | Blind adversarial runs, real-user proof, final verdict (default: NEEDS WORK) | G5 |

## Week 1: Evaluation Harness First

No prompt is written this week. A prompt written before the corpus exists is tuned to the builder's imagination, and every later score is then a score against the builder's imagination.

```text
Week 1, days 1-2: Freeze the corpus
├── Product Manager → quality bar as a number per task class: what "correct" means,
│   what an abstention looks like, what the ceiling cost actually buys
├── Model QA Specialist → ≥ 150 tasks drawn from real user requests already redacted
│   under the input rule, each with machine-checkable assertions, plus adversarial and
│   unanswerable slices (M8)
├── Multi-Agent Systems Architect → the run-record fields every task must emit
├── Prompt Engineer → tuning and held-out split; the held-out file is sealed and
│   read only by the harness
├── RAG Pipeline Engineer → relevance floor fitted on the tuning split only, then frozen
│   before the held-out slice is opened
├── Evidence Collector → corpus version, split hash, redaction rule version, the commit
│   that froze them, and the retention date from the data-protection basis
└── Quality Gate (G1): the corpus is committed and the split is sealed before a prompt
    exists. It fails on (1) one task without an assertion, (2) one held-out task that
    also appears in the tuning split, (3) a corpus below M8, (4) one task that entered
    the corpus before the redaction rule existed or without it applied, and (5) a corpus
    version with no recorded retention date.
```

```text
Week 1, days 3-5: Prove the harness can fail
├── Model QA Specialist → harness runs end to end against a trivial baseline agent,
│   scoring M1, M2, M3, latency and cost from run records
├── AI Engineer → replayable trace store: any run record can be re-executed offline
├── FinOps Engineer → cost per run record from token counts and the provider rate card;
│   an estimate without a rate card is not a cost
├── DevOps Automator → harness runs in CI on every commit; 3 runs of one commit must
│   return the same scores
├── Reality Checker → seeds a fabricated answer with a fake citation and confirms the
│   harness scores it below the bar
└── Quality Gate (G2): the harness fails a deliberately fabricated answer and
    reproduces its own score across 3 runs of one commit. It fails on one seeded defect
    scored as passing, or on any 1-task swing between two runs of the same commit.
```

## Week 2-3: Agent Core

Tools, memory and retrieval are built only as far as the corpus requires.

```text
Week 2: Tools and memory
├── MCP Builder → typed tools with schemas, timeouts, per-tool read/write class and an
│   offline fixture per tool
├── Multi-Agent Systems Architect → one controller, bounded tool loop (M7), context
│   budget per turn, what crosses a turn boundary and what does not
├── AI Engineer → memory: schema for every write, retention window, delete path
├── Prompt Engineer → prompts tuned on the tuning split only; held-out stays sealed
├── Model QA Specialist → expected-tool-call scoring added to the harness output
└── MCP Builder → every wired tool is exercised by at least one corpus task; a tool
    with no task is deleted or given one (G3 clause 4)

Week 3: Retrieval and grounding
├── RAG Pipeline Engineer → chunking, hybrid retrieval, re-ranking, relevance floor
│   fitted on the tuning split so A1 fires exactly where the tuning split has no answer,
│   frozen, then the held-out slice is scored once against it
├── AI Engineer → grounding validator in front of the response: a claim without a
│   trace id does not leave the service
├── Prompt Engineer → abstention path as a separate route from the answer path
├── Reality Checker → adversarial slice and out-of-corpus questions, run blind
├── Evidence Collector → one run record per task, retained with its corpus version
└── Quality Gate (G3): the agent meets M1, M2, M3, M3b, M5 and M7 on the sealed
    held-out slice across 3 consecutive runs, the slice having been scored once after the
    floor and corpus version were frozen. It fails on (1) one answer stating a fact with
    no trace id in its run record, (2) one unanswerable task answered instead of refused,
    (3) any relevance-floor change after the freeze that is not recorded as a corpus
    version change with a new split, and (4) one wired tool that no corpus task exercises.
```

Failure behaviour is binding on every path, and it is written as code with a test, not as prompt text.

| Trigger | Required behaviour | Defect if |
| --- | --- | --- |
| Retrieval returns nothing, or nothing clears the A1 floor | Return a stated abstention that names what was searched and what would be needed, and log the run record as `no_evidence` | The agent answers from model priors, or paraphrases the question as if it were an answer |
| A tool call fails, times out, or returns an error payload | One retry with backoff, then either an alternate source recorded in the run record or a stated abstention naming the failed tool | The error is swallowed, the model is asked to "try again anyway", or the answer is fabricated around the gap |
| Confidence is low — validator rejects the draft twice | Abstain with the reason, and surface the closest retrieved candidates as unverified | The draft is softened with hedging and shipped as an answer |

## Week 4: Guardrails & Cost

```text
Week 4: Bound the blast radius
├── AI-Generated Code Security Auditor → injection review of every tool and of the
│   retrieval path: retrieved content is data, never instruction; tool authorisation is
│   checked server-side, never inferred from the prompt
├── Multi-Agent Systems Architect → the never-without-confirmation list enforced at
│   runtime, with the confirmation request itself in the run record
├── FinOps Engineer → per-conversation budget enforced inside the loop: alert at 80% of
│   the ceiling, hard stop at 100%, cost per active user on a weekly dashboard
├── DevOps Automator → provider outage path: circuit breaker, degraded response, and
│   cross-provider failover only for a task class that scores equal on the corpus
├── Model QA Specialist → safety slice in the harness (injection, exfiltration, off-policy
│   action), with M1 and M3 re-scored with guardrails on
├── AI Engineer → guardrail overhead measured from run records against M9: whole-answer
│   p95 with guardrails minus p95 without them, ≤ 10% of that p95 and so ≤ 1.5 s against
│   the 15 s p95 of M5
└── Quality Gate (G4): a hostile conversation set produces no out-of-policy action, no
    conversation above the hard stop, and guardrail overhead inside M9. It fails on
    (1) one injected instruction executed, (2) one conversation billed past $0.15,
    (3) one tool call made after the M7 abort, and (4) guardrail overhead above M9 on any
    of the 3 consecutive runs.
```

## Week 5-6: Product Surface & Proof

```text
Week 5: Ship the surface
├── Backend Architect → conversation endpoints with idempotency keys, timeouts,
│   backoff, streaming and per-tenant rate limits
├── Frontend Developer → streaming answer, visible abstention state, "why this answer"
│   panel listing sources, and an error state that is not a spinner
├── DevOps Automator → prompt, model id and tool versions deployed independently of the
│   app, rollback in one command
├── Evidence Collector → QA on every increment against the harness, not against the demo
└── Week 5 checkpoint: every row of the failure-behaviour table is reachable from the
    product surface and shows its authored message

Week 6: Prove it
├── Reality Checker → M10 smoke session: 5 representative tasks completed by recruited
│   users from outside the build team, with 0 operator help; if the 5 recruited users are
│   not available on the G5 date the session and G5 record NOT VERIFIED
├── Model QA Specialist → full held-out run against the deployed product, blind scoring
│   with the prompt version withheld from the scorer. This run, not the smoke session, is
│   the quality proof
├── DevOps Automator → the regression suite is a required check; a deliberately regressed
│   prompt must fail its pull request
├── Product Manager → the exception rule: who may accept a regression, how it is
│   recorded, and how long it lives; every accepted regression carries a signed exception
│   record naming an owner and an expiry date
├── Evidence Collector → evidence pack: corpus version, redaction rule version, run
│   records, gate records, cost ledger, abstention and incident logs
└── Quality Gate (G5): the sealed held-out run meets M1 and M2 on the deployed product,
    the M10 session completes with 0 operator help, and the regressed-prompt pull request
    goes red. It fails on (1) held-out M1 below 85% or one claim without a trace id,
    (2) fewer than 5 recruited users available, in which case the smoke session and G5
    record NOT VERIFIED and may never record PASS, (3) one smoke-session task needing
    operator help, (4) one prompt change merging without a scored run, (5) one accepted
    regression without a signed exception record naming an owner and an expiry date, and
    (6) a missing row in the evidence pack.
```

## Key Decisions

| Decision Point | When | Who Decides | Default while unresolved |
| --- | --- | --- | --- |
| Model tier per task class: small tier for routing, extraction and classification, larger tier for synthesis and multi-step tool planning | Week 2 | AI Engineer + Prompt Engineer | Cheapest tier that passes M1 for that class; escalation is per class, never per request |
| Whether a tool is read-only, and what a write tool must carry | Week 2 | MCP Builder + AI-Generated Code Security Auditor | Write tools stay unwired: idempotency key, server-side authorisation and a confirmation gate first |
| What the agent may never do without human confirmation: payments, deletions, external sends, permission or data-scope changes, anything that spends money | Week 4 | Product Manager + Multi-Agent Systems Architect | The action is blocked and a confirmation request is returned instead |
| Provider outage behaviour | Week 4 | DevOps Automator + Backend Architect | Fail closed to a degraded answer or a stated abstention with a visible notice; no cross-provider failover without equal scores on the corpus |
| Who owns prompt changes, and what a change must carry | Week 1 | Prompt Engineer + Product Manager | A prompt change without a scored run and a version id does not merge |
| Memory retention window and deletion path | Week 2 | Product Manager + AI-Generated Code Security Auditor | No memory write |

## Success Criteria

| Metric | Target |
| --- | --- |
| M1 Task success rate, held-out slice | ≥ 85% of tasks pass every assertion, stable across 3 consecutive runs |
| M2 Groundedness | 100% of claims resolved to a trace id in the run record, 0 citations absent from it |
| M3 Abstention correctness | ≥ 95% abstention on unanswerable tasks, ≤ 5% false abstention on answerable tasks |
| M4 Regression delta per accepted change | No drop greater than 2 percentage points on M1 or M3, no drop at all on M2 |
| M5 Latency | p50 ≤ 5 s, p95 ≤ 15 s per answer; retrieval p95 ≤ 800 ms; first token p95 ≤ 1.5 s |
| M6 Cost | p50 ≤ $0.03 and p95 ≤ $0.12 per conversation, hard stop at $0.15; mean ≤ $0.0667 per conversation, giving ≤ $2.00 per active user per month at the declared 30 conversations per user |

## Common Pitfalls

| Pitfall | Mitigation |
| --- | --- |
| Building the demo before the eval set, so every later decision is scored against opinion | G1 freezes the corpus and seals the held-out split before a prompt exists; the phase cannot exit without it |
| Evaluating with the same examples used for prompting | Held-out split is sealed, read only by the harness, and its hash is committed with the corpus version |
| Prompt changes shipped without a regression run | The regression suite is a required check and a deliberately regressed prompt must go red (G5); M4 blocks the merge |
| Unbounded tool loops | M7 tool-call bound, one-retry rule, abort on the third identical call, and the guardrail's latency share counted against M9 at G4 |
| Cost discovered on the invoice | Budget enforced inside the loop with an alert at 80% and a hard stop at the ceiling (M6), verified by an over-limit test at G4 |
| Safety rules that exist only in prose | Every rule in the never-without-confirmation list is a runtime check with a test, and the hostile set at G4 fails the gate when one is bypassed |

## Post-runbook

Metrics whose window is longer than 6 weeks never appear as closed results above. They ship as owned commitments with a date.

| Metric | Owner | Measured on |
| --- | --- | --- |
| Drift after a provider model update: M1, M2 and M3 re-scored on the frozen corpus with the new model id. The M2 tolerance lives here and only here: unresolved claims may rise by at most 2 percentage points above the gate bar on the deployed product, and a claim citing an id absent from its run record is an incident at any rate | Model QA Specialist | Every model id change, and handover + 30 days |
| Cost trend per active user, four-week rolling, against the M6 ceiling | FinOps Engineer | Handover + 30 days, then monthly |
| Human escalation rate: conversations where the user asked for a person or abandoned after an abstention | Product Manager | Handover + 30 days, then monthly |
| Corpus freshness: tasks added from real failures and unanswered production requests, ≥ 10 per month, each one redacted under the corpus redaction rule before it enters the corpus | Model QA Specialist | Monthly, starting handover + 30 days |
| Injection and exfiltration incidents reaching production, target 0 | AI-Generated Code Security Auditor | Handover + 90 days |
