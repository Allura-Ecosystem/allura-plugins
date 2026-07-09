# Dogfood Receipts

Dogfood work must use real receipts. Do not mark a run as executed unless it
actually happened.

## Initial Local Dogfood

Date: 2026-06-02

Scope:

- Build the Allura Cowork plugin package.
- Install it into local Codex and Claude plugin paths.
- Commit a GitHub-tracked copy under `plugins/allura-cowork/`.
- Push a clean plugin-only branch.

Receipts:

- Local validators passed for `~/plugins/allura-cowork`.
- Local validators passed for `~/.claude/plugins/allura-cowork`.
- Repo validator passed for `plugins/allura-cowork`.
- Hook smoke test returned the Allura Cowork reminder.
- Plugin-only branch pushed: `allura-cowork-plugin`.

Known limits:

- This dogfood did not run a live Claude-to-Codex task loop.
- This dogfood did not test marketplace UI rendering.
- Allura Brain writeback was unavailable during the GitHub publish receipt, so
  the local Troy daily note was used as fallback.
