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
  app_contract/        # stable app-facing contracts shared by app and features (route IDs/paths)
  core/                # app-agnostic technical infrastructure: errors, logging, lifecycle, config
  domain/              # optional shared business capabilities; no infrastructure
  design_system/       # tokens, theme, motion, components (Flutter SDK only)
  l10n/                # ARB files (+ generated output)
  features/<feature>/
    models/            # feature-owned app models shared by data and presentation
    data/              # repositories, data sources, DTOs, mapping
    domain/            # optional non-trivial feature business rules/entities
    presentation/      # screens, widgets, notifiers
  supabase/            # Supabase config, migrations, seed and Edge Functions (backend source)
test/                  # mirrors lib/
```

Dependency direction (enforce with a test that scans `lib/` imports; no extra package needed):

- `design_system` imports only Flutter/Dart SDK.
- `core` never imports `features`, `app`, `app_contract`, or `design_system`.
- `app_contract` contains only stable app-facing contracts (route names/paths and typed path builders); it imports no feature or app implementation and contains no GoRouter dependency.
- `features/x` imports its own `models`, `core`, `app_contract`, `design_system`, `l10n`, and explicitly shared domain modules; it never imports `app` or another feature's internals.
- `app` composes everything: it imports feature route declarations and maps `app_contract` route contracts to GoRouter. Nothing imports `app`.
- Cross-feature navigation uses `app_contract` constants/builders, never literal route strings or imports from another feature. Cross-feature business capabilities belong to a dedicated domain module, not `core`.

Starter-kit rule: `core`, `design_system`, and `l10n` contain nothing specific to one product. Product-specific values (brand, API base URL, feature list) enter only through `app/` and configuration.

## Layers

- **Presentation:** widgets and Notifiers (UI state). Never call Dio, Supabase clients, or storage directly.
- **Models:** feature-owned immutable app models live in `features/<feature>/models/`; they are the stable contract consumed by presentation. They are not transport DTOs and do not import Flutter, Supabase, or Dio.
- **Data:** repositories own remote/local fetching, caching, and DTO-to-model mapping. Supabase row maps/SDK response types and API DTOs stay in `data`; map them explicitly to feature models. Do not let widgets or Notifiers consume raw DTOs or Supabase response maps. Use hand-written parsing with explicit type checks and deliberate nullability.
- **Domain:** optional for non-trivial business rules/entities or a genuinely shared business capability. A model-only feature does not need use-case classes. Shared business logic belongs in a dedicated `lib/domain/<capability>/` module or its owning feature's public contract—not `core`. Shared domain modules must not depend on Flutter, Supabase, Dio, app composition, or feature presentation. Do not create use-case classes that merely wrap one repository call.
- **No abstract repository interfaces by default.** Dart classes are implicit interfaces; tests can `implements` the concrete class. Add an abstraction only for a real second implementation.
- **Routing contract:** GoRouter configuration and route registration live in `app/`; route names and path builders consumed by features live in `app_contract/`. Features never import `app/routes.dart`, GoRouter setup, or another feature.
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

## Backend ownership

Supabase is the default backend platform. Flutter talks to Supabase through `supabase_flutter` for Auth, Postgres Data API, Storage, Realtime, and Edge Function invocation. Use each service only when the feature requires it; do not add Realtime, Storage buckets, or backend tables speculatively. Detailed security and operating rules are in `backend-supabase.md`.

- Initialize one Supabase client during bootstrap and expose it through a Riverpod provider; repositories receive it through providers/constructors, never from widgets or global service locators.
- Supabase SDK owns Supabase HTTP/WebSocket traffic. Use Dio for non-Supabase third-party REST APIs or a documented integration that genuinely needs it; do not duplicate Supabase calls through Dio.
- Keep Supabase URL and publishable key as client configuration, not secrets. Never ship secret/service-role keys or Gemini API keys.
- Supabase exceptions are mapped at the repository boundary into the app's `AppFailure`; do not leak raw backend/provider messages to users.

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

- One configured `Dio` in `core/network` only for non-Supabase HTTP integrations: base URL from config, explicit connect/send/receive timeouts, JSON headers, locale header (`Accept-Language`) from active locale. Supabase requests use `supabase_flutter`.
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
- [M] Dependencies limited to the approved baseline: `flutter_localizations` (SDK), `intl`, `go_router`, `flutter_riverpod`, `supabase_flutter`, `dio` (for non-Supabase HTTP only), `shared_preferences`; `flutter_secure_storage` only for app-owned secrets that genuinely need device storage. Verify each package's current stable version, SDK constraint, maintenance, license, and breaking changes. Anything else needs a `DECISIONS.md` entry.
- [M] `analysis_options.yaml` strict; format, analyze, and tests clean at first commit.
- [M] Folder structure and architecture-boundary test, including the allowed `app_contract` dependency and prohibition on feature-to-app/feature-to-feature imports.
- [M] `l10n.yaml` + `app_en.arb` + `app_ar.arb`; locale resolution and persistence (see `localization-accessibility.md`).
- [M] Design-system skeleton: tokens, light/dark theme, motion tokens, one or two real components; app shell on `WidgetsApp.router` (see `design-system.md`).
- [M] Flavors and `--dart-define-from-file` config; distinct app IDs.
- [M] Error model, redacting logging, global error handlers.
- [M] Supabase project config, versioned SQL migrations, RLS on every exposed table, least-privilege grants, and backend security tests (see `backend-supabase.md`).
- [C] Auth providers, Storage buckets, Realtime channels, and Edge Functions are configured only when required; Gemini calls use an authenticated Edge Function and a server-side secret.
- [M] `.gitignore` covers keystores, `key.properties`, service config secrets, env files; no secret committed.
- [M] Settings screen with theme and language (real consumers of persisted preferences; reference feature, not placeholder).
- [M] CI runs format, analyze, and tests (see `quality.md`).
- [M] Four project docs created; README has setup/run/release commands.
- [C] Auth, notifications, deep links, crash reporting, analytics: only when required, each with ADR and privacy review.

## Checklist: architecture review

- [M] Import-boundary test passes. Verify by running the test.
- [M] Every state value has one owner. Verify by searching for duplicated providers/fields representing the same data.
- [M] No widget/Notifier calls Dio, Supabase, or storage directly. Verify by searching presentation code for SDK/client imports and direct data access.
- [M] No hardcoded route strings, design values, or user-facing strings in features. Verify route usage against `app_contract`, then grep plus analyzer/test.
- [M] No dependency outside approved list without ADR. Compare `pubspec.yaml` with `DECISIONS.md`.
- [R] Review largest widgets/Notifiers for mixed responsibilities.
