---
name: mobile-design-research
description: Researches real mobile app screens, onboarding, paywalls, feature journeys, and component patterns using Appllama MCP or other authorized references, then turns findings into original, measurable Flutter design specifications. Use before designing new screens, flows, or improving existing mobile UI when reference research is valuable.
---

# Mobile Design Research

## Shared standards

Use these central documents as the source of truth:
- [Team Operating Model](../../references/team-operating-model.md)
- [Flutter UI Translation](../../references/flutter-ui-translation.md)
- [Design System](../../references/design-system.md)
- [Quality and verification](../../references/quality.md)

## Optional Appllama MCP connection

Appllama documents the MCP endpoint at https://mcp.appllama.io/mcp. Configure it in the coding agent's supported MCP settings and authenticate with the user's own Appllama account. The MCP is optional. If no Appllama tool is available in the current agent environment, do not claim live library access; use supplied references or other authorized sources and state the limitation. Check current plan, credit allowance, and terms in Appllama before research; do not hardcode plan entitlements or credit prices into project code.

## Mission

Replace guesswork with focused evidence from real mobile products. Study how relevant apps solve the same user problem, extract reusable interaction and information patterns, then create an original Flutter design specification.

This skill owns research and synthesis. It does not copy competitor screens, choose the product's strategy, implement Flutter code, or approve the final visual result.

## When to use

Use for:
- New product design when the category has meaningful existing patterns.
- New onboarding, paywall, checkout, subscription, chat, diary, dashboard, or other high-impact flows.
- Reworking a screen whose hierarchy, navigation, conversion, or interaction is unclear.
- Researching a component or interaction such as tabs, sheets, pickers, progress, loaders, or gesture-driven surfaces.

Do not run a full reference study for a trivial spacing fix, a bug with an obvious cause, or a task where the user supplied an approved design spec. Research must answer a question, not become browsing for its own sake.

## Research source and limits

- Appllama MCP is an optional research source for real app profiles, screens, flows, UI elements, and media. Use it only when the MCP is actually connected and available to the agent.
- If Appllama MCP is unavailable, use references supplied by the user or other authorized public sources. Clearly label the source and any gaps; never pretend to have queried Appllama.
- Start with the member's own relevant Appllama boards when the MCP supports them.
- When connected, follow Appllama's current tool documentation. Check credits first when a free credit-status call exists. Be mindful that research calls may consume credits; do not repeat calls without a new question.
- Media links can expire. Record durable screen references/IDs and research notes; do not assume an old media URL remains available.
- Paginate sequentially with the cursor returned by the same query. Do not guess cursors or parallelize cursor-dependent pages.
- Research only what is needed for the user's current product question. Never scrape or export the catalog as a dataset, harvest assets, or bypass usage limits.
- Appllama's library is evidence about published product patterns, not proof that a pattern is best, accessible, ethical, profitable for this product, or legally reusable. Revenue/download/rating are context, not design quality scores.

## Research workflow

### 1. Form a research question

Write one to three questions tied to the product requirement. Examples:
- How do leading habit apps make the daily check-in obvious without filling the screen with cards?
- What is the sequence and purpose of each step in a fitness onboarding flow?
- How do subscription apps explain trial terms, renewal price, and restore purchases?
- How should a chat composer behave when the keyboard opens and the conversation grows?

Identify the target user, screen/flow, platform, and product constraints before searching.

### 2. Select references

When Appllama MCP is available, use the currently documented capabilities as appropriate:
- get_credits: check remaining budget when available.
- list_my_boards / get_board: start with relevant member curation.
- search_apps / get_app: find and qualify relevant products.
- list_flows / get_flow_apps / list_app_screens: inspect journeys in their actual sequence.
- search_screens: use keyword search for named screen types and semantic search for a visual/interaction goal; they answer different questions.
- get_screen: inspect a pivotal screen and related alternatives.
- list_ui_elements / get_element_screens: compare how a particular control or component is used.

Choose a small, relevant cross-app sample. Usually a few strong apps and a handful of pivotal screens are enough for a narrow question. For a complex end-to-end flow, inspect the selected flow across several relevant apps. Do not impose a fixed 20–30 screen quota. Stop when additional references stop changing the design decision (research saturation).

Use relevance to the user's category and journey first; revenue, rating, downloads, geography, and launch date are secondary context. Record why each reference was selected.

### 3. Read journeys, not isolated screenshots

For a selected flow, inspect screens in sequence:
- What triggers the flow and what outcome finishes it?
- What does each step ask from the user, and what does it give in return?
- Which actions are primary, secondary, optional, destructive, or irreversible?
- Which screens are pushed routes, sheets, modals, overlays, or tab destinations?
- What does system Back do at each step on iOS and Android?
- Where are permissions, authentication, trial terms, purchase, restore, cancellation, and failure handled?
- How does the flow behave when the user skips, interrupts, retries, backgrounds, or returns?

For a screen-level question, inspect the incoming and outgoing transition when available. A screenshot cannot establish navigation or gesture behavior.

### 4. Synthesize patterns

Produce a short evidence table:

| Finding | Evidence | Product decision |
|---|---|---|
| Repeated category convention | Which apps/screens show it | Adopt, adapt, or intentionally reject |
| Strong differentiator | Where it appears and why it fits | Use only if aligned with product value |
| Weak or confusing pattern | Observed issue and context | Avoid or improve |
| Unverified assumption | Missing interaction/data | Do not present as fact |

Separate:
- **Observed:** directly visible or documented in a source.
- **Inference:** likely purpose or rationale; explain why.
- **Recommendation:** what this product should do.
- **Rejected:** a pattern that does not fit, with the reason.

Do not infer A/B-test outcomes, conversion impact, accessibility compliance, or business causality from a screenshot or revenue ranking.

### 5. Produce the Flutter design brief

Hand off:
- Screen/flow inventory and user goal.
- Information hierarchy and content priority.
- Layout structure and responsive behavior.
- Semantic token roles, typography roles, spacing/radius rules, and component needs.
- Interaction state model: idle, pressed, selected, loading, disabled, success, error, empty, offline, and permission states where applicable.
- Navigation contract: push, replace/go, tab stack, sheet/modal/overlay, deep link, and Back behavior on both platforms.
- Motion specification: purpose, trigger, source of velocity if gesture-driven, settle behavior, interruption/cancellation, duration/curve or spring class, and reduced-motion alternative.
- Localization, Arabic/RTL, screen-reader, focus, and Dynamic Type implications.
- Evidence references and open questions.
- Acceptance criteria that QA can verify.

Keep this brief in the existing project requirements/design handoff. Do not create a large research archive or copy the entire Appllama catalog into the project. Save only selected source IDs, short notes, and user-authorized evidence required to reproduce the decision.

## Flutter implementation boundary

Use the translation table in references/flutter-ui-translation.md. Research ideas may transfer; Expo APIs and React Native code do not.

Core rules:
- Translate visual/interaction intent into the project's existing first-party Flutter design system and Flutter SDK primitives.
- Keep product identity original. Extract structure and interaction grammar, not pixels, logos, mascots, artwork, text, exact layouts, or protected trade dress.
- Respect the existing architecture, Riverpod, GoRouter, no-generated-code rule, dependency policy, and platform constraints.
- Do not add Reanimated, Gesture Handler, Expo Router, FlashList, Expo Image, or any React Native dependency to Flutter.
- A reference that relies on an iOS-only capability must get an Android-appropriate behavior, not an imitation that breaks Android conventions.
- Never call a Flutter blur approximation the native Apple Liquid Glass material. Escalate a true native-material requirement to Native Platform Integration and verify API/OS availability.

## Visual and motion verification

The research handoff is not implementation acceptance. The rendered Flutter result must go through the project's design, QA, accessibility, and performance gates.

For every important flow:
1. Run on iOS Simulator and Android Emulator/physical device as available.
2. Inspect actual screenshots at target sizes: safe areas, status bar, home indicator, keyboard, long content, loading/empty/error states, and light/dark themes.
3. Screen-record the entire critical journey, not just one hero animation. Inspect normal speed and scrub frames for flashes, jumps, gesture discontinuities, incorrect layering, keyboard jumps, and Back behavior.
4. Check Reduce Motion, system text scaling, English/Arabic, and RTL where supported.
5. Measure performance separately in profile mode on physical hardware. Do not use simulator FPS or an encoded 60 fps video as proof of device performance.
6. Compare the result against the written spec and selected references. Record remaining gaps rather than declaring perfection by intuition.

A flow passes only when its applicable Flutter quality gates pass with evidence. Research ends when the design decisions are justified; implementation ends when the Flutter result is verified.

## Intellectual property and licensing

- Preserve applicable licenses and attribution when adapting licensed skill text or code.
- Do not assume a repository's code license covers its sample assets, third-party names, logos, artwork, screen content, or trade dress.
- Do not copy Expo sample implementations into Flutter. Do not copy GPL-licensed code into a project with a different distribution policy without an explicit license review.
- Use Appllama media as research evidence only within the service's terms. Do not redistribute its watermarked screenshots or reproduce third-party app assets.
- Create original copy, tokens, illustrations, icons, and screen composition. Record asset provenance for shipped assets.

## Acceptance gate

Pass only when:
- The research questions are explicit and relevant.
- Sources are identified, relevant, and not presented as design proof beyond what they show.
- Patterns and recommendations are separated from observations and assumptions.
- The output is a testable Flutter design brief, not a screenshot collage.
- Navigation, platform behavior, motion, accessibility, and failure states are covered where applicable.
- No Expo/React Native code, dependencies, or unlicensed assets entered the Flutter project.
- Research scope stopped at saturation and did not become catalog harvesting.
