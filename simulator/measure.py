"""Layer B - measure REAL skill efficacy and REAL eval-validity with small
models (Haiku, Gemini-flash-lite), then feed the numbers into the Layer-A
population sim so it runs on reality instead of synthetic effects.

Two numbers per skill, per model, are what Layer A needs:

  * effect size (H1) - does the skill make the agent's OUTCOME better?
      Run each held-out task WITH and WITHOUT the skill, grade both by an
      INDEPENDENT registrar (an objective check the agent never sees), and take
      the paired win-rate difference. Feeds World.build's effect input.

  * eval-validity (H2) - is the agent's OWN eval trustworthy?
      Compare the agent's self-verdict to the registrar's ground truth. The
      false-positive rate (agent says good, registrar says bad) is exactly
      EvalGate.specificity's complement; whether those false positives repeat
      across tasks/models is the blind spot.

Runs in MOCK mode with no API keys (synthetic paired outcomes from each task's
base_rate + mock_effect) so the pipeline is exercisable now. Real mode uses the
model adapters + the objective registrars in tasks.py.
"""

import os
import random
from dataclasses import dataclass
from typing import Dict, List, Protocol

from .tasks import Task, load_tasks

# --- live cost meter: charge every call so an unattended run can hard-stop --- #
# USD per token (input, output). Haiku 4.5 = $1/$5 per MTok. Gemini flash-lite
# is ~$0.10/$0.40 per MTok (estimate; it is far cheaper than Haiku either way).
PRICES = {"haiku": (1e-6, 5e-6), "gemini": (0.10e-6, 0.40e-6)}
_SPEND = {"usd": 0.0, "calls": 0, "in_tok": 0, "out_tok": 0}


def _charge(model: str, in_tok: int, out_tok: int) -> None:
    pi, po = PRICES.get(model, (0.0, 0.0))
    _SPEND["usd"] += in_tok * pi + out_tok * po
    _SPEND["calls"] += 1
    _SPEND["in_tok"] += in_tok
    _SPEND["out_tok"] += out_tok


# --------------------------------------------------------------------------- #
# Model adapters - the only thing you implement to go from mock to real.
# --------------------------------------------------------------------------- #
class ModelAdapter(Protocol):
    name: str
    def generate(self, system: str, user: str) -> str: ...


@dataclass
class MockAdapter:
    """Placeholder adapter. In mock mode `measure()` does not call generate()
    at all - it synthesizes paired outcomes from each task's base_rate +
    mock_effect. This exists only so the CLI has an adapter object."""
    name: str = "mock"


# Model IDs are env-overridable so you can point at the exact current string
# without editing code. Gemini's flash-lite id in particular changes across
# releases - set GEMINI_MODEL to the one you want (the default is a guess).
HAIKU_MODEL = os.getenv("HAIKU_MODEL", "claude-haiku-4-5")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash-lite")
_MAX_TOKENS = 1024


_CALL_TIMEOUT_S = 30       # fail fast on a dead connection instead of hanging forever
_CONSEC_FAIL_LIMIT = 8     # abort the run rather than silently grind through an outage
_consec_fail = {"n": 0}


def _retry(fn, attempts=2):
    last = None
    for _ in range(attempts):
        try:
            r = fn()
            _consec_fail["n"] = 0
            return r
        except Exception as e:   # a single flaky call must not kill a long run
            last = e
    _consec_fail["n"] += 1
    print(f"  [warn] generate failed ({last}); returning empty output "
          f"({_consec_fail['n']}/{_CONSEC_FAIL_LIMIT} consecutive)", flush=True)
    if _consec_fail["n"] >= _CONSEC_FAIL_LIMIT:
        # A handful of consecutive empty-response "passes" is invisible in the
        # aggregate stats until someone reads the raw numbers - see EXPERIMENTS.md:
        # a connectivity outage mid-run once produced a clean-looking 0.0/0.0
        # "no effect" reading for 8 skills that was actually just empty responses
        # failing every registrar identically on both arms. Stop instead of
        # quietly producing that a second time.
        raise RuntimeError(
            f"{_CONSEC_FAIL_LIMIT} consecutive generate() failures - this looks like "
            f"a real outage, not one flaky call. Aborting so the run doesn't silently "
            f"produce corrupted zero-signal data. Fix connectivity and re-run.")
    return ""


class _Haiku:
    """Anthropic Haiku. Requires `pip install anthropic` and ANTHROPIC_API_KEY."""
    name = "haiku"
    def __init__(self):
        from anthropic import Anthropic       # lazy: import only when actually used
        self._c = Anthropic(timeout=_CALL_TIMEOUT_S)
    def generate(self, system: str, user: str) -> str:
        def call():
            r = self._c.messages.create(
                model=HAIKU_MODEL, max_tokens=_MAX_TOKENS, system=system,
                messages=[{"role": "user", "content": user}])
            _charge("haiku", r.usage.input_tokens, r.usage.output_tokens)
            return "".join(getattr(b, "text", "") for b in r.content)
        return _retry(call)


class _Gemini:
    """Gemini flash-lite via the google-genai SDK. Requires
    `pip install google-genai` and GEMINI_API_KEY (or GOOGLE_API_KEY)."""
    name = "gemini"
    def __init__(self):
        from google import genai              # lazy import
        from google.genai import types
        self._genai = genai
        self._c = genai.Client(http_options=types.HttpOptions(timeout=_CALL_TIMEOUT_S * 1000))
    def generate(self, system: str, user: str) -> str:
        from google.genai import types
        def call():
            r = self._c.models.generate_content(
                model=GEMINI_MODEL, contents=user,
                config=types.GenerateContentConfig(
                    system_instruction=system, max_output_tokens=_MAX_TOKENS))
            um = getattr(r, "usage_metadata", None)
            if um is not None:
                _charge("gemini", getattr(um, "prompt_token_count", 0) or 0,
                        getattr(um, "candidates_token_count", 0) or 0)
            return r.text or ""
        return _retry(call)


def anthropic_haiku() -> ModelAdapter:
    return _Haiku()


def gemini_flash_lite() -> ModelAdapter:
    return _Gemini()


def get_adapter(name: str) -> ModelAdapter:
    if name == "mock":
        return MockAdapter()
    if name in ("haiku", "claude-haiku-4-5"):
        return anthropic_haiku()
    if name in ("gemini", "gemini-flash-lite"):
        return gemini_flash_lite()
    raise ValueError(f"unknown model {name}")


# --------------------------------------------------------------------------- #
# Grading + measurement.
# --------------------------------------------------------------------------- #
_SELF_EVAL_SYS = ("You are grading whether an answer satisfies a task. "
                  "Reply with exactly one word: PASS or FAIL.")


def _self_assess(adapter, task_user: str, answer: str) -> bool:
    """The agent's OWN verdict on its work - a real model call (no skill, no
    registrar). Comparing this to the objective registrar is the H2 signal:
    does the model's unaided self-eval track ground truth, or is it optimistic?"""
    if not answer.strip():
        return False
    resp = adapter.generate(
        _SELF_EVAL_SYS,
        f"TASK:\n{task_user}\n\nANSWER:\n{answer}\n\n"
        "Did the answer fully and correctly satisfy the task? Reply PASS or FAIL.")
    up = resp.strip().upper()
    return up.startswith("PASS") or ("PASS" in up and "FAIL" not in up)


_MOCK_CHURN = 0.5   # fraction of paired runs whose two arms differ (task noise)


def _paired_ci95(pairs):
    """95% CI on the paired win-rate difference (McNemar). Only the DISCORDANT
    pairs (one arm passes, the other fails) carry signal — which is why a paired
    design needs far fewer samples than two independent arms."""
    n = len(pairs)
    if n == 0:
        return 0.0, (0.0, 0.0)
    b = sum(1 for gw, gwo in pairs if gw and not gwo)   # skill-only win
    c = sum(1 for gw, gwo in pairs if gwo and not gw)   # baseline-only win
    d = (b - c) / n
    var = ((b + c) - (b - c) ** 2 / n) / (n * n)
    se = max(var, 0.0) ** 0.5
    return d, (d - 1.96 * se, d + 1.96 * se)


def _effect_row(pairs: list) -> Dict:
    n = len(pairs)
    w = sum(1 for gw, _ in pairs if gw)
    wo = sum(1 for _, gwo in pairs if gwo)
    eff, (lo, hi) = _paired_ci95(pairs)
    return {
        "effect": round(eff, 3), "n_paired": n,
        "with_pass": round(w / n, 3), "without_pass": round(wo / n, 3),
        "effect_ci95": [round(lo, 3), round(hi, 3)],
        "significant": (lo > 0 or hi < 0),   # CI excludes 0 (either direction)
        "direction": "helps" if lo > 0 else ("HURTS" if hi < 0 else "unclear"),
    }


def measure(adapter: ModelAdapter, tasks: List[Task], runs: int = 5,
            mock: bool = True, budget_usd: float = None,
            out_path: str = "", resume: Dict = None) -> Dict:
    """For each task run WITH and WITHOUT the skill `runs` times (paired: same
    task, both arms), grade by the objective registrar, and estimate the paired
    win-rate difference per skill with a McNemar 95% CI (H1). A real self-assess
    call vs the registrar gives the eval false-positive rate (H2).

    If `budget_usd` is set, the run hard-stops before the next task once spend
    reaches it, and reports `truncated: true` - so an unattended run cannot
    overrun. Partial results are still returned.

    Crash resilience (added after repeated network-outage aborts lost whole
    runs): if `out_path` is set, the partial result is flushed to disk after
    every task, so an outage-triggered circuit-breaker abort keeps every skill
    that finished. `resume` pre-seeds skill_effects from a prior partial file;
    tasks whose skill is already complete there are skipped, so a re-run picks
    up where the last one died instead of re-paying for finished skills."""
    resume = resume or {}
    tasks_per_skill: Dict[str, int] = {}
    for t in tasks:
        tasks_per_skill[t.skill] = tasks_per_skill.get(t.skill, 0) + 1
    # A resumed skill counts as done only if it carries the full pair count we'd
    # produce now (runs * its task count) - a partial skill is re-run cleanly.
    done_skills = {s for s, row in resume.items()
                   if row.get("n_paired", 0) >= runs * tasks_per_skill.get(s, 10 ** 9)}
    per_skill_pairs: Dict[str, list] = {}
    skill_effects: Dict[str, Dict] = {s: resume[s] for s in done_skills}
    fp = tp = fn = tn = 0
    truncated = False

    def _result() -> Dict:
        return {
            "model": adapter.name, "mode": "mock" if mock else "real",
            "skill_effects": skill_effects,                              # H1 -> World.build
            "eval_false_positive_rate": round(fp / ((fp + tn) or 1), 3), # H2 -> 1 - specificity
            "eval_sensitivity": round(tp / ((tp + fn) or 1), 3),
            "n_tasks": len(tasks), "runs": runs, "truncated": truncated,
            "spend_usd": round(_SPEND["usd"], 4), "calls": _SPEND["calls"],
            "tokens": {"in": _SPEND["in_tok"], "out": _SPEND["out_tok"]},
        }

    def _flush():
        if out_path:
            import json as _json
            with open(out_path, "w") as f:
                _json.dump(_result(), f, indent=2)

    try:
        for t in tasks:
            if t.skill in done_skills:
                continue
            if budget_usd is not None and _SPEND["usd"] >= budget_usd:
                truncated = True
                break
            for k in range(runs):
                if mock:
                    rng = random.Random(f"{adapter.name}-{t.tid}-{k}")
                    r = rng.random()
                    b_only = max(0.0, (_MOCK_CHURN + t.mock_effect) / 2)   # skill-only win
                    c_only = max(0.0, (_MOCK_CHURN - t.mock_effect) / 2)   # baseline-only win
                    if r < b_only:
                        gw, gwo = True, False
                    elif r < b_only + c_only:
                        gw, gwo = False, True
                    else:                                                  # concordant pair
                        both = rng.random() < t.base_rate
                        gw = gwo = both
                    # Mock model self-assessment bias (realistic H2 shape: high recall, moderate false-positive rate)
                    self_eval = (rng.random() < 0.95) if gw else (rng.random() < 0.30)
                else:
                    out_with = adapter.generate(t.system_base + "\n" + t.skill_text, t.user)
                    out_without = adapter.generate(t.system_base, t.user)
                    gw, gwo = t.registrar(out_with), t.registrar(out_without)
                    self_eval = _self_assess(adapter, t.user, out_with)   # real H2 signal
                per_skill_pairs.setdefault(t.skill, []).append((gw, gwo))
                truth = gw
                if self_eval and truth: tp += 1
                elif self_eval and not truth: fp += 1
                elif not self_eval and truth: fn += 1
                else: tn += 1
            # Recompute this skill's row from all pairs seen so far and checkpoint.
            skill_effects[t.skill] = _effect_row(per_skill_pairs[t.skill])
            _flush()
    except BaseException:
        # Circuit-breaker abort, Ctrl-C, or any error: persist what completed so
        # a --resume run doesn't re-pay for it, then re-raise.
        _flush()
        raise

    return _result()


if __name__ == "__main__":
    import argparse
    import json
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="mock", help="mock | haiku | gemini")
    ap.add_argument("--runs", type=int, default=5)
    ap.add_argument("--limit", type=int, default=0, help="cap #tasks (cheap smoke test)")
    ap.add_argument("--budget", type=float, default=None, help="hard USD spend cap")
    ap.add_argument("--out", default="", help="write result JSON to this path (checkpointed per-skill)")
    ap.add_argument("--skills", default="", help="comma-separated skill names to filter to")
    ap.add_argument("--resume", action="store_true",
                     help="if --out exists, load it and skip already-complete skills "
                          "(pick up where a prior outage-aborted run left off)")
    ap.add_argument("--selfcheck", action="store_true",
                     help="check registrars against their own fixtures and exit (no API calls, no spend)")
    ap.add_argument("--force", action="store_true",
                     help="skip the automatic pre-spend registrar selfcheck gate")
    args = ap.parse_args()

    tasks = load_tasks()
    if args.skills:
        wanted = {s.strip() for s in args.skills.split(",") if s.strip()}
        tasks = [t for t in tasks if t.skill in wanted]
    if args.limit:
        tasks = tasks[:args.limit]

    from .tasks import FIXTURES, selfcheck as _selfcheck
    problems = _selfcheck(tasks)
    covered = sum(1 for t in tasks if t.tid in FIXTURES)
    if args.selfcheck:
        print(f"# selfcheck: {covered}/{len(tasks)} tasks have fixtures on file")
        if problems:
            print(f"FAILED - {len(problems)} registrar(s) disagree with their own fixture:")
            for p in problems:
                print(f"  - {p}")
            raise SystemExit(1)
        print("OK - every registrar with a fixture correctly passes its positive "
              "sample and rejects its negative sample.")
        raise SystemExit(0)

    if problems and not args.force:
        print(f"REGISTRAR SELFCHECK FAILED - aborting before spending any budget "
              f"({len(problems)} issue(s)):")
        for p in problems:
            print(f"  - {p}")
        print("Fix the registrar (or its fixture in simulator/tasks.py FIXTURES) and "
              "retry, or pass --force to override.")
        raise SystemExit(1)

    resume_effects = None
    if args.resume and args.out and os.path.exists(args.out):
        resume_effects = json.load(open(args.out)).get("skill_effects", {})
        print(f"# --resume: loaded {len(resume_effects)} completed skill(s) from {args.out}")

    result = measure(get_adapter(args.model), tasks, runs=args.runs,
                     mock=(args.model == "mock"), budget_usd=args.budget,
                     out_path=args.out, resume=resume_effects)
    print(json.dumps(result, indent=2))
    if args.out:
        # measure() already checkpointed to out_path after every skill; this is
        # just the final authoritative flush.
        with open(args.out, "w") as f:
            json.dump(result, f, indent=2)
        print(f"\n# wrote {args.out}")

    from collections import Counter
    per_skill = Counter(t.skill for t in tasks)
    print(f"\n# {result['n_tasks']} tasks ({args.runs} runs each) across {len(per_skill)} skills.")
    print("# `significant` per skill = CI-excludes-zero. False → not enough tasks/runs yet")
    print("#   (target ~8-15 tasks/skill). Current per-skill task counts:")
    for s, n in per_skill.most_common():
        print(f"#     {s:<22} {n} tasks")
    print("# H1: skill_effects.effect feeds World.build. H2: eval_false_positive_rate")
    print("#     is (1 - specificity); a value that REPEATS across haiku AND gemini is a")
    print("#     cross-model blind spot — the H2 failure the population sim then propagates.")
