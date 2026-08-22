from __future__ import annotations

import re
import time
from datetime import datetime, timezone
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

from .base import ListingCandidate
from ..raw.models import RawFetch

BASE_URL = "https://www.tayara.tn"
SEARCH_URL = f"{BASE_URL}/listing/c/immobilier/search/"
USER_AGENT = "ImmoDeal-Tunisie/0.2 (+research; respectful daily archive)"
ID_RE = re.compile(r"^[0-9a-f]{24}$", re.I)

PRICE_RE = re.compile(r"(?<![\d+])(\d[\d\s.,]{1,20})\s*DT\b", re.I)
SURFACE_RE = re.compile(r"(?<!\d)(\d[\d\s.,]{0,12})\s*m(?:2|²)\b", re.I)


def extract_raw_fields(html: bytes, url: str) -> dict[str, str | None]:
    text = BeautifulSoup(html, "html.parser").get_text(" ", strip=True)
    price_match = PRICE_RE.search(text)
    surface_match = SURFACE_RE.search(text)
    parts = [p for p in urlparse(url).path.split("/") if p]
    location_raw = None
    if len(parts) >= 4 and parts[0] == "item":
        location_raw = " / ".join(parts[2:4])
    return {
        "price_raw": price_match.group(0).strip() if price_match else None,
        "surface_raw": surface_match.group(0).strip() if surface_match else None,
        "location_raw": location_raw,
    }


def extract_listing_candidates(html: bytes) -> list[ListingCandidate]:
    soup = BeautifulSoup(html, "html.parser")
    found: dict[str, ListingCandidate] = {}
    for anchor in soup.find_all("a", href=True):
        href = anchor.get("href") or ""
        absolute = urljoin(BASE_URL, href)
        parsed = urlparse(absolute)
        if parsed.netloc not in {"www.tayara.tn", "tayara.tn"} or "/item/" not in parsed.path:
            continue
        parts = [p for p in parsed.path.split("/") if p]
        if not parts:
            continue
        source_id = parts[-1]
        if not ID_RE.match(source_id):
            continue
        canonical = f"{BASE_URL}{parsed.path if parsed.path.endswith('/') else parsed.path + '/'}"
        found[source_id] = ListingCandidate("tayara", source_id, canonical)
    return list(found.values())


class TayaraCollector:
    def __init__(self, delay_seconds: float = 1.0, timeout_seconds: float = 20.0):
        self.delay_seconds = delay_seconds
        self.timeout_seconds = timeout_seconds
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": USER_AGENT, "Accept-Language": "fr-FR,fr;q=0.9"})

    def discover(self, url: str = SEARCH_URL) -> list[ListingCandidate]:
        response = self.session.get(url, timeout=self.timeout_seconds)
        response.raise_for_status()
        return extract_listing_candidates(response.content)

    def discover_pages(self, max_pages: int = 1) -> list[ListingCandidate]:
        found: dict[str, ListingCandidate] = {}
        for page in range(1, max_pages + 1):
            url = SEARCH_URL if page == 1 else f"{SEARCH_URL}?page={page}"
            batch = self.discover(url)
            before = len(found)
            for candidate in batch:
                found[candidate.source_listing_id] = candidate
            if page > 1 and len(found) == before:
                break
            if self.delay_seconds and page < max_pages:
                time.sleep(self.delay_seconds)
        return list(found.values())

    def fetch(self, candidate: ListingCandidate) -> RawFetch:
        if self.delay_seconds:
            time.sleep(self.delay_seconds)
        response = self.session.get(candidate.url, timeout=self.timeout_seconds)
        fetched_at = datetime.now(timezone.utc)
        fields = extract_raw_fields(response.content, candidate.url)
        return RawFetch(
            source="tayara",
            source_listing_id=candidate.source_listing_id,
            url=candidate.url,
            snapshot_date=fetched_at.date(),
            fetched_at=fetched_at,
            http_status=response.status_code,
            payload_format="html",
            payload=response.content,
            price_raw=fields["price_raw"],
            surface_raw=fields["surface_raw"],
            location_raw=fields["location_raw"],
            parser_hint_version="tayara-html-v1",
        )
