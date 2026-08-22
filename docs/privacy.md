# Privacy policy for collection

ImmoDeal archives public real-estate listing content for market research, while minimizing personal data collection.

## Collection rule

The ingestion order is mandatory:

```text
FETCH -> REDACT -> HASH -> COMPRESS -> STORE
```

The unredacted payload must not be intentionally persisted to disk, the metadata database, logs, fixtures, or Git history.

## Data intentionally retained

- listing source and public listing ID;
- listing URL;
- observation timestamps;
- property description after personal-data redaction;
- asking price as published;
- raw surface wording;
- raw property location wording;
- non-personal property characteristics;
- public business/agency information when useful and legally appropriate.

## Data intentionally removed

- private seller names;
- clear-text telephone/mobile/WhatsApp numbers;
- personal email addresses;
- unnecessary user/profile identifiers;
- contact/profile HTML blocks when they primarily identify a person.

If a future technical workflow genuinely requires stable comparison of a contact identifier, use a keyed HMAC and never store the original value.

## Parser evolution

Privacy redaction happens before the raw payload enters the immutable archive. New source adapters must include regression tests for any source-specific identity fields discovered in real pages.
