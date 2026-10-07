---
name: writing-plans
description: Create, revise, or supersede an implementation plan in .plan/. Use whenever the user asks for a plan, an approach, or a design doc for a task, or when revising a plan after feedback. Defines the .plan/ lifecycle, the NNN-YYYY-MM-DD-topic.md filename, required metadata, and the nine required sections.
---

# Writing Plans

`.plan/` at the repository root is the source of truth for plans. `000-backlog.md` is the
task queue; every other file is a plan.

## Before writing anything
1. Read the existing `.plan/*.md`. A new plan must build on decisions already made.
2. Read `.doc/product-definition.md` for acceptance criteria and scope, and
   `.doc/architecture.md` for the current module layout.

## Filename
`NNN-YYYY-MM-DD-<topic>.md`, sequential prefix — `001`, `002`, `003`.

## Required metadata
```
Status: draft | active | done | superseded
Owner:
Last updated: YYYY-MM-DD
```
New plans start as `Status: draft`. Only a human flips a plan to `active`.

## Required sections, in this order
`Goal` · `Scope` · `Assumptions` · `Open Questions` · `Steps` · `Validation` · `Risks` ·
`Rollout Order` · `Rollback`

## Content rules
- Repository-relative paths only.
- Generated artifacts belong in `.orchestrate/` (agent reports) or `reports/` (code reviews).
  Never create a `docs/` directory.
- Changes to how the AI reviews code go in `.claude/agents/code-reviewer.md`, not in Python.
- `Validation` is QA's checklist: make every item provable by a test or a command.
- Ask every open question inside the plan, each with a recommended answer.

## Superseding a plan
Set the old plan to `Status: superseded` and link the replacing plan.
