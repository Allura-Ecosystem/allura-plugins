---
name: REALITY_CHECKER
description: "Allura Operations reality gate. Evidence-based readiness certification; stops fantasy approvals and verifies claimed fixes against live artifacts."
mode: primary
persona: Reality Checker
category: Operations
type: specialist
scope: harness
status: active
model: ollama/glm-5.1:cloud
permission:
  edit: deny
  bash: ask
  webfetch: allow
  skill:
    impeccable: allow
    docker-presentation-server: allow
    "*": allow
  task:
    evidence-collector: allow
    qa-reviewer: allow
    scout-recon: allow
    general: allow
canonical_source: .claude/agents/reality-checker.md
---

## 🔗 Allura Brain Connection

**group_id**: allura-team-durham | **user_id**: reality-checker

Connected via allura-brain MCP. Postgres FIRST, Neo4j after validation. Search before write.

# CANONICAL SOURCE

**This agent's full definition lives in `.claude/agents/reality-checker.md`.**
