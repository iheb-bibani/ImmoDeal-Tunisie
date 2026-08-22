# Roadmap

## Phase 0 — Start the historical clock

1. Run respectful daily collection on a small Tayara sample.
2. Validate archived payloads and PII redaction against real pages.
3. Expand coverage gradually only after collection quality is measured.
4. Add a second source adapter without changing the raw snapshot contract.

## Phase 1 — Derived parsing

Reparse archived payloads offline into versioned structured tables. Add geography, property type, transaction type, surface semantics and amenity extraction without mutating the raw archive.

## Phase 2 — Entity resolution

Study real duplicate/republication patterns, create labelled candidate pairs, build `resolution_version` mappings, and measure precision before using unique-property statistics.

## Phase 3 — Market analytics

Build asking-price distributions, robust comparable sets, days-observed metrics, price-change history and reappearance statistics. Show sample sizes and uncertainty.

## Phase 4 — Rentals

Collect rental inventory with the same raw-first contract. Build the first predictive rental model only after leakage, duplicates and temporal validation are controlled.

## Phase 5 — External calibration

Create a quarterly ImmoDeal asking-price index and compare its **growth** with INS transaction-index growth. Do not use INS to infer fine-grained absolute transaction levels.

## Phase 6 — Product research

Only after data quality is understood: comparable-property interface, investor views, alerts, map analytics, and anomaly detection. Transaction-value or liquidity models require separate validation and must not be inferred from listing disappearance alone.
