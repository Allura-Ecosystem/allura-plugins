---
description: "Quick slash commands for Allura Memory surgical team"
allowed-tools: ["Read", "Grep", "Bash", "mcp__MCP_DOCKER__*"]
---

# Quick Slash Commands

Type these directly in your IDE for fast access to Allura Memory workflows.

## Session Commands

| Command          | Action        | Equivalent      |
| ---------------- | ------------- | --------------- |
| `/start`         | Start session | `start-session` |
| `/end <summary>` | End session   | `end-session`   |
| `/dash`          | Dashboard     | `dashboard`     |

## Task Commands

| Command        | Action         | Equivalent             |
| -------------- | -------------- | ---------------------- |
| `/task <desc>` | Create task    | `task-management`     |
| `/promote`     | HITL promotion | `hitl-governance`     |
| `/review`      | Code review    | `code-review`          |

## Memory Commands

| Command            | Action       | Equivalent                         |
| ------------------ | ------------ | ---------------------------------- |
| `/query <term>`    | Memory query | `mcp__MCP_DOCKER__search_memories` |
| `/update <target>` | Memory sync | `memory-client`                   |
| `/party <task>`    | Party mode   | `party-mode`                       |

## Skill Commands

| Command                      | Action              | Equivalent             |
| ---------------------------- | ------------------- | ---------------------- |
| `/create <name>`             | Create new skill    | `skill-create`         |
| `/create <name> --improve`   | Improve skill       | `skill-create --improve` |
| `/create <name> --eval`      | Eval skill          | `skill-create --eval`  |
| `/create <name> --optimize`  | Optimize triggering | `skill-create --optimize` |
| `/propose <skill>`           | Propose skill route | `skill-propose`        |
| `/load <skill>`              | Load & execute      | `skill-load`           |

## Agent Shortcuts

| Shortcut                 | Agent  | Persona         |
| ------------------------ | ------ | --------------- |
| `@brooks-architect`      | Brooks | Frederick Brooks |
| `@jobs-intent-gate`      | Jobs   | Steve Jobs       |
| `@woz-builder`           | Woz    | Steve Wozniak    |
| `@scout-recon`           | Scout  | Utility / Recon  |
| `@pike-interface-review` | Pike   | Rob Pike         |
| `@fowler-refactor-gate`  | Fowler | Martin Fowler    |

## Usage Examples

### Start a Session

```bash
/start
```

Loads memory, verifies infrastructure, prepares tools.

### Create a Task

```bash
/task Add OAuth2 authentication with Google provider
```

Generates structured task file with memory links.

### Launch Party Mode

```bash
/party Implement user dashboard with charts
```

Spawns all agents in parallel for maximum throughput.

### Quick Update

```bash
/update progress Added OAuth2 authentication
```

Updates Allura Brain and logs to events.

### Query Memory

```bash
/query authentication patterns
```

Searches Allura Brain for relevant insights.

### Code Review

```bash
/review
```

Launches Pike, Scout, and Brooks-aligned review checks.

---

**All commands work with Allura Brain integration.**
