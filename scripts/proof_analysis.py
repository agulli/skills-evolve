#!/usr/bin/env python3
"""One-shot proof analysis for the 5 claims (EXP-023).

Given the two full-61 real measurement files, computes:
  - cross-model win/loss with per-model significance
  - Benjamini-Hochberg FDR correction (multiple-comparisons honesty)
  - Layer A culture metrics on the real 61-skill effect table
  - real-data adversarial attack (honest baseline + planted attackers)

    python3 scripts/proof_analysis.py HAIKU_JSON GEMINI_JSON [--corrections C.json]

`--corrections` optionally overrides specific skills with a re-measurement file
(e.g. the requirements-interrogation / culture-telemetry registrar-fix recheck).
"""
import argparse
import json
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


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
    thr = pvals[order[kmax - 1]] if kmax else 0.0
    return thr


def load(path, corrections=None):
    se = json.load(open(path))["skill_effects"]
    if corrections and os.path.exists(corrections):
        se.update(json.load(open(corrections))["skill_effects"])
    return se


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("haiku")
    ap.add_argument("gemini")
    ap.add_argument("--corrections-haiku", default="")
    ap.add_argument("--corrections-gemini", default="")
    args = ap.parse_args()

    H = load(args.haiku, args.corrections_haiku)
    G = load(args.gemini, args.corrections_gemini)
    skills = sorted(set(H) & set(G))

    # ---- cross-model win/loss + FDR ----
    hp = {s: p_from_ci(H[s]["effect"], *H[s]["effect_ci95"]) for s in skills}
    gp = {s: p_from_ci(G[s]["effect"], *G[s]["effect_ci95"]) for s in skills}
    h_thr = bh_fdr([hp[s] for s in skills])
    g_thr = bh_fdr([gp[s] for s in skills])

    def verdict(s, eff, p, thr):
        if p <= thr and eff > 0:
            return "WIN"
        if p <= thr and eff < 0:
            return "LOSS"
        w = H[s] if eff is H else None
        return "ceiling" if _is_ceiling(s) else "nsig"

    def _is_ceiling(s):
        return (H[s]["with_pass"] == H[s]["without_pass"] and H[s]["with_pass"] in (0.0, 1.0)
                and G[s]["with_pass"] == G[s]["without_pass"] and G[s]["with_pass"] in (0.0, 1.0))

    both_win = h_win = g_win = losses = ceiling = nsig = 0
    print(f"{'skill':<26} {'haiku':>16} {'gemini':>16}  verdict")
    rows = []
    for s in skills:
        he, ge = H[s]["effect"], G[s]["effect"]
        hw = (hp[s] <= h_thr and he > 0)
        gw = (gp[s] <= g_thr and ge > 0)
        hl = (hp[s] <= h_thr and he < 0)
        gl = (gp[s] <= g_thr and ge < 0)
        if hl or gl:
            v = "LOSS"; losses += 1
        elif hw and gw:
            v = "WIN(both)"; both_win += 1
        elif hw or gw:
            v = "win(1 model)"; (globals().__setitem__('_x', 0))
            if hw: h_win += 1
            else: g_win += 1
        elif _is_ceiling(s):
            v = "ceiling"; ceiling += 1
        else:
            v = "nsig"; nsig += 1
        rows.append((s, he, ge, v))
    for s, he, ge, v in sorted(rows, key=lambda r: -(max(r[1], r[2]))):
        print(f"{s:<26} {he:>+7.3f} p={hp[s]:<7.1g} {ge:>+7.3f} p={gp[s]:<7.1g}  {v}")

    print(f"\n=== WIN/LOSS (FDR q=0.05; haiku thr p<={h_thr:.3g}, gemini thr p<={g_thr:.3g}) ===")
    print(f"WIN both models:   {both_win}")
    print(f"win 1 model only:  haiku {h_win} / gemini {g_win}")
    print(f"LOSS (either):     {losses}")
    print(f"ceiling (both 100%): {ceiling}")
    print(f"not-significant:   {nsig}")
    print(f"total skills:      {len(skills)}")

    # ---- Layer A on real data ----
    print("\n=== Layer A culture metrics on real 61-skill effect table ===")
    from simulator.run import simulate
    from simulator.world import World
    import random
    measured = {"haiku": H, "gemini-flash-lite": G}
    for scen, kw in [("baseline", {}), ("adversarial", dict(optimist_rate=0.25, gamer_rate=0.10, sybil_orgs=2))]:
        w = World.from_measured(random.Random(7), measured)
        r = simulate(seed=7, nodes=100, rounds=60, malicious_rate=0.0,
                     optimist_rate=kw.get("optimist_rate", 0.0), gamer_rate=kw.get("gamer_rate", 0.0),
                     sybil_orgs=kw.get("sybil_orgs", 0), eval_key="typical", churn_every=0,
                     hard=False, skill_names=[], world=w)
        print(f"  {scen:<12} precision={r['canon_precision']} recall={r['canon_recall']} "
              f"canon_value_strong={r['canon_value_final'][1]} "
              f"promoted={r['n_promoted']}/{r['n_truly_good']}truly-good")

    # ---- real-data adversarial ----
    print("\n=== Real-data adversarial (honest baseline + 6 planted attackers) ===")
    from simulator.adversarial import real_data_attack
    res = real_data_attack(args.haiku, args.gemini, n_malicious=6)
    print(f"  {'sybil':>6} {'cap':>5} {'precision':>10} {'malic_est':>10}")
    for r in res:
        print(f"  {r['sybil_orgs']:>6} {str(r['org_weight_cap']):>5} {r['precision']:>10} "
              f"{r['malicious_established']:>10}")


if __name__ == "__main__":
    main()
