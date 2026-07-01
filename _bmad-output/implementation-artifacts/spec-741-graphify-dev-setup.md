---
title: 'Set up Graphify as a local-only dev tool'
type: 'chore'
created: '2026-06-30'
status: 'in-progress'
baseline_commit: '7df2704e45d402dbd07719393460197377fbe423'
context: []
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Graphify (a knowledge-graph tool for AI coding assistants) is already installed in the local venv but has no gitignore entry for its output directory and no documentation in `CLAUDE.md`, making it invisible to other contributors and risking accidental commits of generated files.

**Approach:** Add `graphify-out/` to `.gitignore` and add a concise documentation block to `CLAUDE.md` (outside the Docker commands section) that clarifies graphify is a local-only tool — not a Docker dependency — with correct install and usage instructions.

## Boundaries & Constraints

**Always:**
- `graphify-out/` must be gitignored so generated graph files (HTML, JSON, GRAPH_REPORT.md) are never committed.
- Graphify docs must live **outside** the "All commands run inside the Docker container" block in `CLAUDE.md` to avoid contradicting that header.
- Install instruction must use `venv/bin/pip install graphifyy` (explicit path, no venv activation required) and note the double-y package name vs single-y CLI name.
- The note must warn against adding `graphifyy` to `requirements-dev.in` or `requirements.in` (Docker uses `--require-hashes`; adding it there would break the Docker install).

**Ask First:**
- If any other output directories produced by graphify (e.g. `graphify-out/obsidian/`) need special gitignore handling beyond `graphify-out/`.

**Never:**
- Add `graphifyy` to `requirements.in`, `requirements-dev.in`, or any compiled requirements file — this is a local AI tool, not a server-side dependency.
- Use `/graphify .` in shell examples — the leading slash makes it an absolute filesystem path, which is invalid. Use `graphify .` (assumes venv activated) or `venv/bin/graphify .` (explicit path).
- Document the graphify Claude Code skill install steps — those are user-level and already configured at `~/.claude/skills/graphify/`.

</frozen-after-approval>

## Code Map

- `.gitignore` — needs `graphify-out/` entry; currently absent
- `CLAUDE.md` — needs a new "Local dev tools" section after the existing Commands block

## Tasks & Acceptance

**Execution:**
- [ ] `.gitignore` -- add `graphify-out/` entry with a one-line comment -- prevents generated graph files from being staged accidentally
- [ ] `CLAUDE.md` -- add a "Local dev tools" subsection after the Docker commands block -- documents graphify install, usage, and the constraint to keep it out of requirements files

**Acceptance Criteria:**
- Given a developer runs `graphify .` from the project root, when they run `git status`, then `graphify-out/` does not appear as an untracked path.
- Given a developer reads `CLAUDE.md`, when they reach the Commands section, then the graphify block is visually separate from the Docker commands intro and clearly labeled as local-only.
- Given a developer reads the graphify install instruction, when they attempt to install, then the command (`venv/bin/pip install graphifyy`) works without venv activation and the double-y naming quirk is explained inline.
- Given a developer reads the graphify docs, when they see the requirements note, then it is explicit that `graphifyy` must not be added to any requirements file.

## Design Notes

Graphify outputs land in `graphify-out/` at whatever directory it is run from. Anchoring the pattern as `/graphify-out/` (leading slash) would restrict it to the project root — which is the intended location — and is more precise than the unanchored form. Use the anchored form.

## Verification

**Manual checks (if no CLI):**
- After applying: `git status` shows a clean working tree (only `.gitignore` and `CLAUDE.md` changed).
- Create `graphify-out/test.txt`, run `git status` — confirm `graphify-out/` does not appear.
- Read `CLAUDE.md` — confirm graphify block follows the Docker commands block and precedes `## Architecture`.