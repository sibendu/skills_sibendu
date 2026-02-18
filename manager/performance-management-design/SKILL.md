---
name: performance-management-design
description: Generate SMART performance goals and KPIs for team roles based on performance categories. Use this skill when users need to create performance management goals, design appraisal frameworks, generate KPIs for roles, or create goal-setting templates for performance reviews. Takes category definitions, role descriptions, and generates structured SMART goals aligned to each category.
---
# Performance Management Design

Generate SMART performance goals with measurable KPIs for organizational roles based on performance categories.

## Overview

This skill creates performance management goals by:
1. Reading performance categories and their descriptions
2. Reading team roles and job descriptions
3. Generating a specified number of SMART goals per category for each role
4. Outputting structured goals with embedded KPIs in Excel format

## Inputs Required

1. **Categories Excel file**: Two columns
  - Column A: Category name (e.g., "AI Adoption", "Personal Development")
  - Column B: Category description
  - Column C: Number_of_Goals i.e. Number of Goals to generate for this category

2. **Roles Excel file**: Two columns
  - Column A: Role name
  - Column B: Job description

3. **Time period** (optional): Duration for goal achievement, default is 12 months
  - This parameter influences goal design but is not explicitly mentioned in output
  - Common values: 3 (quarterly), 6 (semi-annual), 12 (annual)

## SMART Principle Requirements

Each generated goal must follow SMART criteria:

- **Specific**: Clear, unambiguous objective tied to role responsibilities
- **Measurable**: Quantifiable outcomes or observable deliverables
- **Achievable**: Realistic given role scope and organizational context
- **Relevant**: Aligned to category purpose and role's job description
- **Time-bound**: Implicitly bounded by the input time period

## Goal Generation Guidelines

### Goal Quality Standards

1. **Role-specific alignment**: Analyze job description to ensure goals match responsibilities and seniority level
2. **Category alignment**: Each goal must directly address the category's description and intent
3. **Measurable KPIs**: Include 2-4 specific KPI measures per goal that the associate can report at appraisal time
4. **Avoid generic goals**: Tailor each goal to the specific role, not generic templates
5. **Balance quantitative and qualitative**: Use numeric targets where appropriate, descriptive outcomes where necessary

### KPI Measure Examples

**Quantitative KPIs:**
- "Increase team adoption rate from 30% to 60%"
- "Complete 5 certification courses"
- "Reduce processing time by 25%"
- "Deliver 3 major releases"

**Qualitative KPIs:**
- "Demonstrate proficiency through successful project completion"
- "Receive positive stakeholder feedback on deliverables"
- "Establish documented process guidelines adopted by team"
- "Mentor 2 junior team members to successful milestone completion"

### Goal Formatting

Structure each goal cell with:

```
Goal: [Clear goal statement]

KPIs:
- [Specific measurable outcome 1]
- [Specific measurable outcome 2]
- [Specific measurable outcome 3]
```

Use clear line breaks for readability within Excel cells.

## Output Structure

Generate an Excel file with the following structure:

**Column Headers:**
- Column A: "Role"
- Column B: "Job Description"
- Column C onwards: One column per category (header = category name from input)

**Data Rows:**
- One row per role
- Column A: Role name (from input)
- Column B: Job description (from input)
- Column C onwards: Each cell contains ALL goals for that category (one column per category)

**Example structure** (5 categories, 2 goals per category = 10 goals per role):

| Role | Job Description | AI Adoption | Personal Development | Leadership | Quality | Innovation |
| --- | --- | --- | --- | --- | --- | --- |
| Senior Engineer | Leads technical projects... | Goal 1 + KPIs<br><br>Goal 2 + KPIs | Goal 1 + KPIs<br><br>Goal 2 + KPIs | ... | ... | ... |

## Implementation Script

Use the provided Python script to generate goals:

```bash
python scripts/generate_performance_goals.py \
  --categories path/to/categories.xlsx \
  --roles path/to/roles.xlsx \
  --goals-per-category 2 \
  --time-period 12 \
  --output path/to/output.xlsx
```

The script leverages Claude API to generate contextually appropriate SMART goals based on role and category combinations.

## Workflow

1. **Read input files**: Load categories and roles from Excel files
2. **For each role**:
  - For each category:
    - Analyze role description and category description
    - Generate specified number of SMART goals
    - Create measurable KPIs for each goal
    - Format goals with embedded KPIs
3. **Structure output**: Create Excel with role data and category-based goal columns
4. **Save file**: Export formatted Excel workbook

## Quality Checks

Before finalizing output, verify:

- All goals follow SMART principles
- KPIs are specific and measurable
- Goals align with both role responsibilities and category intent
- No duplicate or generic goals across roles
- Proper Excel formatting with clear cell breaks
- All input categories and roles are represented
