# Localization, RTL and Accessibility

## Contents
- Localization rules
- Formatting
- RTL layout rules
- Accessibility rules
- Localization and RTL checklist
- Accessibility checklist

## Localization rules

- Official infrastructure: `flutter_localizations`, `intl`, ARB files, and `flutter gen-l10n` driven by `l10n.yaml`. Check current Flutter i18n docs for output location and generated-file handling. Decide once whether generated output is committed; CI must not depend on an unrun generator.
- Supported locales: `en`, `ar`. English is the template ARB with a `@key` description for every entry (context for translators and future locales).
- **Resolution order:** saved user choice → device locale if supported (match by language) → English. "System" remains a selectable option distinct from an explicit choice. Persist the choice; apply before first frame; changing language updates immediately without restart and updates `Directionality`.
- No user-facing literal strings in features, including semantic labels, tooltips, validation messages, notifications, and error text. Use ICU `plural`/`select`; never concatenate fragments to build sentences (word order differs). Arabic has six plural categories (zero, one, two, few, many, other); supply the categories the message needs.
- Server-provided text is localized by the server or mapped from error codes client-side.
- Placeholders in ARB must declare types (`int`, `DateTime`, `double` with format).

## Formatting

Use `intl` with active locale for dates, times, numbers, percentages, currency, and relative time; never hand-format. Ask the product owner once and record decisions for Arabic-Indic vs Western digits, calendar system (Gregorian vs Hijri display), first day of week, currency symbol placement, and 12/24-hour time. Keep numeric/ID/LTR tokens (phone numbers, emails, URLs, codes) correctly ordered inside RTL text (use `Directionality`/Unicode isolates where mixed-direction text is displayed).

## RTL layout rules

- Use directional APIs only: `EdgeInsetsDirectional`, `AlignmentDirectional`, `BorderRadiusDirectional`, `PositionedDirectional`, `start`/`end`, `TextAlign.start`. Never `left`/`right` unless physically meaningful (e.g. a physical drag handle).
- **Automated enforcement:** vendor `scripts/check_rtl_directionality.py` from this skills repository into the consuming app's `scripts/` directory, then run `python3 scripts/check_rtl_directionality.py --root .` in the app's CI. It flags common physical layout APIs (for example `EdgeInsets.only(left/right:)`, physical `Alignment` corners/edges, `BorderRadius.only(topLeft/topRight/bottomLeft/bottomRight:)`, `Positioned(left/right:)`, and `TextAlign.left/right`). Fix with the corresponding directional API. For a genuinely physical control or coordinate, add a same-line exception comment: `// rtl-lint: ignore -- <why this must remain physical>`. The exception must be specific; do not suppress a whole file or directory. The checker is a targeted guard, not proof that every custom layout is RTL-correct; retain RTL widget/golden tests and review custom geometry.
- Mirror navigation affordances (back, chevrons, progress direction), swipe-action sides, slider direction, list leading/trailing, and drawer side. Do not mirror media controls, clocks, logos, numerals, or charts' time axis unless locale convention says so.
- Text fields: caret, hint alignment, and mixed Arabic/Latin input behave correctly; keyboard type fits content.
- Test every screen and component under `Directionality(rtl)` with Arabic strings longer than English.
- Fonts: verify Arabic glyph coverage and diacritics rendering; test line-height clipping. Tune Arabic line-height and font metrics from rendered-script inspection rather than copying Latin values: check ascenders/descenders, tashkeel, baseline alignment, clipping, mixed Arabic/Latin fallback, and multi-line wrapping across actual target fonts and OS versions. Avoid letter-spacing on connected Arabic text unless the chosen typeface and visual review explicitly justify it; do not globally inflate line-height without checking density and alignment.
- Mirror only icons whose meaning is directional in the current context (back/forward, previous/next, logical progression). Do not mirror universal symbols, media timelines, charts, clocks, physical gestures, or icons whose meaning is not direction-dependent. Verify each icon in both locales; `matchTextDirection` is a behavior choice, not a blanket RTL switch.

## Accessibility rules

- Every interactive element has an accessible name, role, and state through `Semantics` (SDK widgets provide some; custom Pressable-based widgets must supply them). Decorative images are excluded; informative images have localized labels. Group related content (`MergeSemantics`) so it reads as one item; reading order follows visual order in LTR and RTL.
- Touch targets ≥48 dp with adequate spacing; enlarge hit area without enlarging visuals.
- Text scaling: layouts reflow (wrap, scroll, stack) up to the largest system setting; no fixed-height text containers. Verify at 2.0× and with bold text.
- Contrast: see `design-system.md`. Never convey meaning by color alone; add icon/text.
- Focus: logical order, visible focus indicator for external keyboards/switch control, focus moved to first error on failed submit, focus restored after dialogs/sheets close.
- Dynamic announcements: use `SemanticsService` for async results (loaded, saved, error) only where visual change is not otherwise announced.
- Forms: visible labels (not placeholder-only), errors tied to fields and announced, instructions before input, no timeouts without notice.
- Motion: honor reduced motion (see `design-system.md`). No flashing content.
- Follow Android accessibility guidance (TalkBack, Switch Access) and Apple HIG/accessibility (VoiceOver, Dynamic Type, Reduce Motion, Bold Text).

## Checklist: localization and RTL

- [M] Zero hardcoded strings in `lib/features` and `lib/design_system`. Verify with grep/review and tests pumping screens in `ar` and `en` with no missing keys.
- [M] Every ARB key exists in both languages with identical placeholders. Verify with a test/script comparing key sets and placeholder metadata.
- [M] Locale resolution/persistence works: first launch (system), explicit choice, relaunch. Verify with widget/integration tests and mocked prefs.
- [M] No left/right layout assumptions. Verify by searching for non-directional APIs in features and reviewing RTL goldens.
- [M] Dates, numbers, currency via `intl`. Verify with searches for manual formatting and per-locale tests.
- [M] Plurals and gendered text use ICU messages. Verify counts 0, 1, 2, 3, 11, 100 where applicable.
- [M] Every screen verified in RTL + dark + large text. Verify golden/screenshot matrix (see `quality.md`).
- [C] Mixed-direction content (names, URLs, codes) displays correctly when such content exists.
- [R] Run a pseudo-locale/long-string pass to surface overflow before translation.

## Checklist: accessibility

- [M] Every tappable element has a name, role, and ≥48 dp target. Verify `meetsGuideline(androidTapTargetGuideline)`, `iOSTapTargetGuideline`, and `labeledTapTargetGuideline` in widget tests where supported.
- [M] Text/UI contrast meets AA. Verify token contrast test and `textContrastGuideline` where applicable.
- [M] Screens reflow at 2.0× text scale with no overflow. Verify widget/golden tests at 2.0×.
- [M] Reduced motion respected. Verify with `disableAnimations: true`.
- [M] Form errors are inline and announced; focus moves to first error. Verify widget test on semantics tree.
- [M] Meaning is never conveyed by color alone. Verify state visuals.
- [C] Custom gestures have alternatives (buttons/semantic actions) when swipe/drag actions exist.
- [M] Manual screen-reader pass of each critical journey with TalkBack and VoiceOver. Record result per platform; mark not verified when device/emulator access is unavailable.
