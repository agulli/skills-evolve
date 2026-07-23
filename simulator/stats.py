"""Statistical primitives — paired A/B trials and the Beta-posterior promotion
tail. Pure stdlib, deterministic per RNG. Self-contained (no external deps).

A trial is *paired*: the with-skill and without-skill arms run the same task,
so most tasks resolve identically and only a small fraction flip — the variance
reduction that makes A/B on noisy LLM outcomes tractable.
"""

import math
import random
from typing import Tuple

MIN_EFFECT = 0.02  # smallest improvement we care to call real


def paired_ab(rng: random.Random, n: int, effect: float,
              churn: float = 0.06, min_effect: float = MIN_EFFECT,
              z_alpha: float = 1.645) -> Tuple[str, float, float]:
    """Simulate a pre-registered paired A/B trial of `n` tasks.

    `effect` is the *true* per-task improvement probability (P(with wins) −
    P(without wins)); `churn` is the fraction of tasks whose outcome differs
    between arms at all. Returns (outcome, mean_delta, upper95) with outcome
    one of confirm / refute / inconclusive.
    """
    p_plus = max(0.0, (churn + effect) / 2.0)
    p_minus = max(0.0, (churn - effect) / 2.0)
    deltas = []
    for _ in range(n):
        r = rng.random()
        deltas.append(1 if r < p_plus else (-1 if r < p_plus + p_minus else 0))
    mean = sum(deltas) / n
    var = sum((d - mean) ** 2 for d in deltas) / (n - 1) if n > 1 else 0.0
    if var == 0.0:
        return ("confirm" if mean >= min_effect else "refute"), mean, mean
    se = math.sqrt(var / n)
    upper95 = mean + 1.96 * se
    z = mean / se
    if z >= z_alpha and mean >= min_effect:
        return "confirm", mean, upper95
    if upper95 < min_effect:
        return "refute", mean, upper95
    return "inconclusive", mean, upper95


def beta_tail(confirms: float, refutes: float, threshold: float = 0.7) -> float:
    """P(confirmation rate > threshold) under Beta(confirms+1, refutes+1).

    Accepts weighted (fractional) counts so reporter weights can feed in.
    Exact via the regularized incomplete beta — stdlib only.
    """
    return 1.0 - _betainc_reg(confirms + 1.0, refutes + 1.0, threshold)


def _betainc_reg(a: float, b: float, x: float) -> float:
    """Regularized incomplete beta I_x(a, b) (Numerical Recipes §6.4)."""
    if x <= 0.0:
        return 0.0
    if x >= 1.0:
        return 1.0
    ln_front = (math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b)
                + a * math.log(x) + b * math.log(1.0 - x))
    front = math.exp(ln_front)
    if x < (a + 1.0) / (a + b + 2.0):
        return front * _betacf(a, b, x) / a
    return 1.0 - front * _betacf(b, a, 1.0 - x) / b


def _betacf(a: float, b: float, x: float) -> float:
    """Continued fraction for the incomplete beta, by Lentz's method."""
    max_iter, eps, fpmin = 200, 3e-12, 1e-300
    qab, qap, qam = a + b, a + 1.0, a - 1.0
    c = 1.0
    d = 1.0 - qab * x / qap
    if abs(d) < fpmin:
        d = fpmin
    d = 1.0 / d
    h = d
    for m in range(1, max_iter + 1):
        m2 = 2 * m
        aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1.0 + aa * d
        if abs(d) < fpmin:
            d = fpmin
        c = 1.0 + aa / c
        if abs(c) < fpmin:
            c = fpmin
        d = 1.0 / d
        h *= d * c
        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1.0 + aa * d
        if abs(d) < fpmin:
            d = fpmin
        c = 1.0 + aa / c
        if abs(c) < fpmin:
            c = fpmin
        d = 1.0 / d
        delta = d * c
        h *= delta
        if abs(delta - 1.0) < eps:
            break
    return h
