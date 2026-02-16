# Generate PRP

Generate a comprehensive Project Requirement Plan (PRP) for a feature.

## Arguments
- `$ARGUMENTS` - Path to initial file (e.g., `initials/init-feature-name.md`)

## Instructions

You are generating a PRP (Project Requirement Plan) for the {PROJECT_NAME} project.

### Step 1: Gather Context

Read and internalize the following project documentation:
1. `CLAUDE.md` - Project-specific instructions and conventions
2. `docs/PLANNING.md` - Architecture overview and goals
3. `docs/DECISIONS.md` - Past architecture decisions (don't contradict these)
4. `docs/TASK.md` - Current task status
5. `docs/TESTING.md` - Testing standards

### Step 2: Read the Initial File

Read the initial specification at `$ARGUMENTS`:
1. Understand the feature requirements
2. Note any specific constraints or preferences
3. Identify integration points with existing code
4. Check that all open questions are answered

### Step 3: Research Codebase

Based on the feature description, research the codebase:
1. Search for related existing implementations
2. Identify files that will need modification
3. Check `examples/` folder for patterns to follow
4. Look for existing similar patterns

### Step 4: Generate PRP

Create a new PRP file at `prps/prp-{feature-slug}.md` where:
- feature-slug matches the initial file name (e.g., `init-character-api.md` → `prp-character-api.md`)

Use the template at `prps/templates/prp-template.md` as the structure.

Fill in all sections:
1. **Overview**: Clear problem statement and proposed solution
2. **Success Criteria**: Measurable, testable outcomes
3. **Context**: Links to relevant docs, existing code, dependencies
4. **Technical Specification**: Data models, API changes, component structure
5. **Implementation Steps**: Ordered, atomic tasks with file paths
6. **Testing Requirements**: Unit, integration, manual tests needed
7. **Integration Test Plan**: Specific manual tests to verify feature works
8. **Error Handling**: Edge cases and failure scenarios
9. **Cost Impact**: Estimate API and infrastructure costs (if applicable)
10. **Open Questions**: Anything that needs clarification
11. **Rollback Plan**: How to undo if issues arise

### Step 5: Score Confidence

Before finishing, score your confidence (1-10) on each dimension:
- **Clarity**: How well-defined is the scope? (are requirements unambiguous?)
- **Feasibility**: Can this be done with current architecture? (are there blockers?)
- **Completeness**: Does the PRP cover all aspects? (no missing pieces?)
- **Alignment**: Does it align with project goals/constraints? (budget, patterns)

Calculate overall confidence as the average.

If overall confidence is below 7:
- List specific concerns
- Identify what additional context would help
- Ask clarifying questions
- Do NOT proceed until concerns are addressed

### Step 6: Output

1. Create the PRP file in `prps/` folder
2. Report the file path created
3. Display confidence scores
4. List any open questions or concerns

## Example Usage

```
/generate-prp initials/init-user-auth.md
```

This would:
1. Read all context files
2. Read `initials/init-user-auth.md`
3. Research auth patterns in codebase
4. Generate `prps/prp-user-auth.md`
5. Report confidence and concerns

## Quality Checklist

Before completing, verify:
- [ ] Every implementation step has specific file paths
- [ ] Steps are atomic and can be validated individually
- [ ] Test cases cover happy path and error cases
- [ ] Integration test plan is specific and actionable
- [ ] No ADRs are contradicted
- [ ] Cost impact is estimated (if applicable)
- [ ] Rollback plan exists
