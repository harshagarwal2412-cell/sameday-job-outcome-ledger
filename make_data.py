"""
Generates the synthetic sample data in data/.

NOTHING HERE IS REAL. No Sameday systems, customers, or call records were
accessed. These rows exist so the prototype runs and so the shape of the
argument is concrete. Re-run to regenerate.
"""

import csv
import os
import random
from datetime import datetime, timedelta

os.makedirs("data", exist_ok=True)

random.seed(24)

TRADES = ["HVAC", "Plumbing", "Electrical", "Roofing", "Garage Door"]
START = datetime(2026, 5, 1, 7, 0)

# (status, leak_reason, weight) -- weights are a guess, not a claim.
OUTCOMES = [
    ("invoiced", "", 62),
    ("completed_unbilled", "invoice not raised", 4),
    ("cancelled", "customer cancelled pre-arrival", 9),
    ("cancelled", "wrong trade assigned", 6),
    ("cancelled", "capacity conflict - slot unavailable", 8),
    ("cancelled", "duplicate of existing job", 4),
    ("no_show", "customer no-show", 5),
    ("cancelled", "outside service area", 2),
]

TICKET = {
    "HVAC": (180, 4200),
    "Plumbing": (150, 3100),
    "Electrical": (140, 2600),
    "Roofing": (400, 9500),
    "Garage Door": (120, 1400),
}


def pick_outcome():
    total = sum(w for _, _, w in OUTCOMES)
    r = random.uniform(0, total)
    upto = 0
    for status, reason, w in OUTCOMES:
        upto += w
        if r <= upto:
            return status, reason
    return OUTCOMES[0][0], OUTCOMES[0][1]


calls, jobs = [], []
appt_seq = 5000

# Inbound call volume is concentrated in business hours; after-hours is the tail
# the AI exists to catch. Roughly 1/4 of calls, which is where its value lives.
HOUR_WEIGHTS = ([1] * 7) + [6, 14, 16, 15, 13, 11, 13, 14, 12, 10, 8, 5] + [3, 3, 2, 2, 1]

for i in range(1, 941):
    day = random.randint(0, 59)
    hour = random.choices(range(24), weights=HOUR_WEIGHTS, k=1)[0]
    ts = START.replace(hour=0) + timedelta(days=day, hours=hour, minutes=random.randint(0, 59))
    trade = random.choice(TRADES)
    after_hours = ts.hour < 8 or ts.hour >= 18 or ts.weekday() >= 5
    handled_by = "ai" if random.random() < 0.86 else "human"

    # not every call is a booking attempt
    booked = random.random() < (0.47 if handled_by == "ai" else 0.53)
    appt_id = ""
    if booked:
        appt_seq += 1
        appt_id = f"APPT-{appt_seq}"

    calls.append({
        "call_id": f"CALL-{i:04d}",
        "timestamp": ts.isoformat(timespec="minutes"),
        "trade": trade,
        "handled_by": handled_by,
        "after_hours": "yes" if after_hours else "no",
        "duration_sec": random.randint(45, 480),
        "booked": "yes" if booked else "no",
        "appointment_id": appt_id,
    })

    if not booked:
        continue

    status, reason = pick_outcome()

    # A booked job that never reaches dispatch is a distinct, worse failure.
    dispatched = status not in ("cancelled",) or random.random() < 0.35
    completed = status in ("invoiced", "completed_unbilled")

    # Ticket sizes are heavily right-skewed: mostly diagnostics and small repairs,
    # occasionally a system replacement. Uniform would badly overstate the average.
    lo, hi = TICKET[trade]
    quoted = round(lo * (hi / lo) ** (random.random() ** 2.6), 2)
    invoiced = quoted if status == "invoiced" else 0.0
    if status == "invoiced" and random.random() < 0.3:
        invoiced = round(quoted * random.uniform(0.7, 1.35), 2)

    jobs.append({
        "job_id": f"JOB-{appt_seq}",
        "appointment_id": appt_id,
        "scheduled_for": (ts + timedelta(hours=random.randint(2, 96))).isoformat(timespec="minutes"),
        "trade": trade,
        "dispatched": "yes" if dispatched else "no",
        "completed": "yes" if completed else "no",
        "status": status,
        "leak_reason": reason,
        "quoted_value": quoted,
        "invoiced_value": invoiced,
    })

with open("data/calls.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(calls[0].keys()))
    w.writeheader()
    w.writerows(calls)

with open("data/fsm_jobs.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(jobs[0].keys()))
    w.writeheader()
    w.writerows(jobs)

print(f"wrote data/calls.csv ({len(calls)} rows), data/fsm_jobs.csv ({len(jobs)} rows)")
