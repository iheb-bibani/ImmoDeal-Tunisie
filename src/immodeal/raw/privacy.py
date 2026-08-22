from __future__ import annotations

import json
import re
from typing import Any

from bs4 import BeautifulSoup

REDACTED = "[REDACTED]"

PII_KEYS = {
    "phone", "telephone", "tel", "mobile", "whatsapp",
    "email", "mail", "contact_email", "contact_phone",
    "seller_name", "owner_name", "contact_name", "user_name",
    "firstname", "first_name", "lastname", "last_name",
}
GENERIC_IDENTITY_KEYS = {"name"}

EMAIL_RE = re.compile(rb"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", re.I)
TUNISIA_PHONE_RE = re.compile(rb"(?:\+?216[\s.\-]*)?(?:\d[\s.\-]*){8}")
TEL_HREF_RE = re.compile(rb"(?i)(href\s*=\s*[\"'](?:tel|mailto):)[^\"']+")


def _redact_json_value(value: Any, *, parent_key: str | None = None) -> Any:
    if isinstance(value, dict):
        out = {}
        for key, item in value.items():
            normalized = str(key).strip().lower()
            if normalized in PII_KEYS or (
                normalized in GENERIC_IDENTITY_KEYS
                and (parent_key or "").lower() in {"seller", "owner", "contact", "user"}
            ):
                out[key] = REDACTED
            else:
                out[key] = _redact_json_value(item, parent_key=normalized)
        return out
    if isinstance(value, list):
        return [_redact_json_value(item, parent_key=parent_key) for item in value]
    return value


def redact_payload(payload: bytes, payload_format: str) -> bytes:
    if payload_format == "json":
        try:
            parsed = json.loads(payload.decode("utf-8", errors="replace"))
            redacted = _redact_json_value(parsed)
            out = json.dumps(redacted, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
            out = EMAIL_RE.sub(REDACTED.encode(), out)
            out = TUNISIA_PHONE_RE.sub(REDACTED.encode(), out)
            return out
        except json.JSONDecodeError:
            pass

    out = payload
    if payload_format == "html":
        try:
            soup = BeautifulSoup(out, "html.parser")
            sensitive_tokens = ("seller", "owner", "contact", "profile", "phone", "telephone", "whatsapp")
            for tag in soup.find_all(True):
                attrs = " ".join(
                    [str(tag.get("id", "")), " ".join(tag.get("class", [])), str(tag.get("data-testid", ""))]
                ).lower()
                if any(token in attrs for token in sensitive_tokens):
                    tag.decompose()
            out = str(soup).encode("utf-8")
        except Exception:
            pass
    out = TEL_HREF_RE.sub(lambda m: m.group(1) + REDACTED.encode(), out)
    out = EMAIL_RE.sub(REDACTED.encode(), out)
    out = TUNISIA_PHONE_RE.sub(REDACTED.encode(), out)
    return out
