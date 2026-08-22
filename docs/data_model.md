# Raw-first data model

## Source of truth: `raw_snapshots`

A raw snapshot is one observation of one public listing on one date. It is immutable.

Logical key:

```text
(source, source_listing_id, snapshot_date)
```

Important columns include `fetched_at`, `url`, `http_status`, `payload_format`, `payload_path`, `content_hash`, `price_raw`, `surface_raw`, `location_raw`, and `parser_hint_version`.

There is deliberately **no `property_id`** in this table.

## Why property identity is derived

One physical property may be advertised by several agencies, disappear, be republished with a new listing ID, or move across platforms. Matching quality will improve as real duplication patterns accumulate. Freezing a `property_id` at ingestion would make historical corrections difficult.

Property identity therefore belongs to a separate derived mapping such as:

```text
entity_resolution_run
- resolution_version
- generated_at
- algorithm/config hash

listing_property_mapping
- resolution_version
- source
- source_listing_id
- property_id
- match_confidence
- match_reason
```

A new resolution version may regroup old listings without mutating `raw_snapshots`.

## Reappearance observations

A disappearance is not labelled as a sale. After entity resolution becomes reliable, derived analytics may measure gaps between observations of the same inferred property. A return within a chosen horizon is recorded as a reappearance/republication signal only.

## Three distinct price concepts

The model must never collapse these into one field:

- **asking price**: published listing price;
- **transaction price**: concluded/registered transaction value when genuinely observed;
- **market value**: statistical estimate with uncertainty.
