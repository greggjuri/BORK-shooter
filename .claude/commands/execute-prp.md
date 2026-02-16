# Execute PRP

Execute a Project Requirement Plan step-by-step.

## Arguments
- `$ARGUMENTS` - Path to PRP file (e.g., `prps/prp-feature-name.md`)

## Instructions

You are executing a PRP (Project Requirement Plan) for the {PROJECT_NAME} project.

### Step 0: Pre-flight Checks

Before starting:
1. Read `CLAUDE.md` for coding conventions
2. Read the PRP at `$ARGUMENTS` completely
3. Verify all dependencies are met
4. Check that confidence score is ≥ 7 (if not, stop and report concerns)
5. Ensure you understand the success criteria

### Step 1: Execute Implementation Steps

For each implementation step in the PRP:

1. **Announce**: State which step you're starting
2. **Implement**: Write the code changes
3. **Follow conventions**: Match existing patterns in codebase
4. **Validate**: Run tests and lint after each step
5. **Commit**: After validation passes, commit with conventional message

```bash
# After each step
{test_command}  # Run tests
{lint_command}  # Run linter
git add .
git commit -m "{type}: {description}"
```

### Step 2: Handle Failures

If a step fails:

1. **Diagnose**: Understand what went wrong
2. **Fix**: Make minimal changes to resolve
3. **Document**: Note the issue and fix in commit message
4. **Continue**: Only proceed when step validates

If unable to proceed:
1. Report the blocker clearly
2. Suggest potential solutions
3. Ask for guidance before continuing

### Step 3: Run Integration Tests

After all implementation steps:

1. Deploy to test environment: `{deploy_command}`
2. Execute each test in the Integration Test Plan
3. Record pass/fail for each test
4. If failures: diagnose and fix before proceeding

### Step 4: Final Validation

1. Run full test suite
2. Verify all success criteria are met
3. Check for regressions

### Step 5: Update Documentation

1. Update `docs/TASK.md`:
   - Move task from "In Progress" to "Recently Completed"
   - Add any learnings to "Architecture Decisions"
   
2. If architectural decisions were made:
   - Add ADR to `docs/DECISIONS.md`

### Step 6: Report Completion

Provide summary:
```
## PRP Execution Complete

**PRP**: prps/prp-{feature}.md
**Status**: Complete/Partial/Blocked

### Commits Made
- {commit hash}: {message}
- {commit hash}: {message}

### Tests
- Unit: X passing
- Integration: X/Y passing

### Success Criteria
- [x] Criterion 1
- [x] Criterion 2
- [ ] Criterion 3 (if incomplete, explain why)

### Issues Encountered
{List any issues and how they were resolved}

### Follow-up Items
{Any tasks that should be done next}
```

## Example Usage

```
/execute-prp prps/prp-user-auth.md
```

## Commit Message Format

Use conventional commits:
- `feat: add user authentication endpoint`
- `fix: correct password hashing algorithm`
- `refactor: extract auth middleware`
- `test: add auth integration tests`
- `docs: update API documentation`

## Quality Standards

- **No file over 500 lines**: Split if approaching
- **Tests for new code**: Aim for 80% coverage
- **No lint errors**: Fix all warnings
- **Working commits**: Each commit should be deployable
- **Clear commit messages**: Describe what and why

## Emergency Stop

If you encounter:
- Security vulnerability
- Data loss risk
- Contradicting ADR
- Unclear requirements

**STOP** and report before proceeding.

## Notes

- Take your time - quality over speed
- Ask questions if anything is unclear
- It's okay to deviate from PRP if you find a better approach, but document why
- Leave the codebase better than you found it
