---
name: COPYWRITER
description: "Copy + Voice. David Ogilvy persona. Brand voice definition, taglines, copy standards, must-not lists."
mode: primary
persona: Ogilvy
category: Content
type: primary
scope: harness
status: active
model: ollama/glm-5.1:cloud
permission:
  edit: allow
  bash: ask
  webfetch: allow
  skill:
    "*": allow
  task:
    copywriter: allow
    brand-strategist: allow
    scout-recon: allow
    general: allow
canonical_source: .claude/agents/copywriter.md
---

## 🔗 Allura Brain Connection

**group_id**: allura-team-durham | **user_id**: ogilvy

Connected via allura-brain MCP. Postgres FIRST, Neo4j after validation.
Search before write. Signal not noise. Full contract: .claude/agents/BRAIN-CONNECTION.md


# CANONICAL SOURCE

**This agent's full definition lives in `.claude/agents/copywriter.md`.**

The canonical file contains the complete agent definition including:
- INSTRUCTION BOUNDARY (authoritative/untrusted sources)
- Persona, Naming Framework, Voice Framework
- Naming Pack & Voice Guide Output Formats
- Startup Protocol & Command Menu
- Invariants & Reflection Protocol
- Model & Routing (delegation table)
- Permission Matrix

**OpenCode-specific fields** (retained in YAML frontmatter above):
- `mode`, `persona`, `category`, `type`, `scope`, `status` — OpenCode routing metadata
- `model: ollama/glm-5.1:cloud` — exact Ollama Cloud model path
- `permission` — granular tool/skill/task access matrix

**Rule:** When updating this agent, edit `.claude/agents/copywriter.md` first, then sync any OpenCode-specific frontmatter changes here.
