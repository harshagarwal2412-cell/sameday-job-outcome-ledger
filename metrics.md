# The metric tree

Most AI voice products in the trades report from the top of this tree. Contractors renew on the bottom.

```
  calls answered                         ← infrastructure metric. Proves uptime, not value.
    └─ answer speed, containment          ← agent-performance metrics. Vendor-facing.
         └─ appointments booked            ← the industry's headline number. Where reporting stops.
              └─ appointments dispatched   ← first place reality intervenes
                   └─ jobs completed        ← a truck showed up and did work
                        └─ jobs invoiced     ← money exists
                             └─ ATTRIBUTED REVENUE PER 100 CALLS   ← the renewal number
```

Every level down is harder to measure and more expensive to argue about. That's exactly why it's defensible: the vendor who gets to the bottom of this tree owns the renewal conversation, and the ones who stop at "appointments booked" are selling an activity report.

## The four numbers worth putting on a wall

**1. Attributed revenue per 100 calls.** Normalizes across account size and seasonality. The one number an owner can hold in their head and compare month to month.

**2. Booked-to-billed rate.** Of the dollars the AI booked, what fraction actually invoiced? Isolates *booking quality* from *booking volume*. Two agents with identical booking rates can be 20 points apart here, and only this number can tell.

**3. Leakage by cause, in dollars.** Not counts — dollars. Twelve cancelled tune-ups matter less than one mis-triaged commercial job. Ranking by dollars sends engineering at the expensive failure instead of the frequent one.

**4. Time-to-first-leak-signal.** How many days between a booking pattern going bad and someone at Sameday knowing. Today, at most vendors in this category, the honest answer is "until the customer complains." Any number is an improvement on that.

## The trap

Optimizing booking rate alone is the local maximum in this category, and it is a genuinely dangerous one: the fastest way to lift booking rate is to book more marginal calls, which raises leakage, which lands on the dispatcher, who is not the buyer but is absolutely the person who tells the buyer to cancel.

The metric that resolves it is **booked-to-billed**, and you cannot compute it without reading outcomes back out of the FSM. Which is the argument of this whole repo.

## What I'd deprecate

Call sentiment scores, as a customer-facing metric. They're a proxy for a proxy — a model's read of tone, standing in for satisfaction, standing in for revenue — and they're the kind of number that makes a customer trust the dashboard less once they've listened to a call the model scored 9/10 and disagreed with it. Keep them internal for model evaluation. Don't spend buyer trust on them.
