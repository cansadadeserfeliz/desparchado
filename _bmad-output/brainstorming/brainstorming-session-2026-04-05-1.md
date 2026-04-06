---
stepsCompleted: [1, 2]
inputDocuments: []
session_topic: 'BMad configuration for the Desparchado project'
session_goals: 'Full BMad setup for the project'
selected_approach: 'user-selected'
techniques_used: ['SCAMPER Method']
ideas_generated: []
context_file: ''
---

# Brainstorming Session Results

**Facilitator:** Vera
**Date:** 2026-04-05

## Session Overview

**Topic:** BMad configuration for the Desparchado project
**Goals:** Full BMad setup for the project

### Session Setup

_Topic confirmed: full BMad workspace configuration tailored to Desparchado's Django/Vue.js cultural events platform stack, workflow, and team._

## Technique Selection

**Approach:** User-Selected Techniques
**Selected Techniques:**

- **SCAMPER Method**: Systematic seven-lens exploration; examines what a full BMad setup for Desparchado should look like by stress-testing standard config through Substitute, Combine, Adapt, Modify, Put to other uses, Eliminate, and Reverse lenses.

**Selection Rationale:** SCAMPER is ideal for methodically working through configuration decisions where there are many interdependent choices — modules, agents, outputs, workflows — and the goal is to ensure nothing is missed while finding the most tailored fit.

## Technique Execution Results

### SCAMPER Method

**S — Substitute**

**[S #1]**: Backend-Expert / Frontend-Guided Split
_Concept_: Configure BMad so backend work uses lean, fast workflows (Vera knows what she's doing), while frontend work uses more scaffolded, explanation-heavy workflows that give the "why" behind Vue 3 / TypeScript decisions, not just the "what."
_Novelty_: Most BMad setups treat all code the same. This one treats backend as "execute mode" and frontend as "guided learning + planning mode."

**[S #2]**: Frontend Structural Guide as Primary Frontend Role
_Concept_: Instead of a UX/design-focused frontend agent, Desparchado's BMad setup prioritizes a Vue 3 structural advisor — an agent that answers "given what I want to build, here's how to structure it in Vue 3 Composition API, where to put state, how to connect to Django APIs, and what patterns apply."
_Novelty_: Skips design ideation entirely and goes straight to implementation architecture — the gap that actually exists.

---

**C — Combine**

**[C #1]**: Full-Stack Linked Stories
_Concept_: Backend and frontend stories for the same feature are created together and cross-reference each other — the Django API spec and the Vue consumption pattern live in the same story file.
_Novelty_: Most BMad stories are single-discipline. This forces the two halves of a feature to stay in sync from planning through implementation.

**[C #2]**: Vue Component Deep-Dive Ideation Phase
_Concept_: Before any Vue story is written, there's a dedicated planning session that walks through the component's props, state, events, composables needed, and how it connects to the Django API.
_Novelty_: Treats a Vue component like a small system that deserves its own design pass, not just a task to execute.

**[C #3]**: JS/CSS vs. Vue Decision Gate ⭐ TOP PRIORITY
_Concept_: Every frontend task starts with a lightweight decision framework — is this complex enough to need Vue reactivity, state, and lifecycle? Or does vanilla JS + CSS handle it in fewer lines?
_Novelty_: Prevents both over-engineering (Vue for a toggle) and under-engineering (vanilla JS for a complex form with API state).

**[C #4]**: Test-Embedded Stories
_Concept_: Every Desparchado story spec includes a dedicated test planning section — pytest test case names, required factory-boy fixtures, and for frontend tasks, which behaviors need coverage vs. which are acceptable to skip.
_Novelty_: Testing is planned at story creation time, not retrofitted after implementation.

---

**A — Adapt**

**[A #1]**: Tiered Quality Gate by Feature Type
_Concept_: BMad stories carry one of two quality tiers. User-facing tier: strict security review, full corner-case coverage, permission checks mandatory. Admin/scraper tier: relaxed coverage, manual supervision assumed.
_Novelty_: Instead of one quality bar for everything, the story template self-selects its rigor level based on which app it lives in.

**[A #2]**: Permission Model as Story Scaffolding
_Concept_: Every story that touches data creation or editing automatically includes the Desparchado permission matrix: public read → authenticated create → creator/editors/admins edit/delete.
_Novelty_: The permission model isn't something you remember to test — it's baked into the story template as non-negotiable acceptance criteria.

**[A #3]**: Factory-First Test Spec
_Concept_: Test planning in stories always starts from the factory layer. `Model.objects.create()` is treated as a lint violation in story specs, not just in code.
_Novelty_: Enforces factory discipline at planning time, not code review time.

**[A #4]**: CBV-Aware Story Templates
_Concept_: Backend story specs assume Class-Based Views and frame implementation steps accordingly — which mixin, which `get_queryset` override, which `form_valid` hook.
_Novelty_: BMad stories match Desparchado's architectural language so generated guidance doesn't need mental translation.

**[A #5]**: Dashboard = Internal, Everything Else = User-Facing
_Concept_: `dashboard/` app → internal tier (relaxed coverage, admin-supervised). All other apps → user-facing tier (strict security, full corner-case coverage).
_Novelty_: Zero judgement calls at story time. The app directory is the single source of truth for quality tier.

---

**M — Modify**

**[M #1]**: Three-Speed Workflow Model
_Concept_: Desparchado BMad operates in three modes. Full ceremony (significant features): Brief → PRD → UX → Architecture → Epics → Stories → Dev → Review. Tech-only (small features): Architecture → Story → Dev → Review. Quick Dev (bugs): single session, no ceremony.
_Novelty_: The workflow entry point is a deliberate choice, not a default. Every session starts by asking "which mode?" before anything is generated.

**[M #2]**: Scale Up — Vue Component Planning as Deep Phase
_Concept_: For any story involving a new Vue component, there's an expanded planning sub-phase: component props/emits contract, composables needed, API endpoints consumed, reactive state map, JS/CSS vs Vue gate, acceptance criteria framed as user interactions.
_Novelty_: Vue component planning gets the same depth as a backend architecture doc.

**[M #3]**: Scale Down — No Standalone UX Phase for Small Features
_Concept_: UX design as a separate phase only applies to significant features. For small features, UX considerations are folded into the story spec itself.
_Novelty_: Eliminates overhead for features where the UX is already obvious from context.

---

**P — Put to Other Uses**

**[P #1]**: Single Source of Truth — CLAUDE + BMad + MkDocs
_Concept_: docs/ serves Claude Code, BMad agents, and MkDocs simultaneously. One edit, three consumers. BMad's `project_knowledge` config points to docs/.
_Novelty_: Eliminates drift between what Claude knows, what BMad knows, and what the team documents.

**[P #2]**: Distillator for Agent Context Management
_Concept_: As docs grow, run the Distillator periodically to produce lean, token-efficient summaries that agents load instead of full raw files.
_Novelty_: Prevents context bloat from degrading agent quality over time — a maintenance workflow, not just a one-time setup.

**[P #3]**: Adversarial Review on Story Specs Pre-Implementation
_Concept_: Before handing a story to the dev agent, run Adversarial Review on the story spec itself — hunting for permission model gaps, missing test cases, and ambiguous acceptance criteria.
_Novelty_: Adversarial Review normally runs on code diffs. Applied to story specs, it becomes a pre-implementation quality gate.

**[P #4]**: TEA Audit on Existing Test Suite
_Concept_: Run TEA's Test Review skill against Desparchado's current pytest suite to score it (0–100) and surface coverage gaps, antipatterns, and missing factory usage.
_Novelty_: TEA applied to an existing suite becomes a diagnostic tool, not just a new-project scaffold.

---

**E — Eliminate**

**[E #1]**: Eliminate Commercial Phases Entirely
_Concept_: Market research, competitor analysis, and business model workflows removed. The product brief phase is simplified to a mission-alignment check: "does this feature serve people looking for cultural events in Colombia?"
_Novelty_: Replaces commercial framing with a single non-profit value question as the only product filter.

**[E #2]**: Eliminate Multi-Human Team Workflows
_Concept_: All BMad workflows configured for one human operator by default. No handoff ceremonies, stakeholder review gates, or approval chains.
_Novelty_: Removes team coordination overhead entirely — PM, architect, and dev roles all collapse into Vera.

**[E #3]**: Eliminate Async/Periodic Infrastructure Assumptions
_Concept_: No BMad story or architecture template suggests Celery, queues, cron jobs, or background workers. If a feature needs background processing, the story flags it as out of scope and proposes a synchronous alternative first.
_Novelty_: Prevents over-engineering suggestions that would require server capacity Desparchado doesn't have.

**[E #4]**: Static Frontend as Architectural Constraint
_Concept_: All frontend stories assume the output is compiled static files served by Nginx. No SSR, no separate frontend server, no Node.js in production.
_Novelty_: Makes the Vite static build constraint a first-class story requirement, not an afterthought.

**[E #5]**: Eliminate Stakeholder Documentation
_Concept_: No presentation decks, executive summaries, or stakeholder-facing reports. Every artifact has exactly one audience: the developer(s).
_Novelty_: Every BMad artifact is dev-reference or user-facing, nothing in between.

**[E #6]**: Minimal Tool Footprint
_Concept_: BMad configuration prioritizes built-in Django/Python tooling over third-party services. Cost-awareness is a first-class constraint in every story recommendation.
_Novelty_: No paid APIs or external services suggested without explicit flagging.

---

**R — Reverse**

**[R #1]**: Documentation as the Primary Onboarding Agent
_Concept_: BMad's project_knowledge folder (the unified docs/ tree) is designed first for contributor onboarding — a new developer should be able to read it and understand Desparchado's architecture, conventions, and goals without any human explanation.
_Novelty_: Inverts the usual relationship where docs are a byproduct of development. Here, docs are the entry point for both humans and AI agents.

**[R #2]**: Dual-Audience, Dual-Location Documentation ⭐ TOP PRIORITY
_Concept_: Two separate documentation surfaces for two separate audiences. `/docs` (MkDocs, Spanish): user-facing — how to add events, permissions, troubleshooting, for Colombian event organizers who only speak Spanish. Standard open source files (English): developer-facing — README.md, CONTRIBUTING.md, ARCHITECTURE.md, following open source conventions so contributors find them intuitively.
_Novelty_: Matches audience language to the right tool. MkDocs renders the Spanish user site. README/CONTRIBUTING follow the open source standard developers expect. BMad's project_knowledge points to the English dev files, not docs/.

**[R #3]**: Post-Hoc Story Docs for Scrapers and One-Off Commands
_Concept_: For management commands and scrapers, implementation comes first. BMad then reads the finished command and generates the story doc, test plan, and usage notes retroactively.
_Novelty_: Replaces "write spec then implement" with "implement then document" for admin-tier features where the implementation is the spec.

---

## Idea Organization and Prioritization

### Thematic Organization

| Theme | Ideas | Core Insight |
|---|---|---|
| Three-Speed Workflow Engine | M#1, E#1, E#2, E#5 | Match ceremony to work type |
| Frontend Guidance System | S#1, S#2, C#2, C#3, M#2, M#3 | Close the Vue 3 structural gap |
| Story Design Conventions | C#1, C#4, A#1-A#5 | Make every story Desparchado-shaped |
| Documentation as Living Brain | P#1, R#1, R#2, P#2 | One source of truth, two audiences |
| Infrastructure & Cost Constraints | E#3, E#4, E#6 | Hard constraints in every suggestion |
| Quality & Retrospective Workflows | P#3, P#4, R#3 | Repurpose tools for existing codebase |

### Top Priority Ideas

**Priority 1 — [C #3] JS/CSS vs. Vue Decision Gate**
The most immediately actionable idea. Prevents a whole class of architectural mistakes at the earliest possible moment. Teachable and transferable to the frontend collaborator.

**Priority 2 — [R #2] Dual-Audience docs/ Structure**
The highest-leverage long-term investment. Solves contributor onboarding and user self-service simultaneously. Foundation for BMad's project_knowledge context.

### Action Plans

#### Action Plan 1: JS/CSS vs. Vue Decision Gate [C #3]

**Decision Framework:**
```
1. Does it need to react to user input without a page reload?      → Yes → Vue
2. Does it need to call a Django API and render the response?       → Yes → Vue
3. Does it manage state that changes during a session?             → Yes → Vue
4. Is it a one-time interaction (toggle, show/hide, form submit)?  → No  → Vanilla JS
5. Is it purely presentational with no dynamic data?               → No  → CSS only
```

**Next Steps:**
1. Write decision gate as `docs/contributing/frontend-decision-gate.md`
2. Add as required section in BMad frontend story templates
3. Reference in frontend-expert agent definition

**Success Indicators:** Frontend collaborator makes JS vs. Vue call independently. Story specs never leave approach undefined.

#### Action Plan 2: Dual-Audience, Dual-Location Documentation [R #2]

**Two surfaces, two audiences, two languages:**

```
# Developer docs — English, open source convention
README.md                        # Project overview, quick start, stack
CONTRIBUTING.md                  # How to contribute, local setup, PR process
ARCHITECTURE.md                  # Apps, entities, URL structure, key patterns
docs-dev/
├── conventions.md               # CBV, factories, code style, type hints
├── permissions.md               # can_edit(), SuperuserRequiredMixin, quota system
├── testing.md                   # pytest, factory-boy, django_app conventions
├── frontend-decision-gate.md    # JS/CSS vs Vue framework
└── scraper-guide.md             # source_id, deduplication, dashboard tier

# User docs — Spanish, MkDocs site
docs/                            # existing MkDocs project
├── index.md                     # Qué es Desparchado
├── agregar-eventos.md           # Cómo agregar y publicar eventos
├── permisos.md                  # Qué puedes editar, quién aprueba
├── solucion-de-problemas.md     # ¿Por qué no aparece mi evento?
└── reportar-problemas.md        # Cómo reportar errores o pedir ayuda
```

**Next Steps:**
1. Audit existing `docs/` — move any developer content out, keep user-facing content in Spanish
2. Write `docs/solucion-de-problemas.md` first — highest user impact ("why isn't my event showing?")
3. Create or update `README.md` and `CONTRIBUTING.md` following open source conventions
4. Write `ARCHITECTURE.md` porting relevant sections from `CLAUDE.md`
5. Point BMad `project_knowledge` config to the English dev files (README, ARCHITECTURE, docs-dev/)

**Success Indicators:** New contributor finds setup instructions in README without asking. Event organizer in Colombia resolves a visibility issue in Spanish, independently.

## Session Summary and Insights

**Total Ideas Generated:** 27 across 7 SCAMPER lenses
**Themes Identified:** 6
**Top Priorities:** 2 (C#3, R#2)

**Key Achievements:**
- Defined a three-speed workflow model tailored to solo open-source development
- Identified the precise frontend gap (structural guidance, not UX design)
- Created a complete quality-tier system based on app location (dashboard vs. everything else)
- Designed a dual-audience documentation architecture serving contributors and event organizers
- Established hard infrastructure constraints (no async, static frontend, minimal tooling) as first-class story requirements

**Breakthrough Moments:**
- The `dashboard/` = internal rule: a single directory boundary replaces all quality-tier judgment calls
- docs/ as the single source of truth for Claude, BMad, and MkDocs simultaneously
- Post-hoc story docs for scrapers — implementation as spec for admin-tier features

**Next BMad Steps:**
1. Run `bmad-generate-project-context` to create a lean `project-context.md` from the existing codebase
2. Audit and restructure `docs/` into the dual-audience structure
3. Write `docs/contributing/frontend-decision-gate.md`
4. Configure BMad `project_knowledge` to point to `docs/contributing/`
5. Run `bmad-create-story` on a small feature to validate the story template conventions captured here