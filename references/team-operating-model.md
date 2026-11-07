# Team Operating Model

This file defines the shared contract for every specialist skill in this repository. Specialist skills own their domain; this document owns collaboration rules. Do not copy these rules into every skill.

## Shared execution contract

Every assignment must identify:

- **Objective:** the user or business outcome, not just the requested code change.
- **Owner:** one accountable specialist for the deliverable.
- **Scope / out of scope:** explicit boundaries and forbidden changes.
- **Inputs:** requirements, existing implementation, decisions, constraints, platform targets, and dependencies.
- **Acceptance:** observable conditions that prove the deliverable works.
- **Evidence:** commands, tests, screenshots, measurements, review findings, or source references.
- **Risks and assumptions:** unresolved items, impact, owner, and decision deadline.
- **Handoff:** files changed, contracts changed, downstream teams affected, and required next action.

Do not begin implementation when a missing requirement could change data ownership, security, irreversible behavior, product scope, or architecture. Ask the single most useful question or document a safe assumption and its consequence.

## Responsibility boundaries

| Role | Owns | Does not own |
|---|---|---|
| Product discovery | Problem validation, users, outcomes, requirements | Architecture or implementation decisions |
| Product orchestrator | Work routing, dependency order, scope, conflict resolution, final readiness | Quietly overriding a domain specialist's evidence |
| Apple product craft | UX/UI quality, interaction design, visual system, platform fit | Product requirements, backend authorization |
| Architecture | Boundaries, contracts, data flow, technical decisions | Feature implementation or independent approval |
| Flutter engineering | Dart/Flutter implementation and maintainability | Approving its own critical security or release gates |
| Backend engineering | Database, APIs, Edge Functions, backend behavior | Client-only authorization decisions |
| Accessibility/localization | Accessible interaction, language, RTL, platform settings | Removing product requirements to simplify tests |
| QA | Independent verification against acceptance criteria | Silently changing expected product behavior |
| Security | Threat model, controls, independent security verification | Claiming security from static review alone |
| Performance/reliability | Profiling, service objectives, bottleneck analysis, resilience | Premature optimization without measurements |
| Release/operations | CI/CD, signing, deployment, observability, recovery | Publishing or destructive production changes without authorization |

One person or agent may perform multiple roles when resources are limited, but the work must still use separate review passes. Never claim independent review when the same agent only reread its own implementation.

## Handoff protocol

A handoff is accepted only when it contains:

1. Deliverable and its location.
2. Updated interfaces/contracts and compatibility notes.
3. Acceptance criteria with evidence and status.
4. Tests performed and tests not performed.
5. Known defects, security/privacy risks, and assumptions.
6. Dependencies or decisions needed from another role.

Downstream teams must reject ambiguous contracts rather than inventing API shapes, ownership rules, or UI behavior.

## Severity and escalation

- **Critical:** active exposure, data loss/corruption, unauthorized access, app-wide crash, irreversible production damage. Stop the affected release/workflow and escalate immediately.
- **High:** material security, privacy, correctness, accessibility, or reliability defect in a critical journey. Block acceptance until fixed or explicitly risk-accepted by the accountable owner.
- **Medium:** degraded non-critical behavior, maintainability issue, or bounded defect with a safe workaround. Track with owner and due date.
- **Low:** polish or non-blocking improvement. Do not expand scope without value and priority.

A specialist may stop work when a requested action would violate its safety boundary, invalidate evidence, or create irreversible risk.

## Cross-team quality rules

- Requirements are the source of truth for intended behavior. Design files, code comments, and tests must not silently redefine it.
- Architecture decisions are recorded once in the project decision log. Do not maintain duplicate decision documents.
- API, route, event, database, and design-system contracts must have one owner and version/compatibility rules where needed.
- Security, accessibility, privacy, and performance are considered during discovery and design, not added only at release.
- The implementer does not self-approve critical QA, security, or release gates.
- A passing static check is not proof of runtime behavior. A passing test is evidence only for the behavior it actually exercises.
- Mark items Verified, Partially verified, Not verified, Failed, Blocked, or N/A with a reason. Never replace missing evidence with a confidence score.
- Create a shared abstraction only when a real second use or stable contract exists. No placeholder layers, empty features, speculative services, or architecture for hypothetical scale.

## Definition of done

A deliverable is complete only when its applicable specialist gate passes, downstream contracts are updated, known risks are visible, and evidence is recorded. Product release is complete only after application, security, performance, accessibility, backend, and release gates applicable to that product have passed.

## Required output

Use the same concise report shape for every role:

- **Decision / result**
- **Changed artifacts**
- **Acceptance evidence**
- **Not verified / blocked**
- **Risks and handoff**
- **Next owner**

Do not repeat entire source documents in reports.
