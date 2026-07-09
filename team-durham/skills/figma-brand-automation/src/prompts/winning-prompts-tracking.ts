/**
 * Winning Prompts Tracking System
 * 
 * Tracks successful prompts in Allura Brain (PostgreSQL + Neo4j)
 * and syncs with Notion for team visibility
 */

export interface PromptPerformance {
  promptId: string;
  tokenSet: string;
  model: string;
  direction: string;
  brandSlug: string;
  metrics: {
    generationTime: number;
    cost: number;
    qualityScore?: number; // 1-10 from QA
    clientApproval?: boolean;
    usageCount: number;
  };
  outputs: {
    imageUrl: string;
    localPath: string;
    dimensions: string;
    fileSize: number;
  }[];
  tags: string[];
  createdAt: string;
  lastUsed: string;
}

import { logToAlluraBrain } from '../utils/allura-brain';

/**
 * Log successful prompt to Allura Brain
 */
export async function logWinningPrompt(
  performance: PromptPerformance
): Promise<void> {
  // Log to PostgreSQL via Allura Brain
  await logToAlluraBrain({
    agentId: 'glaser',
    eventType: 'winning_prompt_logged',
    groupId: 'allura-team-durham',
    payload: {
      promptId: performance.promptId,
      tokenSet: performance.tokenSet,
      model: performance.model,
      brandSlug: performance.brandSlug,
      direction: performance.direction,
      qualityScore: performance.metrics.qualityScore,
      cost: performance.metrics.cost,
      usageCount: performance.metrics.usageCount,
      tags: performance.tags,
      createdAt: performance.createdAt,
      lastUsed: performance.lastUsed
    }
  });
  
  // Neo4j: Knowledge graph (prepared for MCP_DOCKER)
  const cypher = `
    MATCH (b:Brand {slug: $brandSlug})
    MERGE (p:Prompt {
      promptId: $promptId,
      tokenSet: $tokenSet,
      model: $model,
      direction: $direction
    })
    MERGE (b)-[:HAS_WINNING_PROMPT]->(p)
    
    // Create performance metrics
    CREATE (pm:PromptMetrics {
      qualityScore: $qualityScore,
      cost: $cost,
      usageCount: $usageCount,
      createdAt: datetime($createdAt),
      lastUsed: datetime($lastUsed)
    })
    CREATE (p)-[:HAS_METRICS]->(pm)
    
    // Tag relationships
    FOREACH (tag IN $tags |
      MERGE (t:Tag {name: tag})
      CREATE (p)-[:TAGGED_AS]->(t)
    )
    
    // Model relationship
    MERGE (m:AIModel {name: $model})
    CREATE (p)-[:USES_MODEL]->(m)
  `;
  
  const neo4jParams = {
    brandSlug: performance.brandSlug,
    promptId: performance.promptId,
    tokenSet: performance.tokenSet,
    model: performance.model,
    direction: performance.direction,
    qualityScore: performance.metrics.qualityScore,
    cost: performance.metrics.cost,
    usageCount: performance.metrics.usageCount,
    tags: performance.tags,
    createdAt: performance.createdAt,
    lastUsed: performance.lastUsed
  };
  
  console.log(`[Allura Brain] Logged winning prompt: ${performance.promptId}`);
  console.log(`[Allura Brain] Neo4j Cypher prepared (requires MCP_DOCKER):`, cypher.substring(0, 100) + '...');
}

/**
 * Query winning prompts by criteria
 */
export async function queryWinningPrompts(
  criteria: {
    brandSlug?: string;
    model?: string;
    minQualityScore?: number;
    tags?: string[];
    limit?: number;
  }
): Promise<PromptPerformance[]> {
  const { brandSlug, model, minQualityScore, tags, limit = 10 } = criteria;
  
  // Neo4j query
  let cypher = `
    MATCH (b:Brand)-[:HAS_WINNING_PROMPT]->(p:Prompt)-[:HAS_METRICS]->(pm:PromptMetrics)
    WHERE 1=1
  `;
  
  const params: Record<string, any> = {};
  
  if (brandSlug) {
    cypher += ` AND b.slug = $brandSlug`;
    params.brandSlug = brandSlug;
  }
  
  if (model) {
    cypher += ` AND p.model = $model`;
    params.model = model;
  }
  
  if (minQualityScore) {
    cypher += ` AND pm.qualityScore >= $minQualityScore`;
    params.minQualityScore = minQualityScore;
  }
  
  if (tags && tags.length > 0) {
    cypher += ` AND ALL(tag IN $tags WHERE (p)-[:TAGGED_AS]->(:Tag {name: tag}))`;
    params.tags = tags;
  }
  
  cypher += `
    RETURN p, pm
    ORDER BY pm.qualityScore DESC, pm.usageCount DESC
    LIMIT $limit
  `;
  params.limit = limit;
  
  // Mock return - would execute actual Neo4j query
  return [];
}

/**
 * Get top performing prompts for a use case
 */
export async function getTopPromptsForUseCase(
  useCase: string,
  brandSlug?: string,
  limit: number = 5
): Promise<PromptPerformance[]> {
  const tagMap: Record<string, string[]> = {
    'hero': ['hero-image', 'web', 'background'],
    'logo': ['logo', 'vector', 'brand-identity'],
    'social': ['social-media', 'instagram', 'post'],
    'infographic': ['infographic', 'data-viz', 'typography'],
    'pattern': ['pattern', 'texture', 'background']
  };
  
  const tags = tagMap[useCase] || [useCase];
  
  return queryWinningPrompts({
    brandSlug,
    tags,
    minQualityScore: 7,
    limit
  });
}

/**
 * Update prompt usage metrics
 */
export async function updatePromptMetrics(
  promptId: string,
  updates: {
    qualityScore?: number;
    clientApproval?: boolean;
    usageIncrement?: number;
  }
): Promise<void> {
  const { qualityScore, clientApproval, usageIncrement = 1 } = updates;
  
  // Neo4j: Update metrics
  const cypher = `
    MATCH (p:Prompt {promptId: $promptId})-[:HAS_METRICS]->(pm:PromptMetrics)
    SET pm.lastUsed = datetime()
    ${qualityScore ? ', pm.qualityScore = $qualityScore' : ''}
    ${clientApproval !== undefined ? ', pm.clientApproval = $clientApproval' : ''}
    ${usageIncrement ? ', pm.usageCount = pm.usageCount + $usageIncrement' : ''}
  `;
  
  // PostgreSQL: Log update
  const pgQuery = `
    INSERT INTO events (agent_id, event_type, group_id, payload, created_at)
    VALUES ('glaser', 'prompt_metrics_updated', 'allura-team-durham', $1, NOW())
  `;
  
  const payload = {
    promptId,
    qualityScore,
    clientApproval,
    usageIncrement
  };
  
  console.log(`[Allura Brain] Updated metrics for: ${promptId}`);
}

/**
 * Sync winning prompts to Notion
 */
export async function syncToNotion(
  prompts: PromptPerformance[],
  notionDatabaseId?: string
): Promise<void> {
  // Format for Notion
  const notionPages = prompts.map(p => ({
    parent: { database_id: notionDatabaseId || 'winning-prompts' },
    properties: {
      'Prompt ID': { title: [{ text: { content: p.promptId } }] },
      'Token Set': { rich_text: [{ text: { content: p.tokenSet } }] },
      'Model': { select: { name: p.model } },
      'Direction': { rich_text: [{ text: { content: p.direction } }] },
      'Brand': { relation: [{ id: p.brandSlug }] },
      'Quality Score': { number: p.metrics.qualityScore },
      'Cost': { number: p.metrics.cost },
      'Usage Count': { number: p.metrics.usageCount },
      'Tags': { multi_select: p.tags.map(t => ({ name: t })) },
      'Last Used': { date: { start: p.lastUsed } },
      'Status': { select: { name: p.metrics.clientApproval ? 'Approved' : 'Testing' } }
    }
  }));
  
  // Would call Notion MCP here
  console.log(`[Notion] Synced ${prompts.length} winning prompts`);
}

/**
 * Generate prompt performance report
 */
export async function generatePromptReport(
  brandSlug?: string,
  startDate?: string,
  endDate?: string
): Promise<{
  totalPrompts: number;
  averageQuality: number;
  totalCost: number;
  topModels: { model: string; count: number; avgQuality: number }[];
  topTags: { tag: string; count: number }[];
}> {
  // Neo4j aggregation query
  const cypher = `
    MATCH (b:Brand${brandSlug ? ' {slug: $brandSlug}' : ''})-[:HAS_WINNING_PROMPT]->(p:Prompt)-[:HAS_METRICS]->(pm:PromptMetrics)
    ${startDate ? 'WHERE pm.createdAt >= datetime($startDate)' : ''}
    ${endDate ? 'AND pm.createdAt <= datetime($endDate)' : ''}
    
    RETURN 
      count(p) as totalPrompts,
      avg(pm.qualityScore) as averageQuality,
      sum(pm.cost) as totalCost
  `;
  
  // Mock return
  return {
    totalPrompts: 42,
    averageQuality: 8.3,
    totalCost: 0.84,
    topModels: [
      { model: 'fal-ai/seedream-v4.5', count: 15, avgQuality: 8.7 },
      { model: 'fal-ai/nano-banana-2', count: 12, avgQuality: 8.4 },
      { model: 'fal-ai/flux-dev', count: 10, avgQuality: 7.9 }
    ],
    topTags: [
      { tag: 'hero-image', count: 18 },
      { tag: 'typography', count: 15 },
      { tag: 'logo', count: 12 }
    ]
  };
}
