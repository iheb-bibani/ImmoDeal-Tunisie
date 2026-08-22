from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel


class RawFetch(BaseModel):
    source: str
    source_listing_id: str
    url: str
    snapshot_date: date
    fetched_at: datetime
    http_status: int
    payload_format: Literal["html", "json"]
    payload: bytes
    price_raw: str | None = None
    surface_raw: str | None = None
    location_raw: str | None = None
    parser_hint_version: str = "raw-v1"


class RawSnapshotMetadata(BaseModel):
    snapshot_id: str
    source: str
    source_listing_id: str
    snapshot_date: date
    fetched_at: datetime
    url: str
    http_status: int
    payload_format: Literal["html", "json"]
    payload_compression: Literal["gzip"] = "gzip"
    payload_path: str
    content_hash: str
    payload_size_bytes: int
    parser_hint_version: str
    price_raw: str | None = None
    surface_raw: str | None = None
    location_raw: str | None = None
