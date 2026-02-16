# PRP Template

## PRP-XXX: {Feature Name}

**Created**: {YYYY-MM-DD}  
**Initial**: `initials/init-{feature}.md`  
**Status**: Draft/Ready/In Progress/Complete

---

## Overview

### Problem Statement
{What problem are we solving? Why does this feature matter? Copy/adapt from init.}

### Proposed Solution
{High-level description of what we're building and how.}

### Success Criteria
- [ ] {Criterion 1 - testable}
- [ ] {Criterion 2 - testable}
- [ ] {Criterion 3 - testable}

---

## Context

### Related Documentation
- `docs/PLANNING.md` - Architecture overview
- `docs/DECISIONS.md` - Relevant ADRs (list specific ones)
- {External docs/references}

### Dependencies
- **Required**: {Features/PRPs that must be complete first}
- **Optional**: {Features that enhance but aren't required}

### Files to Modify/Create
```
path/to/file1.py        # Description of changes
path/to/file2.tsx       # Description of changes
path/to/new-file.py     # NEW: Purpose of new file
```

---

## Technical Specification

### Data Models
```{language}
# New or modified models
class ModelName(BaseModel):
    field_name: str = Field(..., description="Description")
    optional_field: int | None = None
```

### API Changes
| Method | Path | Request | Response | Notes |
|--------|------|---------|----------|-------|
| POST | /endpoint | `{...}` | `{...}` | New endpoint |
| PUT | /existing | `{...}` | `{...}` | Modified |

### Component Structure (if frontend)
```
ComponentName/
├── index.tsx           # Exports
├── ComponentName.tsx   # Main component
├── hooks.ts            # Component-specific hooks
└── ComponentName.test.tsx
```

### State Changes (if applicable)
{Describe state management changes}

---

## Implementation Steps

### Step 1: {First Step Title}
**Files**: `path/to/file.py`

{Detailed description of what to implement}

```{language}
# Code example or pseudocode if helpful
def example_function():
    pass
```

**Validation**:
- [ ] Tests pass
- [ ] Lint passes
- [ ] {Specific validation}

---

### Step 2: {Second Step Title}
**Files**: `path/to/file.py`, `path/to/other.py`

{Detailed description}

**Validation**:
- [ ] Tests pass
- [ ] {Specific validation}

---

### Step 3: {Third Step Title}
**Files**: `path/to/file.tsx`

{Detailed description}

**Validation**:
- [ ] Tests pass
- [ ] Manual verification

---

### Step N: Deploy and Integration Test
**Commands**:
```bash
cd {infrastructure_dir} && {deploy_command}
```

**Validation**:
- [ ] Deployment succeeds
- [ ] Integration test checklist passes

---

## Testing Requirements

### Unit Tests
- `test_{feature}_creates_correctly`: {Description}
- `test_{feature}_handles_errors`: {Description}
- `test_{feature}_validates_input`: {Description}

### Integration Tests
- {Scenario 1}: {How to test}
- {Scenario 2}: {How to test}

---

## Integration Test Plan

Manual tests to perform after deployment:

### Prerequisites
- Backend deployed: `{deploy_command}`
- Frontend running: `cd {frontend_dir} && npm run dev`
- Browser DevTools open (Console + Network tabs)

### Test Steps
| Step | Action | Expected Result | Pass? |
|------|--------|-----------------|-------|
| 1 | {Action to take} | {What should happen} | ☐ |
| 2 | {Action to take} | {What should happen} | ☐ |
| 3 | {Action to take} | {What should happen} | ☐ |

### Error Scenarios
| Scenario | How to Trigger | Expected Behavior | Pass? |
|----------|----------------|-------------------|-------|
| {Error case} | {How to cause it} | {Graceful handling} | ☐ |

---

## Error Handling

### Expected Errors
| Error | Cause | Handling |
|-------|-------|----------|
| {Error type} | {What causes it} | {How to handle} |

### Edge Cases
- {Edge case 1}: {How handled}
- {Edge case 2}: {How handled}

---

## Cost Impact (if applicable)

| Component | Change | Est. Impact |
|-----------|--------|-------------|
| {API calls} | {+/- X calls} | {$X/month} |
| {Storage} | {+/- X GB} | {$X/month} |
| **Total** | | **{$X/month}** |

---

## Open Questions

- [ ] {Question 1 - needs answer before implementation}
- [ ] {Question 2}

---

## Rollback Plan

If issues are discovered:
1. {Rollback step 1}
2. {Rollback step 2}
3. {How to verify rollback succeeded}

---

## Confidence Scores

| Dimension | Score (1-10) | Notes |
|-----------|--------------|-------|
| Clarity | X | {Are requirements unambiguous?} |
| Feasibility | X | {Can this be done with current architecture?} |
| Completeness | X | {Does PRP cover all aspects?} |
| Alignment | X | {Does it align with project goals?} |
| **Average** | **X** | |

{If average < 7, list specific concerns and what would help}

---

## Notes

{Any additional context or considerations}
