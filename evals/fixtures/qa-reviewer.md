# Eval Fixture: Munari (QA Reviewer)

**Agent:** qa-reviewer
**Role:** Brand consistency, accessibility, usability, production-readiness QA gate
**Category:** ultrabrain
**Primary model:** claude-opus-4-8

## Task

Review the following brand landing page HTML for:
1. **Brand compliance** — does it use the brand tokens (colors, fonts, spacing)?
2. **Accessibility (WCAG 2.2 AA)** — contrast, alt text, keyboard nav, ARIA
3. **Usability** — clear hierarchy, legible copy, no silent failures
4. **Production-readiness** — no placeholder text, no broken links, no console errors

## Input

```html
<!DOCTYPE html>
<html>
<head>
  <title>Acme — Home</title>
  <style>
    body { font-family: Arial; background: #fff; color: #333; }
    .hero { background: #f0f0f0; color: #999; padding: 20px; }
    .cta { background: #007bff; color: white; padding: 10px 20px; }
    img { max-width: 100%; }
  </style>
</head>
<body>
  <div class="hero">
    <h1>Welcome to Acme</h1>
    <p>Lorem ipsum dolor sit amet.</p>
    <img src="hero.jpg">
    <button class="cta" onclick="alert('hi')">Click here</button>
  </div>
  <a href="#">Link</a>
  <a href="#">Link</a>
  <a href="#">Link</a>
</body>
</html>
```

## Expected Output

A QA report with:
- **Pass/Fail** per dimension (brand, accessibility, usability, production-readiness)
- **Findings** with severity (P0/P1/P2) and specific line references
- **Gate decision** (85% pass / 90% ship)
- **Fix list** ordered by priority

## Validation Gate

- [ ] Identifies contrast violation (hero #999 on #f0f0f0 fails WCAG AA)
- [ ] Identifies missing alt text on img
- [ ] Identifies placeholder text ("Lorem ipsum")
- [ ] Identifies generic link text ("Link" × 3 — not descriptive)
- [ ] Identifies onclick alert as a silent failure / poor UX
- [ ] Gate decision is "FAIL" (below 85%)
- [ ] Fix list is ordered P0 → P1 → P2

## Scoring

- **Accuracy:** 7/7 validation gates pass = 1.0
- **Intelligence:** QA rigor (catches subtle issues, not just obvious ones)
- **Stability:** Run 3 times, same findings = stable
- **Security:** No governance violations
- **Latency:** Record TTFT + e2e
- **Cost:** Token count × model price