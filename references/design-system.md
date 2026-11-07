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

Process: spec → API → implementation → tests → accessibility → visual verification → docs (dartdoc + one usage example) → mark reusable. Search `components/` for an equivalent first; extend with a variant rather than clone. Deprecate with `@Deprecated` + one-version migration path; breaking API changes need a `DECISIONS.md` entry.

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

- **Loading:** show nothing for the first ~150–200 ms when loads are typically fast; then skeleton for known layout, spinner for indeterminate actions. No artificial delay. Keep loaded data visible during refresh; never blank the screen.
- **Skeleton/shimmer:** mirror final layout. Shimmer only on skeletons, one shared animation controller per screen, disabled under reduced motion. Avoid layout shift; crossfade at `motion.fast`.
- **Empty:** explain the situation and offer one useful next action if one exists (clear filters, retry, grant permission, add first item).
- **Error:** map `AppFailure` to localized message + recovery (retry, re-login, settings, offline mode). Distinguish offline from server failure. Form errors appear inline and are announced.
- **Pagination:** footer states for loading/error/end; debounce triggers; preserve scroll position on refresh.

## Motion and interaction

Motion tokens in `tokens/motion`: durations (instant ~100 ms, fast ~200, base ~300, slow ~450; tune and keep as the only values), curves (standard, decelerate for enter, accelerate for exit), and gentle/snappy spring specs. No literal `Duration`/`Curves.*` in features.

- Prefer implicit animations (`AnimatedContainer`, `AnimatedSwitcher`, `TweenAnimationBuilder`) over controllers; explicit controllers only for sequencing/interruption, and dispose them.
- **Feedback within one frame** of touch; never delay an action to finish animation. Animations are interruptible and reversible (reverse from current value, do not restart).
- Gestures: respect gesture arena (nested scrollables, horizontal swipe vs. iOS back-swipe); drags use velocity to choose settle target and spring physics; preserve platform scroll physics unless justified.
- Transitions: Cupertino-style push with interactive back-swipe on iOS; Android default/predictive-back behavior; sheets/dialogs fade + translate using tokens; shared elements via `Hero` with matched tags and `flightShuttleBuilder` when sizes differ.
- Haptics through one `Haptics` service (selection for picker/toggle changes, light for confirmations, heavy/vibrate rarely for errors). Never on every tap or continuous scroll; silently handle unsupported capability.
- **Reduced motion:** when `MediaQuery.disableAnimationsOf(context)` is true, replace movement with instant change or short crossfade, stop shimmer and looping animations.
- Backgrounding: tickers pause automatically; do not leave timers or repeating controllers running off-screen.
- Performance: animate transforms/opacity rather than layout where possible; scope rebuilds with `AnimatedBuilder.child`; add `RepaintBoundary` only when profiling shows benefit. Verify in profile mode on a real device when available; otherwise report not verified on device.

## Governance

- Token naming is semantic (`textSecondary`), never appearance-based (`grey500`) in feature-facing APIs. One definition per value; adding a token requires proving no existing token fits.
- Changes to `design_system/` require review for API consistency and cross-app impact.
- Keep a small debug-only component gallery rendering every component × variant × state in light/dark and LTR/RTL. It doubles as golden-test source. Build it when the library has more than a handful of components, not before.
