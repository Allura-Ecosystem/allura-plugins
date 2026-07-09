type TeamDurhamAgent = {
  name: string
  persona: string
  role: string
  agentFile: string
  canonicalFile: string
  userId: string
  memoryQueries: string[]
}

export const TEAM_DURHAM_AGENTS: TeamDurhamAgent[] = [
  {
    name: "kotler",
    persona: "Philip Kotler",
    role: "Brand Orchestrator",
    agentFile: ".opencode/agents/kotler.md",
    canonicalFile: ".claude/agents/brand-orchestrator.md",
    userId: "kotler",
    memoryQueries: ["active clients blockers brand decisions", "recent outcomes lessons patterns"],
  },
  {
    name: "aaker",
    persona: "Jennifer Aaker",
    role: "Brand Strategist",
    agentFile: ".opencode/agents/aaker.md",
    canonicalFile: ".claude/agents/brand-strategist.md",
    userId: "aaker",
    memoryQueries: ["locked strategy brand truth positioning", "strategy decisions client personality voice"],
  },
  {
    name: "glaser",
    persona: "Milton Glaser",
    role: "Visual Director",
    agentFile: ".opencode/agents/glaser.md",
    canonicalFile: ".claude/agents/visual-director.md",
    userId: "glaser",
    memoryQueries: ["visual direction logo directions approved imagery", "fal.ai runs penpot visual decisions"],
  },
  {
    name: "ogilvy",
    persona: "David Ogilvy",
    role: "Copywriter",
    agentFile: ".opencode/agents/ogilvy.md",
    canonicalFile: ".claude/agents/copywriter.md",
    userId: "ogilvy",
    memoryQueries: ["copy decisions voice rules naming pack", "audience research messaging taglines"],
  },
  {
    name: "rand",
    persona: "Paul Rand",
    role: "Brand Kit Builder",
    agentFile: ".opencode/agents/rand.md",
    canonicalFile: ".claude/agents/brand-kit-builder.md",
    userId: "rand",
    memoryQueries: ["brand kit design tokens logo usage", "production specs visual system"],
  },
  {
    name: "munari",
    persona: "Bruno Munari",
    role: "QA Reviewer",
    agentFile: ".opencode/agents/munari.md",
    canonicalFile: ".claude/agents/qa-reviewer.md",
    userId: "munari",
    memoryQueries: ["qa reports known drift open issues", "brand consistency accessibility evidence"],
  },
  {
    name: "tufte",
    persona: "Edward Tufte",
    role: "Data Analyst",
    agentFile: ".opencode/agents/tufte.md",
    canonicalFile: ".claude/agents/data-analyst.md",
    userId: "tufte",
    memoryQueries: ["competitive intelligence market research evidence", "validated claims category analysis"],
  },
  {
    name: "scout",
    persona: "Scout",
    role: "Read-only Recon",
    agentFile: ".opencode/agents/scout.md",
    canonicalFile: ".claude/agents/scout-recon.md",
    userId: "scout",
    memoryQueries: ["active tasks files decisions", "recent blockers source locations"],
  },
  {
    name: "reality-checker",
    persona: "Reality Checker",
    role: "Evidence-based Readiness",
    agentFile: ".opencode/agents/reality-checker.md",
    canonicalFile: ".claude/agents/reality-checker.md",
    userId: "reality-checker",
    memoryQueries: ["readiness claims evidence blockers", "verification failures open risks"],
  },
  {
    name: "evidence-collector",
    persona: "Evidence Collector",
    role: "Proof Packets",
    agentFile: ".opencode/agents/evidence-collector.md",
    canonicalFile: ".claude/agents/evidence-collector.md",
    userId: "evidence-collector",
    memoryQueries: ["evidence requirements screenshots artifacts", "proof packets qa traces"],
  },
  {
    name: "workflow-architect",
    persona: "Workflow Architect",
    role: "Handoffs and State Machines",
    agentFile: ".opencode/agents/workflow-architect.md",
    canonicalFile: ".claude/agents/workflow-architect.md",
    userId: "workflow-architect",
    memoryQueries: ["workflow decisions handoff contracts", "state machines failure paths"],
  },
  {
    name: "agentic-trust-architect",
    persona: "Agentic Trust Architect",
    role: "Permissions and Audit",
    agentFile: ".opencode/agents/agentic-trust-architect.md",
    canonicalFile: ".claude/agents/agentic-trust-architect.md",
    userId: "agentic-trust-architect",
    memoryQueries: ["agent permissions audit trust decisions", "memory authorization governance"],
  },
  {
    name: "openagent",
    persona: "OpenAgent",
    role: "Fallback Router",
    agentFile: ".opencode/agents/openagent.md",
    canonicalFile: ".claude/agents/openagent.md",
    userId: "openagent",
    memoryQueries: ["routing ownership active context", "unassigned tasks blockers"],
  },
]

export const TEAM_DURHAM_MEMORY = {
  groupId: "allura-team-durham",
  primaryTools: ["allura-brain_memory_search", "allura-brain_memory_list", "allura-brain_memory_add"],
  codexTools: ["mcp__allura_brain__memory_search", "mcp__allura_brain__memory_list", "mcp__allura_brain__memory_add"],
  contract: "Search shared memory before acting; log meaningful decisions and outcomes after work.",
}

export const TEAM_DURHAM_DEFAULTS = {
  entryAgent: "kotler",
  canonicalAgent: "brand-orchestrator",
  memoryRequired: true,
  showMenuOnActivation: true,
  groupId: TEAM_DURHAM_MEMORY.groupId,
  designTeam: ["aaker", "glaser", "ogilvy", "rand", "munari", "tufte"],
  operationsTeam: ["scout", "reality-checker", "evidence-collector", "workflow-architect", "agentic-trust-architect"],
  startupSequence: [
    "Activate Kotler as the Team Durham chair.",
    "Hydrate Allura Brain with group_id allura-team-durham.",
    "Load the Kotler/Brand Orchestrator command menu.",
    "Route design work through the Team Durham specialist roster.",
    "Log meaningful decisions, blockers, and outcomes to Allura Brain.",
  ],
}

export const TeamDurham = async () => {
  return {
    name: "team-durham",
    agents: TEAM_DURHAM_AGENTS,
    memory: TEAM_DURHAM_MEMORY,
    defaults: TEAM_DURHAM_DEFAULTS,
  }
}
