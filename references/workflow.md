# Workflow, Project Memory and Reporting

## Contents
- Task sizing
- Requirements and traceability
- Project docs
- Decision authority
- Reporting format
- Environment limits
- Learning loop

## Task sizing

Match ceremony to risk. A one-line fix needs only the relevant inspect/implement/verify/report steps. A new feature or shared component needs the full workflow. A new project or shared foundation also needs an ADR first.

Before any feature or shared code, answer in the plan (not in a new file): What exists already? For an existing app, classify its current architecture, SDK/toolchain, state management, routing, backend, dependencies, code generation, tests, CI, and release setup as healthy, debt, unsupported, or blocking; state what must be preserved and what evidence justifies a change. What is intended behavior? Edge cases? Acceptance criteria? Platform differences? Backend data ownership and authorization? RLS impact? Migration/rollback? New dependencies (justify or drop)? For Gemini/AI features: data sent to the provider, user consent, quota/cost limits, abuse controls, and failure behavior?

## Requirements and traceability

Give every requirement an ID (`FR-` functional, `NFR-` non-functional, `UX-`, `A11Y-`, `SEC-`, `PERF-`, `PLAT-`) and explicit out-of-scope list. While gathering, flag missing, conflicting, ambiguous, duplicate, unnecessary requirements, and unresolved assumptions. Resolve conflicts by proposing a recommendation, not silently choosing.

Traceability lives in one table that doubles as acceptance checklist:

| ID | Requirement | Acceptance condition (measurable) | Implementation | Test | Evidence | Status |
|---|---|---|---|---|---|---|

Statuses: Not Started, In Progress, Passed, Failed, Blocked, Not Applicable (with justification). Never mark Passed because code exists; Passed means the acceptance condition was observed. Evidence is a command + result, test name, screenshot path, or measurement.

Cross-cutting acceptance criteria every project inherits: gates in `quality.md`, state coverage in `design-system.md`, backend controls in `backend-supabase.md`, and checklists in `localization-accessibility.md`. Add IDs to the traceability table; do not copy all lists into it.

## Project docs (the only four)

Create under `docs/` at project start; keep short; never duplicate content between them or into code comments. For an existing project, inspect and update its current documents rather than replacing them with a new template.

1. **`PROJECT.md`:** product summary, fixed constraints, supported OS versions, folder map, links to code-level conventions, current status, Supabase project/environment identifiers (never secret values), enabled services, migration/deployment status, and Edge Function inventory.
2. **`REQUIREMENTS.md`:** scope, out-of-scope, and traceability/acceptance table, including backend data access, RLS, retention, and AI usage requirements when applicable.
3. **`DECISIONS.md`:** dated one-paragraph ADRs (context, decision, consequences) for long-term-cost choices: dependencies, Supabase service choices, data ownership/RLS model, Gemini data handling and cost controls, storage, auth, architecture deviations. Includes an Assumptions section; remove assumptions as confirmed.
4. **`ISSUES.md`:** known issues with ID, impact, workaround, status. Delete entries when fixed (regression test is permanent record).

In the generated Flutter application, keep its README focused on setup, run, and release commands; the skill repository's README may describe the skill and link its references.

## Decision authority

- **Decide yourself:** technical libraries within stack after verification, folder placement, naming, patterns, token values, default UX behavior, test strategy, bug fixes, and routine Supabase implementation details within approved security rules.
- **Ask product owner:** features/scope, brand identity (name, accent, tone), monetization, personal data collected and why, whether prompts/user content may be sent to Gemini and retained, legal/regulatory positions, store account details.
- **Needs explicit authorization:** see `SKILL.md` operating rules.
- **Cannot do here:** actions unavailable to tools (building iOS on Linux, physical-device testing, store consoles). Say so; never imply completed.

## Reporting format

End every meaningful task with:

- **Changed:** files and what changed, briefly.
- **Verified:** each command/test/check with observed result.
- **Not verified / blocked:** what and why (tool unavailable, no device, no network).
- **Assumptions and decisions:** new entries added to `DECISIONS.md`.
- **Next:** only if genuinely outstanding or user input is required.

Use labels precisely: Verified, Partially verified, Not verified, Failed, Blocked, N/A. No percentages standing in for failed checks.

## Environment limits

State capabilities up front when relevant: Flutter SDK present? Emulator/simulator? Physical device? Network access? macOS/Xcode? Without a toolchain, code can still be written and statically reasoned about, but every runtime claim (builds, tests, layout, performance) is not verified. Provide exact commands for user/CI. If preferred verification is unavailable, give best alternative (e.g. widget tests and goldens instead of device check) and say it is weaker.

## Learning loop

When a new bug, compatibility break, or recurring mistake appears:

1. Find root cause.
2. Ask whether existing guidance would have prevented it.
3. If not, add or amend one entry in `pitfalls.md` or one checklist line in the relevant reference.
4. Do not add a second rule for something already covered; edit existing rule.
5. Delete rules that proved wrong or obsolete.

Upgrade hygiene (SDK, packages, platform targets) belongs in `quality.md`, "Dependencies and upgrades".
