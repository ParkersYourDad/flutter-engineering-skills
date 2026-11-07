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

## Existing-project adaptation

The architecture below is the reference for greenfield projects and for deliberate, approved changes—not a reason to restructure an established app.

Before proposing architecture changes, inventory the actual Flutter/Dart SDK and toolchain, folder/module boundaries, state management, routing, backend and data ownership, dependency graph, code generation, tests, CI, release setup, and documented decisions. Record what is healthy, unsupported, risky, or blocking.

- Preserve established state management, routing, backend, dependency injection, folder conventions, and code-generation workflow when they are maintained, testable, secure, and adequate for the requested work. Do not migrate to Riverpod, GoRouter, Supabase, FVM, or a preferred folder tree solely to match this reference.
- Implement new work using the project's existing conventions unless they create a concrete defect or conflict with an explicit product/security requirement. Do not introduce a second state manager, router, service locator, backend client, or parallel architecture.
- Prefer incremental boundary improvements. Do not combine a feature change with an unrelated architecture migration.
- A migration requires a concrete problem and a decision record covering current state, alternatives, user impact, scope, compatibility, staged plan, rollback/forward-fix, verification, and measurable acceptance. Obtain product-owner approval for material cost, schedule, or behavior trade-offs.
- If a current dependency or SDK is unsupported or has a relevant security issue, identify the specific evidence and propose the smallest safe remediation; do not silently replace the whole stack.

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
test/                  # mirrors lib/
integration_test/       # critical end-to-end journeys (when configured)
supabase/               # ROOT-LEVEL Supabase config, migrations, seed, tests and Edge Functions
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
| Business rule shared across features | Dedicated `lib/domain/<capability>/` module with no infrastructure dependencies; record in `DECISIONS.md` |
| Do not introduce | Service locators alongside Riverpod, screen base classes, global singletons, utils dumping grounds, mappers/factories without a second consumer |

## Config and environments

- **Greenfield default:** pin one exact Flutter stable release with FVM in `.fvmrc`; CI and local commands use that same SDK via `fvm flutter` / `fvm dart`. For existing projects, preserve the established reproducible toolchain manager and exact SDK pin; migrate to FVM only for a documented benefit or support requirement. Do not use beta/dev/master. Dart follows the selected Flutter SDK; `environment.sdk` must be compatible, not used to silently select a different toolchain. If the selected pinned SDK is unavailable, stop and report the toolchain mismatch rather than guessing which Flutter binary ran.
- Three flavors: `dev`, `staging`, `prod`. Android `productFlavors`; iOS schemes + xcconfig. Distinct application IDs/bundle IDs and display names so builds coexist.
- Non-secret config (base URL, flags) via `--dart-define-from-file`, read once in `core/config`. Verify the flag against current Flutter docs.
- Nothing in the app binary is secret. Client-shipped API keys are extractable; secrets must remain on a backend. CI secrets belong in CI secret storage only.

## Backend ownership

For greenfield products that need a backend, Supabase is the preferred default platform. Existing apps should retain their current backend (for example Firebase or a custom API) when it is supported and meets product/security needs; do not migrate backend providers merely to match this baseline. Flutter talks to Supabase through `supabase_flutter` only when Supabase is selected. Use each service only when the feature requires it; do not add Realtime, Storage buckets, or backend tables speculatively. Detailed Supabase security and operating rules are in `backend-supabase.md`.

- When Supabase is selected, initialize one client during bootstrap and expose it through the project's existing dependency-injection/state-management approach (a Riverpod provider when Riverpod is used); repositories receive it through constructors/providers, never from widgets or an untracked global service locator.
- Supabase SDK owns Supabase HTTP/WebSocket traffic. Use Dio for non-Supabase third-party REST APIs or a documented integration that genuinely needs it; do not duplicate Supabase calls through Dio.
- Keep Supabase URL and publishable key as client configuration, not secrets. Never ship secret/service-role keys or Gemini API keys.
- Supabase exceptions are mapped at the repository boundary into the app's `AppFailure`; do not leak raw backend/provider messages to users.

## State (Riverpod 3 greenfield baseline)

Riverpod 3 is the greenfield default, not a required migration target. In an existing app, retain its current state solution when it is healthy and consistent; do not add Riverpod alongside it. If a migration is justified, follow the Existing-project adaptation policy above and record a staged plan.

For projects using Riverpod, verify the current `flutter_riverpod` version and migration notes on pub.dev/riverpod.dev first.

- Use `Notifier`, `AsyncNotifier`, and plain `Provider`/`FutureProvider`/`StreamProvider`. Avoid legacy providers (`StateProvider`, `StateNotifierProvider`, `ChangeNotifierProvider`); Riverpod 3 moved them to `legacy.dart`.
- **Ownership:** each state value has exactly one owning provider in the feature that owns the data. Widgets hold only ephemeral UI state (controllers, focus, tab index) in `StatefulWidget` State.
- **Reads:** `ref.watch` in build, preferably with `.select` for a single field. `ref.read` only in callbacks and Notifier methods. `ref.listen` for side effects (snackbars, navigation); never trigger side effects inside build.
- **Lifecycle:** choose deliberately: `.autoDispose` for screen-scoped state; keep-alive for app-wide state (auth, theme, locale). After every `await` in a Notifier, check `ref.mounted` before writing state; confirm the exact API for the pinned Riverpod release.
- **Async:** model results as `AsyncValue`; render through one shared widget (see `design-system.md`). Mutations (submit, delete) are Notifier methods that set loading/error explicitly and prevent double-submit.
- **Retries:** Riverpod 3 retries failed providers by default. Configure `retry` deliberately so auth failures and non-idempotent operations are not silently retried; verify the API for the pinned version.
- **DI:** infrastructure (`dioProvider`, `prefsProvider`, `clockProvider`) lives in `core`; tests and bootstrap override via `ProviderScope(overrides: ...)`. Await async-initialized dependencies before `runApp` and override them.
- **Optimistic updates:** only for fast, rarely failing actions. Always implement rollback and an error message.
- **Persistence:** persist only user preferences and session; hydrate before first frame to avoid a flash of defaults.

## Navigation (GoRouter greenfield baseline)

GoRouter is the greenfield default, not a required migration target. In an existing app, retain its current router/navigation approach when it is healthy; do not introduce a second router. If a migration is justified, follow the Existing-project adaptation policy above and record a staged plan.

For projects using GoRouter, verify the pinned `go_router` version/API on pub.dev.

- Build `GoRouter` once inside a provider, never in build. Route names and path builders are defined in `app_contract/`; GoRouter route registration and page construction live in `app/`. No route string literals at feature call sites and no generated route code. Validate and parse params at the routing boundary; malformed input leads to not-found/error UI.
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
- Interceptors: add service-specific authentication only when the external API requires it; never forward a Supabase session token to an unrelated host. Handle that service's 401 according to its own contract—do not sign the user out of Supabase merely because a third-party API returned 401. Retry only idempotent operations with bounded backoff/jitter; logging is debug-only and redacts authorization, cookies, tokens, and PII; map errors to `AppFailure`. Test interceptor ordering and retry behavior.
- **Retry policy:** classify failures before retrying. Do not retry validation/client errors (ordinary 4xx), authorization failures, malformed responses, or cancellations. Consider transient connection failures/timeouts, HTTP 408, HTTP 429, and selected 5xx responses retryable only when the endpoint contract permits it. For 429 (and 503 when supplied), honor a valid `Retry-After` within the request's remaining deadline.
- Use a small bounded attempt count and capped exponential backoff with **full random jitter**; inject the random source/clock in tests. Set a total elapsed-time deadline, not only a per-attempt timeout. Cancel pending delays and attempts when the request is cancelled or its owning provider is disposed. Ensure request bodies can be replayed before retrying.
- Never automatically retry a non-idempotent write unless the server provides a documented idempotency contract and the same idempotency key is reused for every attempt. A client-generated key alone does not make a server operation idempotent. Avoid stacking retries in Dio, Riverpod provider retry, and repository code; assign one retry owner per operation and configure Riverpod provider retry deliberately.
- Test retry classification, attempt limits, jitter bounds, `Retry-After`, deadline exhaustion, cancellation, body replay, idempotency, and that permanent failures are not retried. Logging is debug-only and redacts authorization, cookies, tokens, and PII; map errors to `AppFailure`.

### Offline behavior is feature-specific

- Decide explicitly per feature whether offline use is unsupported, read-only from a bounded/stale cache, or supports queued writes and later synchronization. State the freshness contract and what the user can do while offline.
- **Offline-first is conditional**, not a default architecture. Introduce a local source of truth, durable write queue, synchronization, conflict resolution, and connectivity recovery only when product requirements demand them.
- Do not treat a connectivity signal as proof that a host is reachable. The request result is authoritative. Handle reconnects without duplicate submissions; queued writes require idempotency and a defined conflict policy.
- For user-visible mutations such as like/save/follow, use optimistic UI only when the action is reversible or has a clear reconciliation contract: update immediately, retain enough prior state to roll back, expose pending/failure state when useful, and reconcile with the authoritative server response. Prevent rapid duplicate submissions; use server-supported idempotency for writes where available. Define behavior for conflicting updates, stale responses, account switching, and process death. Do not present an unconfirmed mutation as permanently successful.
- Test offline entry, stale-data labeling, optimistic success and rollback, failed/queued writes, process restart with queued work, reconnect, duplicate delivery, conflict resolution where applicable, and cancellation/account switching.
- **Prefetching is conditional and budgeted:** prefetch only when navigation/interaction signals provide a credible next destination and the expected latency benefit justifies the network, memory, CPU, and battery cost. Prefer small metadata or appropriately sized thumbnails; do not eagerly fetch full-resolution media or entire feeds by default. Respect data-saver/low-data settings where available, current connectivity constraints, authentication/authorization, and user privacy. Deduplicate requests, cap concurrency and cache size, assign TTL/invalidation rules, and cancel work when intent changes, the route is left, or the account changes. Never let speculative requests delay foreground work.
- Measure prefetch hit/usefulness rate, bytes fetched but never used, cache hit rate, foreground latency, memory, and battery impact on representative devices/networks. Add prefetch only when measurement shows a net user benefit.
- Cancel in-flight requests with `CancelToken` tied to provider disposal for screen-scoped work.
- Parse large payloads off the UI thread (`Isolate.run`/`compute`) only when profiling shows the work is slow.
- No certificate pinning unless required; it adds operational risk. If required, record an ADR including rotation plan.
- Offline: define per feature whether stale cache is shown, queued writes are allowed, or action is blocked. Do not build a sync engine without a requirement.

## Storage

| Data | Where |
|---|---|
| App-owned credentials/secrets (only when genuinely needed) | `flutter_secure_storage` (Keychain / Android Keystore-backed); Supabase session tokens remain managed by the Supabase SDK |
| Theme, locale, flags, small preferences | `shared_preferences` |
| Small cached API data | JSON in app cache directory or prefs, with timestamp + version |
| Relational/queryable data | Decide with an ADR; codegen-based DBs are not part of the default stack |

Verify current APIs of both packages (`shared_preferences` has newer async APIs). Do not manually duplicate Supabase session/token storage; use the SDK's supported persistence. Handle read failures (corrupt data, undecryptable secure storage after restore/backup): clear and recover, do not crash. Keychain items can survive reinstall on iOS: use a first-run marker and clear stale secure data when it is absent. Version persisted schemas and migrate or safely reset. Never store sensitive data in prefs or logs.

## Code standards

Enforce with tooling, not review: `flutter_lints` as a base plus strict analyzer modes (`strict-casts`, `strict-inference`, `strict-raw-types`) and `dart format`. Beyond analyzer coverage:

- `const` constructors wherever possible; widgets as classes, not helper methods returning widgets when extraction improves rebuild isolation.
- Split widgets when they have multiple responsibilities or build is hard to read, not at arbitrary line counts. Same for methods and files.
- Dispose every controller, focus node, subscription, and timer; prefer SDK widgets that own lifecycle.
- Avoid `!` on values that can be null in practice; avoid `dynamic`; do not use `late` to dodge initialization design.
- Imports: package-relative (`package:app/...`) inside `lib`; no relative cross-feature imports.
- Comments explain why, not what. Public design-system APIs get dartdoc.
- Naming: `snake_case` files, one primary type per file, feature-prefixed providers where naming collisions are possible.

## Official engineering references

- Flutter UI and framework guidance: https://docs.flutter.dev/ui
- Flutter adaptive and responsive design: https://docs.flutter.dev/ui/adaptive-responsive
- Flutter performance practices: https://docs.flutter.dev/perf/best-practices
- Dart Effective Dart: https://dart.dev/effective-dart
- Dart style guide: https://dart.dev/effective-dart/style
- Dart API design guide: https://dart.dev/effective-dart/design
- Dart usage guide: https://dart.dev/effective-dart/usage

## Checklist: project initialization

- [M] Pin the approved stable SDK with FVM first, then create the project with `fvm flutter create --platforms=android,ios`; confirm no web/desktop platform directories.
- [M] Exact Flutter stable SDK pinned in `.fvmrc` and CI; Dart/Flutter constraints in `pubspec.yaml` are compatible; versions verified on official sources and recorded in `docs/PROJECT.md`.
- [M] For greenfield projects, keep the baseline minimal: `flutter_localizations` (SDK), `intl`, `go_router`, `flutter_riverpod`, and `shared_preferences` only for actual preferences. Add `supabase_flutter` only when a new product needs a backend; add `dio` only for non-Supabase HTTP integrations; add `flutter_secure_storage` only for app-owned credentials or when the session-storage threat assessment requires secure session persistence. In existing projects, review new/changed dependencies and retain healthy existing dependencies; do not treat the greenfield list as a migration whitelist. Verify each selected or changed package's current stable version, SDK constraint, maintenance, license, advisories, and breaking changes. Record material additions or migrations in `DECISIONS.md`.
- [M] `analysis_options.yaml` strict; format, analyze, and tests clean at first commit.
- [M] Folder structure and architecture-boundary test, including the allowed `app_contract` dependency and prohibition on feature-to-app/feature-to-feature imports.
- [M] `l10n.yaml` + `app_en.arb` + `app_ar.arb`; locale resolution and persistence (see `localization-accessibility.md`).
- [M] Design-system skeleton: tokens, light/dark theme, motion tokens, one or two real components; app shell on `WidgetsApp.router` (see `design-system.md`).
- [M] Flavors and `--dart-define-from-file` config; distinct app IDs.
- [M] Error model, redacting logging, global error handlers.
- [C] If the product requires a backend: Supabase is the default platform; keep project config, migrations, tests, and Edge Functions under the repository-root `supabase/` directory. Every exposed table needs RLS, least-privilege grants, and passing backend security tests (see `backend-supabase.md`). If no backend is required, do not create an empty Supabase project or placeholder migrations.
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
- [M] Every new or changed dependency has a justified decision record and passes dependency admission. Review existing dependencies for maintenance, security, licensing, and compatibility; do not migrate healthy dependencies solely to match the greenfield baseline.
- [R] Review largest widgets/Notifiers for mixed responsibilities.
