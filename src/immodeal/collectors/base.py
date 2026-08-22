from dataclasses import dataclass


@dataclass(frozen=True)
class ListingCandidate:
    source: str
    source_listing_id: str
    url: str
