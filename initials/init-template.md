# Init Template - Feature Specification

## init-XX: {Feature Name}

**Created**: {YYYY-MM-DD}  
**Priority**: {High/Medium/Low}  
**Depends On**: {init-YY, init-ZZ, or "None"}

---

## Problem Statement

{What problem does this feature solve? Why is it needed? 1-3 sentences.}

## Goal

{What will be true when this feature is complete? What can users do?}

## Requirements

### Must Have (P0)
1. {Requirement 1}
2. {Requirement 2}
3. {Requirement 3}

### Should Have (P1)
1. {Requirement 4}
2. {Requirement 5}

### Nice to Have (P2)
1. {Requirement 6}

## User Stories

**As a** {user type}  
**I want to** {action}  
**So that** {benefit}

{Add more user stories as needed}

## Technical Considerations

### Data Changes
- {New fields, tables, or models needed}
- {Changes to existing data structures}

### API Changes
- {New endpoints}
- {Changes to existing endpoints}

### UI Changes
- {New components or pages}
- {Changes to existing UI}

### Integration Points
- {External services to integrate}
- {Internal systems affected}

## Constraints

- {Constraint 1: budget, performance, etc.}
- {Constraint 2}

## Success Criteria

- [ ] {Testable criterion 1}
- [ ] {Testable criterion 2}
- [ ] {Testable criterion 3}

## Out of Scope

{Explicitly list what this feature does NOT include}

- {Not included 1}
- {Not included 2}

## Open Questions

- [ ] {Question 1}
- [ ] {Question 2}

## Notes

{Any additional context, references, or considerations}

---

## Template Usage

**When creating an init file:**

1. Copy this template to `initials/init-{feature-name}.md`
2. Fill in all sections (delete "Notes" if empty)
3. Be specific in requirements - vague specs lead to scope creep
4. Answer all open questions before generating PRP
5. Review with stakeholders if needed

**What makes a good init spec:**

- **Clear problem statement**: One clear problem, not multiple
- **Measurable success criteria**: Can verify when complete
- **Explicit scope boundaries**: What's in AND what's out
- **Technical awareness**: Considers data, API, UI impacts
- **No implementation details**: Says WHAT, not HOW

**After creating:**

1. In Claude Code: `/generate-prp initials/init-{feature}.md`
2. Review generated PRP
3. Execute: `/execute-prp prps/prp-{feature}.md`
