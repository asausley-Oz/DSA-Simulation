"""Writer for CareHub's official CSV import template.

Column names and accepted values come from CareHub's own downloadable template
and the import instructions on the Data & Export screen:

    Required:  First Name + Last Name, or Full Name
    Optional:  Email, Phone, Address, City, State, ZIP, Campus, Birthday
    For care requests also: Care Type, Description, Urgency

``Urgency`` is a closed vocabulary — ``normal``, ``urgent`` or ``crisis``,
lowercase. Anything else is rejected here rather than by the importer.
"""

from __future__ import annotations

import csv
import os
import re
from typing import List

from .models import VisitRequest

# Exact header row from CareHub's downloaded template, in order.
TEMPLATE_COLUMNS = [
    "First Name",
    "Last Name",
    "Full Name",
    "Email",
    "Phone",
    "Address",
    "City",
    "State",
    "ZIP",
    "Campus",
    "Birthday",
    "Notes",
    "Care Request Type",
    "Care Request Description",
    "Urgency",
]

VALID_URGENCY = ("normal", "urgent", "crisis")


class UrgencyError(ValueError):
    pass


def normalize_phone(raw: str) -> str:
    """Render a phone as 555-123-4567, matching the template's sample row.

    Anything that isn't a plain 10-digit US number is passed through unchanged
    rather than mangled.
    """
    if not raw:
        return ""
    digits = re.sub(r"\D", "", raw)
    if len(digits) == 11 and digits.startswith("1"):
        digits = digits[1:]
    if len(digits) != 10:
        return raw.strip()
    return f"{digits[0:3]}-{digits[3:6]}-{digits[6:10]}"


def normalize_urgency(raw: str) -> str:
    """Map a priority onto CareHub's normal/urgent/crisis vocabulary."""
    value = (raw or "").strip().lower()
    if not value:
        return "normal"
    if value in VALID_URGENCY:
        return value
    raise UrgencyError(
        f"Urgency {raw!r} is not accepted by CareHub. Use one of: "
        + ", ".join(VALID_URGENCY)
    )


def _row(vr: VisitRequest) -> dict:
    first = vr.first_name
    last = vr.last_name
    full = vr.name
    if not (first or last) and full:
        # The importer needs First+Last or Full Name; Full Name alone is fine.
        pass
    return {
        "First Name": first,
        "Last Name": last,
        "Full Name": full,
        "Email": vr.email,
        "Phone": normalize_phone(vr.phone),
        "Address": vr.street or vr.address,
        "City": vr.city,
        "State": vr.state,
        "ZIP": vr.zip_code,
        "Campus": vr.campus,
        "Birthday": vr.birthday,
        "Notes": vr.notes,
        "Care Request Type": vr.request_type,
        "Care Request Description": vr.description,
        "Urgency": normalize_urgency(vr.priority),
    }


def validate(visit_requests: List[VisitRequest]) -> List[str]:
    """Return human-readable problems that would break or degrade the import."""
    problems: List[str] = []
    seen_emails = {}
    for i, vr in enumerate(visit_requests, start=2):  # row 1 is the header
        label = vr.name or f"row {i}"
        if not (vr.first_name and vr.last_name) and not vr.name:
            problems.append(f"{label}: needs First+Last Name or Full Name.")
        if not vr.description:
            problems.append(
                f"{label}: no Care Request Description — the request will "
                "carry no reason."
            )
        if not vr.email:
            problems.append(
                f"{label}: no Email. CareHub uses Email to detect duplicates, "
                "so re-importing this file would create a second copy."
            )
        elif vr.email in seen_emails:
            problems.append(
                f"{label}: shares an email with {seen_emails[vr.email]} — "
                "CareHub would treat them as the same person."
            )
        else:
            seen_emails[vr.email] = label
    return problems


class CareHubTemplateWriter:
    """Write visit requests in CareHub's import template format."""

    def __init__(self, output_dir: str, filename: str = "carehub_import.csv") -> None:
        self.output_dir = output_dir
        self.filename = filename
        os.makedirs(self.output_dir, exist_ok=True)

    @property
    def path(self) -> str:
        return os.path.join(self.output_dir, self.filename)

    def write(self, visit_requests: List[VisitRequest]) -> str:
        with open(self.path, "w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=TEMPLATE_COLUMNS)
            writer.writeheader()
            for vr in visit_requests:
                writer.writerow(_row(vr))
        return self.path
