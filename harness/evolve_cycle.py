#!/usr/bin/env python3
"""End-to-end local-evolution cycle (harness/evolve_cycle.py).

Demonstrates the full Engine loop as RUNNABLE code, not just a SKILL.md spec:

    scan (detect) -> propose (a concrete edit) -> canary (measure on held-out
    evidence) -> decide (promote or revert, gated) -> log (append-only)

Zero dependency, deterministic, no network. The point is to show the loop
actually *operates* against a routing log and makes a gated keep/revert
decision on real evidence — closing the gap between "designed" and "works"
(EXPERIMENTS.md EXP-023). It composes the same override-rate detection as
harness/scan.py and mirrors the tier semantics in skills/ROUTING.md.

Usage:
    python3 harness/evolve_cycle.py --log routing_log.jsonl
    python3 harness/evolve_cycle.py            # runs on a built-in demo log
"""

import argparse
import json
import os
import time
from typing import Dict, List, Any

# The one lever this demo proposes: when a PROPOSE-tier skill is overridden too
# often, tighten it to ASK (more friction) and check whether that would have
# reduced overrides on the held-out slice. A real loop has more levers; one is
# enough to prove the loop closes.
OVERRIDE_TRIGGER = 0.30      # scan fires above this override rate
MIN_INVOCATIONS = 5          # need enough evidence to act
PROMOTE_IF_OVERRIDE_DROP = 0.10  # canary must cut override rate by >=10pp to keep
COST_REGRESSION_TOLERANCE = 0.15  # canary's avg cost/invocation may rise at most 15% and still promote


def _demo_log(cost_regression: bool = False) -> List[Dict[str, Any]]:
    """A routing log where one skill (context-engineering, PROPOSE tier) is
    being overridden heavily early, then — after a hypothetical tightening —
    fires less and is accepted when it does. Split 50/50 into a scan window
    (first half) and a canary window (second half). Tightening PROPOSE->ASK
    adds a human-confirmation round trip, so canary cost/invocation rises a
    bit even when it wins on quality — the real tradeoff this gate checks.

    cost_regression=True produces a second scenario: the same override-rate
    win, but the confirmation turn is expensive enough to blow the cost
    tolerance — demonstrating the gate reverts on cost even when quality
    alone would have promoted."""
    rows = []
    t0 = time.time() - 20000
    # scan window: context-engineering over-fires, high override
    ce_scan = ["overridden"] * 7 + ["accepted"] * 3            # 70% override
    tr_scan = ["accepted"] * 6                                  # trajectory-review fine
    # canary window: after tightening PROPOSE->ASK, it fires less & lands better
    ce_canary = ["overridden"] * 2 + ["accepted"] * 6          # 25% override
    tr_canary = ["accepted"] * 6
    scan_cost = 0.020                                           # $/invocation before the change
    canary_cost = 0.028 if cost_regression else 0.023           # +40% (over tolerance) vs +15% (within)
    seq = ([("context-engineering", "PROPOSE", r, "scan", scan_cost) for r in ce_scan] +
           [("trajectory-review", "AUTO", r, "scan", 0.010) for r in tr_scan] +
           [("context-engineering", "ASK", r, "canary", canary_cost) for r in ce_canary] +
           [("trajectory-review", "AUTO", r, "canary", 0.010) for r in tr_canary])
    for i, (skill, tier, resp, window, cost) in enumerate(seq):
        rows.append({"timestamp": t0 + i * 100, "skill": skill, "tier": tier,
                     "user_response": resp, "window": window, "cost_usd": cost})
    return rows


def _read_log(path: str, cost_regression: bool = False) -> List[Dict[str, Any]]:
    if not path or not os.path.exists(path):
        print(f"[evolve] no log at {path!r}; using built-in demo log")
        return _demo_log(cost_regression=cost_regression)
    rows = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    rows.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return rows


def _override_rate(rows: List[Dict[str, Any]], skill: str) -> tuple:
    hits = [r for r in rows if r.get("skill") == skill]
    if not hits:
        return 0.0, 0
    ov = sum(1 for r in hits if r.get("user_response") == "overridden")
    return ov / len(hits), len(hits)


def _avg_cost(rows: List[Dict[str, Any]], skill: str):
    """Average cost_usd per invocation for `skill`, or None if the log
    carries no cost field — callers must treat None as 'cost unknown', not
    as zero, so an evolution run against an uninstrumented log doesn't
    silently pass a cost check it never actually made."""
    costs = [r["cost_usd"] for r in rows if r.get("skill") == skill and "cost_usd" in r]
    if not costs:
        return None
    return sum(costs) / len(costs)


def run_cycle(log_path: str = "", cost_regression: bool = False) -> Dict[str, Any]:
    rows = _read_log(log_path, cost_regression=cost_regression)
    # window split: explicit "window" field if present, else first/second half
    if all("window" in r for r in rows):
        scan_rows = [r for r in rows if r["window"] == "scan"]
        canary_rows = [r for r in rows if r["window"] == "canary"]
    else:
        mid = len(rows) // 2
        scan_rows, canary_rows = rows[:mid], rows[mid:]

    steps = []

    # 1. SCAN — detect the highest-override PROPOSE/AUTO skill over threshold.
    skills = sorted({r.get("skill") for r in scan_rows})
    flagged = None
    for s in skills:
        rate, n = _override_rate(scan_rows, s)
        if n >= MIN_INVOCATIONS and rate >= OVERRIDE_TRIGGER:
            if flagged is None or rate > flagged["override_rate"]:
                flagged = {"skill": s, "override_rate": round(rate, 3), "n": n}
    steps.append({"step": "scan", "flagged": flagged})
    if flagged is None:
        return {"decision": "no-op", "reason": "no skill over override threshold",
                "steps": steps}

    # 2. PROPOSE — a concrete, reversible edit: tighten the tier one notch.
    proposal = {"skill": flagged["skill"], "change": "tier PROPOSE -> ASK",
                "rationale": f"override_rate {flagged['override_rate']} >= {OVERRIDE_TRIGGER}"}
    steps.append({"step": "propose", "proposal": proposal})

    # 3. CANARY — measure the same skill on the held-out canary window (the
    #    slice that reflects behavior *after* the change would have applied).
    #    Quality and cost are measured from the SAME window so one gate can't
    #    be satisfied at the other's expense by comparing mismatched slices.
    canary_rate, canary_n = _override_rate(canary_rows, flagged["skill"])
    drop = round(flagged["override_rate"] - canary_rate, 3)
    scan_cost = _avg_cost(scan_rows, flagged["skill"])
    canary_cost = _avg_cost(canary_rows, flagged["skill"])
    cost_delta_pct = None
    if scan_cost is not None and canary_cost is not None and scan_cost > 0:
        cost_delta_pct = round((canary_cost - scan_cost) / scan_cost, 3)
    steps.append({"step": "canary", "canary_override_rate": round(canary_rate, 3),
                  "canary_n": canary_n, "override_drop": drop,
                  "scan_cost_usd": scan_cost, "canary_cost_usd": canary_cost,
                  "cost_delta_pct": cost_delta_pct})

    # 4. DECIDE — gate: promote only if the canary (a) cut overrides enough
    #    and (b) didn't blow the cost tolerance doing it; else revert. A
    #    quality win bought with an uncapped cost regression is not a win —
    #    this is the loop's spine, and the reason it isn't a rubber stamp.
    if canary_n == 0:
        decision, reason = "revert", "canary had no evidence — cannot confirm"
    elif drop < PROMOTE_IF_OVERRIDE_DROP:
        decision = "revert"
        reason = (f"override rate did not fall enough (drop {drop} < "
                  f"{PROMOTE_IF_OVERRIDE_DROP}); change rolled back")
    elif cost_delta_pct is not None and cost_delta_pct > COST_REGRESSION_TOLERANCE:
        decision = "revert"
        reason = (f"override rate fell {flagged['override_rate']} -> {round(canary_rate,3)} "
                  f"(drop {drop} >= {PROMOTE_IF_OVERRIDE_DROP}) but cost/invocation rose "
                  f"{cost_delta_pct:+.1%} (> {COST_REGRESSION_TOLERANCE:.0%} tolerance); "
                  f"quality win not worth the cost, change rolled back")
    else:
        decision = "promote"
        cost_note = (f", cost/invocation {cost_delta_pct:+.1%} (within "
                     f"{COST_REGRESSION_TOLERANCE:.0%} tolerance)" if cost_delta_pct is not None
                     else ", cost data unavailable — quality-only gate")
        reason = (f"override rate fell {flagged['override_rate']} -> {round(canary_rate,3)} "
                  f"(drop {drop} >= {PROMOTE_IF_OVERRIDE_DROP}){cost_note}; change kept")
    steps.append({"step": "decide", "decision": decision, "reason": reason})

    return {"decision": decision, "reason": reason, "skill": flagged["skill"],
            "proposal": proposal, "steps": steps}


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--log", default="", help="JSONL routing log (default: built-in demo)")
    ap.add_argument("--out", default="", help="append the cycle record to this JSONL log")
    ap.add_argument("--demo-cost-regression", action="store_true",
                     help="use the built-in demo variant where the quality win costs too "
                          "much (>15%% cost/invocation increase) — demonstrates the gate "
                          "reverting on cost even when override-rate alone would promote")
    args = ap.parse_args()

    result = run_cycle(args.log, cost_regression=args.demo_cost_regression)
    print(json.dumps(result, indent=2))
    if args.out:
        with open(args.out, "a") as f:
            f.write(json.dumps({"ts": time.time(), **result}) + "\n")
        print(f"\n# appended cycle record to {args.out}")
    print(f"\n# DECISION: {result['decision'].upper()} — {result.get('reason','')}")
