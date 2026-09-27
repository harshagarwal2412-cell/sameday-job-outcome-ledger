# Escalation rubric

*Secondary artifact. Included because it's where the outcome loop earns back its cost fastest, and because it's the failure mode with the worst tail.*

## Why this sits next to the ledger

The leakage report ranks failures by dollars. But there's a class of call where the dollar cost is not the real cost: a gas smell, a flooded basement, no heat at 11pm in January, an electrical burning smell. If the agent handles one of those like a routine booking, the outcome isn't a leaked job — it's a customer who never calls again and possibly a safety incident with the contractor's name on it.

These calls are rare, which is exactly why they don't show up in aggregate metrics and why they need a rule rather than a model judgment.

## The principle

**Escalate on consequence, not on confidence.** An agent that hands off when it's unsure is fine. An agent that hands off when the *stakes are high regardless of how sure it is* is correct. The second is a much simpler rule to write, audit, and defend to a contractor.

## Tiers

**Tier 0 — Book it.** Routine: maintenance, tune-ups, quotes, non-urgent repair, reschedules. The overwhelming majority. No human, no flag.

**Tier 1 — Book it, flag it.** Same-day urgency without a safety dimension: no A/C in a heat advisory, no hot water, single-room outage. Books normally, but lands on the dispatcher's board with a marker so a human eyeballs the slot before the day is built.

**Tier 2 — Hand off live, don't book.** Safety language present: gas, smoke, burning smell, sparking, standing water, sewage, carbon monoxide, no heat below a freezing threshold, anyone reporting they feel unwell. The agent's job is to stay warm, capture the address, deliver whatever safety instruction the contractor has pre-approved, and get a human on the line — not to demonstrate booking competence.

**Tier 3 — Out of scope.** Not a service call: commercial contract negotiation, insurance/warranty dispute, a complaint about a previous job, an angry caller escalating. Warm transfer or callback promise with a named owner. Never a booking.

## Design notes

**The threshold is per-contractor, not global.** "No heat" in Phoenix in October and "no heat" in Salt Lake in January are different tiers. Ship the rubric with defaults, expose the thresholds in the playbook, and let the account set them during onboarding — this is also a natural onboarding conversation that surfaces how the business actually thinks about urgency.

**Tier 2 needs a real fallback path.** A handoff rule that dead-ends into a voicemail at 2am is worse than no rule, because the caller was told help was coming. If the account has no after-hours human, Tier 2 must degrade to something honest and specific ("I'm sending this to the on-call tech now, you'll get a call within X minutes") and the ledger should track whether that promise was kept. An escalation SLA that nobody measures is decoration.

**Measure the false negative, ignore the false positive.** Over-escalating costs a dispatcher thirty seconds. Under-escalating costs a customer, and occasionally more. The metric to watch is Tier-2-language calls the agent handled as Tier 0 — audited by keyword sweep over transcripts, weekly, small enough to review by hand. If that number is not zero, nothing else on the roadmap matters as much.
