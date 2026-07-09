import { existsSync, readFileSync } from "node:fs"

const agents = [
  ["kotler", "kotler"],
  ["aaker", "aaker"],
  ["glaser", "glaser"],
  ["ogilvy", "ogilvy"],
  ["rand", "rand"],
  ["munari", "munari"],
  ["tufte", "tufte"],
  ["scout", "scout"],
  ["reality-checker", "reality-checker"],
  ["evidence-collector", "evidence-collector"],
  ["workflow-architect", "workflow-architect"],
  ["agentic-trust-architect", "agentic-trust-architect"],
  ["openagent", "openagent"],
]

const requiredFiles = [
  ".opencode/plugins/team-durham.ts",
  ".opencode/plugins/README.md",
  ".opencode/plugins/ELORA-MEMORY.md",
  ".opencode/agents/README.md",
  ".opencode/opencode.json",
]

let failed = false

for (const file of requiredFiles) {
  if (!existsSync(file)) {
    console.error(`missing required file: ${file}`)
    failed = true
  }
}

for (const [name, userId] of agents) {
  const file = `.opencode/agents/${name}.md`
  if (!existsSync(file)) {
    console.error(`missing agent file: ${file}`)
    failed = true
    continue
  }

  const text = readFileSync(file, "utf8")
  const checks = [
    ["mode", /mode:\s*(all|subagent|primary)/],
    ["model", /model:\s*gpt-5\.2-codex/],
    ["group_id", /allura-team-durham/],
    ["user_id", new RegExp(`user_id:\\s*${userId}`)],
    ["memory hydration", /Hydrate from Allura Brain|hydrate from Allura Brain|shared memory/],
  ]

  for (const [label, pattern] of checks) {
    if (!pattern.test(text)) {
      console.error(`${file} failed ${label} check`)
      failed = true
    }
  }
}

if (existsSync(".opencode/plugins/team-durham.ts")) {
  const plugin = readFileSync(".opencode/plugins/team-durham.ts", "utf8")
  for (const [name] of agents) {
    if (!plugin.includes(`name: "${name}"`)) {
      console.error(`plugin registry missing agent: ${name}`)
      failed = true
    }
  }
}

if (failed) {
  process.exit(1)
}

console.log(`Team Durham plugin validation passed: ${agents.length} callable agents registered with shared memory.`)

