#!/usr/bin/env python3
"""EXP-024: recompute Gemini-only 61-skill win/loss/FDR after adding harder
tasks to the 14 ceiling-locked skills and doubling runs on the 7 closest
near-miss skills. Merges the new measurement files over the EXP-022/023
baseline, same methodology as scripts/proof_analysis.py's FDR step
(Benjamini-Hochberg q=0.05), Gemini-only (that's what the "24/61" baseline
in PROOF.md itself was).
"""
import json
import math
import sys


def p_from_ci(effect, lo, hi):
    se = (hi - lo) / (2 * 1.96)
    if se == 0:
        return 1.0 if effect == 0 else 0.0
    z = abs(effect) / se
    return 2 * (1 - 0.5 * (1 + math.erf(z / math.sqrt(2))))


def bh_fdr(pvals, q=0.05):
    m = len(pvals)
    order = sorted(range(m), key=lambda i: pvals[i])
    kmax = 0
    for rank, i in enumerate(order, start=1):
        if pvals[i] <= (rank / m) * q:
            kmax = rank
    return pvals[order[kmax - 1]] if kmax else 0.0


def main():
    base = json.load(open("simulator/results/gemini_full61_20260723.json"))["skill_effects"]
    hurts_fix = json.load(open("simulator/results/gemini_hurts_recheck_20260723.json"))["skill_effects"]
    nearmiss = json.load(open("simulator/results/gemini_nearmiss7_20260725.json"))["skill_effects"]
    merged = dict(base)
    merged.update(hurts_fix)
    merged.update(nearmiss)
    if len(sys.argv) > 1:
        ceiling = json.load(open(sys.argv[1]))["skill_effects"]
        merged.update(ceiling)
    if len(sys.argv) > 2:
        recheck = json.load(open(sys.argv[2]))["skill_effects"]
        merged.update(recheck)

    skills = sorted(merged)
    pv = {s: p_from_ci(merged[s]["effect"], *merged[s]["effect_ci95"]) for s in skills}
    thr = bh_fdr([pv[s] for s in skills])

    wins, losses, ceiling_locked, nsig = [], [], [], []
    for s in skills:
        v = merged[s]
        eff = v["effect"]
        is_ceiling = v["with_pass"] == v["without_pass"] and v["with_pass"] in (0.0, 1.0)
        if pv[s] <= thr and eff > 0:
            wins.append((s, eff, pv[s]))
        elif pv[s] <= thr and eff < 0:
            losses.append((s, eff, pv[s]))
        elif is_ceiling:
            ceiling_locked.append(s)
        else:
            nsig.append((s, eff, pv[s]))

    print(f"FDR threshold (q=0.05, m={len(skills)}): p <= {thr:.5f}\n")
    print(f"=== WINS ({len(wins)}) ===")
    for s, e, p in sorted(wins, key=lambda r: r[2]):
        print(f"  {s:<28} effect={e:+.3f}  p={p:.4g}")
    print(f"\n=== LOSSES ({len(losses)}) ===")
    for s, e, p in sorted(losses, key=lambda r: r[2]):
        print(f"  {s:<28} effect={e:+.3f}  p={p:.4g}")
    print(f"\n=== STILL CEILING-LOCKED ({len(ceiling_locked)}) ===")
    for s in ceiling_locked:
        print(f"  {s}")
    print(f"\n=== NOT SIGNIFICANT ({len(nsig)}) ===")
    for s, e, p in sorted(nsig, key=lambda r: r[2]):
        print(f"  {s:<28} effect={e:+.3f}  p={p:.4g}")
    print(f"\nTotal: {len(skills)}  wins={len(wins)}  losses={len(losses)}  "
          f"ceiling={len(ceiling_locked)}  nsig={len(nsig)}")


if __name__ == "__main__":
    main()
