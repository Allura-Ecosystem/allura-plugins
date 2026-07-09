# Team Durham Callable Agents

These files expose Team Durham as project-callable OpenCode agents.

Legacy wrappers live in `.opencode/agent/*/AGENTS.md`.
Canonical definitions live in `.claude/agents/*.md`.

## Agent Map

| Callable name | Canonical Team Durham role |
|---------------|----------------------------|
| `kotler` | Brand Orchestrator |
| `aaker` | Brand Strategist |
| `glaser` | Visual Director |
| `ogilvy` | Copywriter |
| `rand` | Brand Kit Builder |
| `munari` | QA Reviewer |
| `tufte` | Data Analyst |
| `scout` | Read-only Recon |
| `reality-checker` | Evidence-based Readiness |
| `evidence-collector` | Proof Packets |
| `workflow-architect` | Handoffs and State Machines |
| `agentic-trust-architect` | Permissions and Audit |
| `openagent` | Fallback Router |

Every agent shim:

- Loads its `.opencode/agent/*/AGENTS.md` wrapper.
- Points back to its `.claude/agents/*.md` canonical definition.
- Hydrates from Allura Brain/shared memory with `group_id: allura-team-durham`.
- Uses the agent-specific `user_id`.

