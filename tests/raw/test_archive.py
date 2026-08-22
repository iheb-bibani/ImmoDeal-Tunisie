from datetime import date, datetime, timezone
import gzip
import sqlite3
import pytest

from immodeal.raw.archive import RawArchive, SnapshotCollisionError
from immodeal.raw.models import RawFetch


def make_fetch(payload=b'{"price": 300000, "phone": "+216 22 333 444"}'):
    return RawFetch(
        source="tayara",
        source_listing_id="abc123",
        url="https://example.test/item/abc123",
        snapshot_date=date(2026, 8, 22),
        fetched_at=datetime(2026, 8, 22, 12, tzinfo=timezone.utc),
        http_status=200,
        payload_format="json",
        payload=payload,
        price_raw="300000",
        surface_raw="105 m2",
        location_raw="La Soukra",
    )


def test_archive_writes_redacted_gzip_and_metadata_without_property_id(tmp_path):
    archive = RawArchive(tmp_path / "meta.db", tmp_path / "payloads")
    meta = archive.ingest(make_fetch())
    archive.close()
    assert meta.payload_path.endswith(".json.gz")
    with gzip.open(tmp_path / "payloads" / meta.payload_path, "rb") as fh:
        stored = fh.read()
    assert b"22333444" not in stored and b"22 333 444" not in stored
    conn = sqlite3.connect(tmp_path / "meta.db")
    columns = [r[1] for r in conn.execute("pragma table_info(raw_snapshots)")]
    conn.close()
    assert "property_id" not in columns


def test_same_snapshot_is_idempotent(tmp_path):
    archive = RawArchive(tmp_path / "meta.db", tmp_path / "payloads")
    a = archive.ingest(make_fetch())
    b = archive.ingest(make_fetch())
    assert a.snapshot_id == b.snapshot_id
    assert archive.count() == 1
    archive.close()


def test_same_key_different_content_raises_collision(tmp_path):
    archive = RawArchive(tmp_path / "meta.db", tmp_path / "payloads")
    archive.ingest(make_fetch())
    with pytest.raises(SnapshotCollisionError):
        archive.ingest(make_fetch(payload=b'{"price": 290000}'))
    archive.close()
