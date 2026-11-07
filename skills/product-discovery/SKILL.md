---
name: product-discovery
description: Defines and validates product problems, users, outcomes, scope, requirements, and measurable acceptance criteria before design and engineering. Use for app ideas, new products, major features, ambiguous requests, or product prioritization.
---

# Product Discovery

## Mission

Convert an idea into a clear, testable product brief. Reduce the risk of building the wrong thing. Do not design architecture or write implementation code.

## Own

- User problem, target segment, context, and current alternatives.
- Evidence quality: interviews, observed behavior, analytics, support signals, market research, and assumptions.
- Product outcome, value proposition, scope, non-goals, and success measures.
- Functional and non-functional requirements with unique IDs.
- User journeys, edge cases, permissions, trust, privacy, and failure expectations at product level.
- Acceptance criteria that QA and design can verify.

## Do not own

- Framework/package selection, database schema, API design, or code structure.
- Pixel-level UI design or visual token decisions.
- Security certification, legal advice, or market-size claims without evidence.
- Turning every suggestion into a requirement.

## Workflow

1. Inspect existing product documentation and analytics before asking questions.
2. State the user/problem/outcome in one concise sentence.
3. Separate verified evidence, user-provided facts, assumptions, and hypotheses.
4. Identify the primary user and the most important job they need to complete.
5. Map the happy path and high-impact alternative paths: first use, empty, error, permission denied, offline, cancellation, account changes, and recovery where relevant.
6. Prioritize using user value, risk, confidence, effort, and dependencies. Avoid false precision in scoring.
7. Define out-of-scope behavior explicitly.
8. Write measurable acceptance criteria and non-functional budgets with the relevant specialist.
9. Hand the brief to Design and Architecture; resolve disagreements before implementation.

## Required deliverables

- Product brief: problem, users, outcome, value, constraints, evidence.
- Scope / non-scope.
- User journey and relevant edge cases.
- Requirements table: ID, requirement, acceptance condition, priority, owner, dependencies, verification.
- Assumptions and open decisions.
- Success metrics with event definitions and data owner.
- Risks involving privacy, AI processing, payments, children, health, or other regulated domains.

## Pitfalls to prevent

- Feature lists presented as product strategy.
- Hypotheses presented as customer research.
- Competitor popularity treated as proof of demand.
- Requirements with words such as fast, intuitive, secure, or premium but no acceptance condition.
- Building for imaginary future scale.
- Defining metrics that cannot be reliably measured.
- Missing cancellation, empty, error, offline, permission, or recovery paths.
- Scope expanding during implementation without a decision and revised acceptance criteria.

## Acceptance gate

Pass only when the primary user/problem/outcome is clear, scope and non-goals are explicit, important assumptions are visible, requirements are testable, critical journeys and failure cases are identified, and downstream owners accept the handoff. Mark unvalidated demand as an assumption, not as proven product-market fit.
