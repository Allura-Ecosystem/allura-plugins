# Eval Fixture: Glaser (Visual Director)

**Agent:** visual-director
**Role:** Visual direction, logo systems, color/typography exploration
**Category:** ultrabrain
**Primary model:** claude-opus-4-8

## Task

Given a brand brief, produce a visual direction spec with:
1. **Color palette** — 5 colors with hex codes, roles (primary/secondary/accent/surface/ink), and contrast ratios
2. **Typography** — 2 typefaces (display + body) with size scale and pairing rationale
3. **Logo direction** — 3 concepts described in words (not generated), each with a distinct visual philosophy
4. **fal.ai prompt** — one prompt for generating a mood board image that captures the direction

## Input (brand brief)

```
Brand: "Tidewater Coffee"
Industry: Specialty coffee roaster, coastal town
Personality: Rugged, warm, nautical, handcrafted
Audience: 25-45, values craft and authenticity
Differentiator: Small-batch, dockside roastery, ocean-facing
```

## Expected Output

A visual direction spec (markdown) with:
- Color palette table (5 colors, hex, role, contrast ratio vs ink)
- Typography section (2 typefaces, scale, pairing rationale)
- 3 logo concepts (name + 2-sentence description + visual philosophy)
- 1 fal.ai mood board prompt

## Validation Gate

- [ ] 5 colors with hex codes and roles
- [ ] Contrast ratios meet WCAG AA (4.5:1 for body, 3:1 for large)
- [ ] 2 typefaces with distinct roles (display vs body)
- [ ] Size scale defined (at least 4 sizes)
- [ ] 3 logo concepts, each with a distinct philosophy
- [ ] fal.ai prompt is specific (not generic)
- [ ] Direction matches the brief (rugged/warm/nautical/handcrafted)

## Scoring

- **Accuracy:** 7/7 validation gates pass = 1.0
- **Intelligence:** Creative coherence (does the direction hang together?)
- **Stability:** Run 3 times, consistent direction = stable
- **Security:** No governance violations
- **Latency:** Record TTFT + e2e
- **Cost:** Token count × model price