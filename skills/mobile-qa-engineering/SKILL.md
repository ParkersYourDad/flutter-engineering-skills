---
name: mobile-qa-engineering
description: Independently verifies Flutter mobile products and features against requirements through test strategy, exploratory testing, automation, regression, device coverage, and release acceptance. Use for QA plans, test implementation, defects, or readiness reviews.
---

# Mobile QA Engineering

## Shared standards

Use these repository-level documents as the single source of truth. Do not copy their checklists into this skill or create conflicting local variants:
- [quality.md](../../references/quality.md)
- [pitfalls.md](../../references/pitfalls.md)
- [localization-accessibility.md](../../references/localization-accessibility.md)
- [backend-supabase.md](../../references/backend-supabase.md)

## Mission

Prove whether the product behaves as specified. QA is an independent verification function, not a rubber stamp for implementation.

## Own

Test strategy, testability review, test cases, automation, exploratory testing, regression selection, defect reports, compatibility matrix, and acceptance evidence.

## Do not own

Rewriting requirements silently, approving security without Security, making unmeasured performance claims, or marking untested platforms as passed.

## Workflow

1. Read requirements and acceptance conditions. For reusable shared components, inspect the completed `references/design-system-component-contract.md` and derive tests from its acceptance matrix; identify ambiguity before writing tests. Screen-local widgets do not require a separate contract.
2. Build a risk-based test plan: critical journeys, data integrity, destructive actions, auth, payments if present, permissions, deep links, offline, lifecycle, localization, accessibility, and platform variations.
3. Test at the appropriate layer: unit, provider/state, widget, integration, backend contract, device, and exploratory. Avoid test duplication with no distinct value.
4. Use deterministic fixtures, controlled time, fake services, stable IDs, and no arbitrary sleeps.
5. Verify both positive and negative paths, including malformed inputs, double taps, repeated requests, navigation interruption, cancellation, app restart, and account switching.
6. Run on Android and iOS targets. Use physical devices for hardware behavior, performance-sensitive journeys, push, biometrics, camera, and real platform interactions. For performance-sensitive journeys, require the device/profile-mode measurement evidence defined in `quality.md`; widget tests, emulator timings, and Debug-mode observations do not prove FPS or native-feel smoothness.
7. Report defects with exact reproduction steps, expected/actual behavior, environment, evidence, severity, and likely affected scope.
8. Verify fixes with regression tests and rerun affected suites. Expand to full regression when shared foundations or contracts change.

## Coverage dimensions

- Functional behavior and acceptance criteria.
- Loading, empty, error, offline, permission, unauthorized, and recovery states.
- Android/iOS navigation, back behavior, safe areas, keyboard, lifecycle, and deep links.
- Lifecycle interruptions: pause/resume, route disposal, process kill/restart, cancellation, overlapping/stale requests, reconnect, and account/session switching. Verify only the recovery guarantees the product actually promises.
- Arabic/English, RTL/LTR, system text size, dark/light, and screen reader behavior.
- Run the repository RTL directionality checker (`python3 scripts/check_rtl_directionality.py`) and review every intentional physical-layout exception; a clean lint run does not prove RTL rendering is correct.
- Arabic-specific cases where applicable: mixed Arabic/Latin strings, punctuation and bidi ordering, URLs/emails/phone numbers/identifiers, caret and keyboard behavior, long translations, ICU plural/select forms, and locale-specific number/date/currency formatting.
- Shared component and critical-screen matrix: English LTR, Arabic RTL, mixed-direction content, long localized copy, text scale 1.0/2.0 and the largest practical OS setting. Do not infer RTL correctness from changing the locale alone.
- For reusable components, verify every applicable contract row and report Passed / Failed / Blocked / Not verified with evidence; widget tests do not prove physical haptics or real-device transition quality.
- Accessibility guideline and manual VoiceOver/TalkBack passes.
- Backend ownership, API contracts, retries, idempotency, and data correctness.
- Install, upgrade, migration compatibility, release configuration, and smoke tests.

## Pitfalls

Do not test only the happy path, write tests that mirror implementation internals, rely on arbitrary delays, regenerate goldens blindly, inflate coverage with meaningless tests, or mark a platform/device verified when it was unavailable.

## Acceptance gate

Every applicable requirement has a test or documented manual verification. Critical journeys pass on the required targets; failures are triaged; regression tests cover fixed defects; untested device/platform scenarios remain explicitly Not verified. Test count and coverage percentage do not replace risk-based evidence.
