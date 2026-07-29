"""Idempotency tracking so repeated runs don't create duplicate requests.

State is a small JSON file mapping ``source_pco_id`` -> content fingerprint.
A person is considered "new" if their id isn't in the state, and "changed" if
their fingerprint differs from the stored one.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Dict, List, Tuple

from .models import VisitRequest, fingerprint


@dataclass
class SyncPlan:
    new: List[VisitRequest]
    changed: List[VisitRequest]
    unchanged: List[VisitRequest]

    @property
    def to_submit(self) -> List[VisitRequest]:
        return self.new + self.changed


class StateStore:
    def __init__(self, path: str) -> None:
        self.path = path
        self._data: Dict[str, str] = {}
        self._load()

    def _load(self) -> None:
        if os.path.exists(self.path):
            with open(self.path, "r", encoding="utf-8") as fh:
                try:
                    self._data = json.load(fh)
                except json.JSONDecodeError:
                    self._data = {}

    def plan(self, visit_requests: List[VisitRequest]) -> SyncPlan:
        new, changed, unchanged = [], [], []
        for vr in visit_requests:
            fp = fingerprint(vr)
            prior = self._data.get(vr.source_pco_id)
            if prior is None:
                new.append(vr)
            elif prior != fp:
                changed.append(vr)
            else:
                unchanged.append(vr)
        return SyncPlan(new=new, changed=changed, unchanged=unchanged)

    def mark_submitted(self, visit_requests: List[VisitRequest]) -> None:
        for vr in visit_requests:
            self._data[vr.source_pco_id] = fingerprint(vr)

    def save(self) -> None:
        directory = os.path.dirname(os.path.abspath(self.path))
        os.makedirs(directory, exist_ok=True)
        tmp = f"{self.path}.tmp"
        with open(tmp, "w", encoding="utf-8") as fh:
            json.dump(self._data, fh, indent=2, sort_keys=True)
        os.replace(tmp, self.path)
