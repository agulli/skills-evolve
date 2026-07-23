"""The eval-harness, modeled as an imperfect classifier — the H2 lever.

"Is their evaluation good?" is the load-bearing question: the whole self-
improvement + culture machinery trusts the eval's pass/fail verdict blindly.
So we model each node's local eval-harness as a *noisy classifier* of the true
effect of a proposed change, with two separable error sources:

  • independent noise  — each node's eval is wrong at random. The culture layer
    (cross-node agreement) AVERAGES THIS AWAY: many independent imperfect evals
    still converge on the truth.
  • correlated blind spot — a bias SHARED across nodes (same weak criteria, same
    judge model, same missing regression class). The culture layer CANNOT fix
    this: if every node's eval is fooled the same way, cross-node agreement just
    confirms the shared mistake faster.

The experiment: sweep `specificity` (does the eval reject truly-bad changes?)
and `blind_spot` (how correlated the errors are) and watch Canon precision.
That curve is the answer to "how good must the eval be, and which kind of
badness is fatal."
"""

import random
from dataclasses import dataclass

from .world import MIN_TRUE


@dataclass
class EvalGate:
    """A node's local eval-harness as a classifier of 'is this change good?'.

    sensitivity : P(pass | change is truly good)      — true-positive rate
    specificity : P(reject | change is truly bad)     — true-negative rate
    blind_spot  : fraction of the specificity error that is CORRELATED across
                  nodes (a shared blind spot) rather than independent.
    """
    sensitivity: float = 0.90
    specificity: float = 0.85
    blind_spot: float = 0.0

    def fp_rate(self) -> float:
        return 1.0 - self.specificity

    def perceive(self, rng: random.Random, true_effect: float,
                 shared_blind_fp: bool) -> float:
        """The effect the node *measures through its eval* — what the A/B then
        acts on. A perfect eval returns the true effect; an imperfect one
        distorts it.

        `shared_blind_fp` is computed ONCE per skill per round and passed to
        every node, so the correlated blind-spot error fires identically for the
        whole population — the difference between "independent noise" (which the
        commons averages away) and "a shared blind spot" (which it can't).
        """
        if true_effect >= MIN_TRUE:
            # truly good: sensitivity = P(the eval sees the win). A miss reads as
            # no effect, so the node won't confirm it.
            return true_effect if rng.random() < self.sensitivity else 0.0
        # truly bad / null: a false positive makes the node perceive a (fake) win.
        if shared_blind_fp:
            false_positive = True                                   # correlated
        else:
            false_positive = rng.random() < self.fp_rate() * (1.0 - self.blind_spot)  # independent
        return (abs(true_effect) + 0.04) if false_positive else true_effect


# Named presets spanning "how good is the eval" — used by the eval-validity sweep.
PRESETS = {
    "strong":      EvalGate(sensitivity=0.95, specificity=0.95, blind_spot=0.0),
    "typical":     EvalGate(sensitivity=0.90, specificity=0.85, blind_spot=0.10),
    "weak":        EvalGate(sensitivity=0.85, specificity=0.65, blind_spot=0.20),
    "blindspotted": EvalGate(sensitivity=0.90, specificity=0.80, blind_spot=0.75),
    "none":        EvalGate(sensitivity=1.00, specificity=0.00, blind_spot=0.0),
}
