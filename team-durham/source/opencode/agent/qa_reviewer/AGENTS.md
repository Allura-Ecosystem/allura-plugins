---
name: QA_REVIEWER
description: "Quality Assurance + Design Review. Bruno Munari persona. Validates brand consistency, accessibility, production readiness."
mode: primary
persona: Munari
category: Design
type: primary
scope: harness
status: active
model: ollama/glm-5.1:cloud
permission:
  edit: allow
  bash: ask
  webfetch: allow
  skill:
    brand-consistency-review: allow
    "*": allow
  task:
    qa-reviewer: allow
    scout-recon: allow
    general: allow
canonical_source: .claude/agents/qa-reviewer.md
---

## 🔗 Allura Brain Connection

**group_id**: allura-team-durham | **user_id**: munari

Connected via allura-brain MCP. Postgres FIRST, Neo4j after validation.
Search before write. Signal not noise. Full contract: .claude/agents/BRAIN-CONNECTION.md


# CANONICAL SOURCE

**This agent's full definition lives in `.claude/agents/qa-reviewer.md`.**

The canonical file contains the complete agent definition including:
- INSTRUCTION BOUNDARY (authoritative/untrusted sources)
- Persona, QA Checklist (60 Items), Scoring Rules
- QA Report Output Format
- Startup Protocol & Command Menu
- Invariants (QA is READ-ONLY) & Reflection Protocol
- Model & Routing (delegation table)
- Vision Capability (DDR-006: qwen3.5:397b multimodal)
- Tool Restrictions & Permission Matrix

**OpenCode-specific fields** (retained in YAML frontmatter above):
- `mode`, `persona`, `category`, `type`, `scope`, `status` — OpenCode routing metadata
- `model: ollama/glm-5.1:cloud` — exact Ollama Cloud model path (multimodal)
- `permission` — granular tool/skill/task access matrix

**Rule:** When updating this agent, edit `.claude/agents/qa-reviewer.md` first, then sync any OpenCode-specific frontmatter changes here.
