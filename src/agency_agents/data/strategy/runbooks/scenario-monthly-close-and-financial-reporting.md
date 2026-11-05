# Runbook: Monthly Close & Financial Reporting

> **Mode**: NEXUS-Micro | **Cycle**: 5 business days per close cycle, recurring monthly | **Agents**: 9

## Scenario

The month ends and the numbers are late, contested, or both. Reconciled balances land after the board pack circulates. Variance commentary is written from memory. The same three accounts break every month because nobody fixed the cause.

The close is a repeatable five-day cycle — reconcile, review variance, report, sign off — and no figure reaches the sign-off line without a reconciled row behind it.

## Applicability

| Use this runbook when | Use a different runbook when |
| --- | --- |
| A recurring close must produce traceable, signed statements | A price change must be decided — use `pricing-and-monetization-review` |
| Variance commentary is late or unwritten | Audit controls must be designed — use `compliance-certification-program` |
| Breaks recur with no owner on the cause | Two ledgers must merge — use `post-merger-integration` |
| A board pack must ship on a fixed date | One-off reconstruction — run it as a project |

## Required Inputs

Inputs are only things this cycle cannot produce: access, an external artifact, a threshold, a chosen standard, or a human decision already taken. Anything the cycle generates is a phase output and appears under its phase, not here.

| Input | Type | Why it blocks | Owner |
| --- | --- | --- | --- |
| Read access to the ledger, the bank portal, and the payment rails | Access | Nothing reconciles against unreadable sources | Finance Tracker |
| Bank, card, and payment-rail statements for the closed month | External artifact | Cash and cut-off lines have no counterparty evidence | Finance Tracker |
| Approved budget for the closed month, at reporting-line granularity, carrying a version ID | External artifact | Every variance row compares actual against budget and T1 is a share of the line's budget; without a versioned budget there is no denominator | Chief Financial Officer |
| HRIS headcount extract and CRM bookings and pipeline report for the closed month, each carrying an extract ID | External artifact | The board narrative states headcount, bookings, and pipeline figures that no ledger row can source | Finance Tracker |
| Pre-cycle threshold record: T1, T2, and T3 valued and signed, with its version ID and the budget version it applies to | Threshold | A threshold agreed after the numbers arrive is fitted to the numbers | Chief Financial Officer |
| Reporting basis for the cycle (local GAAP or IFRS), confirmed in writing | Chosen standard | Variance and provision judgements change with the basis | Chief Financial Officer |
| Account ownership map: one named human per account, signed before day 1 | Human decision | Unowned accounts break within two cycles | Chief Financial Officer |
| Board date and required sign-off date | Human decision | A movable date compresses the evidence gathering | Chief Financial Officer |

## Defined Thresholds

Every gate below cites these IDs. The numbers exist in this table, so a gate that references them can be failed by observation.

| ID | What it governs | Value | Set by | Set when | Recorded in |
| --- | --- | --- | --- | --- | --- |
| T1 | Variance that requires a memo row | Higher of USD 25,000 or 5% of the line's budget in the budget version cited by the threshold record, applied per reporting line | Chief Financial Officer alone | Pre-cycle, in the threshold record, before day 1 of the close and before any actual is pulled | pre-cycle threshold record, field T1; the variance memo header cites that version ID |
| T2 | Manual journal entry that requires a second approver | USD 10,000 absolute per entry, plus any entry touching a revenue, tax, or equity account regardless of amount | Chief Financial Officer alone | Pre-cycle, standing policy re-signed into each cycle's threshold record before day 1 of the close | pre-cycle threshold record, field T2 |
| T3 | Break that must be disclosed to the CFO in the pack | USD 5,000 absolute, or 15 days of age, or any break touching a cash account | Chief Financial Officer alone | Pre-cycle, in the same threshold record session as T1, before day 1 of the close | pre-cycle threshold record, field T3 |

The pre-cycle threshold record is one signed file that exists before day 1 of the close. It carries a version ID, a sign-off date, the three values above, and the budget version ID that T1 measures against. Every phase below reads T1, T2, and T3 from that record; nothing in the cycle authors, edits, or re-thresholds them, and the record for the next cycle is renewed only after this cycle signs off.

## Accounting Treatment Boundary

This runbook does not assert an accounting treatment. Revenue recognition, accrual versus cash, capital versus deductible, and every tax position depend on the jurisdiction, the entity structure, and the reporting basis chosen for the cycle. The Tax Strategist cites the governing rule, its jurisdiction, and the entity assumption it depends on. The Chief Financial Officer, as a named human, decides, and the decision date is recorded against the citation. A position with no recorded decision is disclosed as pending at sign-off; it is not filled in by inference.

## Agent Roster

### Close Command (Always Active)

| Agent | Role |
| --- | --- |
| Agents Orchestrator | Gate convocation, cycle calendaring, escalation when a gate cannot pass |
| Bookkeeper & Controller | Period lock, trial balance export, tie-outs, break register |
| Finance Tracker | Statements intake, cut-off tests, checklist, accrual re-derivation |
| Accounts Payable Agent | Open bills, payment runs, accrual schedule from open POs |

### Review & Variance (Day 3-4)

| Agent | Role |
| --- | --- |
| FP&A Analyst | Variance memo, traceability audit, cause and owner per line |
| Financial Analyst | Driver decomposition, forecast rerun |
| Tax Strategist | Tax position memo with rule citations, filing tie-outs |

### Report & Sign Off (Day 5)

| Agent | Role |
| --- | --- |
| Chief Financial Officer | Thresholds, treatment decisions, approval and signature |
| Executive Summary Generator | Board narrative, decisions requested |
| Document Generator | Statements generated from the trial balance export |

**Gate convocation.** The Agents Orchestrator convokes every gate that follows — the Day 1-2 gate, the Day 3-4 gate whose evidence Review & Variance produces, and the Day 5 gate at which the Chief Financial Officer signs. The Bookkeeper & Controller owns the content of the close; the orchestrator owns its cadence and refuses to advance a phase whose gate did not run. Convoking means opening the gate session before the next phase starts, recording the observed value for each criterion on the close checklist, and declaring pass or fail. A gate with no convocation row, no recorded observation, or a late convocation fails.

## Day 1-2: Reconcile

```text
├── Bookkeeper & Controller → lock the period, export the trial balance with export ID
│   and timestamp; the export is the only statement source for the cycle
├── Finance Tracker → load bank, card, and payment-rail statements, record cut-off boundaries
├── Accounts Payable Agent → open bills, payment runs, vendor statements
├── Bookkeeper & Controller → tie every balance-sheet account to a source, oldest account first
├── Finance Tracker → cut-off tests, prepaid and deferred rollforwards
├── Accounts Payable Agent → accrual schedule from open POs, one open-PO document ID per row
├── Bookkeeper & Controller → open the break register by carrying every unclosed row from the
│   archived register of the previous cycle, then append this cycle's breaks: account, amount,
│   age, cause, owner, fix date; closing a break adds a closure row with an evidence link
├── Finance Tracker → generate the close checklist from this phase tree, one row per step
└── Quality Gate, convoked by the Bookkeeper & Controller (Close Command owner): every
    balance-sheet account on the export shows a source document ID and a
    tie difference of zero, unless it carries a break-register row with cause, owner, and fix
    date; every break meeting T3 has a disclosure line visible in the register header; every
    accrual row from the Accounts Payable Agent carries an open-PO or in-period document ID;
    the period lock timestamp precedes the first journal entry of the cycle, and the journal
    approval log shows two approver IDs for every entry at or above T2
```

**Phase outputs:** locked trial balance export (ID and timestamp), reconciliation workbook, opening break register, day 1-2 checklist rows.

## Day 3-4: Review Variance

```text
├── FP&A Analyst → actual versus budget versus prior month; read the budget version cited in the
│   pre-cycle threshold record and the T1 value from that same record; a reporting line absent
│   from that budget version is reported as unbudgeted, never estimated; no line is re-thresholded
│   mid-cycle
├── Financial Analyst → driver split for every line above T1: volume, price, mix, with the
│   split amounts summing to the line's variance
├── FP&A Analyst → memo row per line above T1: amount, cause, impact, owner; a row reading
│   "timing" needs a reversal date or it is reported as unexplained
├── Tax Strategist → tax position memo: one row per position, governing rule cited, jurisdiction,
│   entity assumption, named decision holder; no treatment is asserted by this runbook
├── Finance Tracker → accruals re-derived from in-period documents; stale accruals reversed
├── Financial Analyst → forecast rerun from closed actuals, variance bridges regenerated
├── Financial Analyst → challenge the two largest unexplained lines in the memo the FP&A Analyst
│   wrote; do not average or merge them
└── Quality Gate, convoked by the Bookkeeper & Controller (Close Command owner): every memo row
    above T1 carries a cause, an owner, and either a reversal date
    or a corrective action date; every line above T1 has a Financial Analyst driver split whose
    components sum to the line variance; every re-derived accrual row references an in-period
    document ID; every tax position row cites a rule and jurisdiction, and any row without a
    CFO decision is marked pending and listed for disclosure
```

**Phase outputs:** variance memo keyed to T1, tax position memo, re-derived accrual schedule, rerun forecast, day 3-4 checklist rows.

## Day 5: Report & Sign Off

**Non-negotiable gate.** 100% of variance-memo rows and 100% of statement line items trace to a reconciled row, and a seeded 25-figure sample drawn over the narrative figures traces with zero misses; every variance above T1 carries a named cause and owner. One untraced row, one sampled figure with no reconciled row, or one variance above T1 without a cause and owner fails the gate: the date moves, the standard does not.

```text
├── Chief Financial Officer → review the pack: P&L, balance sheet, cash, variance memo, break
│   register; approve or return; decide any position the Tax Strategist left pending
├── Executive Summary Generator → board narrative: what changed, why, what it changes next
│   quarter; decisions requested, each with an owner and a requested date; every figure carries
│   its source artifact ID on the page — trial balance export, HRIS extract, or CRM bookings report
├── Document Generator → statements generated from the day 1-2 trial balance export; export ID
│   and timestamp print on every page; no figure retyped
├── FP&A Analyst → traceability audit: trace every variance-memo row and every statement line item
│   to a reconciled row, then trace a 25-figure sample drawn over the narrative figures with a
│   recorded seed; any miss is a gate fail, not a caveat
├── Tax Strategist → filings and provisions tied to the closed ledger; position rows carry the
│   citation plus the CFO decision and its date
├── Bookkeeper & Controller → publish the checklist, archive evidence, carry every unclosed
│   register row into the next cycle's opening register
├── Chief Financial Officer → sign-off by name and date, residual issues and pending positions
│   disclosed on the sign-off record
└── Quality Gate, convoked by the Bookkeeper & Controller (Close Command owner): 100% of
    variance-memo rows and 100% of statement line items carry a reconciled row; the seeded
    25-figure narrative sample records zero misses; zero variance above T1 lacks a named cause
    and owner; every break meeting T3 is disclosed with owner and fix date; every board-narrative
    figure carries its source artifact ID on the page — trial balance export, HRIS extract, or CRM
    bookings report — and a figure with no artifact ID fails; every statement page from the
    Document Generator prints the export ID and timestamp; the sign-off line carries a name,
    a role, and a date
```

**Phase outputs:** signed statement pack, board-ready summary, sign-off record, archived evidence, carried break rows.

### Recurring Close Artifacts

| Artifact | Owner | Definition of done |
| --- | --- | --- |
| Trial balance export | Bookkeeper & Controller | One file from a locked period, printing export ID, export timestamp, and period lock timestamp; Document Generator may read no other source for the cycle |
| Reconciliation workbook | Bookkeeper & Controller | Every balance-sheet account number from the export appears with source document ID, tie difference, preparer, and reviewer; a non-zero tie difference exists only where a break-register row is linked; file hash recorded before Day 3 |
| Break register | Bookkeeper & Controller | Append-only; each row carries account, amount, age in days, cause, owner, fix date, and a closure row with evidence link when closed; the next cycle opens with exactly the rows that have no closure row |
| Close checklist | Finance Tracker | Generated from the phase tree before Day 1 work starts; one row per executed step with owner, timestamp, and evidence link; a step counts as complete only when all three fields are filled |
| Variance memo | FP&A Analyst | One row per line above T1 with amount, driver, cause, owner, and a reversal or corrective date; unexplained lines are labelled unexplained rather than averaged, merged, or dropped |
| Tax position memo | Tax Strategist | One row per position with the governing rule cited, jurisdiction, entity assumption, decision holder, decision, and decision date; a blank decision leaves the row flagged pending and listed on the sign-off record |
| Board-ready summary | Executive Summary Generator | Issued only after the sign-off date exists; every figure in the narrative carries its source artifact ID on the page — trial balance export, HRIS extract, or CRM bookings report; a figure with no artifact ID is not issued; decisions requested listed with owner and requested date |
| Signed statement pack | Document Generator | Statements generated from the trial balance export with export ID and timestamp printed on each page, no retyped figure, per-page hash recorded |
| Sign-off record | Chief Financial Officer | Name, role, date, pack hash, list of disclosed exceptions and pending positions with owner and fix date |

## Key Decisions

| Decision Point | When | Who Decides | Recorded as |
| --- | --- | --- | --- |
| Renewing the pre-cycle threshold record for the next cycle | After this cycle's sign-off and before the next cycle's day 1 | Chief Financial Officer alone | pre-cycle threshold record version ID and sign-off date |
| Convoking a gate: Day 1-2, Day 3-4, Day 5 | Before the phase that follows each gate starts | Bookkeeper & Controller, Close Command owner | close checklist gate row with convocation timestamp and the observed value of each criterion |
| Accounting treatment on a contested item — revenue recognition, accrual versus cash, capital versus deductible, tax position | Day 3-4, before the memo is finalised; carried into Day 5 if still open | Chief Financial Officer, after the Tax Strategist cites the governing rule and jurisdiction | tax position memo row with citation and decision date |
| Approving a manual journal entry | Standing policy, all phases | Chief Financial Officer; any entry at or above T2 needs a second approver | journal approval log |
| A break not resolved inside the cycle | Day 1-2 gate | Chief Financial Officer: disclose with owner and fix date; a balancing plug is not an option | break register row with disclosure line |
| Shipping the pack with a disclosed exception or pending position | Day 5 | Chief Financial Officer | sign-off record exception list |

## Success Criteria

All metrics below are observed inside the 5-day cycle at the stated check.

| Metric | Definition | Target | Measured by | Observed at |
| --- | --- | --- | --- | --- |
| Accounts without a source document ID | Balance-sheet accounts on the trial balance export with no source ID and no break row | 0 | Bookkeeper & Controller | Day 1-2 gate |
| Breaks meeting T3 without a disclosure line | Register rows at or above the T3 value, age, or cash test with no header disclosure | 0 | Bookkeeper & Controller | Day 1-2 gate |
| Variance rows above T1 without cause and owner | Memo rows above the T1 value without cause, owner, and reversal or corrective date | 0 | Chief Financial Officer | Day 3-4 gate |
| Accrual rows without an open-PO document | Accrual schedule rows with no open-PO or in-period document ID | 0 | Accounts Payable Agent | Day 1-2 gate |
| Re-derived accruals without an in-period document | Accrual rows surviving re-derivation with no document dated inside the period | 0 | Finance Tracker | Day 3-4 gate |
| Variance lines above T1 without a driver split | Lines above T1 with no volume, price, and mix split summing to the line variance | 0 | Financial Analyst | Day 3-4 gate |
| Statement pages without the export ID | Pages in the signed pack missing the export ID and timestamp | 0 | Document Generator | Day 5 gate |
| Tax positions without a cited rule | Position rows lacking rule and jurisdiction citation | 0 | Tax Strategist | Day 3-4 gate |
| Untraced variance-memo rows or statement line items | Memo rows and statement line items in the full trace with no reconciled row | 0 | Chief Financial Officer | Day 5 gate |
| Misses in the seeded narrative sample | Narrative figures drawn in the 25-figure sample with no reconciled row | 0 | Chief Financial Officer | Day 5 gate |
| Narrative figures without a source artifact ID | Board summary figures on the page with no trial balance export, HRIS extract, or CRM bookings report ID | 0 | Executive Summary Generator | Day 5 gate |
| Journal entries above T2 with one approver | Entries at or above the T2 value recorded with a single approver ID | 0 | Chief Financial Officer | Day 5 gate |
| Open breaks at sign-off | Register rows with no closure row | ≤ 3, each with owner and fix date | Bookkeeper & Controller | Day 5 gate |
| Sign-off completeness | Name, role, date, pack hash, exception list present | Complete | Chief Financial Officer | Sign-off record |

## Post-runbook

These signals settle after the cycle closes, so they are measured on a later date by a named owner. They are not gates for this cycle.

| Metric | Definition | Owner | Measured on |
| --- | --- | --- | --- |
| Restatements of a signed period | Every correction posted against a signed period, counted cumulatively from its sign-off date to the review date, because a restatement can surface months after the period closed | Bookkeeper & Controller | Day 5 of every following cycle, cumulative from the sign-off date |
| Breaks carried past one cycle | Rows opened in cycle N still without a closure row at the Day 1-2 gate of cycle N+1 | Bookkeeper & Controller | Day 2 of the following cycle |
| Repeating break causes | Rows whose stated cause matches a cause closed in a prior cycle | FP&A Analyst | Day 4 of the following cycle |
| Days-to-close trend | Rolling median of days from period-end date to signed-pack date across the last three signed cycles, target ≤ 4 by the third signed cycle | Chief Financial Officer | Day 5 of the third cycle after this run |
| Rerun forecast error | Absolute variance between the Day 3-4 rerun and the next closed actuals | Financial Analyst | Day 3 of the following cycle |
| Positions decided against the cited recommendation | Tax position rows where the recorded decision differs from the Tax Strategist's recommendation | Tax Strategist | Day 5 of the following cycle |

## Common Pitfalls

| Pitfall | Mitigation |
| --- | --- |
| Close lives in a spreadsheet one person understands | A second agent re-derives the tie-out logic once per cycle and records the check as a checklist row |
| A difference plugged into "other" to hit the date | Every plug appears either as a break row with owner and fix date or as an unexplained memo row; both are visible at the gate |
| Commentary written before review | Memo rows are written after tie-out, and every row above T1 cites the amount it explains |
| A threshold agreed after the numbers arrive | Thresholds are read from the pre-cycle threshold record; a threshold not in that record is not applied |
| The same account breaks every month | Cause text is carried on the register row and compared at the following cycle's Day 4 |
| Accruals copied from last month | Each accrual row needs an in-period document ID; rows without one are reversed, not carried |
| Treatment assumed from last year's filing | The Tax Strategist cites the rule per position, and a position with no citation and no decision blocks the Day 5 gate |
| A fast close because nothing was reconciled | The Day 5 gate requires the full trace of memo rows and statement line items, the seeded 25-figure narrative sample, and the tie differences — not elapsed time |
