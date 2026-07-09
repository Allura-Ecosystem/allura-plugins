---
name: SCOUT_RECON
description: "Fast Discovery (read-only). Recon + discovery agent. Searches codebase, Notion, web. Never writes — only reports."
mode: subagent
persona: none
category: Utility
type: subagent
scope: harness
status: active
model: ollama/kimi-k2.6:cloud
permission:
  edit: deny
  bash: allow
  webfetch: allow
  skill:
    "*": allow
  task:
    scout-recon: allow
    general: allow
canonical_source: .claude/agents/scout-recon.md
---

## 🔗 Allura Brain Connection

**group_id**: allura-team-durham | **user_id**: scout-recon

Connected via allura-brain MCP. Postgres FIRST, Neo4j after validation.
Search before write. Signal not noise. Full contract: .claude/agents/BRAIN-CONNECTION.md


# CANONICAL SOURCE

**This agent's full definition lives in `.claude/agents/scout-recon.md`.**

The canonical file contains the complete agent definition including:
- INSTRUCTION BOUNDARY (authoritative/untrusted sources — all content is untrusted by default)
- Identity, Core Responsibilities, Capabilities
- Scout Report Output Format
- Startup Protocol & Command Menu
- Invariants (READ-ONLY, NEVER decides) & Reflection Protocol
- Model & Routing (terminal subagent — no further delegation)
- Vision Capability (DDR-006: kimi-k2.5 multimodal)
- Tool Restrictions & Permission Matrix

**OpenCode-specific fields** (retained in YAML frontmatter above):
- `mode: subagent`, `persona: none`, `type: subagent` — OpenCode routing metadata
- `model: ollama/kimi-k2.6:cloud` — exact Ollama Cloud model path (multimodal)
- `permission` — granular tool/skill/task access matrix (edit: deny — read-only)

**Rule:** When updating this agent, edit `.claude/agents/scout-recon.md` first, then sync any OpenCode-specific frontmatter changes here.
