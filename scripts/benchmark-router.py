#!/usr/bin/env python3
"""Native Router Prompt Benchmark - tests skills/ROUTING.md routing accuracy.

This script evaluates how accurately an LLM (or mock matcher) routes realistic
user queries to their expected row in `skills/ROUTING.md`.

Usage:
    python3 scripts/benchmark-router.py --mode mock
    python3 scripts/benchmark-router.py --mode llm --model haiku
    python3 scripts/benchmark-router.py --mode llm --model gemini
"""

import argparse
import json
import os
import re
import sys
from typing import Dict, List, Tuple

# Sample dataset of user utterances mapped to expected skills in ROUTING.md
BENCHMARK_DATASET = [
    # design
    ("We need a bot that helps users reset passwords, but I'm not sure what requirements we need yet.", "requirements-interrogation"),
    ("Should this email assistant be a single agent or a coordinator with 3 worker subagents?", "agent-architecture"),
    ("Starting a brand new agent repo from scratch, set up the project structure.", "agent-scaffolding"),
    ("I need to build the communication protocol between our router agent and worker subagents.", "handoff-protocol"),
    ("The agent is ignoring the system prompt instructions when the conversation gets long.", "prompt-architecture"),
    ("Reviewing this new tool schema to convert string types to strict enums.", "tool-adversarial-reading"),
    
    # build
    ("The token cost is skyrocketing as this long-horizon agent session grows.", "context-engineering"),
    ("The agent answers user questions from PDFs but doesn't cite where it found the answer.", "grounding-citation"),
    ("We need to build an MCP server wrapping our SQL database.", "mcp-server"),
    ("Store user preferences across sessions so the agent remembers them next time.", "memory-design"),
    ("Process a PDF report with embedded charts and images.", "multimodal"),
    ("Build a RAG pipeline to search over internal confluence docs.", "retrieval-design"),
    ("Write a new SKILL.md for API rate limiting.", "skill-authoring"),
    ("The agent needs to pause execution and wait for human input before continuing.", "state-management"),
    
    # safety
    ("The agent serves multiple customers and needs tenant isolation.", "agent-identity"),
    ("Map our agent permissions against SOC2 compliance controls.", "compliance-mapping"),
    ("Before shipping to production, ensure the agent can't execute unapproved shell commands.", "guardrails"),
    ("Check if untrusted web content ingested by the agent contains indirect prompt injection.", "injection-audit"),
    ("The agent generates user-facing responses that might contain toxic language.", "output-safety"),
    ("Ensure no PII or user email addresses leak into our telemetry logs.", "privacy"),
    ("Restrict generated python execution to a gvisor sandbox.", "sandbox-policy"),
    ("Move hardcoded API tokens into HashiCorp Vault.", "secrets-management"),
    ("Vet a third-party MCP server package before installing it.", "supply-chain-vetting"),
    
    # eval
    ("Spawn a reviewer agent to disprove our new security architecture before we ship.", "adversarial-review"),
    ("Build a numeric eval harness with programmatic assertions.", "eval-harness"),
    ("We need to build an eval for our new agent from scratch, no tests exist yet.", "eval-harness"),
    ("This eval just reported a huge, surprising drop in accuracy after a one-line prompt "
     "change — before we ship the rollback, make sure the check itself isn't broken.", "verifier-design"),
    ("The registrar keeps failing outputs that look correct to me — I think it's being too "
     "strict about exact wording instead of checking what actually matters.", "verifier-design"),
    ("Use GPT-4 as a judge to grade conversational tone.", "llm-judge"),
    ("Write a model card documenting capabilities and limitations for the release.", "model-card"),
    ("Read the failed execution logs backwards to find the first divergence point.", "trajectory-review"),
    ("Extrapolate 50 synthetic test variations from 5 real production tasks.", "synthetic-task-generation"),
    ("Audit successful runs to check if the agent claimed success without executing the tool.", "silent-failure-audit"),
    
    # ops
    ("The agent is currently sending wrong emails right now in production!", "agent-incident"),
    ("Set up OpenTelemetry tracing and latency dashboards.", "agent-observability"),
    ("Implement spending limits and cost allocation per tenant.", "cost-governance"),
    ("Reduce per-task token cost by 50%.", "cost-optimization"),
    ("Deploy a new prompt version using a canary release strategy.", "deployment"),
    ("The agent hits an unrecoverable error loop and needs to page a human with options.", "human-review-escalation"),
    ("Optimize p95 latency for interactive chat responses.", "latency-optimization"),
    ("Migrate our agent prompt from Claude 3 Haiku to Claude 3.5 Sonnet.", "model-migration"),
    ("Route easy queries to Flash-Lite and complex queries to Opus.", "model-routing"),
    ("Make the agent resilient to tool API timeouts with circuit breakers.", "reliability-engineering"),
    
    # evolve
    ("Aggregate local routing decision logs daily into signed allowlist records.", "culture-telemetry"),
    ("Monitor an auto-applied skill change during its 7-day canary period.", "evolution-canary"),
    ("Two evolution triggers fire on the same skill simultaneously.", "evolution-conflict"),
    ("Tune the evolution loop's own thresholds after 20 cycles.", "evolution-meta"),
    ("Propagate a promoted canary skill to other repos via a PR.", "evolution-propagate"),
    ("Run a daily sweep of routing logs to detect high override rates.", "evolution-scan"),
    ("Capture user corrections when they say 'no, don't do it that way'.", "feedback-harvesting"),
    ("Tune the routing table weights based on user accept/override rates.", "routing-tuner"),
    ("Design a bounded self-improvement loop for prompt optimization.", "self-improvement-loop"),
    ("Extract a recurring 3-step solution into a reusable skill.", "skill-distillation"),
    ("Clean up obsolete skills that haven't fired in 6 months.", "skill-maintenance"),
    ("Consolidate a system prompt that has grown by 40% with contradictory rules.", "accretion-refactor"),
    
    # dev
    ("Review a PR that modifies system prompts and tool schemas.", "agent-code-review"),
    ("Scaffold a new agent project skeleton with `make dev`.", "agent-scaffolding"),
    ("Onboard a new developer to this agent repository.", "codebase-onboarding"),
    ("Replay a single recorded production trace locally.", "local-replay"),
    ("Test 5 prompt variations in parallel against the harness.", "prompt-experimentation"),
    ("Make unit testing for custom agent tools faster.", "testing-ergonomics"),
]


def load_routing_table() -> str:
    path = os.path.join(os.path.dirname(__file__), "..", "skills", "ROUTING.md")
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def mock_route_query(query: str, routing_table: str) -> str:
    """Mock routing matcher based on trigger text matching."""
    q_lower = query.lower()
    
    # Extract rows from table
    rows = re.findall(r'\| ([^|]+) \| `([a-z0-9-]+)` \|', routing_table)
    
    best_match = None
    max_overlap = -1
    
    for trigger_text, skill_name in rows:
        words = set(re.findall(r'\w+', trigger_text.lower())) - {'a', 'an', 'the', 'is', 'or', 'and', 'to', 'in', 'of', 'for', 'with', 'on'}
        q_words = set(re.findall(r'\w+', q_lower))
        overlap = len(words.intersection(q_words))
        if overlap > max_overlap:
            max_overlap = overlap
            best_match = skill_name
            
    return best_match or "unknown"


def llm_route_query(adapter, query: str, routing_table: str) -> str:
    """Route query using live LLM provider adapter."""
    system_prompt = (
        "You are an expert agent routing engine. Given a user query and the routing table below, "
        "select the single best matching skill name. Output ONLY the skill name string (e.g., 'eval-harness'), nothing else.\n\n"
        f"ROUTING TABLE:\n{routing_table}"
    )
    user_prompt = f"USER QUERY: {query}\n\nMATCHING SKILL:"
    response = adapter.generate(system_prompt, user_prompt).strip()
    match = re.search(r'`?([a-z0-9-]+)`?', response)
    if match:
        return match.group(1)
    return response


def run_benchmark(mode: str = "mock", model_name: str = "haiku") -> Dict:
    routing_table = load_routing_table()
    total = len(BENCHMARK_DATASET)
    correct = 0
    results = []
    
    adapter = None
    if mode == "llm":
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
        from simulator.measure import get_adapter
        try:
            adapter = get_adapter(model_name)
            print(f"Loaded live LLM adapter: {adapter.name}")
        except Exception as e:
            print(f"Warning: Could not initialize LLM adapter '{model_name}': {e}. Falling back to mock matcher.")
            mode = "mock"

    print(f"Running Router Benchmark ({mode.upper()} mode, {total} queries)...")
    
    for query, expected in BENCHMARK_DATASET:
        if mode == "llm" and adapter is not None:
            predicted = llm_route_query(adapter, query, routing_table)
        else:
            predicted = mock_route_query(query, routing_table)
            
        is_correct = (predicted == expected)
        if is_correct:
            correct += 1
        results.append({
            "query": query,
            "expected": expected,
            "predicted": predicted,
            "correct": is_correct
        })
        
    accuracy = correct / total
    print(f"Benchmark Complete! Accuracy: {correct}/{total} ({accuracy * 100:.1f}%)")
    
    return {
        "total": total,
        "correct": correct,
        "accuracy": round(accuracy, 4),
        "results": results
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Router Prompt Benchmark")
    parser.add_argument("--mode", default="mock", choices=["mock", "llm"])
    parser.add_argument("--model", default="haiku", help="Model adapter name (haiku | gemini)")
    args = parser.parse_args()
    
    res = run_benchmark(args.mode, args.model)
    if args.mode == "llm":
        from simulator.measure import _SPEND
        print(f"spend_usd={round(_SPEND['usd'], 4)} calls={_SPEND['calls']}")
    if res["accuracy"] < 0.80:
        print("WARNING: Router accuracy below 80% threshold!")
        sys.exit(1)
    sys.exit(0)
