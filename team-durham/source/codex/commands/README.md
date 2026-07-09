# Codex Command Bridge

Canonical command runbooks live in:

```text
../.claude/commands/
```

Codex should treat these as the command source for Team Durham:

- `/orchestrate` → `../.claude/commands/orchestrate.md`
- `/status` → `../.claude/commands/status.md`
- `/validate` → `../.claude/commands/validate.md`
- `/scout` → `../.claude/commands/scout.md`
- `/task` → `../.claude/commands/task.md`
- `/dashboard` → `../.claude/commands/dashboard.md`
- `/start-session` → `../.claude/commands/start-session.md`
- `/end-session` → `../.claude/commands/end-session.md`

OpenCode compatibility shims remain in `../.opencode/command/` and `../.opencode/commands/`.

