"""Adversarial resilience sweep against Layer A's simulated commons mechanism.

    python3 -m simulator.adversarial --out simulator/results/adversarial_sweep.json

Tests two structurally different attack vectors, escalating each to find the
actual breaking point rather than confirming survival at one fixed setting:

  1. Sybil-org scale attack: does the org-jackknife defense (commons.py) hold
     as the NUMBER of independent sybil orgs grows, not just nodes-per-org?
  2. Eval blind-spot exploitation: a shared eval blind spot fools honest AND
     malicious-favoring nodes identically in the same round - the org-jackknife
     can't detect this because it's not an org-independence problem at all.
  3. Worst-case combined attack (all vectors at once) crossed with eval quality.
  4. min_orgs defense-tuning: does raising the org-jackknife's independent-org
     threshold (hardcoded to 3 by default in commons.py) push out the sybil
     breaking point found in sweep 1, and at what cost to legitimate-skill
     promotion speed for newcomer orgs? (Answer, EXP-017: NO - it does nothing
     at any value 3-10, because it was never the binding constraint.)
  5. org_weight_cap defense: caps how much confirm/refute weight ANY single
     org can contribute (regardless of how many rounds it fabricates evidence
     for) - the mechanism sweep 4 shows is actually missing.

NOTE: this tests the MECHANISM's resilience if a real community existed - it is
not a measurement of a real community under attack until one actually exists
and contributes real culture-telemetry (see EXPERIMENTS.md EXP-014/EXP-015).
Deterministic per --seed. Pure stdlib, no network, no LLM calls.
"""
import argparse
import json
import random
from typing import Dict, List

from .run import simulate, load_skill_names
from .world import World


def real_data_attack(haiku_json: str, gemini_json: str, seed: int = 7,
                     nodes: int = 100, rounds: int = 60, n_malicious: int = 6) -> List[Dict]:
    """Run the sybil-scale attack on the REAL measured 61-skill effect
    distribution (honest baseline) + `n_malicious` planted bad actors, with
    and without the org_weight_cap defense from EXP-017. Tests: does the
    culture promote the real good skills while blocking the planted attackers,
    under escalating sybil pressure? (EXP-023)"""
    with open(haiku_json) as f:
        haiku = json.load(f)["skill_effects"]
    with open(gemini_json) as f:
        gemini = json.load(f)["skill_effects"]
    measured = {"haiku": haiku, "gemini-flash-lite": gemini}

    def make_world():
        w = World.from_measured(random.Random(seed), measured)
        w.plant_malicious(random.Random(seed + 1), n_malicious)
        return w

    out = []
    for n_sybil in [0, 4, 8, 16, 24]:
        for cap in [None, 15]:
            r = simulate(seed=seed, nodes=nodes, rounds=rounds, malicious_rate=0.0,
                         optimist_rate=0.0, gamer_rate=0.0, sybil_orgs=n_sybil,
                         eval_key="typical", churn_every=0, hard=False,
                         skill_names=[], world=make_world(),
                         org_weight_cap=cap)
            out.append({
                "sybil_orgs": n_sybil, "org_weight_cap": cap,
                "precision": r["canon_precision"], "recall": r["canon_recall"],
                "malicious_established": r["malicious_established"],
                "n_promoted": r["n_promoted"], "n_truly_good": r["n_truly_good"],
            })
    return out


def _run(skill_names: List[str], seed: int, nodes: int, rounds: int, label: str, **kw) -> Dict:
    defaults = dict(seed=seed, nodes=nodes, rounds=rounds, malicious_rate=0.0,
                    optimist_rate=0.0, gamer_rate=0.0, sybil_orgs=0,
                    eval_key="typical", churn_every=0, hard=False,
                    skill_names=skill_names)
    defaults.update(kw)
    r = simulate(**defaults)
    return {
        "label": label, **{k: v for k, v in kw.items() if k != "skill_names"},
        "precision": r["canon_precision"], "recall": r["canon_recall"],
        "malicious_established": r["malicious_established"],
        "n_promoted": r["n_promoted"], "n_truly_good": r["n_truly_good"],
        "canon_value_strong": r["canon_value_final"][1],
    }


def sweep(skill_names: List[str], seed: int = 7, nodes: int = 100, rounds: int = 60) -> Dict:
    results = {"sybil_scale": [], "blindspot_exploit": [], "worst_case": [],
              "min_orgs_defense": [], "org_weight_cap_defense": []}

    # Sweep 1: sybil-org scale (org-jackknife stress test) at a modest attack.
    for n_sybil in [0, 1, 2, 3, 4, 6, 8, 12, 16, 24]:
        results["sybil_scale"].append(_run(
            skill_names, seed, nodes, rounds, f"sybil={n_sybil}",
            malicious_rate=0.08, sybil_orgs=n_sybil, eval_key="typical"))

    # Sweep 2: eval quality vs. a fixed MODERATE multi-vector attack - is a
    # correlated blind spot a cheaper way in than raw sybil volume?
    for ev in ["strong", "typical", "weak", "blindspotted", "none"]:
        results["blindspot_exploit"].append(_run(
            skill_names, seed, nodes, rounds, f"eval={ev}",
            malicious_rate=0.08, sybil_orgs=2, gamer_rate=0.10,
            optimist_rate=0.15, eval_key=ev))

    # Sweep 3: worst-case combined attack across eval quality.
    for ev in ["strong", "typical", "weak", "blindspotted", "none"]:
        results["worst_case"].append(_run(
            skill_names, seed, nodes, rounds, f"eval={ev}",
            malicious_rate=0.20, sybil_orgs=8, gamer_rate=0.25,
            optimist_rate=0.30, eval_key=ev))

    # Sweep 4: min_orgs defense tuning. Sweep 1 found the org-jackknife (at
    # its hardcoded default min_orgs=3) breaks between sybil_orgs=16 (safe)
    # and sybil_orgs=24 (2 malicious skills established). Does raising
    # min_orgs push that breaking point out, and what does it cost legitimate
    # promotion (sybil_orgs=0, same min_orgs) in the meantime?
    for mo in [3, 5, 7, 10]:
        baseline = _run(skill_names, seed, nodes, rounds, f"min_orgs={mo},sybil=0",
                        malicious_rate=0.08, sybil_orgs=0, eval_key="typical", min_orgs=mo)
        at_16 = _run(skill_names, seed, nodes, rounds, f"min_orgs={mo},sybil=16",
                     malicious_rate=0.08, sybil_orgs=16, eval_key="typical", min_orgs=mo)
        at_24 = _run(skill_names, seed, nodes, rounds, f"min_orgs={mo},sybil=24",
                     malicious_rate=0.08, sybil_orgs=24, eval_key="typical", min_orgs=mo)
        at_32 = _run(skill_names, seed, nodes, rounds, f"min_orgs={mo},sybil=32",
                     malicious_rate=0.08, sybil_orgs=32, eval_key="typical", min_orgs=mo)
        results["min_orgs_defense"].extend([baseline, at_16, at_24, at_32])

    # Sweep 5: org_weight_cap defense - the mechanism sweep 4 shows is
    # actually missing. Cap ANY org's total confirm/refute weight per
    # (skill, class) regardless of round count. Test whether this restores
    # resilience at sybil_orgs=24/32 (where uncapped + any min_orgs failed),
    # and what it costs legitimate promotion at sybil_orgs=0.
    for cap in [None, 50, 20, 10, 5]:
        label_cap = "uncapped" if cap is None else str(cap)
        baseline = _run(skill_names, seed, nodes, rounds, f"cap={label_cap},sybil=0",
                        malicious_rate=0.08, sybil_orgs=0, eval_key="typical",
                        org_weight_cap=cap)
        at_24 = _run(skill_names, seed, nodes, rounds, f"cap={label_cap},sybil=24",
                     malicious_rate=0.08, sybil_orgs=24, eval_key="typical",
                     org_weight_cap=cap)
        at_32 = _run(skill_names, seed, nodes, rounds, f"cap={label_cap},sybil=32",
                     malicious_rate=0.08, sybil_orgs=32, eval_key="typical",
                     org_weight_cap=cap)
        results["org_weight_cap_defense"].extend([baseline, at_24, at_32])

    return results


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--nodes", type=int, default=100)
    ap.add_argument("--rounds", type=int, default=60)
    ap.add_argument("--out", default="", help="write result JSON to this path")
    args = ap.parse_args()

    names = load_skill_names()
    results = sweep(names, seed=args.seed, nodes=args.nodes, rounds=args.rounds)
    print(json.dumps(results, indent=2))
    if args.out:
        with open(args.out, "w") as f:
            json.dump(results, f, indent=2)
        print(f"\n# wrote {args.out}")

    print(f"\n# seeded from {len(names)} real skills, {args.nodes} nodes, {args.rounds} rounds")
    print("# sybil_scale: malicious skills blocked (0 established) until sybil_orgs breaks the")
    print("#   org-jackknife's min_orgs=3 default by sheer volume - see EXPERIMENTS.md EXP-015.")
    print("# blindspot_exploit: a fixed moderate attack (sybil_orgs=2) that fails against every")
    print("#   independently-noisy eval succeeds the moment the eval has a CORRELATED blind spot.")
    print("# worst_case: a well-resourced multi-vector attack that partially defeats even a")
    print("#   'strong' eval - past some attack size, eval quality stops being the dominant lever.")
    print("# min_orgs_defense: does raising the org-jackknife's independent-org threshold push out")
    print("#   the sybil breaking point, and at what cost to legitimate-skill promotion speed?")
