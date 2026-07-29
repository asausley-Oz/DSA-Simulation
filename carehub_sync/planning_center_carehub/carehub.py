"""CareHub sinks: where visit requests go.

CareHub (volunteeru.org) does not publish a public API, so this module offers
two paths:

1. ``FileCareHubClient`` (default, recommended for regular CareHub users):
   writes an import-ready CSV plus a printable Markdown worksheet. You then
   create the visit requests through CareHub's own interface while logged in as
   yourself. Nothing is sent anywhere on your behalf.

2. ``HttpCareHubClient`` (opt-in, advanced): a deliberately incomplete adapter
   for the case where you have a legitimate, authorized way to post visit
   requests to your own CareHub account (for example, an official import
   endpoint, or a request you captured from your own logged-in browser
   session). You must supply the endpoint, payload mapping, and your own auth.
   Do not use this to automate against a service you are not authorized to
   script.
"""

from __future__ import annotations

import csv
import os
from typing import List, Protocol

from .models import VisitRequest


class CareHubSink(Protocol):
    def submit(self, visit_requests: List[VisitRequest]) -> "SubmitResult":
        ...


class SubmitResult:
    def __init__(self, submitted: List[VisitRequest], detail: str = "") -> None:
        self.submitted = submitted
        self.detail = detail


# ---------------------------------------------------------------------------
# Default: produce files for manual entry.
# ---------------------------------------------------------------------------
class FileCareHubClient:
    """Write visit requests to a CSV and a human-friendly worksheet."""

    def __init__(self, output_dir: str) -> None:
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    @property
    def csv_path(self) -> str:
        return os.path.join(self.output_dir, "carehub_visit_requests.csv")

    @property
    def worksheet_path(self) -> str:
        return os.path.join(self.output_dir, "carehub_visit_requests.md")

    def submit(self, visit_requests: List[VisitRequest]) -> SubmitResult:
        self._write_csv(visit_requests)
        self._write_worksheet(visit_requests)
        detail = (
            f"Wrote {len(visit_requests)} visit request(s) to:\n"
            f"  - {self.csv_path}\n"
            f"  - {self.worksheet_path}"
        )
        return SubmitResult(submitted=list(visit_requests), detail=detail)

    def _write_csv(self, visit_requests: List[VisitRequest]) -> None:
        fieldnames = [
            "source_pco_id",
            "name",
            "email",
            "phone",
            "address",
            "request_type",
            "priority",
            "notes",
        ]
        with open(self.csv_path, "w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=fieldnames)
            writer.writeheader()
            for vr in visit_requests:
                row = {k: vr.to_row().get(k, "") for k in fieldnames}
                writer.writerow(row)

    def _write_worksheet(self, visit_requests: List[VisitRequest]) -> None:
        lines = [
            "# CareHub Visit Requests",
            "",
            "Create each of these in CareHub while logged in. Check the box as "
            "you go.",
            "",
        ]
        for i, vr in enumerate(visit_requests, 1):
            lines.append(f"## {i}. [ ] {vr.name}")
            lines.append("")
            lines.append(f"- **Type:** {vr.request_type}")
            lines.append(f"- **Priority:** {vr.priority}")
            if vr.phone:
                lines.append(f"- **Phone:** {vr.phone}")
            if vr.email:
                lines.append(f"- **Email:** {vr.email}")
            if vr.address:
                lines.append(f"- **Address:** {vr.address}")
            if vr.notes:
                lines.append(f"- **Notes:** {vr.notes}")
            lines.append("")
        with open(self.worksheet_path, "w", encoding="utf-8") as fh:
            fh.write("\n".join(lines))


# ---------------------------------------------------------------------------
# Opt-in: direct HTTP submission (you complete this with your own authorized
# endpoint / session). Disabled unless a submit URL is provided.
# ---------------------------------------------------------------------------
class HttpCareHubClient:
    """Post visit requests to a CareHub endpoint you are authorized to use.

    This class ships intentionally unwired. To use it you must provide the
    ``submit_url`` and (optionally) headers such as an authorization token from
    your own logged-in session. See ``build_payload`` for the field mapping to
    adjust once you know the exact request shape CareHub expects.
    """

    def __init__(
        self,
        submit_url: str,
        *,
        headers: dict | None = None,
        timeout: int = 30,
        session=None,
    ) -> None:
        if not submit_url:
            raise ValueError(
                "HttpCareHubClient requires a submit_url you are authorized to "
                "call. Capture it from your own logged-in CareHub session or use "
                "an official import endpoint."
            )
        import requests  # local import so the file sink has no hard dependency

        self.submit_url = submit_url
        self.headers = headers or {}
        self.timeout = timeout
        self.session = session or requests.Session()

    @staticmethod
    def build_payload(vr: VisitRequest) -> dict:
        """Map a VisitRequest to CareHub's expected JSON body.

        Adjust the keys here to match the payload you observe in your browser's
        network tab when you create a visit request by hand.
        """
        return {
            "name": vr.name,
            "email": vr.email,
            "phone": vr.phone,
            "address": vr.address,
            "type": vr.request_type,
            "priority": vr.priority,
            "notes": vr.notes,
            "external_ref": f"pco:{vr.source_pco_id}",
        }

    def submit(self, visit_requests: List[VisitRequest]) -> SubmitResult:
        submitted: List[VisitRequest] = []
        for vr in visit_requests:
            resp = self.session.post(
                self.submit_url,
                json=self.build_payload(vr),
                headers=self.headers,
                timeout=self.timeout,
            )
            resp.raise_for_status()
            submitted.append(vr)
        return SubmitResult(
            submitted=submitted,
            detail=f"POSTed {len(submitted)} visit request(s) to {self.submit_url}",
        )
