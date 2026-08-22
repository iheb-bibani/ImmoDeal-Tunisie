from __future__ import annotations

import gzip
import hashlib
import os
import sqlite3
import tempfile
from pathlib import Path

from .models import RawFetch, RawSnapshotMetadata
from .privacy import redact_payload


DDL = """
CREATE TABLE IF NOT EXISTS raw_snapshots (
    snapshot_id TEXT PRIMARY KEY,
    source TEXT NOT NULL,
    source_listing_id TEXT NOT NULL,
    snapshot_date TEXT NOT NULL,
    fetched_at TEXT NOT NULL,
    url TEXT NOT NULL,
    http_status INTEGER NOT NULL,
    payload_format TEXT NOT NULL,
    payload_compression TEXT NOT NULL,
    payload_path TEXT NOT NULL,
    content_hash TEXT NOT NULL,
    payload_size_bytes INTEGER NOT NULL,
    parser_hint_version TEXT NOT NULL,
    price_raw TEXT,
    surface_raw TEXT,
    location_raw TEXT,
    UNIQUE(source, source_listing_id, snapshot_date)
);
CREATE INDEX IF NOT EXISTS idx_raw_source_date ON raw_snapshots(source, snapshot_date);
CREATE INDEX IF NOT EXISTS idx_raw_listing ON raw_snapshots(source, source_listing_id);
"""


class SnapshotCollisionError(RuntimeError):
    pass


class RawArchive:
    def __init__(self, db_path: str | Path, payload_root: str | Path):
        self.db_path = Path(db_path)
        self.payload_root = Path(payload_root)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.payload_root.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self.conn.executescript(DDL)
        self.conn.commit()

    def close(self) -> None:
        self.conn.close()

    def count(self) -> int:
        return int(self.conn.execute("SELECT COUNT(*) FROM raw_snapshots").fetchone()[0])

    def _existing(self, fetch: RawFetch):
        return self.conn.execute(
            """SELECT * FROM raw_snapshots
               WHERE source=? AND source_listing_id=? AND snapshot_date=?""",
            (fetch.source, fetch.source_listing_id, fetch.snapshot_date.isoformat()),
        ).fetchone()

    @staticmethod
    def _row_to_meta(row: sqlite3.Row) -> RawSnapshotMetadata:
        return RawSnapshotMetadata.model_validate(dict(row))

    def ingest(self, fetch: RawFetch) -> RawSnapshotMetadata:
        redacted = redact_payload(fetch.payload, fetch.payload_format)
        content_hash = hashlib.sha256(redacted).hexdigest()
        existing = self._existing(fetch)
        if existing:
            if existing["content_hash"] != content_hash:
                raise SnapshotCollisionError(
                    f"immutable snapshot collision for {fetch.source}:{fetch.source_listing_id} "
                    f"on {fetch.snapshot_date.isoformat()}"
                )
            return self._row_to_meta(existing)

        snapshot_id = hashlib.sha256(
            f"{fetch.source}|{fetch.source_listing_id}|{fetch.snapshot_date.isoformat()}".encode()
        ).hexdigest()[:24]
        safe_id = "".join(ch if ch.isalnum() or ch in "-_" else "_" for ch in fetch.source_listing_id)
        ext = "json" if fetch.payload_format == "json" else "html"
        rel = Path(fetch.source) / f"{fetch.snapshot_date:%Y}" / f"{fetch.snapshot_date:%m}" / f"{fetch.snapshot_date:%d}" / f"{safe_id}_{content_hash[:12]}.{ext}.gz"
        abs_path = self.payload_root / rel
        abs_path.parent.mkdir(parents=True, exist_ok=True)

        fd, tmp_name = tempfile.mkstemp(prefix=".immodeal-", suffix=".tmp", dir=abs_path.parent)
        os.close(fd)
        try:
            with gzip.open(tmp_name, "wb", compresslevel=6) as fh:
                fh.write(redacted)
            os.replace(tmp_name, abs_path)
        finally:
            if os.path.exists(tmp_name):
                os.unlink(tmp_name)

        values = (
            snapshot_id,
            fetch.source,
            fetch.source_listing_id,
            fetch.snapshot_date.isoformat(),
            fetch.fetched_at.isoformat(),
            fetch.url,
            fetch.http_status,
            fetch.payload_format,
            "gzip",
            rel.as_posix(),
            content_hash,
            len(redacted),
            fetch.parser_hint_version,
            fetch.price_raw,
            fetch.surface_raw,
            fetch.location_raw,
        )
        try:
            self.conn.execute(
                "INSERT INTO raw_snapshots VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                values,
            )
            self.conn.commit()
        except Exception:
            abs_path.unlink(missing_ok=True)
            raise

        return RawSnapshotMetadata(
            snapshot_id=snapshot_id,
            source=fetch.source,
            source_listing_id=fetch.source_listing_id,
            snapshot_date=fetch.snapshot_date,
            fetched_at=fetch.fetched_at,
            url=fetch.url,
            http_status=fetch.http_status,
            payload_format=fetch.payload_format,
            payload_path=rel.as_posix(),
            content_hash=content_hash,
            payload_size_bytes=len(redacted),
            parser_hint_version=fetch.parser_hint_version,
            price_raw=fetch.price_raw,
            surface_raw=fetch.surface_raw,
            location_raw=fetch.location_raw,
        )
