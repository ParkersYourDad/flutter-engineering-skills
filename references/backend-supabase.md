# Supabase Backend and Gemini Integration

## Purpose and boundaries

Supabase is the default full backend for this mobile engineering system:

- **Postgres** — relational source of truth and transactional business data.
- **Auth** — user identity and sessions when the product has accounts.
- **Data API** — client data access governed by database grants and Row Level Security (RLS).
- **Storage** — private/public file storage with bucket and object policies.
- **Realtime** — only for features that need live updates.
- **Edge Functions** — trusted server-side logic, webhooks, integrations, and Gemini API proxying.

Use the services a feature actually needs. "Full backend" means Supabase is the platform and default backend boundary; it does not mean every app must create every service, table, bucket, channel, or function before a requirement exists. Do not add a second backend, custom server, or another database without a documented architectural reason and approval.

The Flutter client uses `supabase_flutter`. Supabase SDK handles Supabase APIs; Dio remains for unrelated third-party HTTP APIs. Do not route ordinary Supabase table queries through Edge Functions merely to hide the publishable key. RLS is the intended authorization boundary for client-accessible data.

## Non-negotiable trust boundaries

| Value / operation | Where it may exist | Rule |
|---|---|---|
| Supabase project URL | Flutter app config | Public endpoint, not a secret |
| Supabase publishable key | Flutter app config | Designed for client use; grants must remain least-privilege and RLS must protect exposed data |
| Supabase secret key / legacy service_role key | Trusted server-side only | Bypasses RLS; never ship to Flutter, source control, assets, CI artifacts, or logs |
| Gemini API key | Supabase Edge Function secret store only | Never place in Flutter, `--dart-define`, app config, Remote Config, bundled env files, or Git |
| User access token | Session storage managed by Supabase SDK | Send through supported SDK invocation; never log or manually persist it |
| User data | Database / private Storage / approved provider request | Minimize collection, access, retention, and external disclosure |

A publishable key is not a user identity and is not authorization. A request is allowed only when database grants, RLS policies, and server-side checks permit that exact action.

## Flutter integration and ownership

- Add `supabase_flutter` as the approved Supabase client dependency. Verify its current stable release, Flutter/Dart constraints, migration guide, and changelog before choosing/upgrading a version. Do not adopt prereleases by default.
- Initialize one Supabase client during app bootstrap, after binding initialization and before `runApp`. Read the URL and publishable key from the app's non-secret environment configuration. Fail startup with a clear configuration error if required values are absent; never silently point production at a development project.
- Expose the client through a Riverpod provider. Repositories/data sources receive the client through dependency injection. Widgets and Notifiers must not call Supabase directly.
- Keep all Supabase SDK types, raw row maps, query builders, and transport parsing inside the feature's `data/` layer. Map results to immutable feature models before returning to presentation.
- Map Supabase Auth, PostgREST, Storage, and Functions errors at the repository boundary into the app's `AppFailure`. Preserve safe diagnostic context for redacted logs; never display raw provider/server messages.
- Clear user-scoped providers, caches, subscriptions, and local user data on sign-out/account switch. Do not allow a previous account's state to flash while the next account loads.
- Use the SDK's supported session refresh and lifecycle behavior. Do not hand-roll JWT parsing, refresh, or token persistence.

## Database, migrations, and RLS

### Schema and migration discipline

- Keep schema changes in versioned SQL migrations under `supabase/migrations/`; commit migrations and review them like application code.
- Develop and test locally or in an isolated development project first. Use the current Supabase CLI documentation and `supabase <command> --help` before relying on CLI commands or flags; CLI behavior changes between major versions.
- Do not make undocumented dashboard-only production schema changes. If an emergency dashboard change is unavoidable, immediately capture it as a reviewed migration and reconcile environments.
- Migrations must be repeatable in a clean local database and have a considered forward-recovery/rollback plan. Destructive migrations require explicit approval and a backup/recovery plan.
- Keep seed data deterministic and free of real user data, production secrets, and credentials.
- Avoid schema-per-feature sprawl, premature generic tables, and storing structured relational data as arbitrary JSON without a demonstrated need.
- Before production stores important user data, define the backup/restore approach appropriate to its value and service plan; test a restore or recovery procedure. Do not claim disaster recovery from the existence of backups alone.

### RLS and grants

- Enable RLS on every table in an exposed schema (especially `public`) before granting client roles access.
- Grant only the required table/function privileges to `anon` and/or `authenticated`. RLS controls rows; grants control whether the role can access the table/API at all. Both are required. Do not assume enabling RLS revokes existing/default grants or removes a schema from Data API exposure; inspect effective grants and API exposure for every exposed schema, and keep grant changes in migrations.
- Write policies per operation (`SELECT`, `INSERT`, `UPDATE`, `DELETE`) and per actual access model: owner, tenant, role, public read, or another explicit rule. Never copy a generic `auth.uid() = user_id` policy onto tables whose ownership model differs.
- For private user rows, derive identity from the verified session with `(select auth.uid())`; do not trust a client-supplied user ID.
- An `authenticated` role check alone is not authorization. Include the ownership/tenant predicate needed to prevent BOLA/IDOR and cross-tenant access.
- `UPDATE` policies should state both `USING` (which existing rows may be changed) and `WITH CHECK` (what the resulting row must satisfy) so users cannot move rows to another owner/tenant. An `UPDATE` also needs the applicable `SELECT` grant and a matching `SELECT` policy for rows being targeted; test the full operation, not just the policy expression.
- Do not use user-editable `user_metadata` / `raw_user_meta_data` for authorization. Use trusted server-managed claims or database relationships and account for JWT claim staleness.
- Do not use deprecated `auth.role()` checks. Target roles with policy `TO anon` / `TO authenticated` and verify the real identity/ownership separately.
- Views can bypass RLS by default. On supported Postgres versions use `security_invoker = true`; otherwise restrict access or place the view in a non-exposed schema.
- Avoid `SECURITY DEFINER` functions. If genuinely necessary, keep them out of exposed schemas, set a safe fixed `search_path` (or fully qualify every object), use a minimally privileged owner, revoke default/public EXECUTE grants and grant only intended roles, validate caller identity and inputs inside the function, document why RLS bypass is required, and run Supabase security advisors.
- Index the columns used by RLS predicates and common tenant/ownership filters when query plans and data volume justify it; verify with `EXPLAIN (ANALYZE, BUFFERS)` on representative data rather than indexing every column mechanically.
- Add SQL database tests under `supabase/tests/` for each exposed table and operation (`SELECT`, `INSERT`, `UPDATE`, `DELETE`): expected allow and deny cases for anon/authenticated, owner/non-owner, and cross-tenant users where applicable. Run the current documented `supabase test db` workflow; a successful owner query alone is insufficient.
- Verify the Data API exposure settings and explicit grants when a table is unexpectedly unavailable. Do not weaken RLS to work around a missing grant.

## Auth

- Add Supabase Auth only when the product needs identity/accounts. Select providers and account lifecycle from product requirements; do not invent auth providers or collect unnecessary personal data.
- Model startup auth as loading/known signed-out/known signed-in. Do not redirect based on a transient null session before initialization completes.
- Protect account-owned rows with RLS even when UI routes are guarded. Route guards are UX, not security.
- Use verified server-side identity for privileged operations. Never authorize from a client-supplied `user_id`, decoded-but-unverified JWT, email string, or user-editable metadata.
- On sign-out, revoke/sign out through the SDK, clear user-scoped state and subscriptions, and navigate to a safe signed-out route. For sensitive operations requiring immediate revocation, account for already-issued JWT validity and verify session state server-side. Deleting an Auth user does not by itself guarantee immediate invalidation of every already-issued access token; revoke/sign out sessions first, and for strict immediate-revocation requirements validate the session server-side (for example, against the current session record) before sensitive actions.
- Deep-link/OAuth callbacks must validate the expected flow and state/PKCE requirements. Test cancelled, expired, replayed, and malformed callbacks.

## Storage

- Private buckets are the default for user files. Public buckets are permitted only for intentionally public assets; never place private user uploads in a public bucket.
- Define bucket-level limits and allowed MIME types, but also validate actual content and size server-side where security matters; client MIME/extension checks are not trusted.
- Storage policies must scope each operation to the correct user/tenant and object path. Do not rely on obscured filenames.
- Signed URLs are temporary bearer credentials: use short expirations appropriate to the action, do not log/share them publicly, and regenerate when needed.
- Storage upsert requires the applicable INSERT, SELECT, and UPDATE permissions/policies; test both first upload and replacement.
- Define deletion/retention behavior for user data and associated files. Do not assume deleting an Auth user automatically removes all application rows and Storage objects.

## Realtime

- Add Realtime only for a concrete live-update requirement; ordinary request/response data should remain ordinary queries.
- Realtime is a notification/stream mechanism, not a substitute for authorization or a durable source of truth. Re-fetch authoritative state when required.
- Scope subscriptions by authorized rows and channels; do not broadcast private data to public channels.
- Create subscriptions outside widget build, own them in a provider/controller with explicit lifecycle, and unsubscribe on disposal, sign-out, and account switch.
- Handle reconnects, duplicate/out-of-order events, missed events, and app pause/resume. Make event handling idempotent and reconcile from the database after reconnect where correctness requires it.
- Test that one user's session cannot receive another user's events.

## Edge Functions

Use Edge Functions for trusted server-side operations: Gemini calls, third-party secrets, webhooks, privileged workflows, and logic that must not run in a mobile client. Keep functions small and focused; do not create one function per trivial database operation.

- Current Supabase guidance uses `@supabase/server` v1's `withSupabase({ auth: 'user' })` pattern for authenticated Fetch handlers; use the supplied `ctx.supabase` caller-scoped client for user data so RLS applies. Verify the current package/runtime import and migration notes before implementation (for Deno, current examples use `npm:@supabase/server@1`). Use `ctx.supabaseAdmin` only for a reviewed privileged operation. The December 1, 2026 removal notice applies only to the package's framework-specific adapters, not to `withSupabase` or plain Fetch handlers. Do not use those deprecated adapters in new framework integrations; use the current framework-bridge guidance instead. If this pattern changes, follow the current official docs rather than copying an old snippet.

- Keep user-facing functions authenticated by default. Leave platform JWT verification enabled unless a documented webhook/service-to-service use case requires a different verification path.
- A valid JWT proves identity, not permission to access every resource. Derive the user from verified claims and authorize every requested record/action. Prefer a caller-scoped Supabase client that preserves RLS.
- Never trust a client-supplied user ID, role, price, quota, ownership, or authorization decision. Recompute trusted values server-side.
- Use a secret/service-role client only for a narrowly defined privileged operation. It bypasses RLS: explicitly filter by verified caller/tenant, constrain selected columns, and test cross-user access. Never use it as the default client for user-facing reads/writes.
- Validate HTTP method, content type, request schema, body size, required fields, enum/model allowlists, and all external inputs. Reject unknown fields when they could alter security-sensitive behavior.
- Add bounded execution time, concurrency controls, request quotas, rate limits, and idempotency for operations that can be retried or billed. Do not implement rate limits in per-instance memory; Edge Function instances are distributed and ephemeral. Use an atomic shared store/limiter appropriate to expected scale.
- Return stable, minimal error codes and appropriate HTTP status codes. Do not return stack traces, SQL errors, provider payloads, secrets, or internal identifiers to clients.
- Redact Authorization headers, API keys, cookies, PII, request bodies, prompts, and provider responses from logs by default. Log request IDs, safe error categories, latency, and usage counters instead.
- Add CORS headers only when a browser client requires them. CORS is not authentication and does not protect a native mobile endpoint from direct calls.
- Webhooks must verify the provider's signature against the raw request body, enforce replay/timestamp protections where supported, and be idempotent. Do not disable JWT verification and then leave a function unauthenticated.
- Test auth failures, authorization failures, malformed/oversized input, rate-limit behavior, provider timeouts/429/5xx, duplicate requests, and redaction.

## Gemini API through Supabase Edge Functions

### Required request path

```
Flutter app
  -> Supabase Auth session + supabase.functions.invoke(...)
  -> authenticated Supabase Edge Function
  -> validate caller, entitlement, quota, input and limits
  -> read GEMINI_API_KEY from Edge Function secret environment
  -> Google Gemini API
  -> validate/normalize response and usage
  -> return minimal typed result to Flutter
```

The Flutter app must never call Gemini directly with a secret API key. Do not put the key in Dart constants, `--dart-define`, app flavors, `.env` assets, Remote Config, crash reports, analytics, or source control. Obfuscation does not make a client-side key secret.

### Secret setup

- Use a named Supabase Edge Function secret such as `GEMINI_API_KEY`. Read it at runtime inside the function using the current documented Edge Runtime environment API (currently `Deno.env.get`).
- Set production secrets through the Supabase Dashboard's Edge Function Secrets or the current documented CLI secret command. Never put secret values in migration SQL, `config.toml`, source code, README, GitHub Actions YAML, or command logs. Use separate Gemini API keys for development and production where practical, restrict each key to the Gemini API and intended project when Google's current key controls support it, and configure provider-side usage/billing alerts.
- For local development, use the documented Edge Function local secret file (currently `supabase/functions/.env`) and add it to `.gitignore`. Commit only a placeholder `.env.example` with variable names and fake/example values, never a real key.
- Missing key must fail closed with a server-side configuration error. Do not fall back to a key supplied by the client.
- Rotate a key immediately if exposure is suspected; inspect provider usage/billing, revoke the old key, deploy the replacement, and review logs/history for further leakage.

### Authentication, authorization and abuse controls

- The function accepts a valid signed-in user's JWT by default. Use the current Supabase-recommended user-auth pattern and preserve caller RLS context for user-scoped data. Verify the exact SDK/helper API against current Supabase docs before implementation. If the product intentionally has no account system, do not simply disable authentication or rely on the publishable key: pause and design an explicit abuse-resistant anonymous access model with server-side quotas, identity/attestation appropriate to the product, and a documented risk decision.
- Do not accept a user ID from the request as proof of identity. Derive identity from the verified JWT. Check entitlement/plan and feature permission server-side; UI hiding is not enforcement.
- Enforce per-user and, where appropriate, per-IP limits; daily/monthly quotas; maximum request bytes; maximum prompt/context size; maximum output tokens; allowed model IDs; execution timeout; and concurrency/budget ceilings.
- Rate-limit and quota updates must be atomic across function instances. A read-then-write counter without transaction/atomicity is raceable.
- Treat user prompts, uploaded files, retrieved documents, and model output as untrusted. Defend against prompt injection; do not let model output authorize database actions, choose arbitrary URLs, or bypass server permission checks.
- If Gemini output triggers tools or mutations, validate every proposed action against server-side allowlists and authorization. Require explicit user confirmation for consequential actions.
- Handle provider 429, quota exhaustion, timeouts, malformed output, safety blocks, and 5xx responses explicitly. Retry only when safe, bounded, and budget-aware; never blindly retry a billed generation request.
- Minimize the data sent to Gemini. Do not send credentials, tokens, hidden app secrets, or unrelated personal data. Disclose external AI processing where required by product/privacy requirements; determine retention and consent before shipping the feature.
- Do not persist prompts/responses by default. If history is a product requirement, define retention, deletion, access controls, encryption-at-rest expectations, and RLS policies before implementation.
- Track usage/cost with safe counters (user ID or internal account ID where appropriate, model, token counts, request ID, timestamp); do not log full prompts or generated content by default. Configure provider billing alerts and project-level budget monitoring where available.
- Model selection and system instructions are server-controlled configuration. Never let a client choose an arbitrary upstream URL, API endpoint, or privileged system prompt.

### Flutter client contract

- Call the Edge Function through the Supabase SDK's supported function invocation API so the current user session is attached correctly.
- Define typed request/response models in the feature boundary; validate response shape and map function error codes to localized UI failures.
- Keep loading, cancellation, timeout, retry, empty, safety-blocked, quota-exhausted, and generic error states explicit.
- Prevent accidental double submission and duplicate billed requests. Use an idempotency key when the backend contract supports it.
- Do not expose provider-specific stack traces or raw Gemini errors in the UI.

## Backend acceptance checklist

- [M] Project URL and publishable key are the only Supabase credentials present in the mobile app.
- [M] No secret/service-role/Gemini key appears in source, build output, Git history, logs, or test fixtures.
- [M] Every exposed table has RLS enabled, least-privilege grants, and deliberate Data API exposure; SQL tests cover allow/deny behavior for each applicable CRUD operation and role, and `supabase test db` passes.
- [M] Cross-user and cross-tenant negative authorization tests pass.
- [M] Migrations rebuild a clean local database and are reviewed before staging/production.
- [M] Auth lifecycle, sign-out cleanup, and account switching are tested when Auth is used.
- [C] Storage policies, upload validation, signed URL expiry, and deletion are tested when Storage is used.
- [C] Realtime authorization, reconnect behavior, and subscription disposal are tested when Realtime is used.
- [C] Every Edge Function has explicit auth mode, authorization, validation, rate/usage limits, safe errors, and redacted logs.
- [C] Gemini function has secret retrieval, provider timeout/429/safety/error handling, per-user quota, token/input/output limits, and cost monitoring.
- [M] Local and production secret setup is documented without recording secret values.
- [M] Backend tests and Supabase security advisors are run where available; unavailable checks are reported as not verified.

## Version and documentation policy

Supabase changes frequently. Before adding/upgrading `supabase_flutter`, Supabase CLI, Edge Runtime APIs, Auth, Storage, Realtime, RLS, or Edge Function helpers:

1. Check the official Supabase changelog for breaking changes.
2. Read the current product documentation and migration guide for the exact service/API.
3. Check the package's stable version and Flutter/Dart constraints on pub.dev.
4. Verify CLI commands with `--help`; do not assume a command or flag from memory.
5. Implement against the verified API, then run local tests and relevant security checks.
6. Record material version/architecture choices in `docs/DECISIONS.md`.

As of 2026-11-07, Supabase has announced the v3 Flutter client as a breaking-change prerelease, with stable release planned for 2026-11-11. Do not adopt a v3 prerelease by default; re-check the current stable channel and migration guide when the skill is used. The Supabase CLI v3 announcement (2026-11-04) also changes its default toward local operations and explicit confirmation for hosted changes; always inspect the installed CLI help and explicitly verify the target project/environment before any hosted operation.

## Official references

- Supabase Flutter client and setup: https://supabase.com/docs/reference/dart/installing
- Supabase Flutter quickstart: https://supabase.com/docs/guides/getting-started/quickstarts/flutter
- Supabase API security and RLS: https://supabase.com/docs/guides/api/securing-your-api
- Supabase Edge Function secrets: https://supabase.com/docs/guides/functions/secrets
- Supabase Edge Function authentication: https://supabase.com/docs/guides/functions/auth
- Supabase server-side request authentication package: https://supabase.com/docs/reference/server/usage-examples
- Supabase RLS testing and grants: https://supabase.com/docs/guides/database/postgres/row-level-security
- Supabase database migration deployment: https://supabase.com/docs/guides/deployment/database-migrations
- Supabase Authorization headers: https://supabase.com/docs/guides/functions/auth-headers
- Supabase breaking changes: https://supabase.com/changelog?types=breaking-change
- Supabase Flutter package versions: https://pub.dev/packages/supabase_flutter
- Google Gemini API key security: https://ai.google.dev/gemini-api/docs/api-key
