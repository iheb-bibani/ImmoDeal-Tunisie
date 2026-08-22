# Methodology

## What ImmoDeal can observe directly

Public listing data describes the seller's asking market, not completed transactions. Online inventory is subject to survivorship/composition bias: correctly priced properties may leave the market faster while overpriced properties remain visible longer.

Therefore asking-price medians are labelled as asking-market references, never as transaction-value ground truth.

## Comparables

Future comparable analysis must operate on inferred unique properties rather than raw listings, expose the number of effective comparables, and report uncertainty. Missing legal status, construction quality, nuisance, exposure, surface definition, syndic quality and other unobserved characteristics must be presented as limitations rather than silently absorbed into a deterministic score.

## No arbitrary Deal Score

ImmoDeal does not use hand-written weighted formulas such as 40% model discount + 20% neighborhood discount. A product surface may instead report robust deviation from comparable asking prices, confidence/sample size, and explicit unknown-risk signals.

## INS index

The Tunisian INS real-estate price index is treated as an external macro trend reference based on registered transactions. It is useful for comparing **growth/drift over time**, subject to the limitations of declared transaction values and its regional/quarterly granularity.

It must not be used to calibrate the absolute transaction level of an individual listing or to arbitrate fine-grained neighborhoods.

## Liquidity and disappearance

A listing disappearance is not a confirmed sale. Sellers may remove, expire or republish listings, including under a new source listing ID. Because this behavior can be correlated with difficulty selling, a naïve survival model would face informative censoring.

ImmoDeal first accumulates disappearance and reappearance observations. A liquidity/survival model is deferred until entity resolution quality and the empirical fraction of republications are understood.

## Rental model before transaction-value model

Rental asking data may ultimately support a more tractable first predictive model than sale transaction value. Any yield derived from sale asking price and rent estimates must be explicitly named as an asking-price-based gross yield, not a realized investment return.
