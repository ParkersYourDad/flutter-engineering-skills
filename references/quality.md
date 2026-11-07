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
- Gates

## Verification commands

Run commands and read output; report results, not intentions.

```sh
dart format --output=none --set-exit-if-changed .
flutter analyze
flutter test
flutter test integration_test        # requires emulator/simulator/device
flutter pub outdated                 # informational dependency health
flutter build apk --release
flutter build appbundle --release
flutter build ipa --release          # macOS + signing only
```

Check current flag names with `flutter build --help` before relying on them.

## Testing

Test behavior and requirements by risk. Do not chase coverage percentages or test implementation details.

- **Unit:** pure logic, parsers/DTO mapping (including malformed input), validators, formatters, failure mapping.
- **State:** Notifiers via `ProviderContainer` with overrides; `addTearDown(container.dispose)`; assert loading → data/error and double-submit protection.
- **Widget:** component states/variants; screens in loading/empty/error/data; interactions; semantics; each in `en`/`ar`, light/dark, text scale 1.0 and 2.0 for shared components.
- **Navigation:** redirects, deep-link parsing, malformed params, back behavior, tab-stack preservation.
- **Data:** repository + fake HTTP adapter: success, timeout, 401 refresh, 5xx, malformed JSON, cancellation.
- **Golden:** shared components and a few key screens only; generate on one CI platform (goldens differ across OSes), load real fonts, review diffs rather than regenerating blindly.
- **Integration:** critical journeys only (first launch, auth if present, core flow, language/theme switch, offline recovery), deterministic data, no arbitrary sleep; use `pumpAndSettle` with care and explicit finders.
- **Architecture/localization tests:** import boundaries, ARB key parity, no hardcoded strings (see other references).
- **Fakes over mocks:** hand-written fakes; use `mocktail` only for a real need recorded in decisions. `mockito` requires forbidden code generation. Inject clock, random, and connectivity for deterministic tests.
- **Defect protocol:** reproduce → root cause → fix cause → regression test → rerun affected tests → full suite if shared code changed → search for same pattern elsewhere.

## Performance

Measure, do not assume. Never say optimized without numbers.

- Measure in **profile mode on a real device** (`flutter run --profile`) using DevTools (Performance, CPU, Memory, Rebuild stats). Debug/emulator numbers are not valid evidence. Without a device, report not measured and apply only known-safe practices.
- Targets (document in `REQUIREMENTS.md` as `PERF-*`): frames within budget at device refresh rate (no sustained jank), cold-start-to-first-interactive time on lowest supported device, memory stable across repeated navigation, no leaks after screens close.
- Known-safe practices: const widgets, narrow `ref.watch(...select)`, `ListView.builder`/slivers with stable keys, `cacheWidth`/`cacheHeight` (or `ResizeImage`) for large images with a caching strategy, defer non-critical init until after first frame, avoid expensive opacity/clipping/saveLayer patterns in scrolling lists, move heavy parsing to isolate, cancel work on dispose.
- Check release-only behavior (minification, `--obfuscate --split-debug-info`) with release build, not only debug.
- Lifecycle: handle pause/resume (refresh stale data, pause streams/timers), low memory (drop caches), connectivity changes.

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

Baseline: OWASP MASVS (and MASTG for test technique). This is not legal/compliance certification; flag items for qualified legal/security review (privacy policy text, GDPR/CCPA/regional laws, children's data, payments, health).

- [M] No secrets or signing material in source control; do not assume client binaries can protect secrets.
- [M] Supabase publishable key may be embedded in a client only because it is designed to be public; it grants no data access without correct grants and RLS. Never embed secret/service-role keys.
- [M] Gemini API key exists only in Supabase Edge Function secrets (e.g. `GEMINI_API_KEY`) and is read at runtime; never use `--dart-define`, `.env` bundled into Flutter, Remote Config, or obfuscation as a secret store.
- [M] Supabase session tokens remain under the Supabase SDK's supported session persistence; do not copy them into app preferences or custom stores. App-owned credentials, if any, use secure storage. Clear user-scoped data on sign-out; no sensitive data in prefs, logs, crash reports, or task-switcher screenshots where relevant (consider `FLAG_SECURE`/blur on sensitive screens).
- [M] HTTPS only; no cleartext (`usesCleartextTraffic` off outside dev; iOS ATS not weakened); no permissive `badCertificateCallback`.
- [M] Validate/sanitize external input (forms, deep-link params, server data); treat deep links/intents as untrusted.
- [M] Logs redact tokens/PII; verbose logs are debug-only.
- [M] Collect minimum data; request permissions at moment of need with rationale; handle denial and settings redirect.
- [M] Android: explicitly decide `allowBackup` (disable or define rules so secrets are not restored), minimize exported components, verify R8/minify with release run.
- [M] iOS: Privacy Manifest and usage-description strings are accurate, including third-party SDKs; choose Keychain accessibility deliberately.
- [C] Certificate pinning, biometric auth, root/jailbreak detection only when required (ADR).
- [M] Dependency vulnerability check at each upgrade/release (pub.dev advisories, `flutter pub outdated`, GitHub Dependabot where available).
- [M] Supabase SDK and CLI changelogs checked for breaking changes before upgrades; use stable SDK releases by default and explicitly reject prereleases unless justified in an ADR.
- [C] Account creation requires in-app account deletion; third-party social login on iOS may require Sign in with Apple. Verify current App Store rules before release.

## Dependencies and upgrades

Admission checklist per package, recorded in `DECISIONS.md`: purpose; SDK alternative considered; official docs read; Dart/Flutter constraints compatible; recent releases and responsive maintainers; license compatible with distribution; known advisories checked; transitive dependencies reviewed; version constraint chosen (caret ranges; commit app lockfile).

Upgrade policy: upgrade deliberately in a dedicated change (SDK first, then packages), read changelogs/migration guides, run full verification, never blind `pub upgrade --major-versions` in a feature change. Review monthly for security fixes and quarterly for SDK/platform updates. Watch deprecations (analyzer warnings are early signal), and annual platform changes (Android target API and Xcode/iOS SDK requirements for store submission); verify current dates in Google Play and App Store Connect docs.

## Android and iOS

- **Minimums:** set minimum Android API and iOS deployment target from Flutter's current supported baseline and product audience; record in `docs/PROJECT.md`; verify current docs.
- **Both:** safe areas/cutouts/Dynamic Island, edge-to-edge system bars with correct icon contrast per theme, keyboard insets, orientation policy decided and enforced, no hardcoded status-bar heights.
- **Android:** application ID per flavor, adaptive/monochrome launcher icon, splash via platform Splash Screen API (verify Flutter setup), permissions only if used, predictive-back decision, notification channels/permission (Android 13+) if notifications exist, App Links verification.
- **iOS:** bundle ID per flavor, icon set without transparency, launch screen, `Info.plist` usage strings, background modes only if used, Associated Domains, push entitlements if used, minimum deployment target consistent across Runner and Pods.
- **Signing:** keystore and `key.properties` / Apple certificates and profiles stay out of repo; CI gets them from secrets; use Play App Signing; document recovery for lost upload key.
- **Store readiness:** versioning (`version: x.y.z+build`, monotonically increasing build), screenshots, metadata, privacy policy URL, Play Data safety / Apple App Privacy answers matching actual behavior, content rating, reviewer demo access when login exists. Publishing is consequential and requires explicit user authorization.

## CI/CD

GitHub Actions: every PR runs format check, analyze, tests (goldens on one runner OS), and Android debug/release build; iOS build on macOS runner when signing is configured. Pin Flutter version (same as `pubspec.yaml`), pin third-party actions by version/SHA, cache pub, upload test/build artifacts. Release workflow: tag-triggered, builds signed artifacts from secrets, never prints secrets, requires manual approval to publish. Verify workflow syntax against current GitHub docs. Local YAML validation is not a real GitHub Actions run.

## Device matrix

Maintain a short table in `docs/PROJECT.md`: lowest + current Android and iOS versions, small/regular/large phone, tablet/foldable if supported, light/dark, `en`/`ar`, text scale 1.0/2.0, gesture vs button navigation, offline/flaky network, low-memory. Use emulators/simulators for repeatability, physical devices for performance, haptics, notifications, biometrics, camera/permissions. Every release report states which rows were tested and which were not.

## Gates

A gate passes only when each applicable item is observed, not assumed.

### Component Gate

- [M] Spec/state model documented; applicable states and variants implemented.
- [M] Tokens only; no hardcoded colors/sizes/durations/strings.
- [M] Widget tests for states; semantics + tap-target + contrast checks pass.
- [M] Verified light/dark, LTR/RTL, text scale 2.0, long/empty content.
- [M] Golden (if valuable) reviewed; dartdoc + usage example; no duplicate component.

### Feature Gate

- [M] Every requirement ID has Passed acceptance with evidence.
- [M] Applicable screen states complete via `AsyncStateView`.
- [M] Failure paths tested (network, validation, unauthorized); double-submit and rapid-navigation safe.
- [M] Localized (`en`/`ar`), RTL verified, accessibility checks pass.
- [M] Lifecycle verified: background/resume, rotation if allowed, process death for critical flows.
- [M] Format, analyze, tests green; no new dependency without ADR.

### Architecture Gate

- [M] Import-boundary test passes; one owner per state; no parallel implementations.
- [M] Shared code contains no product-specific values; ADRs exist for deviations.

### Application Gate

- [M] Traceability table has no Not Started/In Progress/Failed/Blocked items without explicit user sign-off.
- [M] Critical journeys pass as integration tests on at least one Android and one iOS target, or are reported not verified with reason.
- [M] Performance measured in profile/release on device against `PERF-*`, or reported not measured.
- [M] Security checklist, device matrix, dependency audit complete; items needing legal/security review listed.

### Release Gate

- [M] Release-mode builds succeed for both platforms with production flavor and signing from secrets.
- [M] Version/build number bumped; correct environment config; no debug code, test credentials, or verbose logging.
- [M] Permissions, privacy manifest/data-safety answers, and store metadata match actual behavior.
- [M] Smoke test release artifact (install, launch, core journey, upgrade-from-previous if applicable).
- [M] Explicit user authorization before publication.

Critical failures block completion. Unresolved high-risk items must be listed in the report.
