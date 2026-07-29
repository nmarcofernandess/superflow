# Analyst Protocol

Use Analyst to turn a loose request, weak issue, or scary code area into
PRD-quality understanding. Analyst is not a summary writer. Analyst is domain
distillation plus grounded reconnaissance plus a handoff that Build can execute
without guessing.

## Mission

Produce an `analysis.md` that proves the product promise, system terrain,
entities, state transitions, rules, risks, and next phase — under
**feature-mindset-contract.md**: facetas Produto / Backend / Frontend / Copy,
síntese coerente, recodificação retroativa (não waterfall).

If the target touches an existing codebase, the analysis must include
source-backed evidence and an implementation map.

## Golden Lineage

This protocol merges:

- Supervibe / Code Flow Analyst discipline (grill, evidence, entities, handoff).
- DietFlow triad + reuso (portable: search-before-create, data path first).
- Strings-safadas (invariant prose only; data in structure).
- Faceted analysis (Colon-style): analyze facets → synthesize → recode the set
  when a new isolate breaks a category. One sentence of theory is enough.

Do not collapse this into a short PRD. Thin analysis that only fills headings
is a failed analysis (B1).

## Non-Negotiables

- Durable artifact: `analysis.md` or issue body.
- No `TBD` as a central decision — ask one precise question or record assumption
  with risk.
- Mermaid only for diagrams.
- Every code/system claim: `path:line` or `UNPROVEN` (T1, B5).
- Backend claims include **payload/shape** the UI receives when UI is in scope
  (T2).
- Before `new` UI/action: **Reuse Guard** (`reuse-guard-protocol.md`) with
  evidence — graph Tier-2 if fresh, else grep (T4–T6). Plugin **searches**; it
  does not prescribe a universal shell name.
- Copy inventory when UI/copy is in scope; apply strings-safadas (S1–S5).
- **Síntese** paragraph binds facets (F4). Paste of three sections = fail.
- **Recode Log** present; deep work needs honest recode or coherence proof;
  docs-only may use skip_reason (F5–F6, B3).
- Blueprint handoff lists testable **behaviors** without fake test commands
  (D1–D2).
- Grill before `ready for build` or `ready for taskgen`.

## Phase 0 - Native Grill

Score the input before writing. Each missing item is one point of ambiguity:

| Signal | Question |
|---|---|
| Action | What action/result is desired? |
| Persona | Who uses or suffers from this? |
| Input/output | What enters, what changes, what is emitted? |
| Scope | What is in and out? |
| Objective criteria | Have vague words become measurable behavior? |

Rules:

- 0-1 ambiguity points: proceed.
- 2-3: ask one precise question unless repo evidence can answer.
- 4-5: at most three surgical questions, then assumptions if user wants motion.

## Phase 1 - Mode And Scope

Classify: `construction` | `extraction` | `audit` | `hybrid` | `investigation`.

Investigation owns bugs without proven cause: reproduce, read logs/tests/code
until proven or `UNPROVEN`; no separate Discovery phase.

Record source, route, phase budget, expected next phase, whether Build follows.

## Phase 2 - Faceted recon (loop)

Use `code-recon-protocol.md`. Attention order often Product → Backend →
Frontend → Copy, but **do not freeze** a facet when later evidence contradicts
it — log a recode and rewrite the set (F3, F6).

Minimum for existing code:

1. Entry/context (and repo maps if present — T7).
2. Backend: schema, actions, **payload to UI**, guards, hooks.
3. Frontend: shells/primitives — **grep family before inventing**.
4. Copy surfaces: toast/empty/modal/banner candidates.
5. Tests/proofs and ops constraints.

Explorer subagents may help; final `analysis.md` cites files itself.

## Phase 3 - Analyze facets

Write all four facets (or proportional skips with reason):

- **Produto** — promise, surface, non-goals (T3 if data missing).
- **Backend** — evidence table path:line / UNPROVEN + payload.
- **Frontend** — reuse|mode|new table with scan evidence.
- **Copy** — inventory + invariante|estrutura|morte.

## Phase 4 - Synthesize

Write **Síntese**: one hard paragraph that binds the facets. If any facet can
be deleted without breaking the paragraph, rewrite (F4, H1).

## Phase 5 - Recode

When evidence changes a category, update prior facets and append **Recode Log**:

| When | Trigger | Facet | Recode |
|---|---|---|---|

Deep/existing-code: at least one real recode if synthesis moved, or explicit
note that initial synthesis already matched terrain.  
Docs-only: `skip_reason` allowed (B3).  
Fake “N/A” in deep = fail.

## Phase 6 - Entities, State, Rules

Same entity template as before; dumb-machine rules; edge cases.

## Phase 7 - Implementation Map

Context → backend → services/hooks → shells → frontend → tests.  
Each row: path, role, evidence, decision reuse/mode/new/legacy/unknown.

## Phase 8 - Blueprint Handoff

Product/Backend/Frontend/Copy contracts summary; files; sequence; validation;
risks; **testable behavior names** only (no fake commands).

## Phase 9 - Visual Model

Mermaid only when it reduces ambiguity.

## Phase 10 - Grill Verdict

Self-review:

- Facets coherent under Synthesis?
- Evidence for technical claims?
- Recode Log honest for this depth?
- Strings-safadas applied?
- Ready ≠ filled headings?
- One slice or split?

Allowed verdicts:

- `ready for taskgen`;
- `ready for build`;
- `needs recon`;
- `needs human decision`;
- `split required`;
- `capture only`;
- `blocked: insufficient evidence`.

## Required `analysis.md` Shape

Use `assets/templates/analysis.md` headings. Mandatory for existing-system UI
work:

- TL;DR + **Síntese** near top (H1)
- Faceta Produto / Backend / Frontend / Copy
- Recode Log
- Evidence Matrix + Implementation Map
- Story de Usuario + Story Tecnica
- Blueprint Handoff + Grill Verdict

## Ready Gate (binary)

Do **not** declare ready for taskgen/build if:

- Synthesis missing or is section-collage;
- technical claim without path:line or UNPROVEN;
- `new` UI without reuse scan;
- Copy still carries instance prose as approved system text;
- deep package with empty Recode Log and no coherence proof;
- product promise requires data Backend marked UNPROVEN without non-goal;
- blueprint handoff invents TDD commands;
- only achievement is “all headings present” (B1–B2).
