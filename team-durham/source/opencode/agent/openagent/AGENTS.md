---
name: OPENAGENT
description: "Universal agent — flexible, adaptable, any domain. Delegates to specialists, maintains oversight."
mode: primary
persona: none
category: Core
type: primary
scope: universal
status: active
model: ollama/kimi-k2.6:cloud
permission:
  edit: allow
  bash: allow
  webfetch: allow
  skill:
    "*": allow
  task:
    "*": allow
canonical_source: .claude/agents/openagent.md
---

## 🔗 Allura Brain Connection

**group_id**: allura-team-durham | **user_id**: openagent

Connected via allura-brain MCP. Postgres FIRST, Neo4j after validation.
Search before write. Signal not noise. Full contract: .claude/agents/BRAIN-CONNECTION.md


# CANONICAL SOURCE

**This agent's full definition lives in `.claude/agents/openagent.md`.**

The canonical file contains the complete agent definition including:
- INSTRUCTION BOUNDARY (authoritative/untrusted sources)
- Identity, Behavior, Startup Protocol
- Command Menu & Invariants
- Model & Routing (full Team Durham delegation table)
- Permission Matrix

**OpenCode-specific fields** (retained in YAML frontmatter above):
- `mode`, `persona`, `category`, `type`, `scope`, `status` — OpenCode routing metadata
- `model: ollama/kimi-k2.6:cloud` — exact Ollama Cloud model path
- `permission` — granular tool/skill/task access matrix

**Rule:** When updating this agent, edit `.claude/agents/openagent.md` first, then sync any OpenCode-specific frontmatter changes here.
