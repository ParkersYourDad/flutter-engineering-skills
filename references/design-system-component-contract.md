# Reusable Design-System Component Contract

Use this template only when a component is intended for reuse across features or apps. A screen-local widget does not need a standalone contract. Keep the completed contract beside the component or in the project's design-system documentation; do not create a second copy in a skill repository when working in an application repository.

## 1. Identity and purpose

- **Component / family:**
- **Owner:**
- **Status:** Proposed / In progress / Accepted / Deprecated
- **Problem it solves:**
- **Intended consumers:**
- **Explicit non-goals:**
- **Existing component reviewed:** (name or N/A with reason)

## 2. Semantic and public API contract

- **User intent / semantic role:**
- **Public API sketch:** (constructor, required inputs, callbacks, meaningful variants)
- **Content slots:** (only those composition genuinely requires)
- **State ownership:** (what stays local; what remains with the feature)
- **Localization ownership:** (caller-supplied localized content or documented delegate)
- **Disabled / loading / read-only behavior:**
- **Duplicate activation policy:**
- **Token dependencies:** (semantic color, type, spacing, radius, sizing, motion)
- **Platform-specific behavior:** (iOS / Android / shared)

Do not expose business/network operations, analytics policy, navigation decisions, or arbitrary styling knobs through a reusable visual component.

## 3. State and transition model

List only applicable states. Mark other common states N/A with a reason.

| State | Entry condition | Visible / semantic result | Available actions | Exit condition |
|---|---|---|---|---|
| Default | | | | |
| Pressed / focused / hovered | | | | |
| Disabled / read-only | | | | |
| Loading | | | | |
| Selected / expanded | | | | |
| Error / success | | | | |
| Interrupted / cancelled | | | | |

## 4. Motion and feedback (if applicable)

- **Trigger and purpose:**
- **Duration / curve / physics token:**
- **Start and target behavior:**
- **Interruption / reversal / disposal:**
- **Reduced-motion alternative:**
- **Haptic semantic event and timing:** (or N/A)
- **Fallback when platform capability is unavailable:**
- **Why motion or haptics improve the task:**

No information or action may depend only on animation or haptics.

## 5. Accessibility, localization, and layout

- **Accessible name, role, value, and state:**
- **Focus order and keyboard / assistive activation:**
- **Minimum target and non-gesture alternative:**
- **Text scaling and content reflow:**
- **RTL / directional behavior:**
- **Arabic + Latin / long-content cases:**
- **Contrast and light / dark behavior:**
- **Reduced motion and system settings:**

## 6. Performance and lifecycle

- **Expected rendering / rebuild characteristics:**
- **Potential expensive work or animation:**
- **Scroll / large collection behavior:**
- **Background, disposal, and cancellation behavior:**
- **Profile-mode measurement needed:** Yes / No (reason)

Do not add caching, isolates, repaint boundaries, or other optimization machinery without a measured or credible need.

## 7. Verification matrix

| Requirement | Automated test / manual check | Expected result | Evidence / status |
|---|---|---|---|
| Public API and variants | | | |
| Applicable states and callbacks | | | |
| Duplicate activation / cancellation | | | |
| Semantics and focus | | | |
| Light / dark | | | |
| LTR / RTL and mixed direction | | | |
| Text scaling and long content | | | |
| Reduced motion | | | |
| Haptic adapter (if used) | | | |
| Route/device behavior (if applicable) | | | |

Use deterministic tests and injected fakes for platform effects. A widget test cannot prove physical haptic output or real-device animation quality. Use route-level tests for shared-element transitions and physical-device checks when platform behavior is part of acceptance.

## 8. Acceptance and known limitations

- **Acceptance criteria:**
- **Tests run and observed results:**
- **Manual/device checks completed:**
- **Not verified:**
- **Known limitations / follow-up owner:**
- **Documentation and usage example:**
- **Deprecation / migration plan (if applicable):**

A component is not Accepted because it compiles or has a golden image. Mark each check Passed, Failed, Blocked, or Not verified, with evidence.
