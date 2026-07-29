"""Core data models shared across the sync."""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Optional


@dataclass
class Person:
    """A person as pulled from Planning Center People.

    Only the fields useful for creating a care/visit request are kept. The
    ``pco_id`` is the stable Planning Center id and is what we use to avoid
    creating duplicate visit requests on repeated runs.
    """

    pco_id: str
    first_name: str = ""
    last_name: str = ""
    full_name: str = ""
    email: str = ""
    phone: str = ""
    street: str = ""
    city: str = ""
    state: str = ""
    zip_code: str = ""
    status: str = ""

    @property
    def name(self) -> str:
        if self.full_name:
            return self.full_name
        joined = f"{self.first_name} {self.last_name}".strip()
        return joined or f"PCO {self.pco_id}"

    @property
    def address(self) -> str:
        parts = [self.street, self.city, self.state, self.zip_code]
        return ", ".join(p for p in parts if p)

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class VisitRequest:
    """A CareHub visit request derived from a Person.

    This is a deliberately generic shape. CareHub does not publish an API, so
    these are the fields a person would fill in when creating a visit request
    by hand. Adjust :func:`planning_center_carehub.transform.to_visit_request`
    if your CareHub form uses different labels.
    """

    source_pco_id: str
    name: str
    email: str = ""
    phone: str = ""
    address: str = ""
    request_type: str = "Visit"
    priority: str = "Normal"
    notes: str = ""
    # Free-form fields the caller can add without changing the model.
    extra: dict = field(default_factory=dict)

    def to_row(self) -> dict:
        """Flat dict suitable for a CSV row."""
        row = {
            "source_pco_id": self.source_pco_id,
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "address": self.address,
            "request_type": self.request_type,
            "priority": self.priority,
            "notes": self.notes,
        }
        row.update(self.extra)
        return row


def fingerprint(vr: VisitRequest) -> str:
    """A content hash used to detect when a person's details have changed.

    Kept small and stable so re-running the sync only re-emits people whose
    relevant contact info actually changed.
    """
    import hashlib

    basis = "|".join(
        [
            vr.name,
            vr.email,
            vr.phone,
            vr.address,
            vr.request_type,
            vr.priority,
            vr.notes,
        ]
    )
    return hashlib.sha256(basis.encode("utf-8")).hexdigest()[:16]
