# Pitfalls: Common Failures and Prevention

Read when debugging, reviewing, or before declaring a feature done. Each row describes the mistake, why it happens/costs, how to prevent or detect it, and how to fix it/prevent regression. Add or amend a row only through the learning loop in `workflow.md`; do not duplicate rules that live elsewhere.

## AI-assisted workflow

| Mistake | Prevent / detect | Fix / prevent regression |
|---|---|---|
| Invents a package API or version from memory; code fails to compile or behaves differently | Check pub.dev/changelog before use; run `flutter analyze` after writing | Correct against docs; record verified version in `DECISIONS.md` |
| Claims tests pass or build works without running anything | Report only observed output; list unverified items | Run it; otherwise label not verified |
| Rewrites a working file wholesale and drops behavior/conventions | Read first; smallest diff; review removed lines | Restore from VCS, reapply minimal change; add regression test |
| Creates a second helper/component without searching | Search for existing equivalent before adding | Merge, remove duplicate, update call sites |
| Adds a package for a tiny problem | Package admission checklist (`quality.md`); prefer SDK | Remove package and use SDK |
| Fixes symptom (null check, delay) rather than cause | Ask why the state occurred | Fix cause; regression test; search for similar cases |
| Placeholder/fake data presented as finished feature | Acceptance requires observed real behavior | Implement against real source or mark Blocked |

## Architecture and state

| Mistake | Prevent / detect | Fix / prevent regression |
|---|---|---|
| Same data held in two providers/widgets; values drift | One-owner rule; search duplicated fields | Keep one provider; derive with `select`/computed providers |
| Business logic and Dio calls inside widgets | Boundary search in `presentation/` | Move to repository + Notifier; add repository test |
| Feature imports another feature's internals; circular coupling | Import-boundary test | Promote shared piece to `core` or route via IDs |
| Premature interfaces/use-cases/factories with one implementation | Second-consumer rule | Inline and delete |
| `ref.read` in build; UI does not update | `watch` in build, `read` in callbacks | Switch to `watch`; test state-driven rebuild |
| Side effects from build repeat or crash | Use `ref.listen` | Move to listener; test fires once |
| Notifier writes state after disposal | Guard async gaps with current Riverpod lifecycle API | Add guard; test disposal mid-request |
| Wrong lifecycle: state leaks across users or disappears on rebuild | Choose autoDispose/keepAlive deliberately; clear user-scoped state on sign-out | Invalidate on logout; test sequential users |
| Silent auto-retry repeats non-idempotent call | Configure retry policy (`architecture.md`) | Disable retry where unsafe; add idempotency test |
| GoRouter created inside build and resets navigation | Router in provider, created once | Move; test rebuild keeps location |
| Redirect loops/auth flicker at startup | Pure redirect; explicit unknown/loading auth state | Add startup state and navigation test |
| Wrong `go` vs `push` loses expected back stack | Decide per flow in route table | Correct and add back-behavior test |

## Flutter rendering and lifecycle

| Mistake | Prevent / detect | Fix / prevent regression |
|---|---|---|
| Helper methods return widgets and obscure rebuild boundaries | Prefer small widget classes where it improves isolation | Extract class; inspect rebuild stats |
| Controllers, subscriptions, timers not disposed | Dispose; inspect DevTools Memory and lifecycle logs | Dispose; test pumping/unpumping screen |
| BuildContext used after await | Keep lint; check mounted | Capture dependencies before await or guard with mounted |
| RenderFlex overflow at large text/small screens | Flexible/Expanded, wrap, scroll; test 2.0× text and narrow width | Fix layout; add regression test |
| Unbounded constraints (e.g. ListView in Column) | Understand constraints and inspect exception | Use Expanded/shrinkWrap only when justified; consider slivers |
| Keyboard covers inputs or bottom bar jumps | Handle viewInsets; scrollable forms | SafeArea/insets-aware layout; test with keyboard on device |
| Layout ignores notch/home indicator/edge-to-edge | Safe areas and system bars at shell | Fix shell; verify notch + gesture navigation |
| State lost on rotation/background/process death | Decide per screen; persist critical drafts | Add restoration/draft persistence; lifecycle test |

## UI, design system, states

| Mistake | Prevent / detect | Fix / prevent regression |
|---|---|---|
| Hardcoded colors/radii/spacing/durations in features | Lint/search for `Color(`, `Colors.`, literals | Replace with tokens; add check to CI |
| Material defaults leak (ripples, purple, M3 shapes) | `WidgetsApp` shell; inspect both platforms | Replace primitive or fully restyle it |
| Feature-local copy of global component | Search component library first | Remove copy; add missing variant to shared component |
| Only happy path designed; blank error/empty or endless spinner | Per-screen state matrix; `AsyncStateView` | Add missing states and tests |
| Skeleton differs from content; shimmer everywhere | Match dimensions; shimmer only skeletons | Fix sizes; golden skeleton/content |
| Nested cards/borders create noise | Review visual direction | Remove containers; use spacing/type |
| Dark theme is inversion or low contrast | Contrast test and dark goldens | Retune palette and tests |
| Dialog/sheet dismissal loses input or blocks back | `PopScope`, confirm discard | Add behavior and back test |

## Motion and gestures

| Mistake | Prevent / detect | Fix / prevent regression |
|---|---|---|
| Animation delays action or cannot be interrupted | Act immediately; reverse from current value | Decouple action; interruption test |
| Literal durations/curves vary by screen | Motion tokens only | Replace; CI search |
| Reduced motion ignored | Handle in shared primitives | Add reduced-motion path and test |
| Gesture conflicts (horizontal swipe vs back/tab swipe) | Test on real iOS/Android | Adjust gesture arena/hit areas; add alternative |
| Haptics on every tap or absent on key confirmation | Central Haptics policy | Remove excess; add purposeful feedback |
| Jank from layout-heavy animation/offscreen tickers | Profile device; animate transforms | Restructure; record before/after frame timings |

## Forms

| Mistake | Prevent / detect | Fix / prevent regression |
|---|---|---|
| Validation only on submit or on every keystroke | Validate on blur/submit; revalidate on change after first error | Shared form pattern + widget test |
| Errors not announced or shown only in red | Inline text + semantics | Shared field component; semantics test |
| Double submit; button active during loading | Notifier in-flight guard + loading state | Add guard; rapid-tap test |
| Wrong keyboard type, missing autofill/textInputAction | Field component defaults | Correct defaults and test |
| Validation strings hardcoded/untranslated | ARB for every message | Move to ARB; key-parity test |

## Networking and storage

| Mistake | Prevent / detect | Fix / prevent regression |
|---|---|---|
| No timeouts; spinner forever | Set connect/send/receive timeouts | Add; test timeout maps to AppFailure |
| Parallel 401s each refresh token | Single-flight refresh | Add lock; concurrent-401 test |
| Blind POST retry creates duplicate writes | Retry only idempotent requests, bounded with backoff/jitter | Correct policy; test |
| fromJson crashes on null/new field | Defensive parsing; deliberate optionality | Map safely; malformed-JSON tests |
| Request state survives cancellation/disposal | CancelToken + disposal | Wire cancellation; test |
| Tokens in prefs or logs | Storage policy and redaction tests | Migrate to secure storage; rotate leaked tokens |
| Stale secure data after reinstall/restore | First-run marker; catch read failures | Clear + re-auth; test recovery |
| Persisted schema changed without migration | Version persisted schema | Migration or safe reset; upgrade test |
| Connectivity mistaken for reachability | Treat request failures as signal | Handle in repository + error UI |
| Network performance judged by ping or a single happy-path request | Measure end-to-end request P50/P95, request count, payload bytes, retries, and slow-network behavior | Remove duplicate/unbounded requests; paginate and cache only where semantics permit; add a regression measurement |

## Localization and accessibility

| Mistake | Prevent / detect | Fix / prevent regression |
|---|---|---|
| String concatenation for sentences/plurals | ICU messages | Replace; plural tests |
| left/right and non-mirrored navigation in RTL | Directional APIs; RTL goldens | Convert and test |
| Arabic clipped/wrong font fallback | Verify glyphs; test Arabic | Fix text style; golden |
| Locale saved but not applied on first frame | Hydrate prefs before runApp | Preload; first-frame test |
| Dates/numbers formatted manually | intl only | Replace; per-locale test |
| Icon buttons lack semantics; RTL reading order wrong | Tap-target/label guidelines | Add labels and semantics tests |
| Touch target too small | 48 dp minimum | Expand hit region; guideline test |

## Performance

| Mistake | Prevent / detect | Fix / prevent regression |
|---|---|---|
| Performance judged in debug/emulator | Profile on physical device | Re-measure; record environment |
| Fixed 16 ms frame target applied to 90/120 Hz devices | Derive frame budget from actual refresh rate; inspect UI and raster timing separately | Re-baseline at the target refresh rate; update PERF acceptance |
| First frame treated as usable startup | Measure cold/warm start through the first meaningful interactive action | Defer non-critical work safely; test on the lowest supported device |
| Only warm animation runs are profiled | Include first-use/shader-heavy transitions and real user journeys | Profile cold and warmed paths; use supported renderer defaults |
| Memory rise automatically labelled a leak (or ignored) | Compare repeated identical journeys after warm-up and normal GC; inspect retained objects | Identify retaining references/subscriptions/caches; add lifecycle regression test |
| App size changes are not measured | Compare release-size reports and inspect the package/asset breakdown | Remove the actual dominant cost; keep before/after evidence |
| Background polling or subscriptions continue when unused | Inspect app pause/resume, idle network, timers, and subscription ownership | Pause/cancel unneeded work; reconcile state on resume |
| Whole screen rebuilds on one field change | select, smaller widgets, rebuild stats | Narrow watches; measure |
| Long ListView uses children list/no keys | builder/slivers + stable keys | Convert; profile scrolling |
| Full-size images decoded as thumbnails | cacheWidth/cacheHeight and suitable cache strategy | Resize at decode; memory check |
| Heavy parsing/crypto on UI isolate | Profile CPU | Isolate.run; compare before/after |
| Premature RepaintBoundary/caching | Profile first | Remove unproven optimization |

## Supabase and Gemini backend

| Mistake | Prevent / detect | Fix / prevent regression |
|---|---|---|
| Supabase secret/service-role key or Gemini key shipped in the app | Secret scan source, assets, build defines, CI artifacts and Git history | Revoke/rotate immediately; remove exposure and audit usage; never rely on obfuscation |
| Treating publishable key as authorization | Review grants and RLS; test as anon, owner and non-owner | Restrict grants; write operation-specific RLS policies |
| RLS enabled but policy only checks `authenticated` | Test cross-user and cross-tenant access | Add ownership/tenant predicate to every operation |
| UPDATE policy has no `WITH CHECK` | Test changing `user_id`/tenant columns | Add matching `USING` and `WITH CHECK`; prevent ownership reassignment |
| Edge Function trusts client-supplied user ID or decoded JWT claims | Derive identity from verified JWT; test forged IDs and expired tokens | Verify JWT and authorize resource server-side |
| Gemini Edge Function is publicly callable without controls | Verify auth mode, JWT verification, quota and abuse tests | Require user auth unless a signed webhook is the caller; add atomic rate limits and quotas |
| Gemini key is stored in a committed `.env` or printed in logs | `.gitignore`, secret scan, log review | Move to Supabase secret store; rotate exposed key |
| Edge Function uses service-role for every query | Review client creation and DB calls | Use caller-scoped client/RLS; isolate privileged operations and filter by verified user ID |
| Unbounded Gemini input/output or unrestricted model selection | Validate schema, body size, model allowlist, output/token limits, timeout and budget | Reject oversized requests; cap usage; add per-user quotas and provider cost alerts |
| Raw prompts, PII, provider errors or secrets appear in logs | Redaction tests and log inspection | Minimize data; redact; return stable localized error codes |
| Dashboard-only schema changes drift from migrations | Compare local migration history and remote schema | Create/review versioned migration and test reset/upgrade path |
| Realtime subscriptions leak across accounts or outlive screens | Lifecycle and user-switch tests | Scope filters, remove channels on dispose/sign-out, clear user-scoped state |
| Public Storage bucket exposes private uploads | Bucket/policy review and unauthenticated URL test | Private bucket + scoped policies + short-lived signed URLs |

## Security and privacy

| Mistake | Prevent / detect | Fix / prevent regression |
|---|---|---|
| API keys/secrets in repo/assets | Secret scan in CI; .gitignore | Rotate exposed secret, remove from history, move to backend/CI secrets |
| allowBackup/exported activities/cleartext left unsafe | Manifest review in release gate | Fix manifest; release-build check |
| Deep-link/server input trusted | Validate and parse all external input | Add validation + tests |
| Full request/response logged in release | Debug-only redacting logger | Gate by build mode; test redaction |
| Permissions requested at launch | Ask in context; denial path | Add rationale/denied/settings flows |
| Missing iOS privacy manifest/usage strings | Release gate; inspect app and included SDK manifests/required-reason APIs | Add accurate declarations and verify the archived release bundle |
| RLS policies exist but table grants or API exposure are too broad | Review effective grants and exposed schemas as well as policies | Revoke unnecessary grants; add least-privilege grants in a migration and test each operation |
| Authorization is checked only in the UI or route redirect | Attempt direct API access with another user's object ID | Enforce object-level authorization server-side; add cross-user negative tests |
| Backend fetches a client-supplied URL | Review all URL-fetching code and redirect behavior | Use explicit destination allowlists; block private/internal targets and unsafe redirects to prevent SSRF |
| Upload trusts filename or client MIME type | Submit oversized files, spoofed extensions, and mismatched content types | Validate byte size and actual content server-side; reject unsupported formats |
| Local biometric prompt is treated as backend authentication | Review server authorization paths separately from device unlock | Keep server-side identity/authorization checks; use biometrics only as a local gate |
| Privileged CI workflow exposes secrets to fork PR code | Review workflow triggers, permissions, and secret contexts | Remove secret access from untrusted jobs; use protected environments and minimal token permissions |
| A credential is removed from the latest commit but remains exposed | Scan Git history, logs, build artifacts, and package outputs | Revoke/rotate immediately, investigate usage, then remove historical exposure where possible |

## Dependencies, build and release

| Mistake | Prevent / detect | Fix / prevent regression |
|---|---|---|
| Blind pub upgrade breaks transitive dependencies | Dedicated upgrade; read changelogs | Roll back via lockfile; full verification |
| SDK/package constraints mismatch | Check constraints before adding | Choose compatible version; record |
| Package abandoned or unlicensed | Admission checklist | Replace; ADR |
| Debug works, release crashes | Test release early; R8/minify/permissions review | Add required config; release smoke test |
| Build number not incremented | Release checklist | Automate in release workflow |
| Pods/deployment target/Gradle/AGP/Kotlin drift | Follow migration notes; fresh build after upgrade | Align versions; clean build |
| Keystore lost or committed | Secret storage + recovery procedure | Recover via Play App Signing; rotate if leaked |

## Testing

| Mistake | Prevent / detect | Fix / prevent regression |
|---|---|---|
| Tests assert implementation details | Assert user-visible behavior | Rewrite around behavior |
| Flaky tests use real time/network/sleep | Inject clock/fakes; deterministic data | Remove timing dependency |
| Goldens regenerated blindly or differ by OS | Review diffs; one CI platform; real fonts | Re-baseline deliberately |
| Coverage padded with trivial tests | Risk-based test list | Delete meaningless tests |
| Fix lacks regression test | Defect protocol | Add test that fails before fix |
