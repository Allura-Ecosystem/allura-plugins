---
name: BRAND_KIT_BUILDER
description: "Brand Kit Assembly. Paul Rand persona. 10-section master guidelines from all prior phases. The canonical brand document."
mode: primary
persona: Rand
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
    brand-kit-builder: allow
    brand-strategist: allow
    visual-director: allow
    qa-reviewer: allow
    scout-recon: allow
    general: allow
canonical_source: .claude/agents/brand-kit-builder.md
---

## 🔗 Allura Brain Connection

**group_id**: allura-team-durham | **user_id**: rand

Connected via allura-brain MCP. Postgres FIRST, Neo4j after validation.
Search before write. Signal not noise. Full contract: .claude/agents/BRAIN-CONNECTION.md


# CANONICAL SOURCE

**This agent's full definition lives in `.claude/agents/brand-kit-builder.md`.**

The canonical file contains the complete agent definition including:
- INSTRUCTION BOUNDARY (authoritative/untrusted sources)
- Persona, The 10 Sections, Section Content & Validation Rules
- Brand Kit Output Format
- Startup Protocol & Command Menu
- Invariants & Reflection Protocol
- Model & Routing (delegation table)
- Vision Capability (DDR-006: gemma4:31b multimodal)
- Permission Matrix

**OpenCode-specific fields** (retained in YAML frontmatter above):
- `mode`, `persona`, `category`, `type`, `scope`, `status` — OpenCode routing metadata
- `model: ollama/kimi-k2.6:cloud` — exact Ollama Cloud model path (multimodal)
- `permission` — granular tool/skill/task access matrix

**Rule:** When updating this agent, edit `.claude/agents/brand-kit-builder.md` first, then sync any OpenCode-specific frontmatter changes here.
