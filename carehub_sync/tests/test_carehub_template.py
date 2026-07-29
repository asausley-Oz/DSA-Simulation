import csv
import os
import sys

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from planning_center_carehub.carehub_template import (
    TEMPLATE_COLUMNS,
    CareHubTemplateWriter,
    UrgencyError,
    normalize_phone,
    normalize_urgency,
    validate,
)
from planning_center_carehub.models import VisitRequest


def person(**over):
    base = dict(
        source_pco_id="",
        name="Grace Kim",
        first_name="Grace",
        last_name="Kim",
        email="grace@example.org",
        phone="(555) 123-4567",
        street="123 Main St",
        city="Nashville",
        state="TN",
        zip_code="37201",
        request_type="Visit",
        priority="normal",
        description="Please follow up.",
    )
    base.update(over)
    return VisitRequest(**base)


# -- phone ---------------------------------------------------------------
@pytest.mark.parametrize(
    "raw,expected",
    [
        ("(559) 658-7751", "559-658-7751"),
        ("559-658-7751", "559-658-7751"),
        ("5596587751", "559-658-7751"),
        ("1 (559) 658-7751", "559-658-7751"),
        ("", ""),
    ],
)
def test_normalize_phone(raw, expected):
    assert normalize_phone(raw) == expected


def test_odd_phone_passes_through_rather_than_mangled():
    assert normalize_phone("ext 42") == "ext 42"


# -- urgency -------------------------------------------------------------
@pytest.mark.parametrize("raw", ["normal", "Normal", " URGENT ", "crisis"])
def test_valid_urgency_lowercased(raw):
    assert normalize_urgency(raw) in ("normal", "urgent", "crisis")


def test_blank_urgency_defaults_to_normal():
    assert normalize_urgency("") == "normal"


def test_rejected_urgency_names_the_valid_values():
    with pytest.raises(UrgencyError) as exc:
        normalize_urgency("High")
    assert "normal" in str(exc.value) and "crisis" in str(exc.value)


# -- writing -------------------------------------------------------------
def test_header_matches_carehub_template_exactly(tmp_path):
    writer = CareHubTemplateWriter(str(tmp_path))
    writer.write([person()])
    with open(writer.path, newline="", encoding="utf-8") as fh:
        header = next(csv.reader(fh))
    assert header == TEMPLATE_COLUMNS


def test_row_matches_the_sample_shape(tmp_path):
    writer = CareHubTemplateWriter(str(tmp_path))
    writer.write([person()])
    with open(writer.path, newline="", encoding="utf-8") as fh:
        row = next(csv.DictReader(fh))
    assert row["First Name"] == "Grace"
    assert row["Last Name"] == "Kim"
    assert row["Phone"] == "555-123-4567"
    assert row["Address"] == "123 Main St"
    assert row["City"] == "Nashville"
    assert row["ZIP"] == "37201"
    assert row["Urgency"] == "normal"


def test_address_falls_back_to_flat_when_unsplit(tmp_path):
    writer = CareHubTemplateWriter(str(tmp_path))
    writer.write([person(street="", address="1 Somewhere Ln, Oakhurst, CA")])
    with open(writer.path, newline="", encoding="utf-8") as fh:
        row = next(csv.DictReader(fh))
    assert row["Address"] == "1 Somewhere Ln, Oakhurst, CA"


# -- validation ----------------------------------------------------------
def test_missing_email_flagged_for_duplicate_risk():
    problems = validate([person(email="")])
    assert any("duplicate" in p.lower() or "second copy" in p for p in problems)


def test_missing_description_flagged():
    problems = validate([person(description="")])
    assert any("Description" in p for p in problems)


def test_shared_email_flagged():
    problems = validate([person(), person(name="Other Person")])
    assert any("same person" in p for p in problems)


def test_clean_record_has_no_problems():
    assert validate([person()]) == []
