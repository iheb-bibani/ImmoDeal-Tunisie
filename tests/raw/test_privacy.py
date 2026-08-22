import json
from immodeal.raw.privacy import redact_payload


def test_json_redaction_removes_contact_pii_recursively():
    payload = json.dumps({
        "title": "S+2 La Soukra",
        "phone": "+216 22 333 444",
        "seller": {"email": "person@example.com", "name": "Private Person"},
        "price": 300000,
    }).encode()
    out = json.loads(redact_payload(payload, "json"))
    assert out["phone"] == "[REDACTED]"
    assert out["seller"]["email"] == "[REDACTED]"
    assert out["seller"]["name"] == "[REDACTED]"
    assert out["price"] == 300000


def test_html_redaction_removes_email_and_tunisian_phone():
    payload = b'<div>Contact me: person@example.com or +216 22 333 444</div><a href="tel:+21622333444">call</a>'
    text = redact_payload(payload, "html").decode()
    assert "person@example.com" not in text
    assert "22 333 444" not in text
    assert "22333444" not in text
    assert "[REDACTED]" in text


def test_html_redaction_removes_contact_identity_blocks():
    payload = b'<article><h1>Appartement</h1><div class="seller-profile">Private Person +216 22 333 444</div><p>105 m2</p></article>'
    text = redact_payload(payload, "html").decode()
    assert "Private Person" not in text
    assert "Appartement" in text
    assert "105 m2" in text


def test_json_redaction_removes_contact_data_embedded_in_description():
    payload = json.dumps({
        "description": "Appelez +216 22 333 444 ou person@example.com",
        "price": 300000,
    }).encode()
    text = redact_payload(payload, "json").decode()
    assert "22 333 444" not in text
    assert "person@example.com" not in text
    assert "300000" in text
