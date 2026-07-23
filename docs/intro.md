# Agent Skills — Documentation Index

This library is a closed-loop system for agentic software engineering. Agent engineering knowledge today is often *folklore* — prompt tricks and topology tips that live in people's heads and spread by imitation. This library captures production-grade agent practice as **checkable skills**, makes them **fire at the right moment on their own**, and lets them **improve and get validated across a community**.

The system operates across a set of interconnected mechanisms. The documentation is split into the following core parts to explain each component in depth:

### 1. [The Skills Catalog](skills_doc.md)
The **"What"**. A thin, generated index of the 59 procedural markdown files that guide the agent's behavior — each skill self-documents in its own `SKILL.md` (the single source of truth). These turn tribal knowledge and best practices into executable instructions.

### 2. [Skill Routing](routing_doc.md)
The **"When"**. How the library becomes self-driving. Explains the always-loaded router table that maps observable user behaviors to specific skills, using autonomy tiers to keep you in control without needing to memorize commands.

### 3. [Evaluation Mechanism](evals_doc.md)
The **"Gate"**. How skills and proposed changes are actually evaluated. Details the in-flight adversarial checks and post-hoc outcome-based test suites that answer the question, *"Did this actually make the agent better?"*

### 4. [Evolution Mechanism](evolve_doc.md)
The **"Learning Loop"**. How the system prevents skills from getting stale. Explains the automated process that sweeps logs for failures, drafts fixes, tests them against the eval harness, and monitors them in a live canary.

### 5. [Culture Telemetry](telemetry_doc.md)
The **"Commons"**. How local telemetry and routing logs are aggregated and contributed to a public repository to build a shared, validated culture — ensuring full privacy and data boundaries.
