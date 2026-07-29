"""Turn Planning Center people into CareHub visit requests.

This is the one place to edit if your CareHub visit-request form uses different
fields, default priorities, or note wording.
"""

from __future__ import annotations

from typing import Iterable, List

from .models import Person, VisitRequest

DEFAULT_NOTE_TEMPLATE = (
    "Visit request created from Planning Center (person id {pco_id})."
)


def to_visit_request(
    person: Person,
    *,
    request_type: str = "Visit",
    priority: str = "Normal",
    note_template: str = DEFAULT_NOTE_TEMPLATE,
) -> VisitRequest:
    notes = note_template.format(
        pco_id=person.pco_id,
        name=person.name,
        status=person.status,
    )
    return VisitRequest(
        source_pco_id=person.pco_id,
        name=person.name,
        email=person.email,
        phone=person.phone,
        address=person.address,
        request_type=request_type,
        priority=priority,
        notes=notes,
    )


def to_visit_requests(
    people: Iterable[Person], **kwargs
) -> List[VisitRequest]:
    return [to_visit_request(p, **kwargs) for p in people]
