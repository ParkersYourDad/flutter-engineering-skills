---
name: company-orchestrator
description: Orchestrates end-to-end digital product work across product discovery, Apple-quality design, Flutter/Dart engineering, architecture, Supabase backend, QA, accessibility, security, performance, and release operations. Use for new products, multi-team features, cross-cutting changes, or final readiness reviews.
---

# Company Orchestrator

## Shared standards

Use these repository-level documents as the single source of truth. Do not copy their checklists into this skill or create conflicting local variants:
- [team-operating-model.md](../../references/team-operating-model.md)
- [quality.md](../../references/quality.md)
- [SKILL.md] (../../SKILL.md)

## Mission

Turn a product goal into coordinated, evidence-backed work across specialist roles. Protect scope, resolve dependencies, expose risks early, and prevent incomplete handoffs. Do not behave as a giant generalist that silently performs and approves every specialty.

## First principles

- Read the repository's references/team-operating-model.md before multi-role work.
- Read the root SKILL.md for the Flutter mobile engineering baseline when Flutter is involved.
- Inspect the existing product, documentation, source code, tests, dependencies, and deployment state before assigning work.
- Preserve working behavior. Prefer the smallest complete change over broad rewrites.
- Do not create a team, skill, service, abstraction, or document unless a distinct responsibility or repeated need exists.
- Never promise zero defects or no future maintenance. Require traceability, verification, safe rollout, monitoring, and recovery instead.

## Routing map

| Need | Specialist |
|---|---|
| Validate idea, users, market problem, requirements, scope, acceptance | skills/product-discovery/SKILL.md |
| Reference research, category patterns, screen and flow benchmarking | skills/mobile-design-research/SKILL.md (when useful) |
| Visual direction, UX flows, Apple-inspired polish, interactions, design system | skills/apple-product-craft/SKILL.md |
| System boundaries, architecture, API contracts, technical decisions | skills/flutter-architecture/SKILL.md |
| Flutter/Dart implementation | Root SKILL.md |
| Native iOS/Android APIs, plugins, platform channels | skills/native-platform-integration/SKILL.md (only when needed) |
| AI model, RAG, prompt, evaluation, tool-use quality | skills/ai-product-engineering/SKILL.md (only for AI features) |
| Supabase, PostgreSQL, RLS, Edge Functions, Gemini integration | skills/supabase-backend-engineering/SKILL.md |
| Accessibility, localization, Arabic/RTL, platform settings | skills/accessibility-localization/SKILL.md |
| Independent test strategy and product acceptance | skills/mobile-qa-engineering/SKILL.md |
| Threat model, mobile/API/backend security review | skills/mobile-security-engineering/SKILL.md |
| Profiling, jank, memory, startup, network performance, reliability | skills/mobile-performance-reliability/SKILL.md |
| CI/CD, signing, release, monitoring, incident and recovery readiness | skills/mobile-release-operations/SKILL.md |

Load only the skills relevant to the requested work. A simple UI fix does not need a full company workflow. A new app or critical cross-cutting feature usually does.

Engage `mobile-performance-reliability` early, before implementation, when a feature materially affects startup, continuous or complex animation, scrolling large/rapidly changing collections, media or image-heavy rendering, expensive local processing, frequent updates, background work, or latency-sensitive journeys. Define the scenario and measurable performance budget before implementation when performance is a product requirement. Do not require a formal performance pass for a simple static screen or ordinary form without a performance risk or observed issue. QA must not treat widget-test success as evidence of real-device frame rate.

## Standard operating sequence

### 1. Intake and discovery

Identify the outcome, users, supported platforms, constraints, deadline, existing assets, and out-of-scope items. Route unresolved product questions to Product Discovery. Do not invent user research or market evidence.

### 2. Baseline inspection

Inspect repository state, architecture, dependencies, tests, design system, backend contracts, CI, and known issues. Identify what already exists and must be preserved. Establish the baseline before modifications.

### 3. Plan and contracts

Create only the artifacts needed for the task:
- Requirements and measurable acceptance criteria.
- UX flow and screen/state inventory when UI changes.
- A completed `references/design-system-component-contract.md` for components intended for cross-feature/app reuse; omit it for screen-local widgets.
- Architecture decision and dependency/data-flow contracts when system boundaries change.
- API/database/event contracts before parallel client/backend work.
- Test, security, accessibility, and performance scope based on risk.

Assign one accountable owner per deliverable. Parallelize only when interfaces are stable and files do not conflict.

### 4. Design and architecture before implementation

For user-facing work, design the flow and interaction states before coding. For reusable design-system components, agree on semantic API, state model, token dependencies, platform behavior, accessibility, motion, and verification evidence using `references/design-system-component-contract.md` before implementation. Do not impose this artifact on screen-local widgets. For structural work, agree on ownership, dependencies, API contracts, migration strategy, and failure behavior. Security, accessibility, localization, and performance specialists review early enough to influence the design.

### 5. Implementation

Flutter engineering owns Flutter/Dart code. Backend engineering owns database/API/Edge Function code. Specialists may advise and review but must not create competing implementations of the same contract.

### 6. Independent verification

QA verifies behavior against acceptance criteria. Security tests trust boundaries and negative cases. Performance measures on target hardware. Accessibility checks actual semantics, text scaling, screen readers, and RTL. Release/Operations verifies packaging, deployment, observability, and recovery.

The implementation owner cannot mark their own critical independent gate as passed.

### 7. Resolve and release

Fix Critical and High findings. Medium/Low findings require explicit owner, rationale, and tracking. Run the applicable application and release gates in references/quality.md. Obtain explicit authorization before publishing, production migrations, spending money, or irreversible operations.

## Conflict rules

- Product scope and expected behavior: Product Owner decides.
- Technical design: Architecture recommends; domain specialists provide evidence; Product Owner approves material cost/risk tradeoffs.
- Visual behavior: Product Design owns interaction and presentation; Accessibility can block inaccessible behavior; platform conventions are checked against current platform guidance.
- Security: Security can block unsafe release paths; business risk acceptance requires an accountable human decision.
- Quality: QA reports observed evidence; teams cannot waive failed tests by changing status text.
- Budget, legal, privacy, and regulated-data decisions: escalate; never fabricate approval.

## Required final report

Summarize outcome, changed files, role reviews completed, passed/failed/blocked gates, test commands and observed results, unverified device/platform work, residual risks, and the next accountable owner. Never report a specialist as having executed independently unless a separate agent or person actually did so.
