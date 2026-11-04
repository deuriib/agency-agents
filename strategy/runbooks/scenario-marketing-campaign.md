# 📢 Runbook: Multi-Channel Marketing Campaign

Mode: NEXUS-Sprint | Duration: 2-4 weeks | Agents: 15

## Scenario

A campaign is announced before it is designed. One hero asset is resized into five channels, so the feed post is a cut-down banner and the email is a paragraph lifted from the landing page. Tracking is a UTM string somebody will fix later. The calendar is copied from last quarter's template, so three posts land at the same hour on a platform whose own audience peaks elsewhere, and the email sequence greets a list that was never segmented. The launch week is loud, the second week is quiet, and the readout reports reach, saves, and impressions — none of which says whether anything was bought. When the campaign ends, nobody owns the page it pointed at.

Scope is one coordinated campaign across the channels the audience actually uses — organic social, paid amplification, email and lifecycle, blog and search, community — carried from strategy through a readout a finance or executive reader can act on, plus the approval chain that makes the copy legally publishable.

Doctrine: **a campaign is not launched until measurement is verified with a captured test event and every claim in the copy has a substantiation on file. Reach without measurement is spend without evidence.**

Human authority boundary: the Legal Compliance Checker prepares the claims and disclosure package — each claim, its source, its permitted phrasing, and the disclosure its channel and market require. A named human approves publishing against that package. No agent approves a claim, a discount, or a regulated statement on its own.

Boundary against neighbouring runbooks: what to buy and how to bid on it is `paid-media-launch`. Whether one change to a page or funnel step caused the lift is `growth-experiment-loop`. Earned visibility in search and answer engines is `seo-and-ai-search-visibility`. Whether a price or a discount is legal and profitable is `pricing-and-monetization-review`. This runbook decides which channels run, what each one says, and what the campaign is allowed to claim.

## Applicability

| Use this runbook when | Use a different runbook when |
| --- | --- |
| One message must ship across several channels with different formats, cadences, and audiences | The question is which placements to buy and at what bid — use `paid-media-launch` |
| The work is content, sequencing, and coordination rather than a controlled comparison | One variable on one surface must be tested for lift — use `growth-experiment-loop` |
| A launch date is fixed and the assets, the calendar, and the approvals must all land before it | The storefront or app that receives the traffic does not exist yet — use `ecommerce-storefront-launch` |
| Email and lifecycle are part of the channel mix, not a separate programme | The list itself is the whole question: segmentation and deliverability at programme scale |
| The deliverable is a readout a non-marketer can act on | The deliverable is a price, a tier, or a discount policy — use `pricing-and-monetization-review` |

Boundary: one run covers one campaign with one named owner and one budget. A recurring content programme with no end date is not a campaign, it is operations with a launch party.

## Required Inputs

Only what the roster cannot produce. The brief, the calendar, the asset set, the disclosure package, and the readout are outputs of this run — listing them as blocking inputs would make the runbook its own prerequisite.

| Input | Why it blocks | Owner |
| --- | --- | --- |
| Brand and messaging source of truth: approved positioning, voice and tone rules, logo and colour files, and the claims already cleared today | An agent cannot invent a claim the brand cannot defend, and copy that re-words the positioning re-words the company | Brand owner |
| Publishing access to every channel account in scope, with rights to post, to schedule, and to run paid | A channel with no publishing rights is a channel that silently drops out at launch | Channel owner |
| A pre-agreed budget with a stop rule: one currency, the split caps per channel, and the condition that stops spend — cost per acquisition above target for a stated number of days, or measurement unverified | No agent may approve the money it spends, and a budget with no stop rule has no floor | Budget owner |
| The measurement baseline with its date range, plus analytics access: current site traffic and conversion rate, list size and open rate per segment, follower and engagement baseline per platform, and the campaign-link taxonomy already in use | Without a dated baseline no engagement number is a result, and a taxonomy invented at launch makes every later readout unattributable | Analytics owner |
| Legal sign-off path for claims and disclosures: the named human approver, the review window before launch, and the standing policy for regulated statement categories in the markets in scope | The Compliance Checker can prepare a claims package but cannot sign it, and a review path discovered in launch week delays the launch | Legal owner |
| A named campaign owner with written authority over the calendar, the budget split, and the stop decision | An unowned campaign does not stop when it should; it decays | Executive sponsor |

## Agent Roster

Traceability: `G1`–`G3` are the gates closing the phase blocks, `S1`–`S6` the Success Criteria rows. Display names are the agents' `name` value; slugs resolve through `strategy/runbooks.json`.

### Campaign Core (Always Active)

| Agent | Role |
| --- | --- |
| Agents Orchestrator | Pipeline control, phase gating, dev-QA loop, escalation |
| Social Media Strategist | Campaign lead and cross-platform strategy: objective and the one KPI the campaign is judged on, audience definition, channel selection with a written reason per channel and per channel skipped, the four-week calendar, and the engagement protocol per platform. Takes the Go call and the stop call at G2 |
| Content Creator | Source copy and long-form production — blog, articles, landing copy, video scripts — plus the master narrative every channel is authored from rather than resized from |
| Growth Hacker | Acquisition path and budget split: landing page, conversion steps, referral and share mechanics, paid amplification inside the split caps, and the cost-per-acquisition target with its stop rule |
| Brand Guardian | Brand consistency gate: campaign visual rules, messaging framework, tone per channel, and the do's and don'ts an asset is reviewed against at G1 and re-swept before launch |
| Analytics Reporter | Measurement: campaign-link taxonomy, event design per conversion step, the captured test event that gates launch, daily snapshot, weekly report, and the reconciliation that closes G3 |
| Email Marketing Strategist | Email and lifecycle channel: segmentation architecture, welcome/nurture/reactivation/win-back sequences, cadence per segment, deliverability pre-checks, and consent, unsubscribe, and complaint handling per market |

### Platform Specialists (As Needed)

| Agent | Role |
| --- | --- |
| Twitter Engager | Launch thread with its hook, daily engagement posts, reply templates for the objections the thread draws, hashtag set, and real-time response during the launch window |
| TikTok Strategist | Three to five video concepts with hooks written first, trending-format alignment inside brand rules, posting cadence, and the completion-rate read that decides whether the format continues |
| Instagram Curator | Feed posts, Stories sequence with its tap-through path, Reels concepts, visual aesthetic set, and the profile-visit path from a save or a share |
| Reddit Community Builder | Subreddit shortlist with each community's rules read, value-first post drafts that survive moderation, comment engagement plan, and AMA preparation where it applies |
| App Store Optimizer | Store listing copy, screenshot and preview assets, and the on-store page an install campaign points at — engaged only when the campaign sells an install |

### Support (As Needed)

| Agent | Role |
| --- | --- |
| Trend Researcher | Market timing: trending topics worth joining and the ones the brand must stay out of, competitor campaign map with its gaps, and the launch window with the evidence for it |
| Experiment Tracker | A/B variants of subject line, hook, and creative: the variant register, the variant set per channel, and honest reporting of a flat result |
| Executive Summary Generator | The one-page summary a sponsor reads: objective, budget, result, decision, and cost per acquisition |
| Legal Compliance Checker | Claims and disclosure package: every claim with its substantiation, its permitted phrasing, and the disclosure its channel and market require. Prepares the package; never approves it |

## Week 1-2: Strategy & Assets

Two weeks to a launch-ready campaign. Nothing is produced before the channel set has a written reason per channel, because resizing is what happens when channels are chosen after the assets already exist.

```text
Week 1 — Strategy, Measurement Design, Channel Set
├── Social Media Strategist → campaign strategy: objective and the one KPI the campaign is judged on,
│   audience definition, channel selection with a written reason per channel AND a written reason for
│   each channel skipped, four-week calendar, engagement protocol per platform
├── Trend Researcher → timing: trending topics worth joining and the ones the brand stays out of, a
│   competitor campaign map with its gaps, and the launch window with the evidence for it
├── Growth Hacker → acquisition path: landing page, conversion steps, referral and share mechanics, paid
│   amplification plan, and the budget split per channel against the cost-per-acquisition target and its
│   stop rule
├── Email Marketing Strategist → lifecycle plan: segments with their definitions, the welcome, nurture,
│   reactivation, and win-back sequences, cadence per segment, consent basis and unsubscribe path per
│   market, and deliverability pre-checks — authentication, seed test, list hygiene
├── Brand Guardian → campaign guidelines: visual rules, messaging framework, tone per channel, and the
│   do's and don'ts list an asset is reviewed against
├── Analytics Reporter → measurement plan: campaign-link taxonomy, one event per conversion step, the
│   baseline restated with its date range, and the report a non-marketer will read
└── Legal Compliance Checker → claims intake: every claim the copy intends to make, each with its source
    and the disclosure its channel and market require
```

```text
Week 2 — Assets, Authored per Channel
├── Content Creator → source copy and long-form: blog posts, landing page copy, video scripts, and the
│   master narrative every channel is authored from
├── Twitter Engager → launch thread of 10-15 posts with its hook, daily engagement posts, reply templates,
│   hashtag set
├── TikTok Strategist → 3-5 video concepts with hooks written first, format alignment inside brand rules,
│   posting schedule
├── Instagram Curator → feed posts (carousel and single), Stories sequence with its tap-through path,
│   Reels concepts, and the visual set the aesthetic rules produce
├── Reddit Community Builder → subreddit shortlist with its rules read, value-first post drafts, comment
│   plan, AMA preparation where it applies
├── Email Marketing Strategist → sequence copy loaded per segment, subject lines with their variants, test
│   sends rendered on the mobile and desktop clients the list actually uses
├── App Store Optimizer → store listing copy and preview assets when the campaign sells an install
├── Brand Guardian → one review pass per asset against the Week 1 rules, with the rejection reason written
│   wherever an asset fails
└── Quality Gate (G1): open the copy deck and take any claim in it — every claim resolves to a
    substantiation entry naming its source and its permitted phrasing, and every calendar slot holds an
    asset authored for that channel. One claim with no entry, or one asset that is another channel's file
    at another size, fails the gate.
```

### The Claims Package and the Human Signature

The Compliance Checker's package is one row per claim: the claim as it will be published, the substantiation with its source and date, the permitted phrasing, the disclosure required per channel and per market, and any expiry. The named human approver signs one version of that package; the signature records the date and the package version, and the copy is frozen against it. A copy change that adds a claim or re-words one reopens the signature. No agent may sign, waive, or narrow a disclosure, and a discount or regulated statement enters the copy only through this path.

## Week 3-4: Launch & Measure

Launch is a gate, not a date. Spend stays at zero until one captured test event proves the funnel is measured end to end.

```text
Week 3, Days 1-3 — Pre-Launch and Launch
├── Analytics Reporter → one test event captured end to end: campaign link clicked, landing session
│   recorded, conversion event fired, payload captured with its campaign parameters
├── Email Marketing Strategist → seed test and one live send to the smallest segment before the full list
├── Growth Hacker → paid campaigns staged at the split caps, not at the full budget, with the stop rule armed
├── Brand Guardian → final sweep of every live asset against the frozen rules
├── Social Media Strategist → the Go call, taken only when the captured test event and the signed claims
│   package both exist
├── Twitter Engager → launch thread and real-time replies; Instagram Curator → launch posts and Stories;
│   TikTok Strategist → launch videos; Reddit Community Builder → community posts that answer rather than
│   announce; Content Creator → blog post published and email blast sent; App Store Optimizer → listing live
│   when the campaign sells an install
└── Quality Gate (G2): the campaign is live and measured — one published asset per channel in scope from
    its scheduled calendar slot, paid spend inside its caps, and one end-to-end event captured in the
    analytics property from campaign link through landing session to conversion event with its payload.
    A channel with no live asset, spend above a cap, a test-mode event, or an empty report fails.
```

```text
Days 4-14 — Operate, Optimise, Readout
├── Daily, platform agents → posting and engagement per the calendar, replies answered inside the same
│   working day
├── Daily, Analytics Reporter → snapshot: qualified sessions, conversion events, spend, cost per
│   acquisition per channel
├── Daily, Growth Hacker → in-cap reallocation only, with the reason for every cut and every top-up written
│   down
├── Weekly, Social Media Strategist → performance review against the one KPI; the calendar is adjusted,
│   not abandoned
├── Weekly, Experiment Tracker → A/B results and the next variant set; a flat result is reported as flat
├── Weekly, Content Creator → response content drawn from what the first week's comments actually asked
├── Weekly, Email Marketing Strategist → performance per segment, deliverability and complaint rate, and
│   sends paused on any segment whose complaint rate crosses its platform threshold
├── Weekly, Analytics Reporter → funnel by channel and spend to date against the stop rule
├── Readout, Analytics Reporter → totals reconciled to each platform's own export and to the analytics
│   funnel for the same date range, funnel by channel, cost per acquisition where money was spent, and the
│   baseline beside each result
├── Readout, Growth Hacker → channel effectiveness: what the money bought, and the channels that should not
│   run again
├── Readout, Executive Summary Generator → one page: objective, budget, result, decision, and the number the
│   sponsor asked for
├── Readout, Social Media Strategist → lessons filed where the next campaign will read them, plus an owner
│   for every live asset that outlives the campaign
└── Quality Gate (G3): the readout totals reconcile row for row to the platform export and to the analytics
    query for the same range, and the qualified-traffic number appears beside the funnel step it was counted
    at. A readout that reports reach only, or one total that will not reconcile to either source, fails.
```

### Platform KPIs

| Platform | Primary KPI | Secondary KPI | Agent |
| --- | --- | --- | --- |
| Twitter/X | Impressions plus engagement rate | Follower growth | Twitter Engager |
| TikTok | Views plus completion rate | Follower growth | TikTok Strategist |
| Instagram | Reach plus saves | Profile visits | Instagram Curator |
| Reddit | Upvotes plus comment quality | Referral traffic | Reddit Community Builder |
| Email | Open rate plus click-through rate | Unsubscribe and complaint rate | Email Marketing Strategist |
| Blog | Organic traffic plus time on page | Backlinks | Content Creator |
| Paid ads | Return on ad spend plus cost per acquisition | Quality score | Growth Hacker |

### Brand Consistency Checkpoints

| Checkpoint | When | Agent |
| --- | --- | --- |
| Content review before publishing | Every piece | Brand Guardian |
| Visual consistency audit | Weekly | Brand Guardian |
| Voice and tone check | Weekly | Brand Guardian |
| Claims and disclosure review against the signed package | Before launch, then weekly | Legal Compliance Checker prepares, named human approver signs |

## Key Decisions

| Decision Point | Default Rule | Who Decides |
| --- | --- | --- |
| Which channels run and which are skipped | A channel runs only with a written reason tied to the audience and the one KPI, and every skipped channel gets its reason written down; a channel kept because it exists is cut | Week 1, Social Media Strategist proposes, campaign owner approves |
| Budget split across channels | Paid amplification stays inside per-channel caps, organic and email carry the production budget, and no single channel takes more than half the total until the first week's cost per acquisition is known | Week 1, Growth Hacker proposes, budget owner approves |
| Launch date versus asset readiness | The date moves; the gate does not. A launch missing the signed claims package or the captured test event is postponed, and the cost of the delay is reported rather than absorbed | Week 1-2, campaign owner |
| A platform changes its API or policy mid-campaign | Freeze that channel's paid spend within the day, re-read the policy against the live assets, rework only the assets the policy touches, and record the change and its date in the readout; a channel that can no longer be measured stops even when it can still be bought | Same day on detection, Growth Hacker and Analytics Reporter, campaign owner informed |
| A channel underperforming against the stop rule | Pause it after the stated number of days below target instead of optimising it further; it resumes only against a written change to the plan | Weekly review, Growth Hacker |
| A claim with no substantiation on file | The claim is removed from the copy, not softened, and the launch waits for the source or ships without the line | Before launch and on any copy change, Compliance Checker prepares, named human approver signs, campaign owner executes |

## Success Criteria

| Metric | Target |
| --- | --- |
| S1 — Qualified traffic: sessions from campaign links reaching the counted funnel step, against the dated pre-campaign baseline | At least 1.5x the baseline, with the counted funnel step named in the readout |
| S2 — Engagement against baseline per platform, not against an industry figure | At least 20% relative above baseline on two or more platforms, and no platform below its own baseline for two consecutive weeks |
| S3 — Cost per acquisition where paid spend was used | At or below the approved target, with spend stopping at the stop rule rather than averaging under it |
| S4 — Asset delivery on schedule: calendar slots filled with a channel-authored asset at the scheduled time | At least 95% of slots filled on time and zero slots filled with another channel's file |
| S5 — Claims with substantiation on file and a human signature on the package | 100% of published claims resolve to a signed entry, zero exceptions |
| S6 — Readout reconciliation: totals matching the platform export and the analytics query for the same range | Zero unreconciled rows, readout delivered within 3 working days of campaign end |

## Common Pitfalls

| Pitfall | Mitigation |
| --- | --- |
| One asset resized for every channel | Each channel gets an asset authored to its own spec in its own calendar slot; G1 rejects a file that is another channel's asset at another size, and the calendar budgets production time per channel instead of one asset across five |
| Launching before tracking is verified | The captured test event is the launch gate and spend stays at zero until it exists; an empty report is read as a broken campaign rather than a quiet one |
| A calendar that ignores the platform's own posting behaviour | The calendar is built from each platform's own cadence and audience window rather than from a template, then re-read against the first week's hourly data and adjusted |
| Claims published without substantiation | G1 requires an entry per claim and a named human signature on the package before publishing; a claim with no source is removed from the copy, never softened into a version nobody checked |
| Measuring reach instead of the funnel | The readout reports qualified sessions at a named funnel step, cost per acquisition where money was spent, and the baseline beside each result; reach appears as context and never as the result |
| A campaign with no owner after launch week | The owner is a required input, every live asset that outlives the campaign gets an owner named in the readout, and the readout does not close until that list exists |
