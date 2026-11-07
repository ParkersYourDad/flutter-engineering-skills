---
name: mobile-performance-reliability
description: Measures and improves Flutter mobile startup, frame rendering, scrolling, animation, memory, battery, network performance, and service reliability using repeatable evidence. Use for slow or janky apps, performance budgets, profiling, or production reliability.
---

# Mobile Performance and Reliability

## Shared standards

Use these repository-level documents as the single source of truth. Do not copy their checklists into this skill or create conflicting local variants:
- [quality.md] (../../references/quality.md)
- [pitfalls.md] (../../references/pitfalls.md)

## Mission

Find the measured bottleneck and improve the user-visible outcome without premature optimization or unnecessary architecture.

## Own

Performance budgets, profiling plans, startup/frame/memory/network measurements, bottleneck diagnosis, reliability indicators, performance regression checks, and evidence-backed remediation advice.

## Do not own

Visual direction, changing product requirements, broad refactors without evidence, or claiming results from debug/emulator measurements.

## Measurement protocol

- Profile on physical devices in Flutter profile mode; use release builds for release smoke and startup behavior. Debug and emulator results are not release-performance evidence.
- Start with the lowest supported device and include higher-refresh devices when relevant.
- Record device, OS, refresh rate, Flutter/Dart version, build mode, scenario, dataset size, network condition, repetitions, and tools.
- Inspect UI and raster frame timing separately. Frame budget derives from display refresh rate; do not impose one 60 Hz threshold on all devices.
- Report P50/P95 where sample size supports it. Separate cold and warm start, first-use and warmed animations, and local rendering from network wait.
- Measure user journeys: first interaction, primary navigation, scrolling, search/typing, media, sheets, and expensive transitions.
- Measure memory after warm-up and repeated journeys; distinguish temporary allocations and normal garbage collection from retained-object leaks.
- Measure payload sizes, request counts, latency, retries, cancellation, cache hit/miss, and slow-network behavior.
- Monitor energy/background work only when the app uses polling, location, media, frequent sync, or realtime streams.

## Optimization sequence

1. Reproduce the issue under a controlled scenario.
2. Capture a baseline and identify whether the bottleneck is build/layout, raster/GPU, Dart CPU, native/plugin, image decode, memory pressure, I/O, or network.
3. Choose the smallest change that addresses the measured cause.
4. Add or update a regression measurement/test.
5. Compare before and after under the same conditions.
6. Check correctness, accessibility, memory, and battery tradeoffs.

## Avoid

Premature isolates, excessive RepaintBoundary, unbounded caches, loading entire datasets, unnecessary polling, expensive opacity/clipping/saveLayer effects, broad rebuilds, synchronous work in build, and renderer flags without evidence. Keep Flutter renderer defaults unless profiling demonstrates a device-specific issue and the decision is documented.

## Reliability

For production-critical journeys, work with Operations to define SLIs/SLOs for completion, latency, availability, and freshness. Investigate crash/ANR rates, startup regressions, backend dependencies, timeouts, retry storms, and recovery after app pause/resume or connectivity changes.

## Acceptance gate

Every critical performance requirement has a repeatable scenario, environment, metric, percentile, threshold, and baseline. Findings identify the cause; claimed optimizations include before/after evidence. Unmeasured hardware/platform behavior is Not verified.
