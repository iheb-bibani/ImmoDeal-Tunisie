# ImmoDeal Tunisie

Raw-first real-estate intelligence for Tunisia.

This repository starts with immutable daily snapshots of public listings. Asking price, transaction price, and market value are treated as distinct concepts.

## Core principle

```text
SOURCE
  ↓
FETCH
  ↓
PII REDACTION
  ↓
RAW SNAPSHOT (immutable)
  ↓
DERIVED LAYERS (recalculable)
```

No `property_id` is written during raw ingestion. Entity resolution is versioned and recalculable.

## Raw snapshot fields

- source
- source_listing_id
- snapshot_date
- fetched_at
- url
- price_raw
- surface_raw
- location_raw
- payload_format
- payload_path
- content_hash
- http_status
- parser_hint_version

## Privacy

Clear-text phone numbers, personal emails and personal identity fields are redacted before hashing, compression and storage.

## Quick start

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/macOS
source .venv/bin/activate
pip install -r requirements.txt
pip install -e .
pytest -q
```

## Daily collection

```bash
immodeal collect-tayara \
  --db data/raw_metadata.db \
  --payload-root data/raw_payloads \
  --pages 1 \
  --limit 100 \
  --delay 1.5
```
