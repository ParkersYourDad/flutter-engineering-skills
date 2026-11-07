# Flutter UI Translation for Cross-Framework Design Research

This guide translates the intent of common Expo/React Native patterns into the existing Flutter/Dart baseline. It is not a porting recipe and does not authorize adding packages. Verify exact APIs against the project's pinned Flutter SDK and official docs at implementation time.

## Core principle

Transfer user experience decisions, interaction grammar, motion intent, layout rules, state behavior, and verification methods. Rebuild them using Flutter's own rendering, widget, navigation, animation, and platform-integration models.

Never copy React Native code and rename APIs.

## Practical mapping

| Expo / React Native concept | Flutter/Dart approach | Important difference |
|---|---|---|
| Expo Router stack / tabs / modal routes | Project's GoRouter contracts, route registration, push, go, replace, tab shell, and SDK routes/overlays | Preserve route semantics and Back behavior; do not port file-based routing |
| Reanimated timing animations | AnimatedOpacity, AnimatedContainer, AnimatedSwitcher, TweenAnimationBuilder, or explicit AnimationController + CurvedAnimation + transition widgets | Use implicit animation when sufficient; explicit controllers only when sequencing, interruption, or gesture coupling needs control |
| Reanimated gesture springs | GestureDetector / RawGestureDetector + AnimationController.animateWith / fling + SpringSimulation or another appropriate SDK simulation | Feed real release velocity into physics where appropriate; do not approximate a fling with a fixed-duration tween |
| Gesture Handler | GestureDetector, RawGestureDetector, Listener, Scrollable, Draggable, Dismissible, and Flutter's gesture arena | Resolve nested gesture conflicts using Flutter's arena and scroll behavior; do not add a gesture package by default |
| FlashList / virtualized lists | ListView.builder, GridView.builder, SliverList, SliverGrid, CustomScrollView | Choose lazily built slivers/list builders; use stable keys and item extents only when their assumptions are true |
| Reanimated animated node / shared values | Small AnimatedBuilder / AnimatedWidget subtree, ListenableBuilder, or a CustomPainter listening to a Listenable | Keep frame updates local. Do not call a broad setState that rebuilds an entire screen every tick |
| React Context/Zustand/TanStack Query | Project's Riverpod 3 providers/Notifier/AsyncNotifier + repositories for remote state + local ephemeral widget state | Preserve one owner per state. Do not import React state patterns or add another state system |
| Expo Image / recycling keys | Flutter Image, Image.asset / Image.network, cacheWidth / cacheHeight, ResizeImage, precacheImage; package only if a measured need exists | Control decode size and memory. Image caching is not a reason to add a new package automatically |
| React Native Skia Canvas | Flutter CustomPainter, Canvas, dart:ui, and FragmentProgram shaders when justified | Different drawing/runtime APIs; profile raster cost and memory on target devices |
| Safe Area Context | SafeArea, MediaQuery.paddingOf, viewPaddingOf, and viewInsetsOf | Account separately for system bars, persistent insets, and keyboard insets |
| Keyboard Controller | Flutter MediaQuery.viewInsetsOf(context), focus nodes, scroll-to-focused-field behavior, and tested inset-aware layout | Follow actual platform inset changes; do not use guessed keyboard durations or arbitrary delays |
| Expo Haptics | Flutter SDK HapticFeedback APIs from package:flutter/services.dart | Haptics must be purposeful, optional where unsupported, and never the only feedback |
| Native Switch / Slider / Picker / Context Menu | Flutter SDK's Material/Cupertino primitives or a first-party component composed from SDK primitives | Choose by platform behavior and product design; do not let default Material/Cupertino styling leak unintentionally |
| Expo / native image asset preload | Flutter asset bundling, precacheImage, and explicit loading/error states | Do not block startup for below-the-fold assets without a measured reason |
| Expo development simulator loop | fvm flutter run, Flutter DevTools, integration_test, screenshots/video capture, and release/profile device verification | Flutter integration_test cannot interact with native platform dialogs; use a native UI test tool only when a real requirement demands it |

## Motion: translate intent, not library calls

Separate motion into two families:

- **Gesture-driven motion:** the visual follows the pointer/finger and the release behavior accounts for velocity, constraints, and a physically plausible settle. Use Flutter gesture details and physics simulations when justified.
- **Time-driven motion:** a clear state transition, reveal, or feedback animation. Prefer SDK implicit animations for simple changes; use explicit controllers for coordinated sequences or interruptible behavior.

For explicit animations:
- Supply a valid TickerProvider and dispose controllers.
- Keep the animated subtree narrow with AnimatedBuilder's child or an AnimatedWidget.
- Prefer transform/opacity for motion where that preserves layout semantics; do not sacrifice correctness or accessibility for a blanket "no layout animation" rule.
- Handle interruption, reverse, cancellation, route disposal, backgrounding, and TickerMode.
- Respect MediaQuery.disableAnimationsOf(context) and preserve the meaning of the state when motion is reduced.
- Do not copy Reanimated worklet claims into Flutter. Flutter's frame pipeline and isolate model are different; profile the actual UI and raster work rather than assuming a specific thread is free.

Flutter animation references: https://docs.flutter.dev/ui/animations and https://docs.flutter.dev/ui/animations/overview

## Navigation and one-way doors

Before implementation, classify each destination:

- **Push:** the user expects to return to the prior context.
- **Replace / go to a new stack state:** returning would re-enter a completed or invalid step.
- **Tab destination:** peer-level destination; preserve each tab's stack if the product requires it.
- **Modal / sheet / overlay:** interruption or self-contained task; define dismissal, drag, backdrop, system Back, and restoration behavior.
- **One-way door:** completed onboarding, signed-in wall, confirmed purchase, or completed irreversible session must not expose stale prior states through Back. But an auth prompt raised from a feature should preserve the feature context when that is the product's intended journey.

Use GoRouter APIs and route contracts from the project architecture. Do not port Expo Router APIs such as dismissTo, Stack.Protected, or file-system routes.

## Native controls and materials

- Use platform-familiar interactions for text editing, scrolling, pickers, menus, selection, haptics, and Back.
- A custom product control must preserve semantics, focus, keyboard/assistive access, disabled/loading/error states, and platform hit targets.
- BackdropFilter or a custom blur is not automatically equivalent to Apple's native Liquid Glass material. If the requirement specifically calls for Apple's native material, evaluate a narrow SwiftUI bridge on supported iOS versions and define a different but coherent Android treatment. Do not add a broad native dependency for a decorative effect.
- Never assume that an Expo wrapper, native plugin, or sample's OS minimum applies to Flutter.

## Visual research to screen specification

Translate an inspiration screen into these Flutter decisions:

1. Layout constraints and information hierarchy.
2. Token roles, not copied hex values.
3. Existing component reuse or a justified new first-party component.
4. State ownership and data dependencies.
5. Gesture and navigation behavior.
6. Motion purpose, trigger, interruption, reduced-motion path.
7. Platform differences and safe-area/keyboard behavior.
8. Accessibility semantics, focus, text scaling, localization/RTL.
9. Measurable acceptance criteria and visual evidence.

Do not copy exact pixels, text, logos, iconography, mascots, illustrations, or distinctive brand composition. Learn the underlying pattern and make an independent design.

## Verification matrix

| Area | What to verify |
|---|---|
| Screens | Fresh launch, actual route, long content, narrow screen, light/dark |
| Layout | Safe areas, status/navigation bars, keyboard, scroll clipping, orientation if supported |
| Navigation | Push/pop, replace/go, tab reselect, system Back, iOS edge-swipe, deep-link entry |
| Interaction | Press feedback, drag, velocity, interruption, rapid taps, cancellation |
| Motion | Full-flow recording, frame-by-frame inspection, reduced motion, no stale offscreen tickers |
| Accessibility | Semantics, focus, keyboard/switch access, screen reader, system text scaling, contrast |
| Localization | Arabic/English strings, RTL, mixed-direction values, plural/number/date rules |
| Performance | Physical device profile mode, actual refresh-rate budget, UI/raster frame timing, startup/memory/network where relevant |
| Tests | Widget/integration journeys; native system UI requires an appropriate native-aware test tool when it must be automated |

Flutter integration-test guidance: https://docs.flutter.dev/cookbook/testing/integration/introduction

Flutter performance guidance: https://docs.flutter.dev/perf/ui-performance and https://docs.flutter.dev/perf/rendering-performance

Flutter native platform integration: https://docs.flutter.dev/platform-integration

## Source and licensing notes

Appllama's appllama-skills repository publishes its skill material under MIT. Its separate screen/code sample repositories have their own licenses and notices; several reviewed screen galleries identify their code as GPL-3.0 and explicitly state that the license does not grant rights to third-party app logos, screen content, artwork, or trade dress. Inspect the exact repository, package, and asset license before copying anything. This translation deliberately transfers research and engineering concepts, not sample code or assets.

- Appllama skills: https://github.com/Appllama/appllama-skills
- Appllama top welcome screens: https://github.com/Appllama/top-welcome-screens
- Appllama top paywall screens: https://github.com/Appllama/top-paywall-screens
- Appllama Liquid Glass screens: https://github.com/Appllama/liquid-glass-screens
- Appllama Liquid Glass chat UI: https://github.com/Appllama/liquid-glass-chat-ui
- Appllama loader experiments: https://github.com/Appllama/25-unique-loaders
