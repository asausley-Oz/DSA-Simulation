import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from planning_center_carehub.models import Person, VisitRequest, fingerprint
from planning_center_carehub.transform import to_visit_request, to_visit_requests


def sample_person(**over):
    base = dict(
        pco_id="42",
        first_name="Jane",
        last_name="Doe",
        email="jane@example.com",
        phone="555-1212",
        street="1 Main St",
        city="Springfield",
        state="IL",
        zip_code="62704",
        status="active",
    )
    base.update(over)
    return Person(**base)


def test_person_name_and_address():
    p = sample_person()
    assert p.name == "Jane Doe"
    assert p.address == "1 Main St, Springfield, IL, 62704"


def test_name_falls_back_to_full_name_then_id():
    assert sample_person(first_name="", last_name="", full_name="J. Doe").name == "J. Doe"
    assert sample_person(first_name="", last_name="", full_name="").name == "PCO 42"


def test_to_visit_request_maps_fields():
    vr = to_visit_request(sample_person(), request_type="Home Visit", priority="High")
    assert vr.source_pco_id == "42"
    assert vr.name == "Jane Doe"
    assert vr.email == "jane@example.com"
    assert vr.phone == "555-1212"
    assert vr.address == "1 Main St, Springfield, IL, 62704"
    assert vr.request_type == "Home Visit"
    assert vr.priority == "High"
    assert "42" in vr.notes


def test_to_visit_requests_batch():
    people = [sample_person(pco_id="1"), sample_person(pco_id="2")]
    out = to_visit_requests(people)
    assert [vr.source_pco_id for vr in out] == ["1", "2"]


def test_fingerprint_changes_with_content():
    a = to_visit_request(sample_person())
    b = to_visit_request(sample_person(phone="999-0000"))
    assert fingerprint(a) != fingerprint(b)
    assert fingerprint(a) == fingerprint(to_visit_request(sample_person()))
