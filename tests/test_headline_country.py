# -*- coding: utf-8 -*-
import pandas as pd
from swatch import cases, extract


def test_headline_country_outranks_places_in_the_body():
    r = extract.extract("Indonesia Seizes 1.16 Tonnes Of Ketamine From Tanker",
                        "The tanker owner in Selangor, Malaysia, departed from Malaysia.")
    assert r["seizure_country"] == "Indonesia"


def test_sumatra_is_a_place_in_indonesia():
    r = extract.extract("Tanker owner among 2 nabbed over 1.16-tonne drug bust in Sumatra", "Ketamine bound for Myanmar.")
    assert r["seizure_country"] == "Indonesia" and r["seizure_place"] == "Sumatra"


def test_destination_in_headline_is_not_the_seizure_country():
    r = extract.extract("U.S. women arrested for allegedly smuggling drugs to Japan", "")
    assert r.get("seizure_country") != "Japan"


def test_shared_vessel_merges_reports_up_to_two_weeks_apart():
    base = dict(primary_drug="Ketamine", qty_kg=None, qty_units=None, corridor=None, seizure_country="Indonesia",
                seizure_place=None, origin=None, destination=None, vessel="Global 168", container_numbers=None,
                completeness=3, title="a", title_en=None)
    df = pd.DataFrame([dict(base, event_id=1, published=pd.Timestamp("2026-10-01")),
                       dict(base, event_id=2, published=pd.Timestamp("2026-10-09"))])
    assert cases.merge_cases(df)["event_id"].nunique() == 1
