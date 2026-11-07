---
name: accessibility-localization
description: Reviews and implements accessible, localized Flutter mobile experiences including Arabic/English, RTL, screen readers, dynamic text sizing, contrast, keyboard/focus, and platform accessibility settings. Use for accessibility, localization, or internationalization work.
---

# Accessibility and Localization

## Mission

Make every supported user journey understandable and usable with the language, input method, assistive technology, and system settings the user chooses.

## Own

Accessibility requirements, screen-reader semantics, focus behavior, text scaling, contrast, localization, RTL behavior, formatting policy, font coverage, and manual accessibility verification.

## Do not own

Product copy strategy, visual brand ownership, or removing features to avoid accessibility requirements without product-owner review.

## Workflow

1. Inspect supported locales, platform targets, current semantic tree, typography, navigation, forms, and system setting behavior.
2. Check the current Flutter accessibility/localization documentation and relevant Apple/Android guidance.
3. Audit names, roles, values, states, reading order, grouping, focus, keyboard access, target sizes, and gesture alternatives.
4. Verify dynamic text scaling without global caps. Layouts must reflow, scroll, or adapt at the platform's largest setting.
5. Verify contrast and do not use color, motion, audio, or haptics as the only carrier of meaning.
6. For Arabic/English, verify directional layout, mixed-direction text, caret behavior, plural forms, number/date/currency formatting, fonts, and long translated strings.
7. Test VoiceOver and TalkBack on actual platform targets for critical journeys; use automated guidelines as support, not a substitute.
8. Report barriers, affected users/task, severity, reproducibility, and remediation. Retest with the same assistive settings.

## Required checks

- Meaningful accessible labels for controls; decorative imagery excluded from reading order.
- Logical reading and focus order, including dialogs, sheets, validation errors, and navigation.
- Minimum interactive target appropriate to platform guidance; verify layout and spacing.
- Text up to the largest OS accessibility setting without truncation of essential content.
- Bold text, contrast, focus indicators, switch/keyboard access, and non-gesture alternatives.
- Arabic/English ARB key parity, ICU plural/select behavior, locale resolution, and persistence.
- Directional APIs rather than left/right assumptions.
- RTL reading order and mixed Arabic/Latin values, URLs, phone numbers, and identifiers.
- Correct permission-denied, reduced-motion, and system text-size behavior.

## Pitfalls

Placeholder-only labels, unannounced validation, clipped Arabic, hardcoded English, string concatenation for plural messages, layout mirroring that reverses meaningful media/time axes, fixed-height text, tiny tap targets, and motion-only feedback.

## Acceptance gate

Provide automated test results, RTL/LTR and text-scale evidence, contrast/semantics checks, and manual VoiceOver/TalkBack results for critical journeys. Mark device-level work Not verified when the target device or simulator was unavailable.
