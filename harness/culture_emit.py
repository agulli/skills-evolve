#!/usr/bin/env python3
"""Culture-telemetry emitter (harness/culture_emit.py).

Runnable reference for the `culture-telemetry` skill: turn a local routing log
into the ONLY thing allowed to leave a node — an anonymized, signed, aggregate
pattern-card. Zero dependency (stdlib hashlib/hmac only), no network.

The privacy contract is enforced STRUCTURALLY, not by policy text: this emitter
can only read the ALLOWLIST fields below off each log row and only ever emits
counts and rates. There is no code path by which a prompt, a trace, a tool
output, or raw user text reaches the output — a field not on the allowlist is
never touched. That is the whole point (EXPERIMENTS.md EXP-023, telemetry_doc):
"nothing foreign executes, no traces/impl leave."

Usage:
    python3 harness/culture_emit.py --log routing_log.jsonl --secret-file node.key
    python3 harness/culture_emit.py            # built-in demo log, ephemeral key
"""

import argparse
import hashlib
import hmac
import json
import os
import time
from typing import Dict, List, Any

# The ONLY per-row fields the emitter is permitted to read. Anything else in a
# log row (prompt text, user message, tool output, file contents) is
# structurally unreachable — the emitter never indexes those keys.
ALLOWLIST = ("skill", "tier", "user_response", "model_generation")

# The ONLY aggregate fields that appear in a pattern-card. Per-skill: how often
# it fired, the accept rate, and the model generation it was observed under.
# No free text, no ids, no timestamps at row granularity.
K_ANON_FLOOR = 5   # a skill with fewer than this many observations is dropped


def _demo_log() -> List[Dict[str, Any]]:
    import random
    rng = random.Random(7)
    skills = [("tool-design", 0.92), ("context-engineering", 0.78),
              ("secrets-management", 0.95), ("multimodal", 0.60)]
    rows = []
    for i in range(200):
        skill, acc = rng.choice(skills)
        rows.append({
            "timestamp": time.time() - i * 60,
            "skill": skill,
            "tier": "PROPOSE",
            "user_response": "accepted" if rng.random() < acc else "overridden",
            "model_generation": "haiku-4.5",
            # deliberately-sensitive fields that must NEVER leave:
            "prompt": "SECRET SYSTEM PROMPT — should never appear in output",
            "user_message": "private user text — should never appear in output",
            "tool_output": "{...raw tool payload...}",
        })
    return rows


def _read_log(path: str) -> List[Dict[str, Any]]:
    if not path or not os.path.exists(path):
        print(f"[culture] no log at {path!r}; using built-in demo log")
        return _demo_log()
    rows = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    rows.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return rows


def build_pattern_card(rows: List[Dict[str, Any]], node_secret: bytes) -> Dict[str, Any]:
    """Aggregate the log into an emittable pattern-card. Reads ONLY allowlisted
    fields; emits ONLY counts/rates above the k-anonymity floor."""
    per: Dict[tuple, Dict[str, int]] = {}
    for r in rows:
        # structural allowlist: pull only permitted keys, ignore everything else
        skill = r.get("skill")
        gen = r.get("model_generation", "unknown")
        resp = r.get("user_response", "accepted")
        if not skill:
            continue
        key = (skill, gen)
        cell = per.setdefault(key, {"fired": 0, "accepted": 0})
        cell["fired"] += 1
        if resp == "accepted":
            cell["accepted"] += 1

    patterns = []
    for (skill, gen), c in sorted(per.items()):
        if c["fired"] < K_ANON_FLOOR:          # k-anonymity: drop thin cells
            continue
        patterns.append({
            "skill": skill,
            "model_generation": gen,
            "fired": c["fired"],
            "accept_rate": round(c["accepted"] / c["fired"], 3),
        })

    # node id is a salted hash of the secret — stable per node, not reversible
    node_id = hashlib.sha256(b"node-id:" + node_secret).hexdigest()[:16]
    body = {
        "schema": "culture-pattern-card/v1",
        "date": time.strftime("%Y-%m-%d", time.gmtime()),
        "node_id": node_id,
        "patterns": patterns,
    }
    # sign the canonical body so the commons can verify integrity/authenticity
    payload = json.dumps(body, sort_keys=True, separators=(",", ":")).encode()
    body["signature"] = hmac.new(node_secret, payload, hashlib.sha256).hexdigest()
    return body


def assert_no_leak(card: Dict[str, Any], rows: List[Dict[str, Any]]) -> None:
    """Structural safety net: prove no sensitive value leaked into the card.
    Scans the serialized card for any non-allowlisted string value present in
    the source log. Raises if anything foreign is found."""
    blob = json.dumps(card)
    for r in rows:
        for k, v in r.items():
            if k in ALLOWLIST or not isinstance(v, str):
                continue
            if v and v in blob:
                raise AssertionError(f"LEAK: non-allowlisted field {k!r} value appeared in card")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--log", default="", help="JSONL routing log (default: built-in demo)")
    ap.add_argument("--secret-file", default="", help="node secret key file (default: ephemeral)")
    ap.add_argument("--out", default="", help="write the pattern-card JSON here")
    args = ap.parse_args()

    rows = _read_log(args.log)
    if args.secret_file and os.path.exists(args.secret_file):
        secret = open(args.secret_file, "rb").read()
    else:
        secret = os.urandom(32)
        print("[culture] using an ephemeral node secret (pass --secret-file for a stable node id)")

    card = build_pattern_card(rows, secret)
    assert_no_leak(card, rows)   # would raise before anything is written/emitted
    print(json.dumps(card, indent=2))
    print(f"\n# leak check PASSED — only allowlisted aggregates in the card "
          f"({len(card['patterns'])} patterns, k-anon floor {K_ANON_FLOOR})")
    if args.out:
        with open(args.out, "w") as f:
            json.dump(card, f, indent=2)
        print(f"# wrote {args.out}")
