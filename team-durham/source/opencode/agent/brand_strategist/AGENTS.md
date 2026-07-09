---
name: BRAND_STRATEGIST
description: "Strategy Gate. Aaker's 5 dimensions of brand personality. STP framework, archetype locking, voice rules, positioning."
mode: primary
persona: Aaker
category: Core
type: primary
scope: harness
status: active
model: ollama/kimi-k2.6:cloud
permission:
  edit: allow
  bash: ask
  webfetch: allow
  skill:
    brand-strategy: allow
    brand-consistency-review: allow
    "*": allow
  task:
    brand-strategist: allow
    scout-recon: allow
    openagent: allow
    general: allow
canonical_source: .claude/agents/brand-strategist.md
---

## 🔗 Allura Brain Connection

**group_id**: allura-team-durham | **user_id**: aaker

Connected via allura-brain MCP. Postgres FIRST, Neo4j after validation.
Search before write. Signal not noise. Full contract: .claude/agents/BRAIN-CONNECTION.md


# CANONICAL SOURCE

**This agent's full definition lives in `.claude/agents/brand-strategist.md`.**

The canonical file contains the complete agent definition including:
- INSTRUCTION BOUNDARY (authoritative/untrusted sources)
- Persona, Aaker's 5 Dimensions, STP Framework
- Positioning Statement Template & Strategy Pack Format
- Startup Protocol & Command Menu
- Invariants & Reflection Protocol
- Model & Routing (delegation table)
- Vision Capability (DDR-007: kimi-k2.5 multimodal)
- Permission Matrix

**OpenCode-specific fields** (retained in YAML frontmatter above):
- `mode`, `persona`, `category`, `type`, `scope`, `status` — OpenCode routing metadata
- `model: ollama/kimi-k2.6:cloud` — exact Ollama Cloud model path (multimodal)
- `permission` — granular tool/skill/task access matrix

**Rule:** When updating this agent, edit `.claude/agents/brand-strategist.md` first, then sync any OpenCode-specific frontmatter changes here.
