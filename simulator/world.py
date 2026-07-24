"""Sealed ground truth. Each skill has a *true* effect on task success, per
task-class and per model tier. NOTHING in the pipeline may read this — nodes
only sample noisy trial outcomes from it, and the final metrics score the
culture's promotions against it. This is the oracle that makes the simulator
able to say "the culture was right/wrong", which the real network never can.

In the pure (Layer A) sim these effects are synthetic parameters. Layer B
(`measure.py`) replaces them with effects *measured* from real Haiku / Gemini
runs, so the population dynamics run on real skill efficacy.
"""

import random
from dataclasses import dataclass, field
from typing import Dict, List

# Task-classes an adopter node works in — the "use-case classes" of the commons.
CLASSES = ["codegen", "tool-using", "extraction", "support-chat", "research", "planning"]

# Two model tiers = two independent "vendors" (your Haiku + Gemini-flash-lite).
# Cross-tier confirmation is the real test that a norm is culture, not folklore.
TIERS = ["haiku", "gemini-flash-lite"]

GOOD_EFFECT = 0.05   # a (skill, class) pair is "clearly good" at/above this
MIN_TRUE = 0.03      # promotion counts as *correct* at/above this true effect


@dataclass
class SkillTruth:
    name: str
    # effect[tier][class] -> true improvement in success rate from using the skill
    effect: Dict[str, Dict[str, float]]
    gen_sensitive: bool          # effect collapses when the model generation turns
    malicious: bool = False      # planted-bad: actively harms adopters


@dataclass
class World:
    rng: random.Random
    skills: List[SkillTruth] = field(default_factory=list)
    classes: List[str] = field(default_factory=lambda: list(CLASSES))
    tiers: List[str] = field(default_factory=lambda: list(TIERS))
    generation: int = 0

    @classmethod
    def build(cls, rng: random.Random, skill_names: List[str],
              malicious_rate: float = 0.0, good_share: float = 0.35,
              effect_lo: float = 0.04, effect_hi: float = 0.12,
              tier_gap: float = 0.6) -> "World":
        """`good_share`/`effect_lo`/`effect_hi` set how generous reality is.
        Defaults model an "easy world" (many real wins). The `hard` scenario
        shrinks them to what real agent engineering looks like: wins rare and
        small. `tier_gap` (0..1) is how much *less* the weaker tier benefits —
        the small-model ceiling: some skills the weaker model can't fully use.
        """
        w = cls(rng=rng)
        for name in skill_names:
            malicious = rng.random() < malicious_rate
            base = rng.uniform(effect_lo, effect_hi)
            # A skill's "quality" is shared across tiers, but the weaker tier
            # realizes less of it (scaffolding it can't fully follow).
            per_class_quality = {}
            for c in w.classes:
                r = rng.random()
                if malicious:
                    per_class_quality[c] = -rng.uniform(0.02, 0.08)
                elif r < good_share:
                    per_class_quality[c] = base * rng.uniform(0.7, 1.3)   # genuinely helps
                elif r < good_share + 0.20:
                    per_class_quality[c] = -rng.uniform(0.0, 0.04)        # mildly harmful
                else:
                    per_class_quality[c] = rng.gauss(0.0, 0.01)           # ~no effect (folklore)
            effect = {}
            for i, tier in enumerate(w.tiers):
                # tier 0 = strong (full effect); later tiers realize `tier_gap` less.
                realized = 1.0 if i == 0 else (1.0 - tier_gap)
                effect[tier] = {c: q * realized for c, q in per_class_quality.items()}
            w.skills.append(SkillTruth(name, effect, rng.random() < 0.4, malicious))
        return w

    def advance_generation(self) -> None:
        """Model churn: generation-sensitive skills lose their effect (the
        capability moved into the model, or the trick stopped working)."""
        self.generation += 1
        for s in self.skills:
            if s.gen_sensitive:
                for tier in s.effect:
                    for c in s.effect[tier]:
                        s.effect[tier][c] *= 0.15

    def true_effect(self, skill_idx: int, tier: str, uclass: str) -> float:
        return self.skills[skill_idx].effect[tier][uclass]

    def is_truly_good(self, skill_idx: int, uclass: str) -> bool:
        """Oracle: averaged across tiers, does this skill clear the bar here?"""
        s = self.skills[skill_idx]
        mean = sum(s.effect[t][uclass] for t in self.tiers) / len(self.tiers)
        return mean >= MIN_TRUE

    @classmethod
    def from_measured(cls, rng: random.Random,
                       measured: Dict[str, Dict[str, dict]]) -> "World":
        """Build a World from REAL Layer B measurements (`measure.py` output)
        instead of synthetic sealed ground truth. `measured` is
        {tier: {skill_name: {"effect": float, ...}}} for tiers "haiku" and
        "gemini-flash-lite". Only skills present under every tier are
        included, so precision/recall stay apples-to-apples across models.

        Layer B measures ONE aggregate effect per skill (paired WITH/WITHOUT,
        across whatever tasks exist for it) - it does not decompose by
        World.CLASSES, and task uclass tags (safety/eval/evolve/...) don't
        even fully overlap with CLASSES (codegen/tool-using/extraction/...).
        Rather than fabricate a per-class breakdown Layer B was never
        designed to produce, the same real effect is applied uniformly
        across every class - an explicit simplification, not a hidden one.
        gen_sensitive and malicious are unknown for real, already-vetted
        skills, so both default to False (neutral, not guessed) - this run
        is about whether the culture mechanism recognizes real quality, not
        about the malicious-detection question EXP-001 already covers on
        sealed ground truth."""
        w = cls(rng=rng)
        if not measured:
            return w
        names = set.intersection(*(set(d.keys()) for d in measured.values()))
        for name in sorted(names):
            effect = {tier: {c: measured[tier][name]["effect"] for c in w.classes}
                      for tier in w.tiers}
            w.skills.append(SkillTruth(name, effect, gen_sensitive=False, malicious=False))
        return w

    def plant_malicious(self, rng: random.Random, n: int) -> "World":
        """Add `n` synthetic malicious skills on top of the real honest ones,
        for adversarial testing on a REAL honest baseline (EXP-023). The real
        measured skills stay honest (malicious=False); the attack is whether
        the culture blocks these planted bad actors while still promoting the
        real good ones. Returns self for chaining."""
        for i in range(n):
            effect = {tier: {c: -rng.uniform(0.02, 0.08) for c in self.classes}
                      for tier in self.tiers}
            self.skills.append(SkillTruth(f"__malicious_{i}", effect,
                                          gen_sensitive=False, malicious=True))
        return self

    def newcomer_uplift(self, canon_by_class: Dict[str, List[int]], tier: str) -> float:
        """Canon-value curve (the emergence metric): the true uplift a fresh
        adopter of `tier` gets from today's Canon, averaged over classes, with
        diminishing returns on stacking many skills."""
        if not canon_by_class:
            return 0.0
        total, n = 0.0, 0
        for c in self.classes:
            ids = canon_by_class.get(c, [])
            effects = sorted((self.true_effect(i, tier, c) for i in ids), reverse=True)
            uplift, decay = 0.0, 1.0
            for e in effects:
                uplift += max(0.0, e) * decay
                decay *= 0.7
            total += uplift
            n += 1
        return total / n if n else 0.0
