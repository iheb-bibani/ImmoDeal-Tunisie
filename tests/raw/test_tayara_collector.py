from immodeal.collectors.tayara import extract_listing_candidates, extract_raw_fields


def test_extracts_unique_tayara_item_links_and_ids():
    html = b'''<html><body>
      <a href="/item/appartements/tunis/l-aouina/appartement-s2/6a70cc87f1282c6658e2c996/">A</a>
      <a href="https://www.tayara.tn/item/appartements/tunis/l-aouina/appartement-s2/6a70cc87f1282c6658e2c996/">dup</a>
      <a href="/listing/c/immobilier/search/">not item</a>
    </body></html>'''
    found = extract_listing_candidates(html)
    assert len(found) == 1
    assert found[0].source_listing_id == "6a70cc87f1282c6658e2c996"
    assert found[0].url.startswith("https://www.tayara.tn/item/")


def test_extract_raw_fields_keeps_values_un_normalized():
    html = b'<html><body><h1>S+2</h1><div>320 000 DT</div><p>Superficie 105 m2</p></body></html>'
    fields = extract_raw_fields(
        html,
        "https://www.tayara.tn/item/appartements/tunis/l-aouina/appartement-s2/6a70cc87f1282c6658e2c996/",
    )
    assert fields["price_raw"] == "320 000 DT"
    assert fields["surface_raw"] == "105 m2"
    assert fields["location_raw"] == "tunis / l-aouina"
