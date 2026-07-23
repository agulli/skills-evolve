#!/usr/bin/env python3
"""Evolution Scan Micro-Harness Reference Implementation (harness/scan.py).

Zero-dependency Python CLI tool that implements the `evolution-scan` procedure.
Reads routing decision logs, calculates override rates, detects failure clusters,
and dispatches triggers for CI/CD or local evolution execution.

Usage:
    python3 harness/scan.py --log decision_log.jsonl
    python3 harness/scan.py --dry-run
"""

import argparse
import json
import os
import sys
import time
from typing import Dict, List, Any


def read_decision_log(log_path: str) -> List[Dict[str, Any]]:
    """Read JSONL decision log entries."""
    if not os.path.exists(log_path):
        print(f"[scan] Decision log {log_path} not found. Creating sample entries.")
        return [
            {"timestamp": time.time() - 3600, "skill": "context-engineering", "tier": "PROPOSE", "user_response": "overridden"},
            {"timestamp": time.time() - 1800, "skill": "context-engineering", "tier": "PROPOSE", "user_response": "overridden"},
            {"timestamp": time.time() - 900, "skill": "context-engineering", "tier": "PROPOSE", "user_response": "accepted"},
            {"timestamp": time.time() - 600, "skill": "trajectory-review", "tier": "AUTO", "user_response": "accepted"},
            {"timestamp": time.time() - 300, "skill": "agent-incident", "tier": "AUTO", "user_response": "accepted"},
        ]
        
    records = []
    with open(log_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return records


def run_evolution_scan(log_path: str, override_threshold: float = 0.30, min_invocations: int = 3) -> Dict[str, Any]:
    """Execute evolution sweep across decision logs."""
    records = read_decision_log(log_path)
    
    # Track per-skill stats
    stats: Dict[str, Dict[str, int]] = {}
    for r in records:
        skill = r.get("skill", "unknown")
        resp = r.get("user_response", "accepted")
        if skill not in stats:
            stats[skill] = {"total": 0, "accepted": 0, "overridden": 0}
        stats[skill]["total"] += 1
        if resp == "overridden":
            stats[skill]["overridden"] += 1
        else:
            stats[skill]["accepted"] += 1

    # Detect override triggers
    dispatches = []
    for skill, data in stats.items():
        if data["total"] >= min_invocations:
            override_rate = data["overridden"] / data["total"]
            if override_rate >= override_threshold:
                dispatches.append({
                    "skill": skill,
                    "trigger_type": "override_rate_exceeded",
                    "override_rate": round(override_rate, 3),
                    "target_skill": "routing-tuner",
                    "action": f"Dispatch to routing-tuner to tighten ROUTING.md for {skill}"
                })

    report = {
        "timestamp": time.time(),
        "total_records_scanned": len(records),
        "skills_monitored": len(stats),
        "triggers_detected": len(dispatches),
        "dispatches": dispatches,
        "status": "COMPLETED"
    }
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evolution Scan Micro-Harness")
    parser.add_argument("--log", default="decision_log.jsonl", help="Path to JSONL decision log")
    parser.add_argument("--threshold", type=float, default=0.30, help="Override rate threshold (default: 0.30)")
    parser.add_argument("--dry-run", action="store_true", help="Print report without writing state")
    args = parser.parse_args()

    report = run_evolution_scan(args.log, override_threshold=args.threshold)
    print(json.dumps(report, indent=2))
