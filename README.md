# Flutter Engineering Skills

Production-oriented AI-assisted engineering guidance for Flutter and Dart mobile applications (Android and iOS).

## Skill

- `SKILL.md` — skill entrypoint and operating rules.

## References

- `references/architecture.md` — architecture, layers, Riverpod, GoRouter, networking, storage, configuration.
- `references/backend-supabase.md` — Supabase backend architecture, RLS, Auth, Storage, Realtime, Edge Functions, Gemini API security.
- `references/design-system.md` — first-party design system, components, screen states, motion.
- `references/localization-accessibility.md` — English/Arabic localization, RTL, accessibility.
- `references/pitfalls.md` — common failures, prevention, detection, regression practices.
- `references/quality.md` — testing, performance, security, platform, CI/CD, release gates.
- `references/workflow.md` — requirements, traceability, project docs, decision authority, reporting.

Load only the reference needed for the current task. Verify current package APIs, versions, and platform requirements against official sources before implementation.

## Scope

Flutter + Dart; Android and iOS only. Manual Riverpod 3 providers, GoRouter, Dio for non-Supabase HTTP integrations, Supabase as the default full backend, Gemini through Supabase Edge Functions, and a first-party design system. No third-party UI framework as the design foundation and no generated-code dependencies (except Flutter gen-l10n).

## Usage

Install or copy this skill into the AI coding tool's supported skills directory. Keep `SKILL.md` and its `references/` directory together so linked references resolve.
