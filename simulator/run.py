"""Runner — the round loop, the scenarios, and the H1/H2/H3 metrics.

    python3 -m simulator.run --scenario all
    python3 -m simulator.run --scenario baseline --seed 7 --nodes 100 --rounds 60
    python3 -m simulator.run --scenario eval-sweep      # H2: how good must the eval be?
    python3 -m simulator.run --scenario adversarial --json

Deterministic per --seed. Pure stdlib, no network, no LLM calls. Layer A only:
it validates the *mechanism* against sealed ground truth. Layer B (`measure.py`)
supplies real Haiku/Gemini effect sizes to replace the synthetic world.
"""

import argparse
import json
import random
from pathlib import Path
from typing import Dict, List

from .commons import Ledger
from .evalgate import PRESETS
from .nodes import build_population
from .world import World


def load_skill_names() -> List[str]:
    """Seed from the real 54 skills so the sim validates *this* repo. Falls back
    to synthetic names if the skills/ tree isn't found."""
    root = Path(__file__).resolve().parent.parent / "skills"
    names = []
    if root.is_dir():
        for f in sorted(root.glob("*/*/SKILL.md")):
            for line in f.read_text().splitlines():
                if line.startswith("name:"):
                    names.append(line.split("name:", 1)[1].strip())
                    break
    return names or [f"skill_{i:02d}" for i in range(54)]


def truly_good_set(world: World, min_classes: int = 2) -> set:
    """Oracle: skills that clear the true-effect bar in ≥ min_classes classes —
    the same bar the commons promotes on, so precision/recall are fair."""
    good = set()
    for i in range(len(world.skills)):
        n = sum(1 for c in world.classes if world.is_truly_good(i, c))
        if n >= min_classes:
            good.add(i)
    return good


def simulate(seed: int, nodes: int, rounds: int, *, malicious_rate: float,
             optimist_rate: float, gamer_rate: float, sybil_orgs: int,
             eval_key: str, churn_every: int, hard: bool,
             skill_names: List[str], world: World = None,
             min_orgs: int = 3, promote_p: float = 0.9,
             org_weight_cap: float = None) -> Dict:
    rng = random.Random(seed)
    if world is None:
        kw = dict(effect_lo=0.02, effect_hi=0.06, good_share=0.22) if hard else {}
        world = World.build(rng, skill_names, malicious_rate=malicious_rate, **kw)
    pop = build_population(rng, world, n_nodes=nodes, optimist_rate=optimist_rate,
                           gamer_rate=gamer_rate, sybil_orgs=sybil_orgs,
                           eval_preset=PRESETS[eval_key])
    ledger = Ledger()
    n_skills = len(world.skills)
    gate = PRESETS[eval_key]
    fp_blind = gate.fp_rate() * gate.blind_spot   # correlated false-positive rate per skill/round
    canon_value = []  # (round, uplift_strong, uplift_weak)

    for rnd in range(rounds):
        if churn_every and rnd and rnd % churn_every == 0:
            world.advance_generation()
        # Fire the CORRELATED blind-spot once per (round, skill) — shared by every
        # node, so a shared eval blind spot fools the whole population together.
        blind = {sk: (random.Random(f"{seed}-{rnd}-{sk}").random() < fp_blind)
                 for sk in range(n_skills)}
        for node in pop:
            for sk in range(n_skills):
                rep = node.run_trial(world, sk, blind[sk])
                if rep is not None:
                    skill_idx, cw, rw = rep
                    ledger.record(node.org, skill_idx, node.uclass, cw, rw)
        ledger.tally(promote_p=promote_p, min_orgs=min_orgs, org_weight_cap=org_weight_cap)
        cbc = ledger.canon_by_class(promote_p=promote_p, min_orgs=min_orgs,
                                    org_weight_cap=org_weight_cap)
        canon_value.append((rnd,
                            round(world.newcomer_uplift(cbc, world.tiers[0]), 4),
                            round(world.newcomer_uplift(cbc, world.tiers[1]), 4)))

    # ---- metrics vs the sealed oracle ----
    good = truly_good_set(world)
    promoted = ledger.promoted()
    malicious = {i for i, s in enumerate(world.skills) if s.malicious}
    tp = len(promoted & good)
    precision = tp / len(promoted) if promoted else 1.0
    recall = tp / len(good) if good else 1.0
    return {
        "scenario_params": dict(seed=seed, nodes=nodes, rounds=rounds,
                                malicious_rate=malicious_rate, optimist_rate=optimist_rate,
                                gamer_rate=gamer_rate, sybil_orgs=sybil_orgs,
                                eval=eval_key, churn_every=churn_every, hard=hard),
        "n_skills": n_skills, "n_truly_good": len(good), "n_promoted": len(promoted),
        "canon_precision": round(precision, 3),
        "canon_recall": round(recall, 3),
        "malicious_established": len(promoted & malicious),
        "canon_value_final": canon_value[-1] if canon_value else (0, 0, 0),
        "canon_value_curve": canon_value,
    }


SCENARIOS = {
    "baseline":    dict(malicious_rate=0.06, optimist_rate=0.0, gamer_rate=0.0,
                        sybil_orgs=0, eval_key="typical", churn_every=0, hard=False),
    "adversarial": dict(malicious_rate=0.08, optimist_rate=0.25, gamer_rate=0.10,
                        sybil_orgs=2, eval_key="typical", churn_every=0, hard=False),
    "churn":       dict(malicious_rate=0.06, optimist_rate=0.0, gamer_rate=0.0,
                        sybil_orgs=0, eval_key="typical", churn_every=20, hard=False),
    "hard":        dict(malicious_rate=0.06, optimist_rate=0.15, gamer_rate=0.05,
                        sybil_orgs=1, eval_key="typical", churn_every=0, hard=True),
}


def run_one(name, seed, nodes, rounds, skill_names, world=None) -> Dict:
    return simulate(seed=seed, nodes=nodes, rounds=rounds,
                    skill_names=skill_names, world=world, **SCENARIOS[name])


def load_real_world(rng: random.Random, haiku_path: str, gemini_path: str) -> World:
    """Layer B -> Layer A bridge: build a World from two real `measure.py`
    output files instead of sealed synthetic ground truth. Requires both
    files come from the same task set (same --skills filter, ideally none)
    so the intersection of skill names is the full measured set, not an
    accidental subset."""
    with open(haiku_path) as f:
        haiku = json.load(f)
    with open(gemini_path) as f:
        gemini = json.load(f)
    measured = {"haiku": haiku["skill_effects"], "gemini-flash-lite": gemini["skill_effects"]}
    return World.from_measured(rng, measured)


def eval_sweep(seed, nodes, rounds, skill_names, world_factory=None) -> List[Dict]:
    """H2: hold everything fixed, vary only the eval quality. Watch Canon
    precision and malicious-established as the eval degrades — especially the
    'blindspotted' preset, where the error is correlated across nodes.
    `world_factory`, if given, is called fresh per preset (a real World's
    skill effects get mutated in place by churn scenarios elsewhere, so each
    call gets its own instance rather than a shared, possibly-stale one)."""
    out = []
    for key in ["strong", "typical", "weak", "blindspotted", "none"]:
        params = dict(SCENARIOS["baseline"]); params["eval_key"] = key
        world = world_factory() if world_factory else None
        r = simulate(seed=seed, nodes=nodes, rounds=rounds, skill_names=skill_names,
                     world=world, **params)
        out.append({"eval": key, "canon_precision": r["canon_precision"],
                    "canon_recall": r["canon_recall"],
                    "malicious_established": r["malicious_established"],
                    "canon_value": r["canon_value_final"][1]})
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scenario", default="all",
                    choices=["all", "baseline", "adversarial", "churn", "hard", "eval-sweep"])
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--nodes", type=int, default=100)
    ap.add_argument("--rounds", type=int, default=60)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--real", nargs=2, metavar=("HAIKU_JSON", "GEMINI_JSON"),
                    help="run on REAL measure.py output instead of sealed synthetic "
                         "ground truth (Layer B -> Layer A bridge)")
    args = ap.parse_args()
    skill_names = load_skill_names()

    world_factory = None
    n_real_skills = None
    if args.real:
        world_factory = lambda: load_real_world(random.Random(args.seed), *args.real)
        n_real_skills = len(world_factory().skills)

    results = {}
    if args.scenario in ("all", "eval-sweep"):
        results["eval_sweep"] = eval_sweep(args.seed, args.nodes, args.rounds, skill_names,
                                           world_factory=world_factory)
    for name in (["baseline", "adversarial", "churn", "hard"] if args.scenario == "all"
                 else ([] if args.scenario == "eval-sweep" else [args.scenario])):
        w = world_factory() if world_factory else None
        results[name] = run_one(name, args.seed, args.nodes, args.rounds, skill_names, world=w)

    if args.json:
        print(json.dumps(results, indent=2))
        return

    print(f"\nSelf-contained skill-culture simulator — seed {args.seed}, "
          f"{args.nodes} nodes, {args.rounds} rounds, seeded from "
          f"{n_real_skills if args.real else len(skill_names)} "
          f"{'REAL-measured' if args.real else ''} skills\n")
    for name, r in results.items():
        if name == "eval_sweep":
            print("H2 — eval-validity sweep (only the eval changes):")
            print(f"  {'eval':<13} {'precision':>9} {'recall':>7} {'malicious':>10} {'canon_value':>12}")
            for row in r:
                print(f"  {row['eval']:<13} {row['canon_precision']:>9} {row['canon_recall']:>7} "
                      f"{row['malicious_established']:>10} {row['canon_value']:>12}")
            print("  → independent noise (weak) is survivable; a correlated blind spot"
                  " (blindspotted) is where the culture confirms the shared mistake.\n")
        else:
            cv = r["canon_value_final"]
            print(f"H3 — {name}: precision={r['canon_precision']} recall={r['canon_recall']} "
                  f"malicious_established={r['malicious_established']} "
                  f"(promoted {r['n_promoted']}/{r['n_skills']}, truly-good {r['n_truly_good']})")
            print(f"      canon-value (newcomer uplift)  strong-tier={cv[1]}  weak-tier={cv[2]}\n")


if __name__ == "__main__":
    main()
