# Flutter Product Engineering Skills

A coordinated skill set for building high-quality Flutter/Dart Android and iOS products. The engineering target is deep Flutter/Dart correctness and maintainability, paired with original Apple-HIG-informed product craft and platform-appropriate behavior.

## Core entrypoint

- [SKILL.md](SKILL.md) — Flutter/Dart implementation team, fixed constraints, evidence rules, and specialist routing.

## Specialist skills

| Skill | Owns |
|---|---|
| [Company Orchestrator](skills/company-orchestrator/SKILL.md) | Cross-team planning, task routing, dependencies, conflicts, and final readiness |
| [Product Discovery](skills/product-discovery/SKILL.md) | User problem, evidence, scope, requirements, and acceptance criteria |
| [Mobile Design Research](skills/mobile-design-research/SKILL.md) | Appllama-compatible reference research, category patterns, and design briefs for Flutter |
| [Apple Product Craft](skills/apple-product-craft/SKILL.md) | UX/UI, Apple HIG-informed design, visual hierarchy, motion, and native-feeling interaction |
| [Flutter Architecture](skills/flutter-architecture/SKILL.md) | Architecture, state ownership, boundaries, contracts, and ADRs |
| [Supabase Backend Engineering](skills/supabase-backend-engineering/SKILL.md) | PostgreSQL, RLS, Auth, Storage, Realtime, Edge Functions, and Gemini |
| [Native Platform Integration](skills/native-platform-integration/SKILL.md) | Swift/Kotlin host APIs, plugins, platform channels, permissions, and lifecycle (conditional) |
| [AI Product Engineering](skills/ai-product-engineering/SKILL.md) | Model evaluation, RAG, prompts, structured output, tool safety, and cost (conditional) |
| [Accessibility & Localization](skills/accessibility-localization/SKILL.md) | Screen readers, text scaling, contrast, Arabic/English, and RTL |
| [Mobile QA Engineering](skills/mobile-qa-engineering/SKILL.md) | Independent testing, regression, device coverage, and acceptance |
| [Mobile Security Engineering](skills/mobile-security-engineering/SKILL.md) | Threat modeling, client/API/backend security, and independent review |
| [Mobile Performance & Reliability](skills/mobile-performance-reliability/SKILL.md) | Profiling, frame timing, startup, memory, network, and reliability |
| [Mobile Release & Operations](skills/mobile-release-operations/SKILL.md) | CI/CD, signing, rollout, monitoring, incidents, and recovery |

Flutter/Dart implementation remains owned by the root SKILL.md; specialist skills do not create competing Flutter implementations.

## Shared references

- [Team Operating Model](references/team-operating-model.md) — universal role boundaries, handoff contract, severity, evidence, and definition of done.
- [Architecture](references/architecture.md) — project structure, layers, Riverpod, GoRouter, networking, storage, and configuration.
- [Supabase Backend](references/backend-supabase.md) — database security, RLS, migrations, Auth, Storage, Realtime, Edge Functions, and Gemini.
- [Design System](references/design-system.md) — first-party Flutter design system, components, states, and motion.
- [Flutter UI Translation](references/flutter-ui-translation.md) — maps Expo/React Native design ideas to Flutter SDK and Dart equivalents; no Expo code is imported.
- [Localization & Accessibility](references/localization-accessibility.md) — English/Arabic, RTL, formatting, and accessibility requirements.
- [Pitfalls](references/pitfalls.md) — recurring errors, prevention, detection, and regression practices.
- [Quality](references/quality.md) — tests, performance, security, CI/CD, production operations, and release gates.
- [Workflow](references/workflow.md) — requirements, project docs, decision authority, reporting, and learning loop.

## Optional Appllama research

When the agent environment supports custom MCP servers, Appllama documents its MCP endpoint at https://mcp.appllama.io/mcp. Connect it through the target coding agent's supported MCP configuration. The MCP is optional: the Flutter research skill also works from user-provided references and other authorized sources. Check the account's current plan/credit allowance before conducting research.

## How to use

- Use the root SKILL.md for Flutter/Dart implementation tasks.
- Use the Company Orchestrator for new products, multi-team features, or end-to-end delivery.
- Load only relevant specialist skills. Do not load every specialist for a trivial task.
- Keep the repository structure intact so specialist skills can reach shared references under references/.
- If the agent cannot spawn separate agents, it may perform sequential specialist passes, but it must not claim independent team execution.

## Validate the skill repository

GitHub Actions runs the dependency-free validator on pushes and pull requests to main. Run the same check locally before submitting changes:

    python3 scripts/validate_skills.py

It checks Agent Skills frontmatter, unique names, directory/name alignment, and local Markdown links. It validates repository structure only; it does not prove that an agent follows the instructions or that a generated app is correct.

## Product and engineering scope

Flutter + Dart; Android and iOS. SDK-first implementation, first-party design system, stable SDK pinning through FVM, explicit architecture and quality gates, no generated Dart code except Flutter's built-in gen-l10n workflow. Supabase is the default backend when a backend is needed, not a requirement for every app.

## Quality philosophy

No checklist can guarantee zero defects. Quality is earned through explicit requirements, traceable acceptance, independent verification, real-device testing, security controls, measurable performance, controlled releases, monitoring, and recovery drills. Unverified work must stay labeled as unverified.
