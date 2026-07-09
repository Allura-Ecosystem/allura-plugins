---
name: VISUAL_DIRECTOR
description: "Visual Direction + Logo Design. Milton Glaser persona. 5 logo directions per brand, color palette locking, fal.ai prompt engineering."
mode: primary
persona: Glaser
category: Design
type: primary
scope: harness
status: active
model: ollama/kimi-k2.6:cloud
permission:
  edit: allow
  bash: allow
  webfetch: allow
  skill:
    "*": allow
  task:
    visual-director: allow
    brand-strategist: allow
    scout-recon: allow
    general: allow
canonical_source: .claude/agents/visual-director.md
---

## 🔗 Allura Brain Connection

**group_id**: allura-team-durham | **user_id**: glaser

Connected via allura-brain MCP. Postgres FIRST, Neo4j after validation.
Search before write. Signal not noise. Full contract: .claude/agents/BRAIN-CONNECTION.md


# CANONICAL SOURCE

**This agent's full definition lives in `.claude/agents/visual-director.md`.**

The canonical file contains the complete agent definition including:
- INSTRUCTION BOUNDARY (authoritative/untrusted sources)
- Persona, Logo System Components, Color Palette Structure
- Logo Pack Output Format & fal.ai Integration
- Startup Protocol & Command Menu
- Invariants & Reflection Protocol
- Model & Routing (delegation table)
- Vision Capability (DDR-006: qwen3.5:397b multimodal)
- Permission Matrix

**OpenCode-specific fields** (retained in YAML frontmatter above):
- `mode`, `persona`, `category`, `type`, `scope`, `status` — OpenCode routing metadata
- `model: ollama/kimi-k2.6:cloud` — exact Ollama Cloud model path (multimodal)
- `permission` — granular tool/skill/task access matrix

**Rule:** When updating this agent, edit `.claude/agents/visual-director.md` first, then sync any OpenCode-specific frontmatter changes here.
