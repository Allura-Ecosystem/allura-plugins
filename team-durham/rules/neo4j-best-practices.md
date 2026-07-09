---
description: Neo4j best practices for Allura Brain semantic store
globs: [".claude/**", "clients/**"]
---

# Neo4j Best Practices — Team Durham

## The Rules

1. **SUPERSEDES, never mutate** — When a memory node needs updating, create a new version and link with `(v2)-[:SUPERSEDES]->(v1)`. Set `v1.deprecated = true`.
2. **Search first** — Always run a MATCH before CREATE. Never create duplicates.
3. **group_id on every node** — Every node MUST have `group_id` property matching `^allura-`.
4. **Promotion gate** — Only Kotler can write to Neo4j. All other agents read-only.
5. **Batch writes** — At most one Neo4j write per completed task/decision.

## Read Patterns

```cypher
// Find brand truth for a group
MATCH (m:Memory {group_id: 'allura-team-durham', deprecated: false})
WHERE m.content CONTAINS $query
RETURN m.id, m.content, m.score
ORDER BY m.score DESC
LIMIT 10
```

## Write Pattern (SUPERSEDES)

```cypher
// 1. Find existing
MATCH (old:Memory {id: $existing_id, deprecated: false})

// 2. Create new version
CREATE (new:Memory {
  id: randomUUID(),
  group_id: 'allura-team-durham',
  content: $new_content,
  score: $score,
  deprecated: false,
  created_at: datetime()
})

// 3. Link and deprecate
CREATE (new)-[:SUPERSEDES]->(old)
SET old.deprecated = true
```

## Node Schema

```
(:Memory {
  id: UUID,
  group_id: string (^allura-),
  user_id: string,
  content: string,
  score: float (0-1),
  deprecated: boolean,
  created_at: datetime,
  source_event_id: string (optional)
})
```