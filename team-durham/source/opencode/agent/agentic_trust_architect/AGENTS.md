---
name: AGENTIC_TRUST_ARCHITECT
description: "Allura Operations trust architect. Designs agent identity, scopes, delegation chains, memory write authorization, and tamper-evident audit trails."
mode: primary
persona: Agentic Trust Architect
category: Operations
type: specialist
scope: harness
status: active
model: ollama/glm-5.1:cloud
permission:
  edit: allow
  bash: ask
  webfetch: allow
  skill:
    allura-memory-skill: allow
    mcp-docker-memory: allow
    mcp-validation-gate: allow
    "*": allow
  task:
    workflow-architect: allow
    reality-checker: allow
    scout-recon: allow
    general: allow
canonical_source: .claude/agents/agentic-trust-architect.md
---

## 🔗 Allura Brain Connection

**group_id**: allura-team-durham | **user_id**: agentic-trust-architect

Connected via allura-brain MCP. Postgres FIRST, Neo4j after validation. Search before write.

# CANONICAL SOURCE

**This agent's full definition lives in `.claude/agents/agentic-trust-architect.md`.**
