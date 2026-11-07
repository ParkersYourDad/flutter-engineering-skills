---
name: supabase-backend-engineering
description: Designs, implements, and reviews Supabase/PostgreSQL backends for Flutter products, including RLS, grants, Auth, Storage, Realtime, Edge Functions, migrations, and Gemini integrations. Use for backend or data-layer work.
---

# Supabase Backend Engineering

## Mission

Build a secure, maintainable backend for the actual product requirements. Supabase is the default backend choice where a backend is required; it is not a mandate to create services for a local-only product.

## Own

Database schema, migrations, constraints, indexes, grants, RLS, Auth lifecycle, Storage policies, Realtime authorization, Edge Functions, backend tests, server-side integrations, and data retention/deletion mechanics.

## Do not own

Flutter presentation or local widget state, client visual design, product policy decisions, legal advice, or production deployment approval.

## Required workflow

1. Inspect the existing Supabase project, migration history, CLI/runtime/package versions, schema exposure, policies, functions, secrets setup, and app contracts.
2. Identify data classification, actors, tenants, data ownership, allowed operations, retention, deletion, and abuse cases.
3. Design schema and API contracts from requirements. Keep migrations as source of truth; do not create dashboard-only drift.
4. Use least-privilege SQL grants plus operation-specific RLS. Test anon, owner, non-owner, and cross-tenant cases, including both allow and deny paths.
5. Review views, functions, triggers, SECURITY DEFINER, search_path, EXECUTE grants, and exposed schemas.
6. Design Auth/session lifecycle, sign-out/account switching, token expiry, recovery, and authorization for every sensitive operation.
7. Make Storage private by default. Validate file size and actual content server-side; define object-path authorization and deletion.
8. Add Realtime only for real live-update requirements; scope subscriptions and test cross-user isolation and reconnect recovery.
9. Use Edge Functions for trusted operations and provider secrets. Validate request schema, body size, methods, identity, authorization, rate limits, quotas, concurrency, idempotency, timeouts, and safe errors.
10. For Gemini: keep the key server-side, minimize supplied data, control model selection and token budgets, defend against prompt injection, account for billed retries, and measure cost.
11. Test clean database rebuild, upgrade migration, rollback/forward recovery, and security policies in an isolated environment before production.
12. Hand Flutter the typed request/response contract, error codes, auth expectations, pagination, retry/idempotency behavior, and version compatibility window.

## Security requirements

- Never trust a client-supplied user ID, role, ownership, price, quota, or permission.
- A publishable key is not authorization. Grants and RLS jointly control access.
- UPDATE requires the correct row-selection and resulting-row checks, including applicable SELECT privileges/policies.
- SECURITY DEFINER is exceptional; fix safe search_path, ownership, EXECUTE grants, and caller authorization.
- Never expose service-role/secret keys or Gemini keys to mobile source, assets, build defines, logs, or Git.
- Never send Supabase session tokens to unrelated third-party hosts.
- Treat webhook signatures, replay controls, SSRF, uploads, and public signed URLs as explicit threat surfaces.

## Pitfalls

Prevent weak RLS, broad grants, missing WITH CHECK, cross-tenant access, dashboard drift, unsafe SECURITY DEFINER, unauthenticated Edge Functions, per-instance rate-limit counters, unrestricted model IDs, unbounded AI cost, PII in logs, public private-file buckets, stale JWT assumptions, duplicate billed requests, and breaking backend changes for old clients.

## Acceptance gate

Pass only with versioned migrations, reviewed grants and exposed schemas, automated positive and negative SQL tests, Edge Function auth/abuse tests, secrets/log review, migration/recovery evidence, and accepted Flutter contracts. A successful dashboard query or one happy-path test is insufficient.
