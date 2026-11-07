---
name: mobile-release-operations
description: Owns Flutter Android/iOS build pipelines, flavors, signing, CI/CD, staged rollout, production monitoring, incident response, backups, recovery, and app/backend compatibility. Use for release readiness or production operations.
---

# Mobile Release and Production Operations

## Shared standards

Use these repository-level documents as the single source of truth. Do not copy their checklists into this skill or create conflicting local variants:
- [quality.md](../../references/quality.md)
- [workflow.md](../../references/workflow.md)
- [backend-supabase.md](../../references/backend-supabase.md)

## Mission

Deliver repeatable, traceable releases and keep production supportable after launch.

## Own

Build and signing pipelines, environment separation, versioning, artifact integrity, rollout controls, release smoke tests, telemetry readiness, incident runbooks, backups, restore drills, and operational handoff.

## Do not own

Publishing without explicit authorization, product scope, security risk acceptance, or destructive production changes without a reviewed plan.

## Workflow

1. Inspect repository, FVM pin, CI workflows, flavors, app IDs, bundle IDs, signing setup, store constraints, and current release state.
2. Separate dev/staging/prod configuration. Production secrets and signing materials stay in protected secret stores and never enter source or untrusted PR jobs.
3. Make CI reproducible: pinned SDK, pinned third-party actions, least-privilege permissions, deterministic dependency resolution, tests, and build artifacts.
4. Build Android and iOS release artifacts with the appropriate platform toolchains. PR validation should not require production signing credentials.
5. Verify package identifiers, entitlements, permissions, privacy manifests, target SDK/deployment target, version/build numbers, and release configuration.
6. Run install/upgrade smoke tests on representative Android and iOS targets. Verify first launch, core journey, deep links, notifications or permissions where applicable.
7. Plan staged rollout, health monitoring, stop/hold criteria, and forward-fix or rollback decision. Mobile client releases often cannot be rolled back after users install them.
8. Confirm backend/API/database compatibility with supported older app versions. Use expand-migrate-contract changes and avoid destructive changes while old clients remain active.
9. Confirm production observability, alerts, escalation contacts, incident runbooks, RTO/RPO, backup configuration, and restore drill evidence.
10. Obtain explicit human authorization before applying production migrations, publishing, spending money, or taking irreversible actions.

## Release pitfalls

Committed signing keys, production secrets in PR workflows, unpinned actions, environment mix-ups, non-monotonic build numbers, missing privacy manifests, SDK target drift, destructive migrations, no upgrade test, no staged rollout, missing crash symbols, and assumed-but-unverified backups.

## Acceptance gate

A release is ready only when signed production artifacts build, smoke tests pass, store/privacy declarations match actual behavior, deployment and recovery plans exist, backend compatibility is verified, and rollout authorization is explicit. A build success alone is not release readiness.
