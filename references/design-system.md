# Design System, States and Motion

## Contents
- Direction
- Structure and app shell
- Foundations
- Theming and branding
- Component contract
- Component checklist
- Screen states
- Motion and interaction
- Governance

## Direction

## Product craft direction

Use the current Apple Human Interface Guidelines as a quality reference for clarity, craft, hierarchy, feedback, platform familiarity, and accessibility—not as a template to copy. The visual identity must remain original and fit the product's purpose.

The target is a Flutter-owned design system with Apple-level attention to detail:
- Precise typography, spacing, alignment, optical balance, and content hierarchy.
- Fast, intentional, interruptible transitions and tactile feedback.
- Calm surfaces and restrained effects; do not apply blur, translucency, glass, gradients, or shadows by default.
- Native-feeling iOS interactions while preserving Android expectations. Use shared product logic with platform-specific behavior only where users benefit.
- Current HIG and Flutter platform-adaptation guidance must be checked for the task; platform guidance and SDK behavior evolve.
- Do not distribute Apple's San Francisco font files on Android. Use platform system fonts or fonts licensed for every target platform; verify Arabic and Latin glyph coverage.
- Do not equate an Apple-like appearance with usability. Verify actual tasks, accessibility, and rendered behavior.

Premium, minimal, modern, soft, refined, with iOS-quality fit and finish. Hierarchy comes from typography, spacing, and whitespace, not boxes. Rounded geometry follows one consistent radius logic. Restraint is the design: few colors, few weights, subtle depth.

Avoid cards for everything, card-in-card, borders on everything, heavy shadows, random gradients, decorative noise, inconsistent radii, and template-looking screens. Do not impose one identity on every app; the system is a refined neutral foundation that brands override through configuration.

## Structure and app shell

```
design_system/
  tokens/       # colors, typography, spacing, radii, sizing, opacity, elevation, motion
  theme/        # AppTheme (InheritedWidget), light/dark, AppBrand
  components/   # one folder per component family
  foundation/   # Pressable, haptics, AsyncStateView, responsive helpers
```

- Root app uses `WidgetsApp.router` so no Material theme drives appearance. Wrap with `AppTheme`, `MediaQuery` handling, and localization delegates (`GlobalWidgetsLocalizations`; add Material/Cupertino delegates only if those widgets are used).
- Access tokens through `AppTheme.of(context)`. Features never read `Colors.*`, `Theme.of`, or construct `Color(...)`, `TextStyle(...)`, `EdgeInsets.all(<literal>)`, `Duration(<literal>)`, or `BorderRadius.circular(<literal>)`.
- If a Material/Cupertino primitive is genuinely needed (platform date picker, text-selection toolbar, `showDatePicker`), wrap it locally with a theme built from tokens, keep wrapper inside `design_system`, and record the choice in `DECISIONS.md`. Verify both themes and RTL.
- Platform adaptivity means platform-correct behavior (scroll physics, back swipe, haptics, selection handles, sheet gestures) with our visual identity. Do not fork screens per platform unless UX requires it.

## Foundations

- **Color: three tiers.** Primitive palette → semantic roles (`background`, `surface`, `surfaceRaised`, `textPrimary/Secondary/Disabled`, `accent`, `onAccent`, `border`, `divider`, `success/warning/danger` + `on*`, `overlay`) → component tokens only when a component needs a deviation. Features use semantic roles only.
- Light and dark are complete, separately tuned palettes, not inversions. Dark uses elevated surface tones rather than shadows. Contrast: WCAG AA (4.5:1 body text, 3:1 large text and UI boundaries), checked by unit test over every text/background pair.
- **Typography:** one scale (display, title, headline, body, label, caption) defined as role → size/weight/height/letter-spacing. Honor the full system text scaler; do not apply a global text-scale cap. Layouts must reflow, scroll, or adapt when text grows. A narrowly scoped exception is allowed only when a specific control cannot remain usable otherwise; document the reason, preserve an accessible way to read the full content, and test the affected flow at the platform's largest text setting. Verify at 2.0× as a minimum engineering test, not as a replacement for the platform maximum. Bundle fonts as assets (never fetch at runtime), confirm license and Arabic + Latin glyph coverage; Arabic generally needs more line height and no letter-spacing.
- **Spacing:** 4-pt grid scale (`xxs`…`xxl`) as constants. **Radii:** small scale; nested corners are concentric (inner radius = outer radius − padding). Prefer `RoundedSuperellipseBorder`/continuous corners only if supported by the pinned SDK; otherwise use standard rounded rectangles consistently.
- **Elevation:** depth by surface tone + hairline first; soft, low-opacity shadows only for floating layers (sheets, menus, dialogs). One shadow recipe per level.
- **Icons:** one coherent bundled set; directional icons mirror in RTL (`matchTextDirection`), others do not.
- **Sizing and layout:** minimum interactive size 48 dp (also satisfies iOS 44 pt); max content width for large screens; breakpoints only where layout truly changes (phone vs. large/tablet/foldable). Use `LayoutBuilder`/`MediaQuery.sizeOf`, never device-model checks.
- **Motion tokens:** see Motion below.

## Theming and branding

`AppBrand` (accent color, optional font family, radius character, product-specific illustrations) is the only input an app supplies. The system derives accent states (pressed, disabled, on-color) and validates contrast. Brand never requires editing `tokens/` or `components/`. Theme mode (system/light/dark) is persisted and applied before first frame; system mode follows platform brightness changes live.

## Component contract

Every shared component:

- Has one purpose and consistent API. Require semantic labels where meaning is not visible. `onPressed == null` means disabled. Variants are enums, not boolean pairs. Content uses slots (`Widget`); styling uses tokens. No raw `Color`/size parameters except sanctioned style objects.
- Is built on shared `Pressable` (pressed feedback, hit target, focus, semantics, haptics, reduced motion) so behavior is consistent.
- Documents its state model: default, pressed, focused, hovered (pointer/stylus), disabled, loading, selected, expanded, error, read-only, success. Include only applicable states and explain omitted common states.
- Works in light/dark, LTR/RTL, text scale up to 2.0×, and with long/empty content without overflow.
- Meets the Component Gate in `quality.md`.

Process: spec → API → implementation → tests → accessibility → visual verification → docs (dartdoc + one usage example) → mark reusable. For a component intended for reuse across features or apps, complete the [Reusable Design-System Component Contract](design-system-component-contract.md); screen-local widgets do not need a separate contract document. Search `components/` for an equivalent first; extend with a variant rather than clone. Deprecate with `@Deprecated` + one-version migration path; breaking API changes need a `DECISIONS.md` entry.

## Reusable component implementation contract

Treat this as a decision and review contract, not a mandate to create every component family or one universal widget API.

### Public API and ownership

- Keep public APIs small and task-oriented. Prefer named constructors or a small enum for genuinely different semantic variants; do not expose a boolean for every visual option.
- Separate semantic intent from rendering: a button exposes its action, label/content, and meaningful variant; the shared foundation owns pressed/focus/hover feedback, hit testing, semantics, and the configured haptic policy.
- Keep transient interaction state local to the component unless another part of the product must observe it. Business state and asynchronous operation ownership remain with the feature/state layer.
- Use explicit slots only where composition is a real requirement (for example leading/trailing content); avoid turning every component into a generic layout framework.
- Define disabled, loading, and read-only behavior explicitly. A loading action must prevent duplicate activation without unexpectedly changing its layout or losing its accessible name.
- Keep localization outside component internals: accept localized text/semantics from the caller or use a clearly documented localization contract. Never hardcode user-facing strings in shared components.
- Inject platform effects such as haptics behind a narrow service boundary when they need deterministic tests. Do not introduce a service abstraction for effects that are not used or cannot vary meaningfully.

### Interaction and motion contract

For each animated or interactive component, record only the applicable items:
- Trigger and semantic purpose; what user-visible state changes.
- Duration/curve token or gesture physics; no per-feature magic values.
- Initial, target, interrupted, reversed, cancelled, and disposed behavior.
- Reduced-motion behavior that preserves the same information and action.
- Focus, keyboard, screen-reader, and non-gesture operation.
- Haptic event and platform behavior, if any; haptics occur once after the semantic action is committed, never during build or animation ticks.
- Loading, failure, and retry behavior where the component owns or represents an asynchronous action.

A component should not own network requests, business mutations, analytics policy, or navigation decisions merely to make its API convenient.

### Reusable implementation patterns

- **Action controls:** compose a shared pressable foundation with visual variants. Keep the interactive/semantic node singular; avoid nested gesture detectors that compete for the same tap.
- **Async content:** keep request/state ownership outside the visual state presenter. A shared state view may map explicit loading/error/empty/data states, but callers provide the empty predicate and recovery action.
- **Skeletons:** provide a small set of tokenized shapes or composition primitives only when repeated layouts justify them. Do not build a universal skeleton tree or force shimmer.
- **Shared-element transitions:** keep Hero at route/content composition boundaries, not buried inside a generic card/button. The feature supplies stable object identity and a fallback.
- **Typography:** expose semantic text roles and controlled emphasis, not arbitrary per-feature style construction. Verify actual Arabic glyph metrics and mixed-script wrapping with the bundled font.
- **Directional visuals:** expose semantic direction or use Flutter's directional APIs; decide mirroring from meaning, not from whether an icon happens to point left or right.

### Component test recipe

A reusable component should have focused tests mapped to its completed [component contract](design-system-component-contract.md):
1. Public API defaults and each supported variant.
2. Applicable enabled/disabled/loading/selected/error/focus states.
3. User action, duplicate activation prevention, and callback count.
4. Semantics (label, role, value, enabled/selected state, and announcements where applicable).
5. Keyboard/focus and non-gesture activation where the control supports them.
6. Light/dark, LTR/RTL, long content, and text scaling; test the largest relevant platform setting in addition to the 2.0× engineering baseline when practical.
7. Reduced motion: assert the alternate behavior or absence of ongoing animation, not a screenshot alone.
8. Haptics through an injected fake/recording adapter when the component emits them; assert semantic event and exactly-once behavior. Do not claim physical vibration was tested by a widget test.
9. Golden tests only where stable visual regression coverage adds value; keep behavioral assertions independent of goldens.

For Hero/shared-element behavior, use route-level tests for identity, navigation interruption, and fallback. A widget test that merely finds a Hero is not proof of a correct flight animation. Verify real platform gesture and visual behavior manually on target devices when that behavior is part of acceptance.

## Component checklist

Build a component only when a requirement needs it. In addition to the contract:

| Family | Must handle |
|---|---|
| Buttons (primary/secondary/tertiary/destructive), IconButton | Loading (keeps width, blocks re-tap), disabled, pressed, focus, minimum target; icon-only needs label |
| Text field, Search field | Focus/error/disabled/read-only, helper + announced error, clear, obscure toggle, keyboard type/action, autofill, RTL caret/alignment, IME insets, search debounce, no-results hook |
| Checkbox, Radio, Switch, Slider | Selected/indeterminate, disabled, label tap target, value semantics, drag + keyboard/semantic increments, haptic tick on change |
| Dialog, Bottom sheet | Focus trap, barrier-dismiss policy, drag-to-dismiss, safe areas, keyboard avoidance, back/PopScope, scrollable content, destructive confirmation |
| Snackbar/Toast | One queue, screen-reader announcement, action support, duration scaled to length, does not cover primary actions/keyboard |
| Menu, Tooltip | Anchored, flips near edges, RTL placement, long-press tooltip, keyboard/semantic access |
| Tabs, Navigation bar | Selected state, badges, per-tab stack preservation, reselect behavior, semantics, large-screen adaptation |
| Lists / tiles / dividers | Builder/slivers for long lists, stable keys, swipe actions with non-gesture alternative, token separators |
| Progress, Loading indicators | Determinate/indeterminate, semantics value, reduced-motion variant |
| Skeleton | Matches final layout dimensions (no shift), reduced-motion static variant |
| Empty/Error state | Icon/illustration + title + explanation + single action; localized |
| Avatar, Badge, Chip | Image fallback, loading/error placeholder, count overflow, selected/removable chip, minimum target |
| Card/Surface | Used only to group genuinely distinct content; no nesting |
| Pickers (date/time/select) | Locale-aware calendar/numeral policy, RTL, min/max validation, accessibility, text-scale safety |

## Screen states

Define per screen only applicable states: initial, loading, skeleton, empty (first-use, no results, no filter results, nothing saved), populated, partial content, refreshing, error, offline, permission denied, unauthorized/expired session, pagination (loading-more, end, error-more), restoration after background/resume.

One shared `AsyncStateView` maps `AsyncValue` (+ emptiness predicate) to loading/error/empty/data so screens behave consistently.

- **Loading:** avoid flashing transient loading UI for operations that usually complete within ~150–200 ms; this is a heuristic to validate, not a mandatory timer. Then choose feedback by context: preserve existing content during refresh, use a skeleton when the destination layout is known and content is being assembled, and use a compact progress indicator for an indeterminate action or unknown layout. Never delay the actual action to wait for the indicator.
- **Skeleton/shimmer:** use only when it communicates the shape of content that is genuinely loading. Match final geometry closely to prevent layout shift; do not use skeletons for every button, tiny request, or unknown layout. Prefer a static skeleton under reduced motion; if shimmer is retained, use one bounded shared animation per visible region and verify its raster cost. Crossfade to content without hiding errors or stale-data status.
- **Empty:** explain the situation and offer one useful next action if one exists (clear filters, retry, grant permission, add first item).
- **Error:** map `AppFailure` to localized message + recovery (retry, re-login, settings, offline mode). Distinguish offline from server failure. Form errors appear inline and are announced.
- **Pagination:** footer states for loading/error/end; debounce triggers; preserve scroll position on refresh.

## Motion and interaction

Motion tokens in `tokens/motion`: durations (instant ~100 ms, fast ~200, base ~300, slow ~450; tune and keep as the only values), curves (standard, decelerate for enter, accelerate for exit), and gentle/snappy spring specs. No literal `Duration`/`Curves.*` in features.

- Prefer implicit animations (`AnimatedContainer`, `AnimatedSwitcher`, `TweenAnimationBuilder`) over controllers; explicit controllers only for sequencing/interruption, and dispose them.
- **Feedback within one frame** of touch; never delay an action to finish animation. Animations are interruptible and reversible (reverse from current value, do not restart).
- Gestures: respect gesture arena (nested scrollables, horizontal swipe vs. iOS back-swipe); drags use velocity to choose settle target and spring physics; preserve platform scroll physics unless justified.
- Transitions: Cupertino-style push with interactive back-swipe on iOS; Android default/predictive-back behavior; sheets/dialogs fade + translate using tokens. Use shared-element transitions (`Hero`) only when both routes represent the same semantic object and continuity helps orientation; tags must be stable, unique within the active route subtree, and based on object identity rather than list index. Handle different geometry, clipping, and route interruption with an appropriate flight shuttle or a deliberate non-shared fallback. Avoid duplicate/nested Hero collisions and do not animate unrelated content as if it were the same object.
- Haptics through one `Haptics` service (selection for discrete picker/toggle changes, light for meaningful confirmations, stronger feedback rarely for consequential events). Match the platform convention and interaction meaning; never vibrate on every tap, continuous scroll, or repeated rebuild. Trigger feedback once per committed user action, not during animation frames. Respect system settings and silently handle unsupported capability; haptics never replace visible or semantic feedback.
- **Reduced motion:** when `MediaQuery.disableAnimationsOf(context)` is true, replace movement with instant change or short crossfade, stop shimmer and looping animations.
- Backgrounding: tickers pause automatically; do not leave timers or repeating controllers running off-screen.
- Performance: animate transforms/opacity rather than layout where possible; scope rebuilds with `AnimatedBuilder.child`; add `RepaintBoundary` only when profiling shows benefit. Verify in profile mode on a real device when available; otherwise report not verified on device.

## Governance

Official guidance to consult when relevant:
- Apple Human Interface Guidelines: https://developer.apple.com/design/human-interface-guidelines/
- Apple design principles: https://developer.apple.com/design/human-interface-guidelines/design-principles/
- Apple motion guidance: https://developer.apple.com/design/human-interface-guidelines/motion
- Apple layout guidance: https://developer.apple.com/design/human-interface-guidelines/layout
- Flutter adaptive and responsive design: https://docs.flutter.dev/ui/adaptive-responsive
- Flutter platform adaptations: https://docs.flutter.dev/ui/adaptive-responsive/platform-adaptations

- Token naming is semantic (`textSecondary`), never appearance-based (`grey500`) in feature-facing APIs. One definition per value; adding a token requires proving no existing token fits.
- Changes to `design_system/` require review for API consistency and cross-app impact.
- Keep a small debug-only component gallery rendering every component × variant × state in light/dark and LTR/RTL. It doubles as golden-test source. Build it when the library has more than a handful of components, not before.
