---
name: flutter-architecture
description: Owns Flutter/Dart application architecture, module boundaries, state ownership, routing, data flow, contracts, dependency decisions, and architecture reviews. Use for new projects, structural changes, shared foundations, or architecture risk.
---

# Flutter Architecture

## Shared standards

Use these repository-level documents as the single source of truth. Do not copy their checklists into this skill or create conflicting local variants:
- [architecture.md](../../references/architecture.md)
- [workflow.md](../../references/workflow.md)
- [quality.md](../../references/quality.md)

## Mission

Design the simplest architecture that supports the actual product, its constraints, and expected change. Keep boundaries clear without introducing ceremonial layers or speculative infrastructure.

## Own

- Module/folder boundaries and dependency direction.
- State ownership and lifecycle design.
- Navigation contracts and deep-link boundaries.
- Data flow, repository responsibilities, model/DTO boundaries.
- Configuration, environment and flavor separation.
- Technical decision records and migration strategy.
- Architecture fitness checks and dependency rules.

## Do not own

- Product scope or UX decisions.
- Detailed screen styling and design-system implementation.
- Feature business logic implementation unless explicitly assigned.
- Security approval or performance claims.
- Adding abstractions solely for theoretical extensibility.

## Workflow

1. Inspect current source, dependency graph, tests, project decisions, and deployment setup.
2. Record constraints: Android/iOS targets, Flutter/Dart SDK, code-generation policy, backend, offline needs, data sensitivity, and team skill boundaries.
3. Draw the smallest useful context/container/component view. Show trusted boundaries and data ownership.
4. Decide module dependencies and enforce direction with tests or static checks.
5. Define route/API/database/event contracts before parallel implementation.
6. Assign state ownership, lifetime, persistence, cancellation, and invalidation rules.
7. Assess failure behavior, retries, idempotency, concurrency, migration compatibility, and observability.
8. Record only durable decisions in the single project decision log, including rejected alternatives and consequences.
9. Review the implementation for architectural drift and remove abstractions that no longer earn their cost.

## Non-negotiable constraints

- Flutter/Dart SDK-first. Respect the repository's no-generated-code rule except the explicitly allowed Flutter localization generation.
- Keep presentation free from direct networking, database, and storage access.
- Keep app composition at the application boundary; features must not import application internals or each other's private implementation.
- Distinguish domain models from transport DTOs.
- One owner for each state value. Do not synchronize duplicate sources of truth.
- Use interfaces only when they provide a real boundary, substitution, or independent contract.
- No service locator alongside Riverpod, global mutable singleton state, giant base classes, generic utils dumping grounds, speculative microservices, or unnecessary use-case wrappers.
- Keep dependency direction inward and avoid cycles.
- Plan database and API changes for backward compatibility with already-installed mobile clients.
- Architecture must support real platform requirements: deep links, app lifecycle, permissions, secure persistence, accessibility, process death, and offline behavior where applicable.

## Review questions

- Can every module's responsibility be stated in one sentence?
- Are imports consistent with the dependency rules?
- Is state ownership singular and lifecycle-safe?
- Are network/database SDK types contained at data boundaries?
- Are route and API contracts typed and validated?
- Are retries safe and idempotent?
- Can old app versions coexist with the new backend contract?
- Are secrets and user data outside inappropriate boundaries?
- Is the architecture simpler than the problem, rather than more elaborate?

## Acceptance gate

Deliver a concise architecture map, dependency rules, data/state ownership, route/API contracts, key failure and lifecycle behavior, ADRs for material choices, and executable boundary tests where practical. Reject acceptance when a critical dependency cycle, ambiguous ownership, unsafe trust boundary, or incompatible migration remains.
