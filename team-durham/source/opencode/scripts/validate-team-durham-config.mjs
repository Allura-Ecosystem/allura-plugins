import { existsSync, readFileSync } from "node:fs"

let failed = false

const required = [
  ".opencode/plugins/team-durham.ts",
  ".opencode/plugins/ELORA-MEMORY.md",
  ".opencode/skills/team-durham-agent-router/SKILL.md",
  ".opencode/opencode.json",
]

for (const file of required) {
  if (!existsSync(file)) {
    console.error(`missing required file: ${file}`)
    failed = true
  }
}

if (existsSync(".opencode/opencode.json")) {
  const config = readFileSync(".opencode/opencode.json", "utf8")
  const expectedSkillPaths = [
    "/home/ronin704/Projects/design/brand-maker/.opencode/skills",
    "/home/ronin704/Projects/design/brand-maker/.claude/skills",
    "/home/ronin704/Projects/design/brand-maker/.agents/skills",
  ]

  for (const expected of expectedSkillPaths) {
    if (!config.includes(expected)) {
      console.error(`opencode config missing skill path: ${expected}`)
      failed = true
    }
  }

  if (config.includes("/home/ronin704/Projects/Brand maker/.claude/skills")) {
    console.error("opencode config still contains stale Brand maker .claude skill path")
    failed = true
  }
}

if (existsSync(".opencode/skills/team-durham-agent-router/SKILL.md")) {
  const router = readFileSync(".opencode/skills/team-durham-agent-router/SKILL.md", "utf8")
  for (const word of ["Elora", "allura-team-durham", ".opencode/agents", ".opencode/plugins/team-durham.ts"]) {
    if (!router.includes(word)) {
      console.error(`team-durham-agent-router missing ${word}`)
      failed = true
    }
  }
}

if (existsSync(".opencode/plugins/ELORA-MEMORY.md")) {
  const memory = readFileSync(".opencode/plugins/ELORA-MEMORY.md", "utf8")
  for (const word of ["allura-team-durham", "allura-brain_memory_search", "mcp__allura_brain__memory_search"]) {
    if (!memory.includes(word)) {
      console.error(`ELORA-MEMORY.md missing ${word}`)
      failed = true
    }
  }
}

if (failed) {
  process.exit(1)
}

console.log("Team Durham config validation passed: router, Elora memory, and OpenCode skill paths are wired.")

