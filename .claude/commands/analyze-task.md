---
description: Analyze a task from tasks.md and write a plan to .claude/plan.md (no code changes)
argument-hint: Task number (e.g. 3)
---

Read the file `.claude/tasks.md` and find the task with number $ARGUMENTS.

Then explore the codebase to fully understand the impact of this task: which models, views, forms, templates, URLs, and tests will be affected. Read all relevant files before planning.

Once you have a thorough understanding, write a structured implementation plan to `.claude/plan.md` in the project root.

The plan must follow this structure:

```
# Plan: [task title]

> Task $ARGUMENTS from tasks.md

## Summary
One paragraph describing what will be done and why.

## Affected files
List every file that needs to be created or modified, with a one-line reason for each.

## Implementation steps
Numbered steps in the exact order they should be applied.
Each step must include:
- The file to change
- What exactly to add, modify, or remove
- Any important constraints or edge cases to handle

## Tests
List of test cases to write or update.

## Open questions
Any ambiguities or decisions that need input before implementation.
```

**Important constraints:**
- Do NOT edit any source code files. Write only `.claude/plan.md`.
- Always overwrite `.claude/plan.md` completely, even if it already exists.
- If the user asks to change or refine the plan (without running this command again), edit `.claude/plan.md` in place — do not rewrite it from scratch.
- If the task number is not found in `tasks.md`, say so clearly.
- Be specific: reference actual class names, method names, and file paths from the codebase.