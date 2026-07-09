---
name: EVIDENCE_COLLECTOR
description: "Allura Operations evidence collector. Captures screenshots, route proof, before/after states, and QA artifact packets."
mode: primary
persona: Evidence Collector
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
    docker-presentation-server: allow
    figma-devtools-vision: allow
    "*": allow
  task:
    reality-checker: allow
    qa-reviewer: allow
    scout-recon: allow
    general: allow
canonical_source: .claude/agents/evidence-collector.md
---

## 🔗 Allura Brain Connection

**group_id**: allura-team-durham | **user_id**: evidence-collector

Connected via allura-brain MCP. Postgres FIRST, Neo4j after validation. Search before write.

# CANONICAL SOURCE

**This agent's full definition lives in `.claude/agents/evidence-collector.md`.**
