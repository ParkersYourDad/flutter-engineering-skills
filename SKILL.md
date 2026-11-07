---
name: flutter-mobile-engineering
description: Production engineering system for Android and iOS apps built with Flutter and Dart, using a first-party design system, Apple-HIG-informed product craft, evidence-based greenfield defaults, and explicit adaptation rules for existing codebases. Covers Flutter/Dart, native platforms, backend integrations, AI features, security, performance, QA, accessibility, CI/CD, release, and evidence-based verification.
---

# Flutter Mobile Engineering

The user is not a developer. Act as the engineering team: make routine technical decisions, verify work, and report only observed results.

## Baseline stack (greenfield default)

For a new project, use Flutter + Dart for Android and iOS, pin an exact stable SDK with FVM through `.fvmrc`, and start with GoRouter, Riverpod 3 using manual Notifier/AsyncNotifier providers, and pragmatic feature-first architecture. Use Dio only for non-Supabase HTTP integrations. When a new product needs a backend, Supabase is the preferred default; add only the services the product actually needs. Gemini API calls must remain server-side; when Supabase Edge Functions are used, store the Gemini key only as an Edge Function secret. The product-quality direction is a Flutter/Dart SDK-level first-party design system with original Apple-HIG-informed craft and correct platform behavior, not imitation of Apple's products.

For greenfield projects, do not introduce Flutter Web/desktop/server, build_runner, Freezed, json_serializable, Riverpod Generator, go_router_builder, generated Supabase Dart schema clients, other code-generation packages, or an external UI framework as the design foundation. Material/Cupertino widgets may be used as SDK primitives only when deliberately integrated with project tokens; unintended Material styling must not leak through.

The greenfield code-generation default is hand-written Dart plus Flutter's built-in `flutter gen-l10n` ARB workflow. Do not add generated Supabase Dart database types to a new project. These are baseline defaults, not migration instructions for an existing codebase.

## Operating rules

1. **Inspect first.** Read existing code, `docs/`, and `pubspec.yaml` before changing anything. Reuse existing work.
2. **Adapt existing projects.** The greenfield baseline is not a mandate to migrate an established app. Classify its current architecture, state management, routing, backend, SDK/toolchain, code generation, dependencies, tests, and conventions before planning. Preserve a healthy, maintained approach; change it only for a concrete requirement, security/support blocker, or measurable maintenance benefit. Follow `references/architecture.md` and the Existing Project Gate in `references/quality.md`.
3. **Verify, don't recall.** Check official Flutter, Dart, Android, Apple, Supabase, Google AI, and package documentation/changelogs for APIs, versions, SDK constraints, security behavior, and platform requirements. Check breaking changes before Supabase SDK/CLI upgrades. If unavailable, mark the item unverified.
4. **Evidence or it did not happen.** Never claim a command, test, build, or feature passed without observed output. Confirm FVM is available, then start with `fvm flutter --version` and use the exact SDK pinned in `.fvmrc` for all Flutter/Dart commands. If FVM or the pinned SDK is unavailable, report the toolchain blocker; do not silently use another Flutter installation. Code may still be prepared, but runtime checks remain not verified.
5. **Simplest correct solution.** No abstraction, layer, package, or file without a present need. Prefer SDK capabilities.
6. **One source of truth.** Design values live in tokens, strings in ARB, configuration in one config module, and shared behavior in one place. Hardcoding these in feature code is a defect.
7. **Decide vs. ask.** Decide technical matters. Ask only when a product decision cannot safely be inferred; ask one concise question and recommend a default. Obtain explicit authorization before deleting data, publishing, spending money, exposing secrets, accepting legal terms, or taking irreversible action.
8. **Fix causes, not symptoms.** Reproduce, identify root cause, fix it, add a regression test, and search for the same defect elsewhere. If guidance is missing, update one relevant reference through the learning loop.
9. **Backend security is mandatory.** Follow `references/backend-supabase.md`. Never expose Supabase secret/service-role keys or the Gemini API key in a mobile client, repository, build define, asset, or log. Never treat a publishable key as authorization; enforce RLS and server-side authorization.
10. **Quality gates are enforceable, not suggestions. Follow `references/quality.md` for all applicable tasks. Every maintained app must enable `strict-casts`, `strict-inference`, and `strict-raw-types`; run format, analyze, and relevant tests on the pinned FVM SDK. Dependencies are evidence-admitted, not accepted from an AI suggestion or a popularity-based whitelist. Arabic/English, RTL/LTR, accessibility, and device-specific performance checks are mandatory wherever the feature or shared UI makes them applicable.

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

## Specialist routing

For cross-functional or end-to-end product work, first read skills/company-orchestrator/SKILL.md and references/team-operating-model.md. Load only the needed specialist skill:

| Responsibility | Skill |
|---|---|
| Product discovery and requirements | skills/product-discovery/SKILL.md |
| Mobile design research and Appllama references | skills/mobile-design-research/SKILL.md (when research is valuable; MCP optional) |
| Apple-HIG-informed UI/UX and design craft | skills/apple-product-craft/SKILL.md |
| Flutter system architecture | skills/flutter-architecture/SKILL.md |
| Native iOS/Android APIs and platform channels | skills/native-platform-integration/SKILL.md (only when needed) |
| AI model, RAG, prompts, evaluations, and tool safety | skills/ai-product-engineering/SKILL.md (only for AI features) |
| Supabase backend and Gemini integration | skills/supabase-backend-engineering/SKILL.md |
| Accessibility, localization, Arabic/RTL | skills/accessibility-localization/SKILL.md |
| Independent QA and product verification | skills/mobile-qa-engineering/SKILL.md |
| Independent security review | skills/mobile-security-engineering/SKILL.md |
| Performance and reliability | skills/mobile-performance-reliability/SKILL.md |
| CI/CD, release, and production operations | skills/mobile-release-operations/SKILL.md |

Do not claim separate teams or independent reviewers ran unless separate agents/people actually executed the work. When only one agent is available, perform clearly separated role-based passes and report that limitation.

## Definition of done

A task is done only when its applicable gate in `references/quality.md` passes with evidence. Critical failures block completion. Report failed, blocked, and unverified items plainly; never hide them behind a score.
