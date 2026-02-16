# {PROJECT_NAME} - Project Instructions

## What This Is

{Brief 1-2 sentence description of the project}

**Live URL**: {your-domain.com} (if applicable)
**Repository**: {github.com/org/repo}

## Tech Stack

- **Frontend**: {React/Vue/etc} + TypeScript
- **Backend**: {Lambda/Express/etc} (Python/Node)
- **Database**: {DynamoDB/PostgreSQL/etc}
- **AI**: {Claude API/OpenAI/etc} (if applicable)
- **IaC**: {CDK/Terraform/etc}

## Critical Constraints

1. **Budget limit**: ${X}/month - {Cost control strategies}
2. **File size limit: 500 lines max** - Split into modules when approaching
3. **Commit after every feature** - Atomic, working commits with conventional messages

## File Naming Conventions

- Feature specs: `initials/init-{name}.md`
- Implementation plans: `prps/prp-{name}.md`
- Use kebab-case for all file names

## Workflow: Claude.ai ↔ Claude Code

| Claude.ai (this chat) | Claude Code |
|-----------------------|-------------|
| Architecture decisions | Write code |
| Create/review `init-*` specs | Run `/generate-prp` |
| Review PRPs before execution | Run `/execute-prp` |
| Troubleshoot blockers | Run tests, deploy |
| Update planning docs | Git operations |

### To Start New Feature:
1. **Here**: Create `initials/init-{feature}.md` with requirements
2. **Claude Code**: `/generate-prp initials/init-{feature}.md`
3. **Here** (optional): Review generated PRP
4. **Claude Code**: `/execute-prp prps/prp-{feature}.md`

## Key Project Files

Always check these files in the repo for current state:
- `docs/PLANNING.md` - Architecture, data models, API design
- `docs/TASK.md` - Current sprint tasks and status
- `docs/DECISIONS.md` - Architecture Decision Records (ADRs)
- `CLAUDE.md` - Detailed coding conventions for Claude Code

## Cost Breakdown Target (if applicable)

| Component | Budget |
|-----------|--------|
| AI API | ${X}/month |
| Cloud Services | ${Y}/month |
| **Total** | **< ${Z}/month** |

## When Starting a New Chat

1. Check attached `TASK.md` for current work status
2. Check attached `PLANNING.md` for architecture context
3. Check attached `DECISIONS.md` for past decisions (don't contradict)
4. Reference the GitHub repo for latest code state

## Quick Reference

- **Database Keys**: {Your key patterns, e.g., PK=USER#{id}}
- **Backend Pattern**: {e.g., Powertools + Pydantic + type hints}
- **Frontend Pattern**: {e.g., Functional components + hooks + Tailwind}
- **Commit Format**: `feat:`, `fix:`, `refactor:`, `docs:`

---

## Template Usage Notes

**To customize this template:**

1. Replace all `{PLACEHOLDERS}` with your project specifics
2. Remove sections that don't apply (e.g., AI API if not using)
3. Add domain-specific constraints or rules
4. Keep this file attached to your Claude.ai Project

**Key principles this workflow embodies:**

- **Separation of concerns**: Claude.ai for architecture, Claude Code for implementation
- **Documentation-first**: Specs before code
- **Atomic progress**: Small, working commits
- **Cost awareness**: Budget constraints are explicit
- **Decision tracking**: ADRs prevent contradictions
