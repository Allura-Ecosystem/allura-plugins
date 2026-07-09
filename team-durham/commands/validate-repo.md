# Validate Repository

Comprehensive validation command that checks the entire Brand Maker repository for consistency between agent definitions, skills, rules, contracts, templates, and deliverables.

## Usage

```bash
/validate-repo
```

## What It Checks

This command performs a comprehensive validation of:

1. **Agent & Skill Definitions**
   - Agent definitions completeness
   - Skill file existence and syntax
   - Command file references
   - Subagent type declarations

2. **Brand Infrastructure**
   - Client workspace structure
   - Brand kit directory structure
   - Template file existence
   - Rules and contracts files

3. **Pipeline Deliverables**
   - Deliverable completeness
   - Brand asset versioning
   - Output directory structure
   - Missing deliverables defined in plan

4. **Consistency Checks**
   - BLUEPRINT.md alignment with actual project state
   - Strategy contracts match brand kit output
   - QA review status on deliverables
   - group_id enforcement across DB operations

5. **Context File Structure**
   - All referenced context files exist
   - Context file organization is correct
   - No orphaned context files

6. **Cross-References**
   - Agent dependencies exist
   - Command references are valid
   - Skill references are satisfied
   - Template mappings are correct

## Output

The command generates a detailed report showing:
- ✅ What's correct and validated
- ⚠️ Warnings for potential issues
- ❌ Errors that need fixing
- 📊 Summary statistics

## Instructions

You are a validation specialist. Your task is to comprehensively validate the Brand Maker repository for consistency and correctness.

### Step 1: Validate Agent & Skill Definitions

1. Read and parse all agent definition files in `.claude/agents/`
2. Validate structure:
   - Agent IDs are unique
   - Required fields present (name, type, description)
   - Subagent types are valid
   - Command references exist

3. Verify each agent file exists
4. Check for duplicate IDs
5. Validate skill SKILL.md files exist in `.claude/skills/`

### Step 2: Validate Brand Infrastructure

For each infrastructure element:

1. **Client Workspace**
   - `clients/_template/` directory exists
   - Template contains phase deliverable files

2. **Brand Kit**
   - All expected brand kit sections referenced
   - Version markers present

3. **Templates**
   - `.claude/templates/BLUEPRINT.template.md` exists
   - `.claude/templates/DDR.template.md` exists
   - `.claude/templates/BRAND-DICTIONARY.template.md` exists

### Step 3: Validate Pipeline Deliverables

For each client:
1. Check phase deliverables 00-07 exist
2. Report status: ✅ Complete, 🔄 In Progress, ⏳ Pending, ❌ Missing

### Step 4: Validate Consistency

1. Check `.claude/rules/` files exist and are valid
2. Check `.claude/context/` files exist
3. Check `.claude/AGENTS.md` references match actual agents
4. Check `.claude/contracts/harness-v1.md` exists

### Step 5: Generate Report

Create a comprehensive report with:
- ✅ Validated Successfully
- ⚠️ Warnings
- ❌ Errors
- 📊 Statistics
- 🔧 Recommended Actions