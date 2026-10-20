# Packages for other runtimes

These generated packages use their target runtime's distribution format. They are listed here so you can find the right installation instructions; they are not Claude or Codex marketplace plugins.

| Package | Use it for | Runtime and instructions |
|---|---|---|
| [Mortagate Cowork](mortagate-cowork/README.md) | Mortgage-file evidence review | Microsoft Cowork / Microsoft 365 Agent Skills |

## Source and release contract

[Mortagate](https://github.com/Allura-Ecosystem/mortagate) owns the source. The catalog exports the exact 23-file allowlist, plus generated provenance and per-file SHA-256 evidence. Full source commits and contracts are recorded in [`source-locks.json`](../source-locks.json).

Make content changes in the source repository, then update the pin and regenerate. Manual edits inside these generated package directories will be replaced and fail drift checks.
