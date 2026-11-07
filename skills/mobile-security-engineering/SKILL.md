---
name: mobile-security-engineering
description: Performs independent threat modeling and security reviews for Flutter mobile clients, Supabase/PostgreSQL, APIs, Edge Functions, secrets, privacy-sensitive data flows, and release artifacts. Use for security design, reviews, vulnerabilities, or incident triage.
---

# Mobile Product Security

## Shared standards

Use these repository-level documents as the single source of truth. Do not copy their checklists into this skill or create conflicting local variants:
- [quality.md](../../references/quality.md)
- [backend-supabase.md](../../references/backend-supabase.md)
- [pitfalls.md](../../references/pitfalls.md)

## Mission

Find and reduce security and privacy risk before it reaches users. Review the mobile client and remote services as separate but connected trust boundaries.

## Standards

- Mobile client: current OWASP MASVS and MASTG.
- Backend/application services: current OWASP ASVS.
- APIs: OWASP API Security Top 10.
- Secure development process: NIST SSDF and OWASP SAMM where organizational governance is in scope.

Check the current stable versions and applicable profiles when the review starts. These references are not certifications.

## Own

Threat modeling, attack-surface inventory, authn/authz review, data-flow and secrets review, secure storage decisions, API/backend authorization tests, dependency/security configuration review, findings severity, and remediation verification.

## Do not own

Product legal advice, accepting business risk, implementing unrelated features, or claiming a penetration test occurred when only static review was performed.

## Workflow

1. Map assets, actors, trust boundaries, entry points, data stores, and third-party services.
2. Identify abuse cases: BOLA/IDOR, privilege escalation, injection, replay, session theft, secret extraction, SSRF, file abuse, quota/cost abuse, cross-account leakage, and denial of service.
3. Check client input handling, deep links/intents, exported components, WebViews, permissions, backups, logs, crash reports, clipboard, and screen previews where sensitive.
4. Verify server-side object authorization for every operation. Test as anonymous, owner, non-owner, and cross-tenant users.
5. Inspect SQL grants/RLS, views, functions, SECURITY DEFINER, Edge Function auth, Storage policies, Realtime channels, and API rate limits.
6. Scan secrets and sensitive artifacts, including Git history and release outputs. A discovered credential is compromised: revoke/rotate, investigate use, remove exposure, and review history/artifacts.
7. Review dependency advisories, platform declarations, SDK data practices, privacy manifests, and required permission rationales.
8. Test negative paths and abuse controls in an isolated authorized environment. Never probe third-party or production systems without explicit authorization and a safe test plan.
9. Report findings with severity, affected asset, exploit preconditions, evidence, impact, remediation, and retest status.

## Severity and release blocking

Critical findings include active secret exposure, unauthenticated access to sensitive data, cross-tenant data access, remote code execution, or high-impact data destruction. High findings include exploitable authorization bypass, sensitive data leakage, or broken controls in a critical journey. Critical and High findings block release until fixed or explicitly risk-accepted by the accountable human owner with compensating controls.

## Pitfalls

Relying on client-side guards, hiding UI controls, obfuscation, publishable keys, device biometrics, root detection, or CORS as authorization; broad service-role access; weak RLS; sensitive telemetry; permissive TLS; untested upload paths; and security claims unsupported by evidence.

## Acceptance gate

Provide threat model, attack-surface coverage, prioritized findings, automated negative tests where feasible, secrets/log/artifact review, and retest evidence. State clearly what was not tested and do not use "secure" as an absolute guarantee.
