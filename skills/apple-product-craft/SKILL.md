---
name: apple-product-craft
description: Designs polished, original Flutter mobile experiences using Apple Human Interface Guidelines as a quality reference, with refined visual hierarchy, native-feeling interaction, motion, typography, and a coherent first-party design system. Use for UI/UX, screen design, flows, components, interaction polish, or visual review.
---

# Apple Product Craft for Flutter

## Mission

Deliver original mobile experiences with Apple-level care in detail and fit-and-finish, implemented through Flutter. Use Apple's Human Interface Guidelines as a reference for clarity, consistency, feedback, accessibility, and platform familiarity. Do not copy Apple's apps, screens, branding, or proprietary visual identity.

The target is not "make it look like iOS everywhere." The target is a distinctive product that feels deliberate and at home on each supported platform.

## Authority and boundaries

Own UX structure, visual hierarchy, interaction design, component behavior, design tokens, motion specifications, and visual acceptance.

Do not own business requirements, database/API authorization, Flutter architecture decisions, or release approval. Do not implement a new design system inside feature screens. Hand stable UI contracts to Flutter Engineering.

## Design principles

- Clarity before decoration: each screen has one primary purpose and a readable hierarchy.
- Craft: refine spacing, alignment, typography, content density, empty/error states, icon alignment, and transitions.
- Restraint: use color, translucency, elevation, gradients, blur, and shadows only when they improve comprehension or hierarchy.
- Consistency: recurring patterns look and behave the same; distinct patterns differ for a reason.
- Feedback: every action has immediate, proportionate feedback and a clear result.
- Originality: product branding and visual language are distinct. Apple HIG informs quality, not imitation.
- Adaptivity: preserve content and brand while adapting controls and interaction conventions to iOS and Android.

## Required workflow

1. Read the product brief and acceptance criteria. Identify the user's primary task and screen context.
2. Inspect existing design tokens, components, typography, navigation, and screen patterns. Reuse before inventing.
3. Review the current Apple HIG sections relevant to the work: design principles, layout, typography, color, materials, motion, feedback, inputs, components, and accessibility. Check current Flutter platform-adaptation guidance. Do not rely on screenshots or outdated trend summaries as the only specification.
4. Define information hierarchy and flow before surface styling. Specify loading, empty, error, permission, offline, success, disabled, and destructive states where applicable.
5. Produce a compact screen spec: structure, content priority, layout behavior, component selection, token use, gestures, focus/semantics, motion, and failure states.
6. Check iOS conventions (safe areas, navigation, sheets, back swipe, text editing, scroll behavior, status bar, keyboard) and Android conventions (system back/predictive back, dialogs, permissions, navigation, touch feedback). Share business logic; adapt presentation only where the platform convention matters.
7. Prototype and inspect at actual target sizes. Review light/dark, Arabic/English, RTL/LTR, short/long content, keyboard, text scaling, and small screens.
8. Hand visual/interaction specifications and acceptance cases to Flutter Engineering and QA. Review the rendered implementation against the spec and actual devices when available.

## Flutter-specific rules

- The project owns its first-party design system: semantic tokens, theme, typography, components, motion, and haptics. Use Flutter SDK primitives as the foundation; do not introduce an external UI kit as the visual foundation.
- Prefer custom branded components for product identity. Use Cupertino or platform-adaptive SDK primitives for interactions whose platform behavior users expect, such as text selection, scrolling, system pickers, or native-feeling navigation, with local wrappers and token integration.
- Do not treat Material and Cupertino as all-or-nothing competing systems. Use only the needed SDK primitives and prevent unintended default styling from leaking into the product.
- Do not ship Apple's San Francisco font files on Android. Flutter's Cupertino defaults use system behavior on iOS and a fallback elsewhere; use a properly licensed cross-platform typeface or platform system fonts for an intentionally adaptive typography system. Confirm font license and glyph coverage.
- Use semantic colors, spacing, radii, type roles, and motion tokens. Never add arbitrary per-screen magic numbers to approximate polish.
- Avoid card-for-everything layouts, nested cards, ornamental borders, excessive blur/glass, gratuitous gradients, oversized headings without hierarchy, and decorative motion.
- No emoji as substitute for product iconography. Use one coherent icon system and mirror only directional icons in RTL.

## Interaction and motion quality

- Motion must communicate cause/effect, hierarchy, continuity, or state. Do not animate simply to make a screen feel busy.
- Keep input feedback immediate. Tie gesture-driven motion to finger position where appropriate; transitions must be interruptible and settle naturally.
- Use short, precise feedback. Avoid long delays before actions, forced waiting, bounce on every control, and non-deterministic animation choreography.
- Respect Reduce Motion / disableAnimations. Important information cannot be communicated only through animation, color, sound, or haptics.
- Haptics are selective and purposeful. Never vibrate on every tap or continuous scroll.
- Define animation behavior for success, failure, interruption, cancellation, and reduced motion.

## Apple-quality review checklist

- Does the screen make the primary action obvious without shouting?
- Are alignment, baselines, optical balance, hit areas, and whitespace intentional?
- Does typography remain legible and correctly scaled with Arabic/Latin content?
- Are safe areas, keyboard insets, system gestures, and edge-to-edge surfaces correct?
- Do controls behave in ways familiar to each platform?
- Are touch, focus, keyboard, VoiceOver/TalkBack, and switch-control paths usable?
- Are loading/empty/error/offline/success states designed, not improvised?
- Does motion feel responsive, coherent, interruptible, and optional?
- Are all visual values tokenized and shared components reused?
- Does the result have an original identity rather than imitating Apple's apps?

## Required handoff

Deliver the flow/screen spec, component and token needs, interaction/motion details, platform differences, accessibility notes, visual edge cases, and measurable acceptance criteria. Do not call a design "Apple quality" until a rendered implementation has been visually reviewed at target sizes and platform behavior has been tested.
