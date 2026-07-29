import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from planning_center_carehub.planning_center import PlanningCenterClient


def _person_page(people):
    """Build a JSON:API page from (id, name) tuples."""
    return {
        "data": [
            {
                "type": "Person",
                "id": pid,
                "attributes": {"name": name},
                "relationships": {},
            }
            for pid, name in people
        ],
        "included": [],
        "links": {},
    }


class FakeClient(PlanningCenterClient):
    """Client whose search results come from a canned mapping."""

    def __init__(self, results):
        super().__init__("app", "secret")
        self._results = results
        self.queries = []

    def find_people_by_name(self, name, *, per_page=25):
        self.queries.append(name)
        page = _person_page(self._results.get(name, []))
        return list(self._people_from_pages(iter([page])))


def test_resolves_unique_names():
    client = FakeClient({"Jane Doe": [("1", "Jane Doe")], "John Roe": [("2", "John Roe")]})
    matched, not_found, ambiguous = client.resolve_names(["Jane Doe", "John Roe"])
    assert [p.pco_id for p in matched] == ["1", "2"]
    assert not not_found and not ambiguous


def test_reports_missing_names():
    client = FakeClient({})
    matched, not_found, ambiguous = client.resolve_names(["Nobody Here"])
    assert not matched
    assert not_found == ["Nobody Here"]


def test_multiple_matches_are_ambiguous_not_guessed():
    client = FakeClient({"Smith": [("1", "Al Smith"), ("2", "Bo Smith")]})
    matched, not_found, ambiguous = client.resolve_names(["Smith"])
    assert not matched
    assert "Smith" in ambiguous
    assert len(ambiguous["Smith"]) == 2


def test_exact_full_name_wins_over_partial_matches():
    client = FakeClient(
        {"Jane Doe": [("1", "Jane Doe"), ("2", "Jane Doeman")]}
    )
    matched, not_found, ambiguous = client.resolve_names(["Jane Doe"])
    assert [p.pco_id for p in matched] == ["1"]
    assert not ambiguous


def test_blank_names_skipped():
    client = FakeClient({"Jane Doe": [("1", "Jane Doe")]})
    matched, _, _ = client.resolve_names(["  ", "Jane Doe", ""])
    assert len(matched) == 1
    assert client.queries == ["Jane Doe"]
