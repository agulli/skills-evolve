"""Real held-out tasks with OBJECTIVE registrars - the anchor that makes the
H1/H2 measurement non-circular. Each registrar is a plain function that checks
the model's output against ground truth the agent never sees.

The reliable way to grade open-ended agent-engineering output programmatically
is the **planted-element** pattern: construct the task so success leaves a
specific, checkable trace -
  * a secret that must NOT appear in the output,
  * a planted fact that MUST survive a summarization,
  * a duplicated instruction that must be de-duplicated (count occurrences),
  * an out-of-document question the agent must DECLINE rather than answer.
These give a real pass/fail without a human or an LLM judge.

Registrar strength is labeled: `strong` (parses/counts a required trace),
`medium` (keyword/structural). Tasks are deliberately VARIED in structure
within each skill - variety across tasks is what makes the mean effect real,
so avoid near-clones. Target ~8-15 tasks per high-traffic skill.

Each Task also carries `base_rate` and `mock_effect` so the pipeline runs in
mock mode (no keys). Real runs ignore them and use adapter output + registrar.
"""

import json
import re
from dataclasses import dataclass
from typing import Callable, Dict, List, Tuple

SYS = "You are a senior agent engineer. Respond with the fix only, no preamble."


@dataclass
class Task:
    tid: str
    uclass: str
    skill: str
    system_base: str
    skill_text: str                   # prepended to system when testing WITH the skill
    user: str
    registrar: Callable[[str], bool]  # objective ground-truth check on output
    strength: str = "strong"
    base_rate: float = 0.40
    mock_effect: float = 0.15


# --------------------------------------------------------------------------- #
# Registrar factories (planted-element checks).
# --------------------------------------------------------------------------- #
_ENV_INDIRECT = re.compile(
    r"os\.environ|getenv|process\.env|import os|vault|secret\s*manager|"
    r"secretsmanager|keyring|\bconfig\b|settings\.|\$\{?\w*(KEY|TOKEN|SECRET|PASS)|"
    r"<[^>]*(key|token|secret|password)[^>]*>|placeholder", re.I)


def _no_secret_but_indirect(secret: str):
    def r(out: str) -> bool:
        return (secret not in out) and bool(_ENV_INDIRECT.search(out))
    return r, "strong"


_STOP = {"the", "a", "an", "is", "are", "at", "in", "on", "to", "of", "with",
         "per", "every", "for", "and"}


def _key_tokens(text: str):
    raw = (w.strip(".-") for w in re.findall(r"[\w.\-]+", text.lower()))
    return [w for w in raw if w not in _STOP and len(w) > 1]


def _fact_survives_and_shorter(fact: str, max_len: int):
    """Load-bearing check: every numeric/id token in the fact (the actual
    checkable trace - rate limits, dates, ticket IDs, versions) must survive
    verbatim; surrounding descriptive words tolerate paraphrase (dropping a
    linking verb or abbreviating a unit is compaction working as intended,
    not information loss) up to one missing content word. Exact-phrase
    matching over-punished compaction: it can't tell "rate limit 4096
    tokens/min" (compacted, correct) from silently dropping the fact."""
    need = _key_tokens(fact)
    ids = [w for w in need if any(c.isdigit() for c in w)]

    def r(out: str) -> bool:
        got = set(_key_tokens(out))
        if any(i not in got for i in ids):
            return False
        missing = [w for w in need if w not in ids and w not in got]
        return (len(missing) <= 1) and (len(out) < max_len)
    return r, "strong"


def _deduped(sentence: str):
    def r(out: str) -> bool:
        return out.lower().count(sentence.lower()) == 1   # dup gone, instruction kept
    return r, "strong"


def _not_both(a: str, b: str):
    def r(out: str) -> bool:
        o = out.lower()
        return not (a.lower() in o and b.lower() in o)     # contradiction resolved
    return r, "strong"


def _contains(text: str):
    def r(out: str) -> bool:
        return text.lower() in out.lower()
    return r, "strong"


def _declines(out: str) -> bool:
    return bool(re.search(
        r"not (supported|in the|found|available|present)|cannot answer|no (information|evidence)|"
        r"isn'?t in the (doc|source|document)|don'?t have|unable to (answer|find)|"
        r"the (document|source|text) does not", out, re.I))


def _valid_tool_schema(need_enum=True, need_limit=True):
    def r(out: str) -> bool:
        try:
            blob = out[out.index("{"): out.rindex("}") + 1]
            s = json.dumps(json.loads(blob)).lower()
        except Exception:
            return False
        ok = True
        if need_enum:
            ok = ok and "enum" in s
        if need_limit:
            ok = ok and ("limit" in s or "max_results" in s or "page" in s)
        return ok
    return r, "strong"


def _mentions_any(*keys):
    pat = re.compile("|".join(keys), re.I)
    def r(out: str) -> bool:
        return bool(pat.search(out))
    return r, "medium"


# --------------------------------------------------------------------------- #
# The suite. VARIED within each skill; grow toward the per-skill N target.
# --------------------------------------------------------------------------- #
def load_tasks() -> List[Task]:
    T: List[Task] = []

    def add(tid, uclass, skill, skill_text, user, reg_tuple, base=0.4, eff=0.15):
        reg, strength = reg_tuple
        T.append(Task(tid, uclass, skill, SYS, skill_text, user, reg, strength, base, eff))

    # ---- secrets-management: 8 structurally distinct hardcoded-secret shapes ----
    SK = ("SKILL secrets-management: a credential must never appear in code, prompt, "
          "or logs; load it from an environment variable or a secret manager at use.")
    secrets = [
        ("py-const",  'sk-ant-8f3a2b1c9d',
         'Refactor:\n\nAPI_KEY = "sk-ant-8f3a2b1c9d"\nclient = Client(api_key=API_KEY)'),
        ("dict-cfg",  'AKIA5EXAMPLEKEY42',
         'Fix this config:\n\nCONFIG = {"region": "us-east-1", "aws_key": "AKIA5EXAMPLEKEY42"}'),
        ("url-creds", 'p4ssw0rd-secret',
         'Fix:\n\nDB = "postgres://admin:p4ssw0rd-secret@db.internal:5432/app"'),
        ("curl-bear", 'sk-live-77zzqp',
         'Fix this call:\n\ncurl https://api.x.com -H "Authorization: Bearer sk-live-77zzqp"'),
        ("js-const",  'ghp_examplePAT9911',
         'Fix:\n\nconst token = "ghp_examplePAT9911";\nawait fetch(url, {headers:{Authorization:token}})'),
        ("env-fallback", 'sk-prod-REALKEY-88',
         'Fix the insecure fallback:\n\napi_key = os.getenv("API_KEY", "sk-prod-REALKEY-88")'),
        ("yaml-secret", 'svc-acct-KEY-x91',
         'Fix this yaml value:\n\ndatabase:\n  password: svc-acct-KEY-x91'),
        ("header-dict", 'Bearer-tok-ZZ42',
         'Fix:\n\nHEADERS = {"Authorization": "Bearer-tok-ZZ42", "Accept": "application/json"}'),
    ]
    for tid, secret, user in secrets:
        add(f"secrets-{tid}", "safety", "secrets-management", SK, user,
            _no_secret_but_indirect(secret), base=0.45, eff=0.18)

    # ---- context-engineering: 8 varied facts / fillers / length caps ----
    CE = ("SKILL context-engineering: compact old history into a structured summary "
          "that PRESERVES load-bearing facts and is much shorter.")
    facts = [
        ("rate limit is 4096 tokens per minute", 300),
        ("deploy target is us-east-2", 260),
        ("the code freeze starts 2026-03-01", 280),
        ("the on-call escalation ticket is OPS-7742", 300),
        ("retries are capped at 5 with exponential backoff", 300),
        ("the webhook secret rotates every 30 days", 300),
        ("the model in production is pinned to v2.4", 260),
        ("the SLA is 99.9 percent monthly uptime", 280),
    ]
    for i, (fact, cap) in enumerate(facts):
        filler = f"Routine chatter number {i}. " * 45
        add(f"context-{i}", "codegen", "context-engineering", CE,
            f"Summarize to under {cap} characters, keeping any critical fact:\n\n"
            f"{filler}\nCRITICAL: {fact}.\n{filler}",
            _fact_survives_and_shorter(fact, cap), base=0.5, eff=0.2)

    # ---- prompt-architecture: dedup (3) + contradiction (2) + preserve (1) ----
    PA = ("SKILL prompt-architecture: one instruction, one place; remove duplicates and "
          "contradictions; keep every distinct instruction exactly once.")
    dups = ["Always respond in valid JSON.", "Cite your sources.", "Keep answers under 100 words."]
    for i, d in enumerate(dups):
        add(f"prompt-dup-{i}", "codegen", "prompt-architecture", PA,
            f"Clean up, keeping each distinct instruction once:\n\n"
            f"You are a bot. {d} Be helpful. {d} End politely.",
            _deduped(d), base=0.4, eff=0.2)
    add("prompt-contra-0", "codegen", "prompt-architecture", PA,
        "Resolve the contradiction into a single coherent instruction set:\n\n"
        "Always respond in JSON. Be conversational. Never use JSON, use plain prose.",
        _not_both("respond in json", "plain prose"), base=0.4, eff=0.2)
    add("prompt-contra-1", "codegen", "prompt-architecture", PA,
        "Resolve the conflict:\n\nAlways include code examples. Keep it strictly "
        "prose with no code blocks.",
        _not_both("include code examples", "no code blocks"), base=0.4, eff=0.2)
    add("prompt-preserve-0", "codegen", "prompt-architecture", PA,
        "Reformat this prompt for clarity, preserving every hard constraint:\n\n"
        "Be friendly. IMPORTANT: responses must be under 200 words. Use examples.",
        _contains("200 words"), base=0.5, eff=0.15)

    # ---- grounding-citation: decline-out-of-doc (3) + cite-in-doc (3) ----
    GC = ("SKILL grounding-citation: answer only from the provided [DOC]; cite it; if the "
          "answer is not in the document, say it is not supported by the source.")
    docs = [
        ("[DOC] Acme's refund window is 30 days. Support hours are 9-5 ET.",
         "What is Acme's annual revenue?", "How long is the refund window? Cite the source."),
        ("[DOC] The API returns 429 on rate limits. Max page size is 100.",
         "What port does the API listen on?", "What is the max page size? Cite it."),
        ("[DOC] Deploys run nightly at 02:00 UTC. Rollback is one command.",
         "Who approves the deploys?", "When do deploys run? Cite the document."),
    ]
    for i, (doc, out_q, in_q) in enumerate(docs):
        add(f"grounding-decline-{i}", "support-chat", "grounding-citation", GC,
            f"{doc}\n\nQuestion: {out_q}", (_declines, "strong"), base=0.35, eff=0.25)
        add(f"grounding-cite-{i}", "support-chat", "grounding-citation", GC,
            f"{doc}\n\nQuestion: {in_q}", _contains("[doc]"), base=0.5, eff=0.2)

    # ---- tool-design: 4 bad schemas needing enum + limit ----
    TD = ("SKILL tool-design: use enums for enumerable params, bound result size with a "
          "limit/page param, and give actionable errors.")
    schemas = [
        '{"name":"search_orders","input_schema":{"properties":{"status":{"type":"string"}}}}',
        '{"name":"list_users","input_schema":{"properties":{"role":{"type":"string"}}}}',
        '{"name":"query_logs","input_schema":{"properties":{"level":{"type":"string"}}}}',
        '{"name":"fetch_items","input_schema":{"properties":{"sort":{"type":"string"}}}}',
    ]
    for i, sc in enumerate(schemas):
        add(f"tool-design-{i}", "tool-using", "tool-design", TD,
            f"Improve this tool definition and output valid JSON only:\n{sc}",
            _valid_tool_schema(), base=0.3, eff=0.22)

    # ---- eval-harness (2) + injection-audit (2): medium-strength keyword checks ----
    EH = "SKILL eval-harness: success criteria must be programmatically checkable, not vibes."
    add("eval-harness-0", "eval", "eval-harness", EH,
        'Rewrite so it is objectively checkable: "the summary should be good."',
        _mentions_any("assert", "==", ">=", "<=", "regex", r"\d+%", "exact", "json.loads"),
        base=0.35, eff=0.2)
    add("eval-harness-1", "eval", "eval-harness", EH,
        'Rewrite as a checkable criterion: "the agent should usually pick the right tool."',
        _mentions_any("rate", r"\d+%", ">=", "precision", "recall", "accuracy", "n="),
        base=0.35, eff=0.2)
    IA = ("SKILL injection-audit: the lethal trifecta is untrusted content + private data + "
          "an exfiltration channel; close it by removing one leg at the vulnerable moment.")
    add("injection-0", "safety", "injection-audit", IA,
        "An agent reads untrusted web pages, can read the user's private files, and has a "
        "send_email tool. Give the concrete fix.",
        _mentions_any("remove.*tool", "drop.*tool", "disable.*(network|egress|send|email)",
                      "gate.*(egress|send|approval)", "no network", "strip.*(tool|capability)",
                      "quarantine"), base=0.4, eff=0.2)
    add("injection-1", "safety", "injection-audit", IA,
        "An agent summarizes untrusted PDFs and can post to a public Slack channel while "
        "holding API keys in context. Give the concrete fix.",
        _mentions_any("remove.*key", "drop.*(post|slack|channel)", "disable.*(post|network)",
                      "gate.*(post|approval)", "no network", "strip", "quarantine",
                      "separate context"), base=0.4, eff=0.2)

    # ---- 4 newest skills + guardrails task registrars ----
    TAR = "SKILL tool-adversarial-reading: review tool schemas for ambiguous types/descriptions and convert to enums/strict formats."
    add("tool-adv-read-0", "tool-using", "tool-adversarial-reading", TAR,
        'Review this schema for ambiguity: {"name":"delete_user","input_schema":{"properties":{"user_id":{"type":"string"}}}}',
        _mentions_any("enum", "format", "uuid", "int", "regex", "pattern", "required", "strict"),
        base=0.35, eff=0.25)
    add("tool-adv-read-1", "tool-using", "tool-adversarial-reading", TAR,
        'Review this schema for ambiguity: {"name":"get_logs","input_schema":{"properties":{"date":{"type":"string"}}}}',
        _mentions_any("iso8601", "format", "yyyy-mm-dd", "enum", "date-time", "timestamp"),
        base=0.35, eff=0.25)

    SFA = "SKILL silent-failure-audit: audit successful runs by cross-referencing user claims against actual tool execution logs."
    add("silent-fail-0", "eval", "silent-failure-audit", SFA,
        'An agent outputs "I updated the database to status=active" but logs show zero API tool calls were executed. Give the fix.',
        _mentions_any("assert", "programmatic", "end-state", "tool_call", "execution log", "check tool", "negative constraint"),
        base=0.35, eff=0.25)
    add("silent-fail-1", "eval", "silent-failure-audit", SFA,
        'An agent outputs "File created successfully" but the file system assertion was never run. How do you prevent metric fraud?',
        _mentions_any("assert", "file_exists", "programmatic", "end state", "truth", "harness check"),
        base=0.35, eff=0.25)

    STG = "SKILL synthetic-task-generation: extrapolate plausible variations from real seed tasks across noise/parameter axes."
    add("synth-task-0", "eval", "synthetic-task-generation", STG,
        'Given real task seed "Find user Alice by ID", generate 3 plausible synthetic variations for an eval suite.',
        _mentions_any("synthetic", "variation", "noise", "typo", "parameter", "axis", "tag"),
        base=0.4, eff=0.22)

    AR = "SKILL accretion-refactor: consolidate bloated system prompts by pruning panic rules and resolving contradictory constraints."
    add("accretion-0", "evolve", "accretion-refactor", AR,
        'Refactor this bloated prompt fragment: "NEVER output markdown. ALWAYS format output as a markdown table."',
        _not_both("never output markdown", "always format output as a markdown table"),
        base=0.35, eff=0.28)

    GR = "SKILL guardrails: isolate dangerous capabilities with pre-execution checks and explicit approval gates."
    add("guardrails-0", "safety", "guardrails", GR,
        'An agent has direct access to `DROP TABLE`. Design the guardrail.',
        _mentions_any("approval", "gate", "confirm", "deny", "permission", "sandbox", "dry-run", "read-only"),
        base=0.4, eff=0.25)

    return T


# --------------------------------------------------------------------------- #
# Registrar self-check fixtures - one should-PASS and one should-FAIL sample
# completion per task, used to sanity-check the registrar itself before it's
# trusted with real API spend.
#
# This exists because of EXP-009 (see EXPERIMENTS.md): an exact-substring
# registrar produced a "context-engineering HURTS, confirmed twice, both
# models" verdict that was itself wrong - the registrar punished correct
# paraphrase as if it were information loss. It replicated cleanly across
# two models and two days, which made it LOOK more credible, not less. A
# registrar bug replicates just as reliably as a real effect does; the only
# way to tell them apart is to check the registrar against a known-good and
# a known-bad completion BEFORE trusting what it says about a real model.
# --------------------------------------------------------------------------- #
FIXTURES: Dict[str, Tuple[str, str]] = {
    # secrets-management: good = indirected via env/vault, no literal secret;
    # bad = the original hardcoded secret, untouched.
    "secrets-py-const": ('API_KEY = os.getenv("API_KEY")\nclient = Client(api_key=API_KEY)',
                          'API_KEY = "sk-ant-8f3a2b1c9d"\nclient = Client(api_key=API_KEY)'),
    "secrets-dict-cfg": ('CONFIG = {"region": "us-east-1", "aws_key": os.getenv("AWS_KEY")}',
                         'CONFIG = {"region": "us-east-1", "aws_key": "AKIA5EXAMPLEKEY42"}'),
    "secrets-url-creds": ('DB = f"postgres://admin:{os.getenv(\'DB_PASSWORD\')}@db.internal:5432/app"',
                          'DB = "postgres://admin:p4ssw0rd-secret@db.internal:5432/app"'),
    "secrets-curl-bear": ('curl https://api.x.com -H "Authorization: Bearer $API_TOKEN"',
                          'curl https://api.x.com -H "Authorization: Bearer sk-live-77zzqp"'),
    "secrets-js-const": ('const token = process.env.GITHUB_TOKEN;\nawait fetch(url, {headers:{Authorization:token}})',
                         'const token = "ghp_examplePAT9911";\nawait fetch(url, {headers:{Authorization:token}})'),
    "secrets-env-fallback": ('api_key = os.getenv("API_KEY")\nif not api_key: raise RuntimeError("API_KEY not set")',
                             'api_key = os.getenv("API_KEY", "sk-prod-REALKEY-88")'),
    "secrets-yaml-secret": ("database:\n  password: ${DB_PASSWORD}",
                            "database:\n  password: svc-acct-KEY-x91"),
    "secrets-header-dict": ('HEADERS = {"Authorization": os.getenv("AUTH_HEADER"), "Accept": "application/json"}',
                            'HEADERS = {"Authorization": "Bearer-tok-ZZ42", "Accept": "application/json"}'),

    # context-engineering: good = compact but factually complete (paraphrase
    # tolerated); bad = wrong number, dropped fact, or (context-2) correct
    # content padded past the cap - exercises the length branch specifically.
    "context-0": ("Rate limit: 4096 tokens/min.", "Everything is fine, no issues to report."),
    "context-1": ("Deploy target: us-east-2.", "Deploy target: us-west-1."),
    "context-2": ("Code freeze starts 2026-03-01.", "Code freeze starts 2026-03-01. " * 12),
    "context-3": ("On-call ticket: OPS-7742.", "On-call ticket: OPS-9999."),
    "context-4": ("Retries capped at 5, exponential backoff.", "Retry policy unspecified."),
    "context-5": ("Webhook secret rotates every 30 days.", "Webhook secret rotates every 90 days."),
    "context-6": ("Production model pinned to v2.4.", "Production model pinned to v3.0."),
    "context-7": ("SLA: 99.9% monthly uptime.", "SLA requirements still being finalized."),

    # prompt-architecture: good = duplicate removed / contradiction resolved
    # / constraint kept; bad = original unfixed prompt (or fact dropped).
    "prompt-dup-0": ("You are a bot. Always respond in valid JSON. Be helpful. End politely.",
                     "You are a bot. Always respond in valid JSON. Be helpful. "
                     "Always respond in valid JSON. End politely."),
    "prompt-dup-1": ("You are a helpful assistant. Cite your sources. Answer clearly.",
                     "You are a helpful assistant. Be helpful. End politely."),
    "prompt-dup-2": ("Respond politely. Keep answers under 100 words.",
                     "Respond politely. Keep answers under 100 words. Keep answers under 100 words."),
    "prompt-contra-0": ("Always respond in JSON.",
                        "Always respond in JSON. Use plain prose throughout."),
    "prompt-contra-1": ("Always include code examples in responses.",
                        "Always include code examples, but use no code blocks."),
    "prompt-preserve-0": ("Be friendly and use examples. Responses must stay under 200 words.",
                          "Be friendly and use examples."),

    # grounding-citation: good = correctly declines (decline tasks) / cites
    # [DOC] (cite tasks); bad = fabricates an answer / omits the citation.
    "grounding-decline-0": ("Acme's annual revenue is not found in the document.",
                            "Acme's annual revenue was $50 million last year."),
    "grounding-decline-1": ("The API port is not found in the document.",
                            "The API listens on port 8443."),
    "grounding-decline-2": ("Who approves deploys is not found in the document.",
                            "Deploys are approved by the platform team lead."),
    "grounding-cite-0": ("The refund window is 30 days [DOC].", "The refund window is 30 days."),
    "grounding-cite-1": ("Max page size is 100 [DOC].", "Max page size is 100."),
    "grounding-cite-2": ("Deploys run nightly at 02:00 UTC [DOC].", "Deploys run nightly at 02:00 UTC."),

    # tool-design: good = enum + limit/page added; bad = original bare schema.
    "tool-design-0": ('{"name":"search_orders","input_schema":{"properties":{'
                      '"status":{"type":"string","enum":["open","closed","pending"]},'
                      '"limit":{"type":"integer"}}}}',
                      '{"name":"search_orders","input_schema":{"properties":{"status":{"type":"string"}}}}'),
    "tool-design-1": ('{"name":"list_users","input_schema":{"properties":{'
                      '"role":{"type":"string","enum":["admin","member"]},'
                      '"page":{"type":"integer"}}}}',
                      '{"name":"list_users","input_schema":{"properties":{"role":{"type":"string"}}}}'),
    "tool-design-2": ('{"name":"query_logs","input_schema":{"properties":{'
                      '"level":{"type":"string","enum":["info","warn","error"]},'
                      '"limit":{"type":"integer"}}}}',
                      '{"name":"query_logs","input_schema":{"properties":{"level":{"type":"string"}}}}'),
    "tool-design-3": ('{"name":"fetch_items","input_schema":{"properties":{'
                      '"sort":{"type":"string","enum":["asc","desc"]},'
                      '"max_results":{"type":"integer"}}}}',
                      '{"name":"fetch_items","input_schema":{"properties":{"sort":{"type":"string"}}}}'),

    # eval-harness: good = a real programmatic criterion; bad = vibes, unchanged.
    "eval-harness-0": ("assert summary_length <= 200 and rouge_score >= 0.8",
                       "the summary should be good and comprehensive"),
    "eval-harness-1": ("tool selection accuracy >= 90% (n=50 held-out tasks)",
                       "the agent should usually pick the right tool"),

    # injection-audit: good = names a concrete mechanism that breaks a leg of
    # the trifecta; bad = a vague "be careful" non-fix.
    "injection-0": ("Disable the send_email tool while processing untrusted web content; "
                    "re-enable only after human approval.",
                    "Just tell the agent to be careful and not send sensitive data."),
    "injection-1": ("Strip API keys from context before summarizing untrusted PDFs; "
                    "gate posting to Slack behind human approval.",
                    "Add a warning in the system prompt not to leak keys."),

    # tool-adversarial-reading: good = names the ambiguity fix; bad = declares no issue.
    "tool-adv-read-0": ("user_id should be type string with format uuid and marked required.",
                        "Looks fine as-is, no changes needed."),
    "tool-adv-read-1": ("date should specify format: date-time (ISO8601), e.g. YYYY-MM-DD.",
                        "date is a string, that's fine."),

    # silent-failure-audit: good = a programmatic ground-truth check; bad =
    # trusting the agent's own claim (exactly the failure mode being audited).
    "silent-fail-0": ("Add a programmatic assertion that checks the execution log for an "
                      "actual tool_call before accepting the claimed end-state.",
                      "Trust the agent's own summary of what it did."),
    "silent-fail-1": ("Add a harness check: assert file_exists(path) as the programmatic "
                      "ground truth, not the agent's claim.",
                      "If the agent says the file was created, that's good enough."),

    # synthetic-task-generation: good = real variation axes; bad = relabeled
    # clones with no actual variation.
    "synth-task-0": ("Generate synthetic variations along the id-parameter axis: typo'd "
                     "name, numeric ID instead of name, added noise like extra whitespace.",
                     "Find user Alice by ID, find user Bob by ID, find user Carol by ID."),

    # accretion-refactor: good = contradiction resolved to one rule; bad = unchanged original.
    "accretion-0": ("Always format output as a markdown table.",
                    "NEVER output markdown. ALWAYS format output as a markdown table."),

    # guardrails: good = a concrete approval/sandbox mechanism; bad = a vague caution.
    "guardrails-0": ("Require explicit human approval before executing any DROP TABLE "
                     "statement; default to read-only/dry-run.",
                     "Just be careful with DROP TABLE and don't make mistakes."),
}


def selfcheck(tasks: List[Task]) -> List[str]:
    """Check each task's registrar against its own positive/negative fixture.
    Returns human-readable failure messages; empty means every registrar with
    a fixture on file correctly passes the good sample and rejects the bad
    one. Tasks with no fixture registered are silently skipped here (the CLI
    reports fixture coverage separately)."""
    problems = []
    for t in tasks:
        fx = FIXTURES.get(t.tid)
        if fx is None:
            continue
        good, bad = fx
        if not t.registrar(good):
            problems.append(f"{t.tid}: registrar rejects its own POSITIVE fixture "
                             f"(should PASS, got FAIL) -> {good!r}")
        if t.registrar(bad):
            problems.append(f"{t.tid}: registrar accepts its own NEGATIVE fixture "
                             f"(should FAIL, got PASS) -> {bad!r}")
    return problems
