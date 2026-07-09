---
name: WORKFLOW_ARCHITECT
description: "Allura Operations workflow architect. Maps workflow trees, state machines, failure modes, recovery paths, and handoff contracts."
mode: primary
persona: Workflow Architect
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
    task-management: allow
    mcp-validation-gate: allow
    "*": allow
  task:
    reality-checker: allow
    agentic-trust-architect: allow
    scout-recon: allow
    general: allow
canonical_source: .claude/agents/workflow-architect.md
---

## 🔗 Allura Brain Connection

**group_id**: allura-team-durham | **user_id**: workflow-architect

Connected via allura-brain MCP. Postgres FIRST, Neo4j after validation. Search before write.

# CANONICAL SOURCE

**This agent's full definition lives in `.claude/agents/workflow-architect.md`.**
