# Quality: Testing, Performance, Security, Platform, Release and Gates

## Contents
- Verification commands
- Testing
- Performance
- Security and privacy
- Dependencies and upgrades
- Android and iOS
- CI/CD
- Device matrix
- Production operations and reliability
- Gates

## Verification commands

Run commands and read output; report results, not intentions.

```sh
fvm --version
fvm flutter --version
fvm dart format --output=none --set-exit-if-changed .
fvm flutter analyze
python3 scripts/check_rtl_directionality.py --root .  # vendor this checker from the skill repository into the app
python3 scripts/validate_skills.py
fvm flutter test
fvm flutter test integration_test        # requires emulator/simulator/device
fvm flutter pub outdated                 # informational dependency health
fvm flutter build apk --release
fvm flutter build appbundle --release
fvm flutter build ipa --release          # macOS + signing only
```

Check current flag names with `flutter build --help` before relying on them.

### Dart static-analysis baseline

Every maintained Flutter app must commit an explicit `analysis_options.yaml`; do not rely on whichever defaults happen to ship with the current SDK or a transitive lint package. Enable Dart's sound static-analysis modes:

```yaml
analyzer:
  language:
    strict-casts: true
    strict-inference: true
    strict-raw-types: true
 ```

Keep the project's selected lint rules in the same file (or a deliberately included, pinned lint package). Do not silence diagnostics globally, add broad exclusions, or use file-level ignores without a narrow explanation and a follow-up condition. Prefer fixing the underlying type/API issue. When an ignore is unavoidable, scope it to the smallest line/block and explain why.

- [M] Verify the committed analyzer configuration contains all three strict modes.
- [M] Run `fvm flutter analyze` on the pinned SDK; warnings/errors must be resolved or explicitly classified with evidence. Do not claim strict type safety merely because analysis exits successfully if strict modes are not enabled.
- [M] CI runs the same analyzer configuration and pinned SDK as local development.
- [R] Review newly introduced `dynamic`, raw collection types, unchecked casts, and broad `Object?` conversions during code review.


## Testing

Test behavior and requirements by risk. Do not chase coverage percentages or test implementation details.

- **Unit:** pure logic, parsers/DTO mapping (including malformed input), validators, formatters, failure mapping.
- **State:** Notifiers via `ProviderContainer` with overrides; `addTearDown(container.dispose)`; assert loading → data/error and double-submit protection.
- **Widget:** component states/variants; screens in loading/empty/error/data; interactions; semantics; each in `en`/`ar`, light/dark, text scale 1.0 and 2.0 for shared components. For Arabic coverage, include RTL geometry, longer translated strings, mixed Arabic/Latin values (URLs, email, phone, identifiers), punctuation, caret/input behavior, and ICU plural/select cases used by the product.
- **Navigation:** redirects, deep-link parsing, malformed params, back behavior, tab-stack preservation.
- **Data:** repository + fake HTTP adapter: success, timeout, 401 refresh, 5xx, malformed JSON, cancellation.
- **Golden:** shared components and a few key screens only; generate on one CI platform (goldens differ across OSes), load real fonts, review diffs rather than regenerating blindly.
- **Integration:** critical journeys only (first launch, auth if present, core flow, language/theme switch, offline recovery), deterministic data, no arbitrary sleep; use `pumpAndSettle` with care and explicit finders.
- **Lifecycle/recovery:** test pause/resume, route disposal, cancellation reaching the request, overlapping requests where stale results could win, process restart for recoverable work, and sign-out/account switch. Verify no duplicate timer/subscription or replay under the wrong account.
- **Architecture/localization tests:** import boundaries, ARB key parity, no hardcoded strings (see other references).
- **Fakes over mocks:** hand-written fakes; use `mocktail` only for a real need recorded in decisions. `mockito` requires forbidden code generation. Inject clock, random, and connectivity for deterministic tests.
- **Defect protocol:** reproduce → root cause → fix cause → regression test → rerun affected tests → full suite if shared code changed → search for same pattern elsewhere.

## Performance

Measure before changing code. "Optimized", "smooth", and "fast" are claims that require repeatable evidence.

### Measurement protocol

- Profile on a physical device in **profile mode** for Flutter UI/raster diagnosis; use a release build for release-only behavior and final smoke checks. Debug/emulator timings are not performance evidence.
- Test the lowest supported device first. Also test a representative higher-refresh device when the product targets devices with 90 Hz/120 Hz displays.
- Record device model/chipset, OS version, refresh rate, Flutter version, build mode, app version, test data size, network condition, scenario, run count, and measurement tool. Compare like with like.
- Repeat representative runs sufficiently to distinguish a real change from noise. Record sample count and report median (P50) and tail latency (P95; P99 only when sample size supports it). Keep a small baseline table in `REQUIREMENTS.md` or release evidence; do not create a separate performance document by default.
- Use DevTools Performance (Flutter frames chart, Frame analysis, and Timeline), CPU Profiler, Memory, and Network views as relevant. Inspect UI-thread and raster-thread work separately. Flutter's performance overlay does not show the platform thread; when plugin/native work is suspected, use the relevant Android Studio profiler, Xcode Instruments, or Perfetto trace rather than attributing the delay to Dart automatically. Identify whether the bottleneck is Dart CPU, build/layout/paint, raster work, platform/plugin execution, image decode, I/O, or network before changing code.
- For frame evidence, capture `FrameTiming` data where appropriate (`buildDuration`, `rasterDuration`, and `totalSpan`). Interpret paired UI/raster work as a pipelined frame process; do not blindly add the two durations or treat either one alone as the complete user-visible frame latency.

### Rendering and interaction

- Define frame budget from the tested display refresh rate: `1000 / Hz` milliseconds (about 16.67 ms at 60 Hz, 11.11 ms at 90 Hz, and 8.33 ms at 120 Hz). Evaluate UI and raster frame timing against the actual display budget; do not use a universal 16 ms target on every device.
- Track janky-frame percentage and P50/P95 UI and raster frame times during defined journeys (scrolling, navigation, opening sheets, typing, and representative animations). The project sets its own acceptable limits in `PERF-*`; do not invent a universal pass percentage.
- Check first-use animations and shader-heavy screens separately from warmed-up repeats. DevTools can identify frames involving shader compilation; classify these explicitly and verify the actual target devices and renderer. Impeller reduces runtime shader-compilation work through build-time shader compilation, but do not assume this eliminates every first-use rendering issue. Keep Flutter's supported renderer defaults unless device evidence and a documented decision justify a change; never force renderer flags or add custom shader warm-up machinery as generic optimizations.
- Prefer lazy lists/slivers for large collections, stable keys where state identity matters, bounded image decoding/cache, localized rebuilds, and cancellation of screen-scoped work. Paginate large data rather than loading it all.
- For speculative prefetching, compare foreground latency and cache usefulness against unused bytes, memory, and battery; verify cancellation, request deduplication, bounded concurrency/cache, TTL/invalidation, and that foreground requests take priority. Do not add prefetch as a default optimization.
- For optimistic interactions, verify immediate visual response, duplicate-tap handling, server reconciliation, rollback on rejection/timeout, stale-response ordering, and offline/account-switch behavior. Test the mutation contract, not just the optimistic animation.
- Avoid expensive `saveLayer`, unnecessary opacity/clipping, intrinsic layout passes in large scrolling content, and layout-affecting animations when a transform/opacity animation is sufficient. Do not add `RepaintBoundary`, caching layers, isolates, or custom render objects without profiling evidence.
- Do not perform network calls, expensive parsing, sorting, image work, or repeated allocations in `build()`. Move CPU-heavy work off the UI isolate only after profiling identifies it as a bottleneck.

### Startup, memory, size, and energy

- Measure **cold start and warm start separately**. Define "first interactive" as the point the user can complete the first meaningful action; first frame alone is not enough. Record P50/P95 and test on the lowest supported device.
- Measure memory after warm-up and after repeated navigation through the same journeys. Look for retained screens/controllers/subscriptions, unbounded image/data caches, duplicate listeners, and growth that does not settle after normal garbage collection. High memory once is not itself proof of a leak.
- Track release artifact size and its change from the previous release. Use Flutter's `--analyze-size` report to find the responsible Dart packages, native libraries, fonts, and assets before removing dependencies or compressing assets.
- When a critical journey depends on a backend or third-party API, measure client-observed request latency (P50/P95), request count, payload bytes, retry/timeout/error rates, and behavior on representative slow or unreliable networks. Measure the complete request, not just ping time. Check pagination, duplicate requests, cache behavior, and whether stale/offline behavior matches the feature contract.
- For products with background work, media, location, frequent sync, or realtime subscriptions, test idle/background behavior, request frequency, stream disposal, battery/thermal impact, and pause/resume recovery. Do not poll or keep animations/timers active when the feature is not visible or needed.
- Define budgets per product in `REQUIREMENTS.md`: device class, mode, scenario, dataset, network condition, metric, percentile, threshold, and baseline. A change that regresses a critical journey beyond its approved budget must be fixed or explicitly accepted by the product owner with a recorded reason.

Useful tools, not blanket rules (never substitutes for measurement): `const` widgets where applicable, `ref.watch(...select)` when it meaningfully narrows a dependency, lazy lists, decode-size-aware images, bounded caches, deferring non-critical work without delaying first interaction, and disposing/cancelling work when no longer needed. Do not add `.select()` mechanically to every provider or optimize rebuilds without identifying an actual dependency/rebuild concern.

Release optimization: verify obfuscation/minification and `--split-debug-info` behavior in release builds. Archive symbol files privately for crash diagnosis; do not publish them as public artifacts.

## Backend security (Supabase and Gemini)

Apply `backend-supabase.md` to every backend feature. The following are release-blocking controls:

- [M] Every table in an exposed schema has RLS enabled before client access is granted. Policies enforce ownership/tenant/role authorization per operation; `TO authenticated` alone is not authorization.
- [M] Every view is reviewed for RLS behavior; use security-invoker semantics where supported or restrict exposure. Review every privileged SQL function for SECURITY DEFINER and EXECUTE grants.
- [M] No Supabase secret/service-role key or Gemini API key exists in Flutter source, assets, build defines, CI artifacts, logs, or Git history. Client receives only the project URL and publishable key.
- [M] Edge Functions that serve signed-in users validate the user JWT and authorize the requested resource. Keep platform JWT verification enabled unless a documented webhook/service-to-service design requires otherwise; `apikey` alone is not user authentication.
- [M] Gemini calls occur only in Edge Functions. Secrets are configured in Supabase secret storage; local secret files are ignored by Git. Apply per-user quotas/rate limits, input validation, bounded output/token limits, timeouts, and safe error mapping.
- [M] No `service_role`/secret-key database access is used for ordinary user requests; use the caller-scoped client and RLS. Any privileged path has explicit authorization, narrow scope, and tests.
- [M] Migrations are versioned, reviewed, and tested against a local/staging database before production. Verify RLS policies as anon, authenticated owner, and authenticated non-owner where applicable.
- [M] Gemini request limits and quotas use atomic shared state, not in-memory per-instance counters; provider costs and abuse are monitored.

## Security and privacy

Use separate security baselines for each trust boundary:

- **Flutter mobile clients:** current OWASP MASVS control groups and MASTG test guidance. Choose a risk-appropriate MAS profile; MASVS is a client-side standard and does not verify the remote API/backend by itself.
- **Backend and web/API services:** OWASP ASVS 5.0.0 (or the latest stable version verified at task time) for application/service controls, plus the OWASP API Security Top 10 for API-specific threat coverage. Apply the controls relevant to the actual API architecture; Supabase RLS checks are necessary but do not replace API/service security verification.
- **Organization-wide secure development:** use NIST SSDF and OWASP SAMM as process-improvement references where organizational maturity is in scope; do not claim certification or blanket compliance merely because a checklist exists.

Select risk-appropriate verification depth for each product. This is an engineering baseline, not a claim of OWASP certification or legal compliance. Review privacy, payments, children’s data, health, and regulated-data requirements with qualified specialists where applicable.

### Threat model and data handling

- [M] For every non-trivial feature, identify the data involved, where it travels, who can call it, which component is trusted, and what happens if the operation is abused. Explicitly consider account/tenant boundaries, object-level authorization (BOLA/IDOR), replay/duplicate requests, automation, quota/cost abuse, injection, and data leakage.
- [M] Classify data before choosing storage or telemetry: public, internal, personal, sensitive, credentials. Collect only what the feature needs; document purpose, access, retention, deletion, and external processors in the project requirements.
- [M] Treat the app, deep links, intents, clipboard, files, network responses, push payloads, and AI/model output as untrusted input. Validate type, size, range, format, ownership, and allowed state at the trust boundary. Client-side validation improves UX but never replaces server-side validation/authorization.
- [M] Enforce object-level authorization on the server for every read/write/action. A hidden button, route guard, client-supplied owner ID, role, price, quota, or decoded-but-unverified JWT is not authorization.
- [M] Use parameterized database operations. Never interpolate untrusted input into SQL, shell commands, file paths, or upstream URLs. For backend URL fetching, restrict destinations to an explicit host/protocol allowlist and defend against SSRF, redirects to private/internal addresses, and DNS rebinding.
- [C] For file upload features, enforce byte-size limits and allowed formats server-side; inspect actual content rather than trusting extension or client MIME type. Define private/public access, ownership, retention, and deletion. Add malware scanning when the threat model and file types justify it.

### Secrets, sessions, and local data

- [M] No secrets, signing material, private keys, or service-role credentials in source control, Flutter assets, app binaries, build defines, Remote Config, analytics, crash reports, or logs. Client-embedded values are extractable; obfuscation is not secret storage.
- [M] Supabase publishable keys are public identifiers, not authorization. Protect exposed data with least-privilege grants, RLS, and server-side checks. Never embed Supabase secret/service-role keys or Gemini API keys.
- [M] Supabase session tokens remain under the SDK's supported session-persistence API; do not create a second app-owned token store. Do not assume SDK-managed storage is encrypted: Supabase Flutter v2 defaults to SharedPreferences, and current v3 documentation uses SharedPreferences-backed async storage by default. Record the session-at-rest risk decision. For higher-sensitivity apps, use the pinned SDK version's supported secure-storage adapter (v2 `LocalStorage`; v3 `AuthAsyncStorage`/`asyncStorage`) and verify both session and auth-flow/PKCE verifier persistence across restart and deep-link return. App-owned credentials use secure storage. The prohibition on sensitive preferences applies to app-owned storage; document any SDK-default exception. Secure storage reduces exposure at rest; it does not make data safe on a compromised/unlocked device or replace authorization.
- [M] Clear user-scoped caches, files, providers, subscriptions, and in-memory state on sign-out/account switch. Prevent previous-account data from flashing during the next account's bootstrap.
- [M] Redact authorization headers, cookies, tokens, passwords, API keys, session IDs, prompts, personal data, signed URLs, and sensitive payloads from logs. Use request IDs and safe event categories instead. Test the redaction layer.
- [C] Protect sensitive screens from task-switcher previews, screenshots, clipboard exposure, and notification previews when the product's data classification requires it. Apply platform controls narrowly; do not block screenshots globally without a product/security reason.
- [C] Biometric checks are a local device-user-presence gate, not proof of server identity or permission. Root/jailbreak detection, app attestation, and anti-tampering are conditional defense-in-depth controls; never rely on them instead of server authorization.

### Network and platform security

- [M] Use HTTPS for every production endpoint. Reject invalid certificates; never install permissive certificate callbacks or disable hostname validation. Any debug-only cleartext exception must be scoped to explicit development hosts and absent from release variants.
- [M] Validate deep links and Android intents as untrusted external input. Explicitly review exported Android components, intent filters, content providers, URL schemes, Associated Domains, and custom URL handlers. Expose only what the product needs.
- [M] Android: review manifest permissions, exported components, backup/data-extraction rules, network security config, WebView use (if any), and R8/minification in a release artifact. Exclude secrets and sensitive app data from backups where appropriate; decide recovery behavior deliberately.
- [M] iOS: verify accurate usage descriptions, entitlements, Keychain accessibility, Associated Domains, and the app's `PrivacyInfo.xcprivacy` manifest. Review required-reason API declarations and privacy manifests/signatures for all included third-party SDKs against Apple's current required SDK list. Invalid manifests can block submission.
- [M] Ask for permissions in context, only when needed. Provide a useful denied/restricted path and a manual alternative where possible; do not repeatedly prompt after denial.
- [C] Certificate pinning, biometric-gated sensitive actions, device attestation, and anti-tampering require a documented threat-based decision, recovery/rotation plan, and false-positive handling.

### Dependency and CI supply-chain security

- [M] Review direct and transitive dependencies for purpose, maintenance, license, SDK compatibility, advisories, and unnecessary platform permissions before adoption and at release. `flutter pub outdated` reports version status; it is not a vulnerability scanner.
- [M] Commit the app's `pubspec.lock`; keep local and CI Flutter SDK versions aligned. Use reproducible dependency resolution and review lockfile changes rather than accepting unexplained transitive upgrades.
- [M] GitHub Actions: grant the workflow/job only the `GITHUB_TOKEN` permissions it needs; pin third-party actions to verified full commit SHAs; protect production environments and require approval for production deployment/migrations.
- [M] Never expose production secrets to untrusted fork pull requests or untrusted code. Do not check out and execute untrusted PR code in a privileged `pull_request_target` workflow. Use OIDC/short-lived credentials where the target service supports it; never print secrets or upload them in build artifacts.
- [M] Run secret scanning and dependency/security checks in CI where available; treat any exposed credential as compromised: revoke/rotate it, inspect usage, remove the source, and review Git history/artifacts. Deleting the visible line alone is not remediation.

### Privacy and store obligations

- [M] Keep privacy disclosures, consent, retention, deletion, analytics/diagnostics, AI-provider sharing, App Store privacy answers, and Google Play Data safety answers aligned with actual runtime behavior and all third-party SDKs.
- [M] If accounts can be created, implement in-app account deletion and define deletion of related database rows, Storage objects, and provider-held data where applicable. Do not assume deleting an Auth user cascades through every system.
- [M] Verify current Google Play and Apple submission rules, target SDK/Xcode requirements, required SDK manifests/signatures, and permission declarations at each release. Do not rely on a date or requirement copied from an old project.
- [M] Security testing must include negative authorization cases, malformed/oversized input, session expiry/revocation behavior, secret/log scans, and release-artifact review. Add platform/penetration tests according to the chosen risk profile.

## Dependencies and upgrades

Admission checklist per package, recorded in `DECISIONS.md`: purpose; SDK alternative considered; official docs read; Dart/Flutter constraints compatible; recent releases and responsive maintainers; license compatible with distribution; known advisories checked; transitive dependencies reviewed; version constraint chosen (caret ranges; commit app lockfile). The baseline stack is a default, not a blanket whitelist: a new package may be admitted when it solves a real requirement better than the SDK or an existing dependency and passes every admission check. Do not add packages speculatively, duplicate existing capabilities, or adopt a package solely because an AI agent suggested it. Record rejected alternatives when the decision is non-obvious.

Upgrade policy: upgrade deliberately in a dedicated change (SDK first, then packages), read changelogs/migration guides, run full verification, never blind `pub upgrade --major-versions` in a feature change. Review monthly for security fixes and quarterly for SDK/platform updates. Watch deprecations (analyzer warnings are early signal), and annual platform changes (Android target API and Xcode/iOS SDK requirements for store submission); verify current dates in Google Play and App Store Connect docs.

## Android and iOS

- **Minimums:** set minimum Android API and iOS deployment target from Flutter's current supported baseline and product audience; record in `docs/PROJECT.md`; verify current docs.
- **Both:** safe areas/cutouts/Dynamic Island, edge-to-edge system bars with correct icon contrast per theme, keyboard insets, orientation policy decided and enforced, no hardcoded status-bar heights.
- **Android:** application ID per flavor, adaptive/monochrome launcher icon, splash via platform Splash Screen API (verify Flutter setup), permissions only if used, predictive-back decision, notification channels/permission (Android 13+) if notifications exist, App Links verification.
- **iOS:** bundle ID per flavor, icon set without transparency, launch screen, `Info.plist` usage strings, background modes only if used, Associated Domains, push entitlements if used, minimum deployment target consistent across Runner and Pods.
- **Signing:** keystore and `key.properties` / Apple certificates and profiles stay out of repo; CI gets them from secrets; use Play App Signing; document recovery for lost upload key.
- **Store readiness:** versioning (`version: x.y.z+build`, monotonically increasing build), screenshots, metadata, privacy policy URL, Play Data safety / Apple App Privacy answers matching actual behavior, content rating, reviewer demo access when login exists. Publishing is consequential and requires explicit user authorization.

## CI/CD

GitHub Actions should make routine checks repeatable without giving every workflow production access.

- Every PR runs format check, analyze, unit/widget tests, architecture/localization checks, and an Android debug build. Run golden tests on one controlled runner OS. On macOS, compile and test the iOS simulator target without production signing; do not make iOS verification depend on having production certificates available to PR jobs.
- When Supabase is used, run local database migration and pgTAP/RLS tests in CI for changes to migrations, policies, or database functions; run Edge Function type/tests for function changes. Keep Docker/CLI setup isolated and pin the toolchain used by CI.
- Pin the Flutter SDK to the project's `.fvmrc` version and use the same SDK in local development and CI. Pin third-party actions to verified full commit SHAs, not mutable tags alone; review updates deliberately.
- Set least-privilege workflow/job `permissions` explicitly (read-only by default); grant write/deploy permissions only to the job that needs them.
- Do not pass secrets to fork PRs or untrusted code. Avoid privileged `pull_request_target` workflows that execute PR-controlled code. Keep signing/deployment secrets in protected GitHub Environments; require approval for production deploys and migrations.
- Prefer OIDC/short-lived credentials when supported by the destination service. Masking is not a substitute for not printing, persisting, or uploading secrets.
- Cache pub dependencies safely; do not share writable caches from untrusted jobs with privileged release jobs. Retain and restrict access to build artifacts and symbol files.
- Release workflow: protected tag/release trigger, production flavor, signed Android/iOS release artifacts on the appropriate platform runners, production credentials from protected secrets only, no debug/test credentials or verbose logging, and a manual approval gate before publication. PR jobs must never receive production signing material. Keep crash-symbol files private and retrievable for the exact release.
- Run repository-owned validator self-tests in CI, including positive and negative cases for metadata and local-link boundaries; keep these checks independent of Flutter SDK availability.
- Validate workflow syntax and permissions; a local YAML parse is not a GitHub Actions run. Report actual workflow run IDs/results when available.

## Device matrix

Maintain a short table in `docs/PROJECT.md`: lowest + current Android and iOS versions, small/regular/large phone, tablet/foldable if supported, light/dark, `en`/`ar`, text scale 1.0/2.0, gesture vs button navigation, offline/flaky network, low-memory. Use emulators/simulators for repeatability, physical devices for performance, haptics, notifications, biometrics, camera/permissions. Every release report states which rows were tested and which were not.

## Production operations and reliability

Apply this section to production apps and services; mark genuinely unused capabilities N/A with a reason. Production readiness is not complete at "the build passed".

### Service objectives and observability

- [M] Identify critical user journeys and their service dependencies. Define a small set of measurable SLIs and product-specific SLOs for availability, successful completion, latency, and data freshness where relevant. Define the measurement window and exclusions; do not invent a universal uptime target.
- [M] Define alert thresholds and an accountable owner for each critical SLO. Use error budgets to inform release risk only when a meaningful SLO exists; do not turn metrics into vanity dashboards or individual performance scores.
- [M] Mobile observability: monitor crash-free users/sessions and Android ANRs, startup and critical-journey failures, app version/OS/device distribution, and safe request failure categories. Select analytics/crash SDKs only after reviewing exact SDK versions, automatic collection defaults, data fields, subprocessors, destinations/regions, retention/deletion, platform manifests, license, and user controls. Disable collection that is not required; do not assume an SDK is privacy-safe because it is popular or has a consent toggle.
- [M] Backend observability: structured logs, metrics, and traces for critical services; correlate requests with a generated opaque request/trace ID across client, Edge Function, and provider where supported. Never put access tokens, raw prompts, sensitive payloads, or personal data into telemetry by default. Never use a user email, phone, raw account identifier, or resource identifier as a trace ID or metric label.
- [M] Define an event contract before adding product analytics: stable event names; a documented allowlist of typed properties; trigger/owner; purpose; identity policy; consent/legal basis as determined by the product owner; retention; deletion behavior; and dashboard/alert consumer. Prohibit arbitrary maps, free-text fields, raw URLs/query strings, search terms, form values, prompt/response content, precise location, and identifiers unless a reviewed requirement explicitly permits a narrowly scoped field.
- [M] Keep operational diagnostics separate from product analytics. Use opaque correlation IDs and coarse error categories; do not attach full request/response bodies, headers, cookies, tokens, SQL/provider messages, stack-local variables, or user-generated content. Scrub crash reports before transmission and test the scrubber with sentinel secrets and PII.
- [M] Telemetry queues must respect consent/opt-out, identity changes, retention limits, and deletion requests; prevent events captured under one account from being attributed to another after sign-out. Bound offline queues and retries; avoid duplicate event delivery where the SDK supports stable event IDs. Never block a critical user action on analytics delivery.
- [M] Verify telemetry itself: events are emitted at the correct semantic point and not on widget rebuild, properties have stable types/names, timestamps and identity are correct, failures are visible, and consent/opt-out controls are respected. Do not treat analytics events as the authoritative source for financial, security-critical, or audit records.
- [M] Test with a recording/fake telemetry sink: assert required events and allowed properties, assert forbidden fields are absent, verify consent/opt-out and account-switch behavior, and verify release builds do not emit debug-only diagnostics.

### Incident response and recovery

- [M] Every production service has an owner, severity definitions, an escalation/contact path, and a short runbook for the most likely high-impact failures (outage, auth failure, data exposure, quota/cost spike, bad release, migration failure).
- [M] Incident workflow: detect → assess/severity → contain → communicate → recover → verify → document lessons. Security/privacy incidents also follow the applicable legal and contractual notification process; do not improvise breach notification advice.
- [M] Define service-specific recovery objectives (RTO/RPO) from business impact. Configure backups accordingly and perform a restore/recovery drill; backup existence or a green dashboard is not proof that restore works.
- [M] After significant incidents, write a blameless post-incident review with impact, timeline, root/contributing causes, detection gaps, corrective actions, owners, and due dates. Track actions to closure; do not stop at "add more tests".

### Safe deployment and compatibility

- [M] Mobile releases are difficult to roll back after users install them. Use staged rollout where available, monitor release health, and define a stop/hold/rollback-or-forward-fix decision path before release.
- [M] Keep backend APIs and database migrations compatible with supported app versions. Prefer expand → migrate clients/data → contract; do not remove fields/endpoints or tighten constraints while older installed clients may still call them.
- [M] Destructive or irreversible migrations require an explicit backup/recovery plan and authorization. Test both fresh-install and upgrade paths; document forward-fix steps if SQL rollback is unsafe.
- [C] Use feature flags or server-side kill switches for high-risk features and provider integrations. Flags must not replace authorization, and client-only flags must never protect privileged operations.
- [M] Define how users on old app versions are handled (minimum supported version, graceful upgrade message, API compatibility window, and emergency disable behavior) without assuming forced update is available or appropriate.

### Delivery health

- [R] For teams that deliver continuously, review DORA's five software delivery metrics at the service/team level: change lead time, deployment frequency, failed-deployment recovery time, change fail rate, and deployment rework rate. Interpret them together and in context; do not optimize one metric or compare individuals/teams without accounting for service risk and workload.

## Gates

A gate passes only when each applicable item is observed, not assumed.

### Component Gate

- [M] Spec/state model documented; applicable states and variants implemented.
- [M] For components intended for cross-feature/app reuse, the `references/design-system-component-contract.md` is completed and its applicable acceptance rows have evidence; screen-local widgets are exempt from a standalone contract.
- [M] Tokens only; no hardcoded colors/sizes/durations/strings.
- [M] Widget tests cover public defaults, variants, applicable states, callbacks, duplicate activation, and semantics.
- [M] Interactive controls have verified focus/keyboard or assistive activation paths where applicable; hit targets and contrast checks pass.
- [M] Verified light/dark, LTR/RTL, text scale 2.0, long/empty content; test the largest practical OS text setting for critical/shared controls.
- [M] Reduced-motion behavior is asserted for animated components; tests prove state/behavior, not only a static screenshot.
- [C] If haptics are emitted, an injected fake verifies semantic event and exactly-once timing. Physical vibration remains device-level verification.
- [C] If Hero/shared-element transitions are used, route-level tests cover object identity, interruption, and fallback; actual platform gesture/flight behavior is manually verified on target devices when required.
- [C] If skeleton/shimmer is used, verify geometry against final content, no material layout shift, and reduced-motion behavior.
- [C] Golden (if valuable) reviewed; dartdoc + usage example; no duplicate component.

### Feature Gate

- [M] Every requirement ID has Passed acceptance with evidence.
- [M] Applicable screen states complete via `AsyncStateView`.
- [M] Failure paths tested (network, validation, unauthorized); double-submit and rapid-navigation safe.
- [M] Localized (`en`/`ar`), RTL verified, accessibility checks pass. For relevant Arabic journeys, include mixed-direction content, locale-sensitive number/date/currency formatting, and required ICU plural categories; report platform/device coverage rather than assuming a locale toggle proves correctness.
- [M] Lifecycle verified for applicable flows: pause/background and resume, route/provider disposal, cancellation, stale-response ordering, account/session switch, and process death/restart for work the product promises to recover. State explicitly which scenarios are not applicable or not verified.
- [M] Format, analyze, tests green; no new dependency without ADR.

### Existing Project Gate

Apply this gate when modifying an established app; mark it N/A for a genuinely new project.

- [M] Current SDK/toolchain, architecture, state management, routing, backend, code generation, dependencies, tests, CI, and release setup have been inspected and classified as healthy, debt, unsupported, or blocking.
- [M] Healthy existing conventions are preserved; no parallel router, state manager, backend client, or architecture has been introduced without an approved migration reason.
- [M] Every proposed migration cites a concrete requirement, security/support issue, or measurable maintenance benefit; conformity with the greenfield baseline alone is not sufficient.
- [M] Material migrations have an ADR covering alternatives, scope, user impact, compatibility, staged rollout, rollback/forward-fix, verification, and measurable acceptance.
- [M] Existing behavior and critical journeys have baseline tests/evidence before structural changes; regression verification is completed after each migration stage.
- [M] Existing dependencies and generated-code workflows are not removed solely to match greenfield defaults; new or changed dependencies pass the dependency admission review.

### Architecture Gate

- [M] Import-boundary test passes; one owner per state; no parallel implementations.
- [M] Shared code contains no product-specific values; ADRs exist for deviations.

### Security Gate

- [M] Feature threat model and data classification exist for every sensitive or externally callable flow; trust boundaries and abuse cases are addressed.
- [M] Server-side object authorization and negative tests pass; client route/UI checks are not counted as security controls.
- [M] Secrets scan, log-redaction checks, dependency review, and release-artifact review show no exposed credentials or sensitive payloads.
- [M] Applicable Supabase grants/RLS, Edge Function auth/abuse controls, and Storage permissions pass backend tests.
- [M] Android/iOS manifests, permissions, exported surfaces, backup behavior, privacy declarations, and included SDK requirements are reviewed for the actual release build.
- [M] Selected OWASP MASVS profile covers the mobile client and applicable OWASP ASVS/API Security controls cover backend/API surfaces; scope and deviations are recorded with owner and reason. No certification claim is made.

### Performance Gate

- [M] Each critical journey has a measurable `PERF-*` budget with device, OS, build mode, refresh rate, scenario, dataset, network conditions, metric, percentile, and threshold.
- [M] Profile-mode measurements on the lowest supported physical device are recorded; higher-refresh targets are tested where relevant.
- [M] Frame jank/UI/raster timing, cold/warm startup, memory behavior, and release artifact size are measured; energy/background behavior is measured when the product uses ongoing background work.
- [M] Results are compared with the previous baseline. Regressions beyond the approved budget are fixed or explicitly accepted and recorded; unmeasured performance is marked Not verified.

### Production Operations Gate

- [M] Production-critical journeys have owned SLIs/SLOs, alert thresholds, and a documented response owner.
- [M] Crash/ANR and backend telemetry are usable, correlated where possible, privacy-reviewed, and tested for redaction.
- [M] Incident severity, escalation, user communication, and recovery runbooks exist for the highest-impact failure modes.
- [M] RTO/RPO are defined for important data/services; backup restoration has been exercised and recorded.
- [M] Mobile release stop/hold/forward-fix path and app/backend compatibility window are defined; applicable migrations have a safe recovery plan.

### Application Gate

- [M] Traceability table has no Not Started/In Progress/Failed/Blocked items without explicit user sign-off.
- [M] Critical journeys pass as integration tests on at least one Android and one iOS target, or are reported not verified with reason.
- [M] Device matrix and release-specific dependency audit complete; items needing legal/security review listed.
- [M] Supabase RLS/authorization tests and Edge Function authentication/abuse tests pass for applicable backend features, or are explicitly reported not verified with a reason.

### Release Gate

- [M] Release-mode builds succeed for both platforms with production flavor and signing from secrets.
- [M] Version/build number bumped; correct environment config; no debug code, test credentials, or verbose logging.
- [M] Permissions, privacy manifest/data-safety answers, and store metadata match actual behavior.
- [M] Smoke test release artifact (install, launch, core journey, upgrade-from-previous if applicable).
- [C] Applicable Supabase migrations are reviewed and applied to the explicitly selected production project; production secrets are configured in Supabase secret storage and never included in release artifacts.
- [M] Explicit user authorization before publication.

Critical failures block completion. Unresolved high-risk items must be listed in the report.

## Official references

- OWASP MASVS: https://mas.owasp.org/MASVS/
- OWASP ASVS 5.0: https://asvs.owasp.org/
- OWASP API Security Project: https://owasp.org/www-project-api-security/
- OWASP SAMM: https://owaspsamm.org/model/
- NIST Secure Software Development Framework: https://csrc.nist.gov/projects/ssdf
- DORA software delivery metrics: https://dora.dev/guides/dora-metrics/
- Flutter performance best practices: https://docs.flutter.dev/perf/best-practices
- Flutter performance profiling: https://docs.flutter.dev/perf/ui-performance
- Flutter DevTools Performance view: https://docs.flutter.dev/tools/devtools/performance
- Flutter app size analysis: https://docs.flutter.dev/perf/app-size
- OWASP MASVS usage and risk-based profiles: https://mas.owasp.org/MASVS/03-Using_the_MASVS/
- Android app security best practices: https://developer.android.com/privacy-and-security/security-best-practices
- Google Play target API requirements: https://developer.android.com/google/play/requirements/target-sdk
- Apple privacy manifests and SDK requirements: https://developer.apple.com/documentation/bundleresources/adding-a-privacy-manifest-to-your-app-or-third-party-sdk
- GitHub Actions security: https://docs.github.com/en/actions/security-for-github-actions
