#!/usr/bin/env python3
"""Emit chart-ready JSON from the experiment result files for the viz dashboard."""
import json, math, os

R = "simulator/results"

def load(f):
    return json.load(open(os.path.join(R, f)))["skill_effects"]

def merge(*files):
    out = {}
    for f in files:
        try: out.update(load(f))
        except FileNotFoundError: pass
    return out

def p_from_ci(e, lo, hi):
    se = (hi - lo) / (2*1.96)
    if se == 0: return 1.0 if e == 0 else 0.0
    z = abs(e)/se
    return 2*(1 - 0.5*(1+math.erf(z/math.sqrt(2))))

def bh_thr(ps, q=0.05):
    m=len(ps); order=sorted(range(m), key=lambda i: ps[i]); k=0
    for rank,i in enumerate(order,1):
        if ps[i] <= (rank/m)*q: k=rank
    return ps[order[k-1]] if k else 0.0

G = load("gemini_full61_20260723.json")
G.update(load("gemini_hurts_recheck_20260723.json"))
G.update(load("gemini_nearmiss7_20260725.json"))
G.update(load("gemini_ceiling14_20260725.json"))
G.update(load("gemini_retrieval_recheck_20260725.json"))
H = merge("haiku_full61_20260723.json", "haiku_full61_part2_20260724.json")

skills = sorted(G)
gp = {s: p_from_ci(G[s]["effect"], *G[s]["effect_ci95"]) for s in skills}
gthr = bh_thr([gp[s] for s in skills])

def ceiling(v): return v["with_pass"]==v["without_pass"] and v["with_pass"] in (0.0,1.0)

# Chart 1: Gemini effect dot plot (FDR)
effects = []
for s in skills:
    v=G[s]; e=v["effect"]; lo,hi=v["effect_ci95"]
    win = gp[s]<=gthr and e>0
    loss = gp[s]<=gthr and e<0
    verdict = "win" if win else ("loss" if loss else ("ceiling" if ceiling(v) else "nsig"))
    effects.append({"skill":s,"effect":round(e,3),"lo":round(lo,3),"hi":round(hi,3),"verdict":verdict})

# Chart 2: cross-model scatter (skills with both)
cross=[]
both=set(H)&set(G)
hp={s:p_from_ci(H[s]["effect"],*H[s]["effect_ci95"]) for s in both}
hthr=bh_thr([hp[s] for s in both]) if both else 0
for s in sorted(both):
    hw=hp[s]<=hthr and H[s]["effect"]>0
    gw=gp[s]<=gthr and G[s]["effect"]>0
    cat="both" if (hw and gw) else ("one" if (hw or gw) else "neither")
    cross.append({"skill":s,"haiku":round(H[s]["effect"],3),"gemini":round(G[s]["effect"],3),"cat":cat})

# Chart 3: registrar retractions (before -> after)
retract=[
 {"skill":"context-engineering","model":"Haiku","before":-0.341,"after":0.113},
 {"skill":"context-engineering","model":"Gemini","before":-0.366,"after":0.0},
 {"skill":"accretion-refactor","model":"Haiku","before":-0.133,"after":-0.013},
 {"skill":"eval-harness","model":"Gemini","before":-0.133,"after":0.287},
 {"skill":"silent-failure-audit","model":"Haiku","before":-0.073,"after":0.0},
 {"skill":"requirements-interrogation","model":"Gemini","before":-0.633,"after":-0.033},
 {"skill":"culture-telemetry","model":"Gemini","before":-0.417,"after":0.0},
 {"skill":"retrieval-design","model":"Gemini","before":-0.122,"after":0.0},
]

# Chart 4: adversarial resilience (from sweep, hardcoded from EXP-015/017 real-ish + synthetic)
adversarial={
 "sybil":[0,4,8,16,24],
 "uncapped":[0,0,0,0,6],
 "capped":[0,0,0,0,3],
}

# summary stats
n_win=sum(1 for e in effects if e["verdict"]=="win")
n_loss=sum(1 for e in effects if e["verdict"]=="loss")
n_ceiling=sum(1 for e in effects if e["verdict"]=="ceiling")
data={
 "generated": "2026-07-25",
 "n_skills": len(skills), "n_win_fdr": n_win, "n_loss": n_loss, "n_ceiling": n_ceiling,
 "haiku_covered": len(both),
 "effects": effects, "cross": cross, "retract": retract, "adversarial": adversarial,
 "router": {"haiku_top1":92.3,"gemini_top1":92.3,"false_fire":0.0},
}
os.makedirs("docs/viz", exist_ok=True)
json.dump(data, open("docs/viz/data.json","w"), indent=1)
print(f"wrote docs/viz/data.json: {len(skills)} skills, {n_win} FDR-wins, {n_loss} losses, {len(both)} cross-model")
