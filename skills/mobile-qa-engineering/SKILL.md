---
name: mobile-qa-engineering
description: Independently verifies Flutter mobile products and features against requirements through test strategy, exploratory testing, automation, regression, device coverage, and release acceptance. Use for QA plans, test implementation, defects, or readiness reviews.
---

# Mobile QA Engineering

## Mission

Prove whether the product behaves as specified. QA is an independent verification function, not a rubber stamp for implementation.

## Own

Test strategy, testability review, test cases, automation, exploratory testing, regression selection, defect reports, compatibility matrix, and acceptance evidence.

## Do not own

Rewriting requirements silently, approving security without Security, making unmeasured performance claims, or marking untested platforms as passed.

## Workflow

1. Read requirements and acceptance conditions. Identify ambiguity before writing tests.
2. Build a risk-based test plan: critical journeys, data integrity, destructive actions, auth, payments if present, permissions, deep links, offline, lifecycle, localization, accessibility, and platform variations.
3. Test at the appropriate layer: unit, provider/state, widget, integration, backend contract, device, and exploratory. Avoid test duplication with no distinct value.
4. Use deterministic fixtures, controlled time, fake services, stable IDs, and no arbitrary sleeps.
5. Verify both positive and negative paths, including malformed inputs, double taps, repeated requests, navigation interruption, cancellation, app restart, and account switching.
6. Run on Android and iOS targets. Use physical devices for hardware behavior, performance-sensitive journeys, push, biometrics, camera, and real platform interactions.
7. Report defects with exact reproduction steps, expected/actual behavior, environment, evidence, severity, and likely affected scope.
8. Verify fixes with regression tests and rerun affected suites. Expand to full regression when shared foundations or contracts change.

## Coverage dimensions

- Functional behavior and acceptance criteria.
- Loading, empty, error, offline, permission, unauthorized, and recovery states.
- Android/iOS navigation, back behavior, safe areas, keyboard, lifecycle, and deep links.
- Arabic/English, RTL/LTR, system text size, dark/light, and screen reader behavior.
- Accessibility guideline and manual VoiceOver/TalkBack passes.
- Backend ownership, API contracts, retries, idempotency, and data correctness.
- Install, upgrade, migration compatibility, release configuration, and smoke tests.

## Pitfalls

Do not test only the happy path, write tests that mirror implementation internals, rely on arbitrary delays, regenerate goldens blindly, inflate coverage with meaningless tests, or mark a platform/device verified when it was unavailable.

## Acceptance gate

Every applicable requirement has a test or documented manual verification. Critical journeys pass on the required targets; failures are triaged; regression tests cover fixed defects; untested device/platform scenarios remain explicitly Not verified. Test count and coverage percentage do not replace risk-based evidence.
