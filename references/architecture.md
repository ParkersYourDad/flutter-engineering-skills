# Architecture

## Contents
- Structure and dependency rules
- Layers
- Where code goes
- Config and environments
- State (Riverpod 3)
- Navigation (GoRouter)
- Errors
- Networking (Dio)
- Storage
- Code standards
- Project initialization checklist
- Architecture review checklist

## Structure and dependency rules

```
lib/
  main.dart            # bootstrap only: init, ProviderScope, runApp
  app/                 # App widget, router, root providers, composition
  core/                # app-agnostic infra: network, storage, errors, logging, config
  design_system/       # tokens, theme, motion, components (Flutter SDK only)
  l10n/                # ARB files (+ generated output)
  features/<feature>/
    data/              # repositories, data sources, DTOs
    domain/            # only if real business rules exist
    presentation/      # screens, widgets, notifiers
test/                  # mirrors lib/
```

Dependency direction (enforce with a test that scans `lib/` imports; no extra package needed):

- `design_system` imports only Flutter/Dart SDK.
- `core` never imports `features`, `app`, or `design_system`.
- `features/x` imports `core`, `design_system`, and `l10n`; never another feature's internals. Cross-feature needs go through routes (IDs in paths) or shared providers promoted to `core`.
- `app` composes everything. Nothing imports `app`.

Starter-kit rule: `core`, `design_system`, and `l10n` contain nothing specific to one product. Product-specific values (brand, API base URL, feature list) enter only through `app/` and configuration.

## Layers

- **Presentation:** widgets and Notifiers (UI state). Never call Dio or storage directly.
- **Data:** repositories own fetching, caching, and DTO-to-model mapping. DTOs use hand-written `fromJson`/`toJson` with explicit type checks; decide deliberately which fields are optional.
- **Domain:** add only when logic is shared across features or non-trivial (pricing rules, validation policies). Do not create use-case classes that wrap one repository call.
- **No abstract repository interfaces by default.** Dart classes are implicit interfaces; tests can `implements` the concrete class. Add an abstraction only for a real second implementation.
- **Models:** immutable (`final` fields); hand-write `==`/`hashCode`/`copyWith` only where equality or copying is used. Use Dart 3 sealed classes and pattern matching for variants and results.

## Where code goes

| Situation | Decision |
|---|---|
| Used by one feature | Stays in that feature |
| Needed by a second feature | Duplicate once if tiny; promote on the third real use (UI: second use if it is a visual primitive) |
| Visual primitive/pattern | `design_system/components` |
| Infrastructure with no UI (HTTP, storage, logging) | `core` |
| Business rule shared across features | Domain in a shared module under `core` or a dedicated feature; record in `DECISIONS.md` |
| Do not introduce | Service locators alongside Riverpod, screen base classes, global singletons, utils dumping grounds, mappers/factories without a second consumer |

## Config and environments

- Three flavors: `dev`, `staging`, `prod`. Android `productFlavors`; iOS schemes + xcconfig. Distinct application IDs/bundle IDs and display names so builds coexist.
- Non-secret config (base URL, flags) via `--dart-define-from-file`, read once in `core/config`. Verify the flag against current Flutter docs.
- Nothing in the app binary is secret. Client-shipped API keys are extractable; secrets must remain on a backend. CI secrets belong in CI secret storage only.

## State (Riverpod 3)

Verify the current `flutter_riverpod` version and migration notes on pub.dev/riverpod.dev first.

- Use `Notifier`, `AsyncNotifier`, and plain `Provider`/`FutureProvider`/`StreamProvider`. Avoid legacy providers (`StateProvider`, `StateNotifierProvider`, `ChangeNotifierProvider`); Riverpod 3 moved them to `legacy.dart`.
- **Ownership:** each state value has exactly one owning provider in the feature that owns the data. Widgets hold only ephemeral UI state (controllers, focus, tab index) in `StatefulWidget` State.
- **Reads:** `ref.watch` in build, preferably with `.select` for a single field. `ref.read` only in callbacks and Notifier methods. `ref.listen` for side effects (snackbars, navigation); never trigger side effects inside build.
- **Lifecycle:** choose deliberately: `.autoDispose` for screen-scoped state; keep-alive for app-wide state (auth, theme, locale). After every `await` in a Notifier, check `ref.mounted` before writing state; confirm the exact API for the pinned Riverpod release.
- **Async:** model results as `AsyncValue`; render through one shared widget (see `design-system.md`). Mutations (submit, delete) are Notifier methods that set loading/error explicitly and prevent double-submit.
- **Retries:** Riverpod 3 retries failed providers by default. Configure `retry` deliberately so auth failures and non-idempotent operations are not silently retried; verify the API for the pinned version.
- **DI:** infrastructure (`dioProvider`, `prefsProvider`, `clockProvider`) lives in `core`; tests and bootstrap override via `ProviderScope(overrides: ...)`. Await async-initialized dependencies before `runApp` and override them.
- **Optimistic updates:** only for fast, rarely failing actions. Always implement rollback and an error message.
- **Persistence:** persist only user preferences and session; hydrate before first frame to avoid a flash of defaults.

## Navigation (GoRouter)

Verify the pinned `go_router` version/API on pub.dev.

- Build `GoRouter` once inside a provider, never in build. Route paths/names are constants in `app/routes.dart`; no route string literals at call sites. Do not use generated route code. Validate and parse params manually; malformed input leads to not-found/error UI.
- Tabs: `StatefulShellRoute.indexedStack` preserves per-tab stacks. Use `go` to switch locations and `push` for stack-based detail/modal flows.
- Auth: one pure, loop-free `redirect` function driven by auth state via an appropriate refresh mechanism. Every redirect target must itself resolve without another redirect loop; handle loading/unknown auth state explicitly. Verify current GoRouter refresh APIs.
- Deep links: Android App Links (`assetlinks.json`) and iOS Universal Links (`apple-app-site-association` + Associated Domains) require server-side files and a verified domain. Test with `adb shell am start -a android.intent.action.VIEW -d <url>` and `xcrun simctl openurl booted <url>`.
- Back behavior: use `PopScope` for unsaved changes rather than deprecated `WillPopScope`. Verify Android predictive-back requirements against current Flutter/Android docs. iOS pages should preserve expected swipe-back behavior.
- State restoration: set `restorationScopeId` only for flows where losing state matters (e.g. long forms).

## Errors

- One sealed `AppFailure` hierarchy (network, timeout, unauthorized, server, validation, storage, unknown). Repositories convert exceptions at the data boundary; Notifiers expose `AsyncError` carrying an `AppFailure`.
- UI maps each failure to a localized, actionable message (+ retry where sensible). Never show raw exception text. Log the original with redaction.
- Catch narrowly. No empty `catch`. Set global handlers (`FlutterError.onError`, `PlatformDispatcher.instance.onError`) during bootstrap to log and route to crash reporting only if the product uses it.

## Networking (Dio)

- One configured `Dio` in `core/network`: base URL from config, explicit connect/send/receive timeouts, JSON headers, locale header (`Accept-Language`) from active locale.
- Interceptors: auth (attach token; on 401 refresh once using single-flight coordination, then retry, else sign out) → retry (idempotent methods only, bounded backoff and jitter) → logging (debug only, redact authorization, cookies, tokens, PII) → error mapping to `AppFailure`. Ensure ordering and retry behavior are tested.
- Cancel in-flight requests with `CancelToken` tied to provider disposal for screen-scoped work.
- Parse large payloads off the UI thread (`Isolate.run`/`compute`) only when profiling shows the work is slow.
- No certificate pinning unless required; it adds operational risk. If required, record an ADR including rotation plan.
- Offline: define per feature whether stale cache is shown, queued writes are allowed, or action is blocked. Do not build a sync engine without a requirement.

## Storage

| Data | Where |
|---|---|
| Tokens, credentials, keys | `flutter_secure_storage` (Keychain / Android Keystore-backed) |
| Theme, locale, flags, small preferences | `shared_preferences` |
| Small cached API data | JSON in app cache directory or prefs, with timestamp + version |
| Relational/queryable data | Decide with an ADR; codegen-based DBs are not part of the default stack |

Verify current APIs of both packages (`shared_preferences` has newer async APIs). Handle read failures (corrupt data, undecryptable secure storage after restore/backup): clear and recover, do not crash. Keychain items can survive reinstall on iOS: use a first-run marker and clear stale secure data when it is absent. Version persisted schemas and migrate or safely reset. Never store sensitive data in prefs or logs.

## Code standards

Enforce with tooling, not review: `flutter_lints` as a base plus strict analyzer modes (`strict-casts`, `strict-inference`, `strict-raw-types`) and `dart format`. Beyond analyzer coverage:

- `const` constructors wherever possible; widgets as classes, not helper methods returning widgets when extraction improves rebuild isolation.
- Split widgets when they have multiple responsibilities or build is hard to read, not at arbitrary line counts. Same for methods and files.
- Dispose every controller, focus node, subscription, and timer; prefer SDK widgets that own lifecycle.
- Avoid `!` on values that can be null in practice; avoid `dynamic`; do not use `late` to dodge initialization design.
- Imports: package-relative (`package:app/...`) inside `lib`; no relative cross-feature imports.
- Comments explain why, not what. Public design-system APIs get dartdoc.
- Naming: `snake_case` files, one primary type per file, feature-prefixed providers where naming collisions are possible.

## Checklist: project initialization

- [M] `flutter create --platforms=android,ios`; confirm no web/desktop platform directories.
- [M] SDK and Flutter constraints pinned in `pubspec.yaml`; versions verified on official sources and recorded in `docs/PROJECT.md`.
- [M] Dependencies limited to the approved baseline: `flutter_localizations` (SDK), `intl`, `go_router`, `flutter_riverpod`, `dio`, `shared_preferences`; `flutter_secure_storage` only when sensitive data exists. Verify each package's current version, SDK constraint, maintenance, and license. Anything else needs a `DECISIONS.md` entry.
- [M] `analysis_options.yaml` strict; format, analyze, and tests clean at first commit.
- [M] Folder structure and architecture-boundary test.
- [M] `l10n.yaml` + `app_en.arb` + `app_ar.arb`; locale resolution and persistence (see `localization-accessibility.md`).
- [M] Design-system skeleton: tokens, light/dark theme, motion tokens, one or two real components; app shell on `WidgetsApp.router` (see `design-system.md`).
- [M] Flavors and `--dart-define-from-file` config; distinct app IDs.
- [M] Error model, redacting logging, global error handlers.
- [M] `.gitignore` covers keystores, `key.properties`, service config secrets, env files; no secret committed.
- [M] Settings screen with theme and language (real consumers of persisted preferences; reference feature, not placeholder).
- [M] CI runs format, analyze, and tests (see `quality.md`).
- [M] Four project docs created; README has setup/run/release commands.
- [C] Auth, notifications, deep links, crash reporting, analytics: only when required, each with ADR and privacy review.

## Checklist: architecture review

- [M] Import-boundary test passes. Verify by running the test.
- [M] Every state value has one owner. Verify by searching for duplicated providers/fields representing the same data.
- [M] No widget calls Dio/storage directly. Verify by searching presentation code for Dio/SharedPreferences access.
- [M] No hardcoded route strings, design values, or user-facing strings in features. Verify with grep plus analyzer/test.
- [M] No dependency outside approved list without ADR. Compare `pubspec.yaml` with `DECISIONS.md`.
- [R] Review largest widgets/Notifiers for mixed responsibilities.
