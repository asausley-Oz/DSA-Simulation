"""Configuration loaded from environment variables (and an optional .env file)."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional


def _load_dotenv(path: str = ".env") -> None:
    """Minimal .env loader (no dependency). Ignores if the file is absent."""
    if not os.path.exists(path):
        return
    with open(path, "r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, val = line.partition("=")
            key = key.strip()
            val = val.strip().strip('"').strip("'")
            # Do not clobber values already set in the real environment.
            os.environ.setdefault(key, val)


@dataclass
class Config:
    pco_app_id: str
    pco_secret: str
    source: str  # "list" | "all" | "names"
    list_id: Optional[str]
    status_filter: Optional[str]
    names_file: Optional[str]
    names: Optional[list]
    output_dir: str
    state_path: str
    request_type: str
    priority: str
    # Opt-in direct submission.
    carehub_submit_url: Optional[str]
    carehub_auth_header: Optional[str]

    @classmethod
    def from_env(cls, dotenv_path: str = ".env") -> "Config":
        _load_dotenv(dotenv_path)
        return cls(
            pco_app_id=os.environ.get("PCO_APP_ID", ""),
            pco_secret=os.environ.get("PCO_SECRET", ""),
            source=os.environ.get("PCO_SOURCE", "list").lower(),
            list_id=os.environ.get("PCO_LIST_ID") or None,
            status_filter=os.environ.get("PCO_STATUS_FILTER") or None,
            names_file=os.environ.get("PCO_NAMES_FILE") or None,
            names=None,
            output_dir=os.environ.get("OUTPUT_DIR", "output"),
            state_path=os.environ.get(
                "STATE_PATH", os.path.join("output", "sync_state.json")
            ),
            request_type=os.environ.get("VISIT_REQUEST_TYPE", "Visit"),
            priority=os.environ.get("VISIT_PRIORITY", "Normal"),
            carehub_submit_url=os.environ.get("CAREHUB_SUBMIT_URL") or None,
            carehub_auth_header=os.environ.get("CAREHUB_AUTH_HEADER") or None,
        )
