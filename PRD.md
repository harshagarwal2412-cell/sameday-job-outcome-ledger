# PRD — Job Outcome Ledger

**Status:** external proposal, unsolicited
**Author:** Harsh Agarwal
**One-liner:** Close the loop from AI-booked call to invoiced job, so Sameday can prove revenue instead of reporting activity.

---

## Problem

Sameday writes appointments *into* the contractor's field service management system. It does not read outcomes back *out*. The consequence is a measurement asymmetry:

- **Sameday knows:** call answered, duration, transcript, sentiment, appointment created.
- **Sameday does not know:** whether that appointment was dispatched, whether a tech ran it, whether it was cancelled or rescheduled, what it invoiced for, whether it was the right trade.

Three things break because of this.

**1. Renewal is a vibe, not a number.** The buyer is an owner or GM watching a $449–789/month line item. Activity dashboards don't survive a slow quarter; a dollar figure does.

**2. Quality has no ground truth.** Call scoring grades the conversation against a rubric written by the vendor. It cannot tell you that the AI's *best-scored* calls are the ones booking emergency plumbing into a next-day slot the dispatcher has to tear up every morning. The model is being optimized against a proxy.

**3. Failure is silent and lagging.** When the AI mis-books, the pain lands on a dispatcher who works around it quietly for six weeks. The vendor's first signal is a churn conversation.

## Users

| Who | Cares about |
|---|---|
| Owner / GM (the buyer) | Did this make me money? Do I renew? |
| Dispatcher / office manager (the daily user) | Did the AI create work for me or remove it? |
| Sameday CS | Which accounts are quietly dying, and why, before they say so |
| Sameday product/ML | Is the agent optimizing for booked jobs or for booked *appointments*? |

## Proposal

A nightly reconciliation job that pulls job records from the connected FSM, matches them to AI-handled calls, and maintains a per-account ledger of what happened after the booking.

**Three surfaces:**

**A. ROI statement (owner-facing).** One screen, monthly cadence, emailable. Attributed completed revenue, cost, ratio. Trend line. Designed to be forwarded to a business partner without explanation.

**B. Leakage report (dispatcher- and CS-facing).** Booked jobs that never billed, grouped by cause and ranked by dollars: wrong trade assigned, capacity conflict, customer cancelled pre-arrival, no-show, duplicate of an existing job, out of service area. Each row links to the call recording. This is the artifact that makes a dispatcher an ally instead of a quiet opponent.

**C. Outcome signal back into the agent.** Booking decisions get labelled with what actually happened. That's a training and playbook-tuning input that no amount of transcript QA can substitute for.

## Scope

**In scope for v1**
- One FSM integration end to end (ServiceTitan first — deepest API, highest-value accounts)
- Nightly batch reconciliation, not real time
- Deterministic matching: appointment ID written at booking time, phone + timestamp as fallback
- Six seeded leakage categories, derived from FSM status/job-type fields rather than inferred
- Owner ROI email + in-app leakage table

**Explicitly out of scope for v1**
- Real-time intervention ("this booking looks wrong, fix it now") — earn the read loop first
- Multi-FSM parity — Housecall Pro / Jobber / FieldRoutes follow once the model holds
- Marketing-attribution-style multi-touch credit — one call, one job, conservative credit
- Automatic playbook changes from outcome data — surface it to a human first

## Sequencing

| Phase | What ships | Why this order |
|---|---|---|
| 0 | Read-only ServiceTitan pull for 5 design-partner accounts, output as a manual monthly PDF from CS | Tests whether the number is *believed* before anything is built |
| 1 | Automated nightly reconciliation + leakage table in app | Dispatcher value; also generates the CS churn signal |
| 2 | Owner ROI statement + monthly email | Renewal weapon; requires phase-1 numbers to be trusted first |
| 3 | Outcome labels exposed to playbook tuning | Only worth doing once the ledger is accurate enough to train against |

Phase 0 is the whole bet. If five owners look at a hand-built PDF and argue with the number instead of forwarding it, the design is wrong and it cost a week.

## Success metrics

**Primary:** net revenue retention on accounts with the ledger enabled vs. matched accounts without it. This is the only metric that justifies the build.

**Secondary**
- % of booked jobs successfully matched to an FSM outcome (data quality floor — below ~85% the ROI number isn't credible enough to show an owner)
- Leakage rate: attributed booked value that never invoices. The number that should go *down* over time as playbooks improve.
- CS-initiated saves triggered by leakage alerts, ahead of a customer complaint

**Guardrail:** booking rate must not fall. If the agent gets conservative to protect the ledger, the ledger has broken the product it was meant to measure.

## Risks

| Risk | Mitigation |
|---|---|
| Contractor disputes attribution | Conservative credit rules, one call → one job, visible methodology, an "exclude this job" control |
| FSM API access varies by customer tier | Phase 0 on 5 accounts confirms feasibility before committing roadmap |
| Match rate too low to be credible | Write the appointment ID at booking time; treat match rate as a launch gate, not a metric |
| The number is bad for some accounts | It is going to be. That's an account that was going to churn anyway — this just moves the discovery six weeks earlier, into a room where CS can still act |

## Open questions I'd need to be inside to answer

1. What does the existing ServiceTitan integration already read, and is any of this partly built?
2. What's actual churn reasoning today — priced out, trust, or dispatcher friction? That reorders phases 1 and 2.
3. Does the agent currently know a business's real capacity when it books, or only its stated hours? If it's the latter, the leakage report will be dominated by one cause and the fix is upstream of anything in this document.
