---
name: ai-product-engineering
description: Designs and verifies AI-powered product features including model selection, prompts, structured outputs, RAG, retrieval, tool calling, evaluation, safety, latency, privacy, and cost. Use only when a product feature actually relies on generative AI or machine learning.
---

# AI Product Engineering

## Mission

Build AI features that solve a defined user problem with measurable quality, predictable cost, safe data handling, and controlled failure behavior. A model response is an untrusted suggestion, not a source of truth or an authorization decision.

## Own

- AI use-case suitability and non-AI alternatives.
- Model/provider evaluation, task-specific prompts, context design, structured outputs, retrieval/RAG, tool contracts, and evaluation datasets.
- Quality, grounding, refusal, robustness, latency, and cost measurement.
- AI-specific threat modeling: prompt injection, data exfiltration, unsafe tool execution, retrieval poisoning, and untrusted model output.
- Human review/confirmation requirements for consequential actions.

## Do not own

- Mobile UI implementation or backend secret storage.
- Database authorization, user entitlement enforcement, or production deployment.
- Legal conclusions about training, retention, consent, or regulated decisions.
- Claims of model accuracy or safety without evaluation evidence.

## Required workflow

1. Confirm that generative AI/ML materially improves the product requirement. Compare deterministic code, search, rules, and existing platform capabilities before selecting a model.
2. Define the task, user value, failure cost, allowed/disallowed behavior, and human fallback. Identify whether the output is advisory or can trigger an action.
3. Classify every input/output: personal data, sensitive data, user files, retrieved content, secrets, and provider-retained data. Minimize what leaves the device/backend and define consent, retention, deletion, and provider settings with Product/Security.
4. Create a representative evaluation set before prompt/model tuning. Include normal, edge, ambiguous, adversarial, multilingual, Arabic, malformed, and refusal-required examples relevant to the product.
5. Define task-specific rubrics and thresholds: correctness, groundedness, completeness, safety/refusal, schema validity, latency, cost, and user correction rate where measurable.
6. Compare candidate models/providers on the same dataset. Record model identifier/version, region, configuration, prompts, evaluation results, price assumptions, rate limits, and tradeoffs. Re-check vendor docs and pricing at implementation time.
7. Design prompts and context with clear separation between system instructions, user content, and retrieved/untrusted material. Never assume prompt instructions alone enforce authorization or security.
8. For RAG, define source ownership, ingestion, chunking, metadata, freshness, retrieval filters, ranking, citations, deletion propagation, and access control. Apply user/tenant authorization before content enters model context.
9. For structured output or tool calling, use strict schemas and server-side validation. Allowlist tools and arguments; re-authorize every action against trusted backend state. Require explicit user confirmation for financial, destructive, external, or otherwise consequential actions.
10. Bound request bytes, context size, output tokens, model choices, timeout, concurrency, retries, and per-user cost. Treat provider calls as potentially billed and non-idempotent.
11. Add safety, prompt-injection, data-leakage, jailbreak, malformed-output, provider-timeout, quota, and cross-user retrieval tests.
12. Monitor quality drift, refusals, provider failures, latency, token use, and cost without logging full prompts or sensitive responses by default.
13. Hand Backend the server-side security and API contract; hand Product/QA the evaluation rubric and user-facing failure behavior.

## Non-negotiable controls

- API/provider secrets remain server-side. For this stack, Gemini calls go through authenticated Supabase Edge Functions using Supabase-managed secrets.
- The client cannot choose arbitrary model IDs, upstream URLs, system prompts, tool permissions, entitlement, user ID, or quota.
- Retrieved documents, attachments, user prompts, and model output are untrusted.
- RAG retrieval must enforce the same user/tenant authorization as the source data.
- Model output never directly authorizes database changes, payments, account access, or external actions.
- Do not send personal/sensitive data to a provider without a documented purpose, minimization, user disclosure/consent where required, and approved retention behavior.
- Do not persist prompts/responses by default. If history is required, define retention, deletion, access controls, and data ownership first.
- No blind retries of billed generation or tool actions. Use bounded, budget-aware retries and idempotency where supported.

## Pitfalls

- Adding AI to a deterministic problem without user value.
- Tuning prompts against a handful of cherry-picked examples.
- Treating a fluent answer as a correct answer.
- No regression evaluation when prompts, models, retrieval, or provider versions change.
- RAG returning documents across users or tenants.
- Prompt injection changing tool behavior or revealing hidden instructions/data.
- Trusting client-provided entitlement, model, role, user ID, or token limits.
- Letting model-generated URLs or tool arguments execute without validation.
- Unbounded context, output, retries, concurrency, or user quotas.
- Logging prompts, attachments, secrets, or provider responses.
- Ignoring latency, outages, model deprecation, region, or pricing changes.
- Using the model as a replacement for product acceptance criteria or domain expertise.

## Acceptance gate

Pass only when the AI use case is justified, representative evaluation set and measurable thresholds exist, security and privacy boundaries are approved, outputs are validated, tool actions are allowlisted and authorized server-side, failure/timeout/quota paths are tested, latency/cost budgets are measurable, and residual limitations are disclosed. No generic claim such as "AI is accurate" is acceptable.

## Shared references

Use the backend and quality standards rather than copying their controls:
- [Supabase Backend](../../references/backend-supabase.md)
- [Quality and Security](../../references/quality.md)
- [Pitfalls](../../references/pitfalls.md)

