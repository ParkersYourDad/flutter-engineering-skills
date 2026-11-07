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

Before any feature or shared code, answer in the plan (not in a new file): What exists already? What is intended behavior? Edge cases? Acceptance criteria? Platform differences? New dependencies (justify or drop)?

## Requirements and traceability

Give every requirement an ID (`FR-` functional, `NFR-` non-functional, `UX-`, `A11Y-`, `SEC-`, `PERF-`, `PLAT-`) and explicit out-of-scope list. While gathering, flag missing, conflicting, ambiguous, duplicate, unnecessary requirements, and unresolved assumptions. Resolve conflicts by proposing a recommendation, not silently choosing.

Traceability lives in one table that doubles as acceptance checklist:

| ID | Requirement | Acceptance condition (measurable) | Implementation | Test | Evidence | Status |
|---|---|---|---|---|---|---|

Statuses: Not Started, In Progress, Passed, Failed, Blocked, Not Applicable (with justification). Never mark Passed because code exists; Passed means the acceptance condition was observed. Evidence is a command + result, test name, screenshot path, or measurement.

Cross-cutting acceptance criteria every project inherits: gates in `quality.md`, state coverage in `design-system.md`, and checklists in `localization-accessibility.md`. Add IDs to the traceability table; do not copy all lists into it.

## Project docs (the only four)

Create under `docs/` at project start; keep short; never duplicate content between them or into code comments.

1. **`PROJECT.md`:** product summary, fixed constraints, supported OS versions, folder map, links to code-level conventions, current status. Starts from stack in `SKILL.md`; link to rules rather than restating them.
2. **`REQUIREMENTS.md`:** scope, out-of-scope, and traceability/acceptance table.
3. **`DECISIONS.md`:** dated one-paragraph ADRs (context, decision, consequences) for long-term-cost choices: dependencies, storage, auth, architecture deviations. Includes an Assumptions section; remove assumptions as confirmed.
4. **`ISSUES.md`:** known issues with ID, impact, workaround, status. Delete entries when fixed (regression test is permanent record).

README holds setup, run, and release commands only.

## Decision authority

- **Decide yourself:** technical libraries within stack after verification, folder placement, naming, patterns, token values, default UX behavior, test strategy, bug fixes.
- **Ask product owner:** features/scope, brand identity (name, accent, tone), monetization, personal data collected and why, legal/regulatory positions, store account details.
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
