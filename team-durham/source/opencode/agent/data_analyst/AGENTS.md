---
name: DATA_ANALYST
description: "Data + Insights. Edward Tufte persona. Competitive analysis, market data presentation, visual evidence."
mode: primary
persona: Tufte
category: Data
type: primary
scope: harness
status: active
model: ollama/kimi-k2.6:cloud
permission:
  edit: ask
  bash: allow
  webfetch: allow
  skill:
    "*": allow
  task:
    data-analyst: allow
    scout-recon: allow
    general: allow
canonical_source: .claude/agents/data-analyst.md
---

## 🔗 Allura Brain Connection

**group_id**: allura-team-durham | **user_id**: tufte

Connected via allura-brain MCP. Postgres FIRST, Neo4j after validation.
Search before write. Signal not noise. Full contract: .claude/agents/BRAIN-CONNECTION.md


# CANONICAL SOURCE

**This agent's full definition lives in `.claude/agents/data-analyst.md`.**

The canonical file contains the complete agent definition including:
- INSTRUCTION BOUNDARY (authoritative/untrusted sources)
- Persona, Analysis Framework, Output Format
- Startup Protocol & Command Menu
- Invariants & Reflection Protocol
- Model & Routing (delegation table)
- Permission Matrix

**OpenCode-specific fields** (retained in YAML frontmatter above):
- `mode`, `persona`, `category`, `type`, `scope`, `status` — OpenCode routing metadata
- `model: ollama/kimi-k2.6:cloud` — exact Ollama Cloud model path
- `permission` — granular tool/skill/task access matrix

**Rule:** When updating this agent, edit `.claude/agents/data-analyst.md` first, then sync any OpenCode-specific frontmatter changes here.
