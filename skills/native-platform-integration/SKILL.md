---
name: native-platform-integration
description: Integrates Flutter apps with native iOS and Android capabilities using Swift/Objective-C, Kotlin/Java, plugins, platform channels, permissions, lifecycle APIs, entitlements, and platform build configuration. Use only when a product feature requires host-platform code or native SDK integration.
---

# Native Platform Integration

## Shared standards

Use these central references as the source of truth:
- [Architecture](../../references/architecture.md)
- [Quality and platform verification](../../references/quality.md)
- [Design system and platform behavior](../../references/design-system.md)

## Mission

Bridge Flutter/Dart to required iOS and Android capabilities safely, with minimal native code and a stable Dart-facing contract. Native code is a deliberate boundary, not a second application architecture.

## Own

- iOS host integration using Swift/Objective-C and Apple frameworks.
- Android host integration using Kotlin/Java and Android APIs.
- Flutter plugins, platform channels, native lifecycle hooks, permissions, entitlements, and platform build configuration.
- Threading, callback/cancellation behavior, resource ownership, and native error mapping.
- Native integration tests and supported OS-version verification.

## Do not own

- Flutter screen design or product state ownership.
- Backend authorization or data policy.
- Adding native code when a maintained Flutter SDK/plugin already meets the requirement.
- Duplicating business logic between Dart and host platforms.
- Changing the project's no-generated-code policy.

## Required workflow

1. Confirm the product requirement cannot be met reliably by Flutter SDK behavior or an approved maintained plugin.
2. Check current Flutter platform integration docs, platform API docs, minimum OS versions, plugin maintenance, license, privacy declarations, and breaking changes.
3. Define one small Dart-facing contract: operations, typed inputs/outputs, error categories, cancellation, permission states, and lifecycle behavior.
4. Keep platform-specific code behind a narrow adapter/service. UI and feature business logic remain in Dart.
5. Prefer an existing plugin when its maintenance, license, platform coverage, privacy, and behavior meet the requirement. Build a private plugin only when multiple apps or independent reuse justify it.
6. Use platform channels for a small app-specific bridge where suitable. Namespace channel names, validate arguments on both sides, handle missing plugins and OS-version failures, and keep the channel contract backward compatible.
7. Do not use Pigeon or other code generation under the current no-generated-code constitution. If type-safe generated bindings become necessary, stop and request an explicit architecture-policy decision before introducing them.
8. Respect threading: UI/platform-main-thread work stays short; expensive work uses supported background mechanisms; channel calls and callbacks follow the current Flutter engine contract.
9. Handle app lifecycle, permission denial/revocation, process death, background restrictions, multiple Flutter engines, plugin attach/detach, and resource cleanup.
10. Test on both platforms and real devices when hardware, biometrics, camera, notifications, Bluetooth, background execution, or OS integration is involved. Verify release-mode behavior and minimum supported OS versions.
11. Hand Dart the contract, platform differences, permissions/entitlements, error mapping, and test evidence.

## Critical pitfalls

- Performing native initialization in the wrong lifecycle callback.
- Assuming a single Flutter engine/plugin instance or using static state for engine-owned resources.
- Blocking the main/UI thread.
- Calling APIs unavailable on the minimum OS version without availability checks.
- Requesting permissions at startup or failing to handle revoked/denied permissions.
- Leaking observers, listeners, channels, activities, view controllers, or native resources.
- Returning untyped or undocumented channel maps.
- Exposing native secrets or sensitive data through logs.
- Adding a plugin without verifying maintenance, privacy manifest, entitlements, and transitive dependencies.
- Assuming simulator success proves camera, biometrics, Bluetooth, push, or background behavior.

## Acceptance gate

Pass only when the Dart contract is documented, platform code is isolated, permission/lifecycle/error paths are tested, iOS and Android builds succeed for applicable targets, real-device-only behavior is verified or marked Not verified, and no generated bindings or unnecessary native layers were introduced.

## Official references

- Flutter platform channels: https://docs.flutter.dev/platform-integration/platform-channels
- Flutter package/plugin development: https://docs.flutter.dev/packages-and-plugins/developing-packages
- Flutter platform integration: https://docs.flutter.dev/platform-integration
- Apple app lifecycle: https://developer.apple.com/documentation/uikit/managing-your-app-s-life-cycle
