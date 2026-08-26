"""
Job Outcome Ledger -- prototype.

Joins an AI call log to a field-service-management job export and answers the
question the call log alone cannot: how much of what the AI booked actually
turned into money, and where the rest went.

Usage:  python3 ledger.py   ->   writes report.html

Standard library only. Synthetic data -- see README.
"""

import csv
import html
from collections import defaultdict

# Public list price, Scale tier, one quarter, plus rough overage on this volume.
PLATFORM_COST = 789.0 * 3 + 350.0

# Attribution rule. Deliberately conservative: a contractor will argue with any
# number that credits the AI for a call their office would have picked up anyway.
# Only calls that arrived when nobody was there to answer count as incremental.
# Gross attribution is shown too, but the incremental figure is the one to defend.
INCREMENTAL_ONLY_AFTER_HOURS = True


def load(path):
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def money(x):
    return f"${x:,.0f}"


def build_ledger(calls, jobs):
    by_appt = {j["appointment_id"]: j for j in jobs}
    ai_calls = [c for c in calls if c["handled_by"] == "ai"]

    rows = []
    for c in ai_calls:
        job = by_appt.get(c["appointment_id"]) if c["booked"] == "yes" else None
        rows.append({"call": c, "job": job})
    return ai_calls, rows


def funnel(ai_calls, rows):
    answered = len(ai_calls)
    booked = sum(1 for r in rows if r["job"])
    dispatched = sum(1 for r in rows if r["job"] and r["job"]["dispatched"] == "yes")
    completed = sum(1 for r in rows if r["job"] and r["job"]["completed"] == "yes")
    invoiced = sum(1 for r in rows if r["job"] and float(r["job"]["invoiced_value"]) > 0)
    return [
        ("Calls answered by AI", answered),
        ("Appointments booked", booked),
        ("Dispatched", dispatched),
        ("Jobs completed", completed),
        ("Jobs invoiced", invoiced),
    ]


def leakage(rows):
    lost = defaultdict(lambda: {"count": 0, "value": 0.0})
    for r in rows:
        j = r["job"]
        if not j or float(j["invoiced_value"]) > 0:
            continue
        reason = j["leak_reason"] or "unclassified"
        lost[reason]["count"] += 1
        lost[reason]["value"] += float(j["quoted_value"])
    return sorted(lost.items(), key=lambda kv: kv[1]["value"], reverse=True)


def by_segment(rows, key_fn):
    seg = defaultdict(lambda: {"booked": 0, "billed": 0, "value": 0.0, "quoted": 0.0})
    for r in rows:
        j = r["job"]
        if not j:
            continue
        k = key_fn(r)
        seg[k]["booked"] += 1
        seg[k]["quoted"] += float(j["quoted_value"])
        if float(j["invoiced_value"]) > 0:
            seg[k]["billed"] += 1
            seg[k]["value"] += float(j["invoiced_value"])
    return seg


def render(ai_calls, rows):
    f = funnel(ai_calls, rows)
    leaks = leakage(rows)

    attributed = sum(float(r["job"]["invoiced_value"]) for r in rows if r["job"])
    quoted_booked = sum(float(r["job"]["quoted_value"]) for r in rows if r["job"])
    leaked = quoted_booked - sum(
        float(r["job"]["quoted_value"]) for r in rows
        if r["job"] and float(r["job"]["invoiced_value"]) > 0
    )
    incremental = sum(
        float(r["job"]["invoiced_value"]) for r in rows
        if r["job"] and (r["call"]["after_hours"] == "yes" or not INCREMENTAL_ONLY_AFTER_HOURS)
    )

    booked_n = f[1][1]
    billed_n = f[4][1]
    b2b = (billed_n / booked_n * 100) if booked_n else 0
    per_100 = attributed / len(ai_calls) * 100 if ai_calls else 0
    roi = incremental / PLATFORM_COST if PLATFORM_COST else 0

    trade = by_segment(rows, lambda r: r["job"]["trade"])
    hours = by_segment(rows, lambda r: "After hours" if r["call"]["after_hours"] == "yes" else "Business hours")

    top = f[0][1]
    funnel_rows = "".join(
        f"<tr><td>{html.escape(label)}</td><td class='n'>{n:,}</td>"
        f"<td class='n'>{n/top*100:.0f}%</td>"
        f"<td><div class='bar' style='width:{max(n/top*100,1):.1f}%'></div></td></tr>"
        for label, n in f
    )

    leak_rows = "".join(
        f"<tr><td>{html.escape(reason)}</td><td class='n'>{d['count']:,}</td>"
        f"<td class='n neg'>{money(d['value'])}</td>"
        f"<td class='n'>{d['value']/leaked*100:.0f}%</td></tr>"
        for reason, d in leaks
    )

    def seg_rows(seg):
        out = ""
        for k, d in sorted(seg.items(), key=lambda kv: kv[1]["value"], reverse=True):
            rate = d["billed"] / d["booked"] * 100 if d["booked"] else 0
            cls = "neg" if rate < b2b - 5 else ""
            out += (f"<tr><td>{html.escape(k)}</td><td class='n'>{d['booked']:,}</td>"
                    f"<td class='n {cls}'>{rate:.0f}%</td><td class='n'>{money(d['value'])}</td></tr>")
        return out

    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Job Outcome Ledger</title>
<style>
  :root {{ --bg:#fff; --fg:#16181d; --mut:#6b7280; --line:#e5e7eb;
           --pos:#0f766e; --neg:#b4530a; --card:#f9fafb; }}
  @media (prefers-color-scheme: dark) {{
    :root {{ --bg:#111317; --fg:#e8eaed; --mut:#9aa1ab; --line:#2a2e35;
             --pos:#5eead4; --neg:#fbbf24; --card:#181b20; }}
  }}
  * {{ box-sizing:border-box; }}
  body {{ margin:0; padding:40px 24px; background:var(--bg); color:var(--fg);
         font:15px/1.55 ui-sans-serif,-apple-system,Segoe UI,Roboto,sans-serif; }}
  .wrap {{ max-width:920px; margin:0 auto; }}
  h1 {{ font-size:26px; margin:0 0 4px; letter-spacing:-.02em; }}
  h2 {{ font-size:15px; text-transform:uppercase; letter-spacing:.07em;
        color:var(--mut); margin:40px 0 12px; font-weight:600; }}
  .sub {{ color:var(--mut); margin:0 0 32px; }}
  .kpis {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(190px,1fr)); gap:12px; }}
  .kpi {{ background:var(--card); border:1px solid var(--line); border-radius:10px; padding:16px; }}
  .kpi .v {{ font-size:26px; font-weight:650; letter-spacing:-.02em; }}
  .kpi .l {{ color:var(--mut); font-size:12.5px; margin-top:4px; }}
  .scroll {{ overflow-x:auto; }}
  table {{ width:100%; border-collapse:collapse; font-size:14px; }}
  th,td {{ text-align:left; padding:9px 10px; border-bottom:1px solid var(--line); }}
  th {{ color:var(--mut); font-weight:600; font-size:12px;
        text-transform:uppercase; letter-spacing:.05em; }}
  td.n {{ text-align:right; font-variant-numeric:tabular-nums; }}
  .neg {{ color:var(--neg); }}
  .pos {{ color:var(--pos); }}
  .bar {{ height:9px; background:var(--pos); border-radius:5px; opacity:.75; }}
  .note {{ margin-top:44px; padding:14px 16px; border-left:3px solid var(--line);
           color:var(--mut); font-size:13.5px; }}
</style></head><body><div class="wrap">

<h1>Job Outcome Ledger</h1>
<p class="sub">AI-handled calls reconciled against field-service job outcomes &middot; sample quarter &middot; synthetic data</p>

<div class="kpis">
  <div class="kpi"><div class="v pos">{money(incremental)}</div><div class="l">Incremental revenue &mdash; after&#8209;hours calls only</div></div>
  <div class="kpi"><div class="v">{roi:.0f}&times;</div><div class="l">Return on {money(PLATFORM_COST)} platform cost</div></div>
  <div class="kpi"><div class="v">{b2b:.0f}%</div><div class="l">Booked&#8209;to&#8209;billed rate</div></div>
  <div class="kpi"><div class="v neg">{money(leaked)}</div><div class="l">Booked value that never billed</div></div>
  <div class="kpi"><div class="v">{money(attributed)}</div><div class="l">Gross attributed &mdash; all AI calls</div></div>
  <div class="kpi"><div class="v">{money(per_100)}</div><div class="l">Revenue per 100 AI calls</div></div>
</div>

<p class="note" style="margin-top:16px">
<strong>On attribution.</strong> The headline number credits the AI only for calls that
arrived after hours or at weekends &mdash; calls that would otherwise have reached
voicemail. Gross attribution is shown for completeness, but it is the number a contractor
will argue with, and losing that argument costs more than the larger figure wins.
</p>

<h2>Where calls go</h2>
<div class="scroll"><table>
<tr><th>Stage</th><th class="n">Count</th><th class="n">of calls</th><th></th></tr>
{funnel_rows}
</table></div>

<h2>Leakage &mdash; ranked by dollars, not counts</h2>
<div class="scroll"><table>
<tr><th>Reason booked work never billed</th><th class="n">Jobs</th><th class="n">Value lost</th><th class="n">Share</th></tr>
{leak_rows}
</table></div>

<h2>Booked&#8209;to&#8209;billed by trade</h2>
<div class="scroll"><table>
<tr><th>Trade</th><th class="n">Booked</th><th class="n">Billed rate</th><th class="n">Revenue</th></tr>
{seg_rows(trade)}
</table></div>

<h2>Booked&#8209;to&#8209;billed by time of call</h2>
<div class="scroll"><table>
<tr><th>Window</th><th class="n">Booked</th><th class="n">Billed rate</th><th class="n">Revenue</th></tr>
{seg_rows(hours)}
</table></div>

<p class="note">
Read the leakage table before the revenue number. The revenue number is what renews the
account; the leakage table is what makes the revenue number go up next quarter &mdash; and
the largest rows in it are usually not calls the agent lost, but calls it won into a slot
the business could not serve. All figures generated from synthetic data.
</p>

</div></body></html>"""


def main():
    calls = load("data/calls.csv")
    jobs = load("data/fsm_jobs.csv")
    ai_calls, rows = build_ledger(calls, jobs)

    with open("report.html", "w") as f:
        f.write(render(ai_calls, rows))

    booked = sum(1 for r in rows if r["job"])
    billed = sum(1 for r in rows if r["job"] and float(r["job"]["invoiced_value"]) > 0)
    attributed = sum(float(r["job"]["invoiced_value"]) for r in rows if r["job"])
    print(f"{len(ai_calls)} AI calls -> {booked} booked -> {billed} billed")
    print(f"booked-to-billed: {billed/booked*100:.0f}%   attributed: ${attributed:,.0f}")
    print("wrote report.html")


if __name__ == "__main__":
    main()
