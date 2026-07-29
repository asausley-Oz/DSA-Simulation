import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from planning_center_carehub.planning_center import PlanningCenterClient


# A realistic JSON:API page from /people/v2/people?include=emails,phone_numbers,addresses
PAGE = {
    "data": [
        {
            "type": "Person",
            "id": "101",
            "attributes": {
                "first_name": "Jane",
                "last_name": "Doe",
                "name": "Jane Doe",
                "status": "active",
            },
            "relationships": {
                "emails": {"data": [{"type": "Email", "id": "e1"}]},
                "phone_numbers": {"data": [{"type": "PhoneNumber", "id": "p1"}]},
                "addresses": {"data": [{"type": "Address", "id": "a1"}]},
            },
        }
    ],
    "included": [
        {"type": "Email", "id": "e1", "attributes": {"address": "jane@example.com", "primary": True}},
        {"type": "PhoneNumber", "id": "p1", "attributes": {"number": "555-1212", "primary": True}},
        {
            "type": "Address",
            "id": "a1",
            "attributes": {
                "street": "1 Main St",
                "city": "Springfield",
                "state": "IL",
                "zip": "62704",
                "primary": True,
            },
        },
    ],
    "links": {},
}


def _client():
    # Credentials are only validated for truthiness at construction time.
    return PlanningCenterClient("app", "secret")


def test_parse_person_with_includes():
    client = _client()
    people = list(client._people_from_pages(iter([PAGE])))
    assert len(people) == 1
    person = people[0]
    assert person.pco_id == "101"
    assert person.name == "Jane Doe"
    assert person.email == "jane@example.com"
    assert person.phone == "555-1212"
    assert person.address == "1 Main St, Springfield, IL, 62704"
    assert person.status == "active"


def test_primary_selection_prefers_primary_email():
    page = {
        "data": [
            {
                "type": "Person",
                "id": "2",
                "attributes": {"name": "Multi Email"},
                "relationships": {
                    "emails": {
                        "data": [
                            {"type": "Email", "id": "x1"},
                            {"type": "Email", "id": "x2"},
                        ]
                    }
                },
            }
        ],
        "included": [
            {"type": "Email", "id": "x1", "attributes": {"address": "secondary@x.com", "primary": False}},
            {"type": "Email", "id": "x2", "attributes": {"address": "primary@x.com", "primary": True}},
        ],
        "links": {},
    }
    client = _client()
    person = list(client._people_from_pages(iter([page])))[0]
    assert person.email == "primary@x.com"


def test_missing_contact_info_is_blank_not_error():
    page = {
        "data": [
            {"type": "Person", "id": "3", "attributes": {"name": "No Contact"}, "relationships": {}}
        ],
        "included": [],
        "links": {},
    }
    client = _client()
    person = list(client._people_from_pages(iter([page])))[0]
    assert person.email == ""
    assert person.phone == ""
    assert person.address == ""
