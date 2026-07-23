"""The adopter population — 100 nodes, each an org running trials on its own
tasks with one model tier, and reporting evidence to the commons.

Node behaviours model the adversaries the culture layer must survive:
  • honest   — reports its true A/B outcome, gated by its local eval.
  • optimist — publication bias: suppresses refutes, over-reports confirms.
  • gamer    — games its own local eval so bad changes pass (tests whether the
               cross-node layer catches what one node's eval misses).
  • sybil    — fabricates confirms regardless of trials (a malicious org).
"""

import random
from dataclasses import dataclass, field
from typing import List

from .evalgate import EvalGate
from .stats import paired_ab
from .world import World


@dataclass
class Node:
    node_id: int
    org: int                      # sybils share one org id → org-jackknife can discount them
    tier: str                     # "haiku" | "gemini-flash-lite"
    uclass: str                   # the task-class this node works in
    behaviour: str                # honest | optimist | gamer | sybil
    eval: EvalGate
    rng: random.Random
    trials_per_round: int = 40

    def run_trial(self, world: World, skill_idx: int, shared_blind_fp: bool):
        """Trial one skill this round. Returns a signed report the node would
        submit to the commons: (skill_idx, weight_confirm, weight_refute) — or
        None if the node has nothing to say. The node measures the skill's
        effect *through its own eval* (which may be blind), then runs a paired
        A/B on that perceived effect. Adversaries distort further."""
        if self.behaviour == "sybil":
            # fabricates a confirm without running anything real
            return (skill_idx, 1.0, 0.0)

        eff = world.true_effect(skill_idx, self.tier, self.uclass)

        # what the node *measures* — the eval can hide a real harm as a fake win
        perceived = self.eval.perceive(self.rng, eff, shared_blind_fp)
        if self.behaviour == "gamer" and eff < 0:
            perceived = abs(eff) + 0.04  # games its own eval so bad changes read as wins

        outcome, mean, _ = paired_ab(self.rng, self.trials_per_round, perceived)
        if self.behaviour == "optimist":
            # suppresses refutes, upgrades inconclusive to confirm (pub bias)
            if outcome == "refute":
                return None
            if outcome == "inconclusive":
                outcome = "confirm"
        if outcome == "confirm":
            return (skill_idx, 1.0, 0.0)
        if outcome == "refute":
            return (skill_idx, 0.0, 1.0)
        return None  # inconclusive: no evidence submitted


def build_population(rng: random.Random, world: World, n_nodes: int = 100,
                     optimist_rate: float = 0.0, gamer_rate: float = 0.0,
                     sybil_orgs: int = 0, eval_preset: EvalGate = None) -> List[Node]:
    """Assemble a heterogeneous population: split across the two model tiers and
    the task-classes, with a configurable share of each adversary type."""
    from .evalgate import PRESETS
    gate = eval_preset or PRESETS["typical"]
    nodes: List[Node] = []
    org = 0
    for i in range(n_nodes):
        tier = world.tiers[i % len(world.tiers)]
        uclass = world.classes[i % len(world.classes)]
        r = rng.random()
        if r < gamer_rate:
            behaviour = "gamer"
        elif r < gamer_rate + optimist_rate:
            behaviour = "optimist"
        else:
            behaviour = "honest"
        nodes.append(Node(node_id=i, org=org, tier=tier, uclass=uclass,
                          behaviour=behaviour, eval=gate,
                          rng=random.Random(rng.random())))
        org += 1
    # a bloc of sybil nodes sharing a small number of orgs (a coordinated attack)
    for j in range(sybil_orgs):
        for _ in range(5):  # 5 fake nodes per sybil org
            nodes.append(Node(node_id=len(nodes), org=org, tier=world.tiers[0],
                              uclass=world.classes[j % len(world.classes)],
                              behaviour="sybil", eval=gate,
                              rng=random.Random(rng.random())))
        org += 1
    return nodes
