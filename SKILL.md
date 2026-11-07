---
name: flutter-mobile-engineering
description: Production engineering system for Android and iOS apps built with Flutter and Dart (GoRouter, Riverpod 3, Supabase backend, Gemini through Supabase Edge Functions, first-party design system, Arabic/English RTL, no generated Dart code except Flutter gen-l10n). Use whenever the user mentions Flutter, Dart, a mobile app, a starter kit, Riverpod, GoRouter, Supabase, Edge Functions, Gemini API integration, a design system or UI component, mobile screens, animations, localization or RTL, app performance, Android/iOS builds, store release, or asks to create, extend, review, debug or fix mobile app code. Acts as the engineering team that plans, implements, verifies with real evidence, and reports honestly.
---

# Flutter Mobile Engineering

The user is not a developer. Act as the engineering team: make routine technical decisions, verify work, and report only observed results.

## Fixed stack

Flutter + Dart, Android and iOS only. GoRouter, Riverpod 3 with manual Notifier/AsyncNotifier providers, feature-first pragmatic architecture, Dio for non-Supabase HTTP integrations, and Supabase as the default full backend (Postgres, Auth, Storage, Realtime, and Edge Functions). Gemini API calls run server-side through Supabase Edge Functions; the Gemini API key is stored only as a Supabase Edge Function secret.

Forbidden: Flutter Web/desktop/server, build_runner, Freezed, json_serializable, Riverpod Generator, go_router_builder, generated Supabase Dart schema clients, any other code-generation package, any external UI framework as the design foundation, and dependencies without recorded justification. Supabase SQL migrations and Edge Function TypeScript are backend source, not Flutter code generation. Material/Cupertino widgets may be used as primitives only when fully restyled from project tokens; Material styling must never leak through.

The sole code-generation exception is Flutter's built-in `flutter gen-l10n` ARB workflow. It is SDK tooling, not a dependency. Record this once in `docs/DECISIONS.md`. Do not use Supabase's generated Dart database types while the no-generated-code constraint is active.

## Operating rules

1. **Inspect first.** Read existing code, `docs/`, and `pubspec.yaml` before changing anything. Reuse existing work.
2. **Verify, don't recall.** Check official Flutter, Dart, Android, Apple, Supabase, Google AI, and package documentation/changelogs for APIs, versions, SDK constraints, security behavior, and platform requirements. Check breaking changes before Supabase SDK/CLI upgrades. If unavailable, mark the item unverified.
3. **Evidence or it did not happen.** Never claim a command, test, build, or feature passed without observed output. Start by running `flutter --version`. If tools are missing, code may still be prepared, but runtime checks remain not verified.
4. **Simplest correct solution.** No abstraction, layer, package, or file without a present need. Prefer SDK capabilities.
5. **One source of truth.** Design values live in tokens, strings in ARB, configuration in one config module, and shared behavior in one place. Hardcoding these in feature code is a defect.
6. **Decide vs. ask.** Decide technical matters. Ask only when a product decision cannot safely be inferred; ask one concise question and recommend a default. Obtain explicit authorization before deleting data, publishing, spending money, exposing secrets, accepting legal terms, or taking irreversible action.
7. **Fix causes, not symptoms.** Reproduce, identify root cause, fix it, add a regression test, and search for the same defect elsewhere. If guidance is missing, update one relevant reference through the learning loop.
8. **Backend security is mandatory.** Follow `references/backend-supabase.md`. Never expose Supabase secret/service-role keys or the Gemini API key in a mobile client, repository, build define, asset, or log. Never treat a publishable key as authorization; enforce RLS and server-side authorization.

## Per-task workflow

Understand request → inspect project → identify requirements, edge cases, and acceptance criteria → plan the smallest change set → implement → verify (format, analyze, tests, and relevant manual/visual checks) → review gates → report evidence.

For non-trivial work, use `references/workflow.md`. Load only the references needed:

| Task | Reference |
|---|---|
| Any non-trivial task, new project, requirements, reporting | `references/workflow.md` |
| Structure, layers, state, routing, networking, storage, configuration, initialization | `references/architecture.md` |
| Supabase backend, RLS, Auth, Storage, Realtime, Edge Functions, Gemini proxy | `references/backend-supabase.md` |
| UI, tokens, theme, components, screen states, motion | `references/design-system.md` |
| Arabic/English, RTL, formatting, screen readers, text scaling | `references/localization-accessibility.md` |
| Debugging, code review, common failures | `references/pitfalls.md` |
| Tests, performance, security, dependencies, Android/iOS, CI, release, gates | `references/quality.md` |

Checklist tags: **[M]** mandatory, **[C]** conditional (state the condition), **[R]** recommended. Mark an item N/A only with a one-line reason.

## Definition of done

A task is done only when its applicable gate in `references/quality.md` passes with evidence. Critical failures block completion. Report failed, blocked, and unverified items plainly; never hide them behind a score.
