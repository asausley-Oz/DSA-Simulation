"""Planning Center People API client.

Authentication uses a Personal Access Token (a PAT is an Application ID +
Secret pair used as HTTP Basic auth). Create one at
https://api.planningcenteronline.com/oauth/applications under "Personal Access
Tokens". The token only needs read access to the People product.
"""

from __future__ import annotations

import time
from typing import Dict, Iterator, List, Optional, Tuple

import requests

from .models import Person

BASE_URL = "https://api.planningcenteronline.com/people/v2"

# Contact info lives in related resources; ask the API to include them so we
# don't have to make a request per person.
_INCLUDES = "emails,phone_numbers,addresses"


class PlanningCenterError(RuntimeError):
    pass


class PlanningCenterClient:
    def __init__(
        self,
        app_id: str,
        secret: str,
        *,
        base_url: str = BASE_URL,
        session: Optional[requests.Session] = None,
        timeout: int = 30,
        max_retries: int = 4,
    ) -> None:
        if not app_id or not secret:
            raise PlanningCenterError(
                "Planning Center credentials missing. Set PCO_APP_ID and "
                "PCO_SECRET (Personal Access Token application id + secret)."
            )
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries
        self.session = session or requests.Session()
        self.session.auth = (app_id, secret)
        self.session.headers.update({"Accept": "application/json"})

    # -- low level ---------------------------------------------------------
    def _get(self, url: str, params: Optional[dict] = None) -> dict:
        """GET with basic retry/backoff and rate-limit handling."""
        attempt = 0
        while True:
            attempt += 1
            resp = self.session.get(url, params=params, timeout=self.timeout)
            if resp.status_code == 429:
                # Planning Center returns Retry-After on rate limit.
                wait = int(resp.headers.get("Retry-After", "2"))
                time.sleep(wait)
                continue
            if resp.status_code == 401:
                raise PlanningCenterError(
                    "Planning Center rejected the credentials (401). Check the "
                    "Personal Access Token application id and secret."
                )
            if resp.status_code >= 500 and attempt <= self.max_retries:
                time.sleep(min(2 ** attempt, 16))
                continue
            if resp.status_code >= 400:
                raise PlanningCenterError(
                    f"Planning Center API error {resp.status_code}: {resp.text[:300]}"
                )
            return resp.json()

    def _paginate(self, url: str, params: Optional[dict] = None) -> Iterator[dict]:
        """Yield each JSON:API page, following ``links.next`` to the end."""
        page = self._get(url, params=params)
        yield page
        while True:
            next_url = (page.get("links") or {}).get("next")
            if not next_url:
                break
            # ``links.next`` is a fully-formed URL with its own query string.
            page = self._get(next_url)
            yield page

    # -- parsing -----------------------------------------------------------
    @staticmethod
    def _index_included(included: List[dict]) -> Dict[Tuple[str, str], dict]:
        return {(item["type"], item["id"]): item for item in (included or [])}

    @staticmethod
    def _pick_primary(items: List[dict], value_key: str) -> str:
        """Return the primary related item's value, else the first, else ""."""
        if not items:
            return ""
        primary = next(
            (i for i in items if (i.get("attributes") or {}).get("primary")), None
        )
        chosen = primary or items[0]
        return str((chosen.get("attributes") or {}).get(value_key) or "")

    def _person_from_resource(
        self, resource: dict, index: Dict[Tuple[str, str], dict]
    ) -> Person:
        attrs = resource.get("attributes") or {}
        rels = resource.get("relationships") or {}

        def related(rel_name: str) -> List[dict]:
            data = (rels.get(rel_name) or {}).get("data") or []
            out = []
            for ref in data:
                item = index.get((ref.get("type"), ref.get("id")))
                if item:
                    out.append(item)
            return out

        emails = related("emails")
        phones = related("phone_numbers")
        addresses = related("addresses")

        addr = {}
        if addresses:
            addr_primary = next(
                (a for a in addresses if (a.get("attributes") or {}).get("primary")),
                addresses[0],
            )
            addr = addr_primary.get("attributes") or {}

        return Person(
            pco_id=str(resource.get("id")),
            first_name=str(attrs.get("first_name") or ""),
            last_name=str(attrs.get("last_name") or ""),
            full_name=str(attrs.get("name") or ""),
            email=self._pick_primary(emails, "address"),
            phone=self._pick_primary(phones, "number"),
            street=str(addr.get("street") or ""),
            city=str(addr.get("city") or ""),
            state=str(addr.get("state") or ""),
            zip_code=str(addr.get("zip") or ""),
            status=str(attrs.get("status") or ""),
        )

    def _people_from_pages(self, pages: Iterator[dict]) -> Iterator[Person]:
        for page in pages:
            index = self._index_included(page.get("included") or [])
            for resource in page.get("data") or []:
                # ``/lists/{id}/people`` returns Person resources directly.
                if resource.get("type") == "Person":
                    yield self._person_from_resource(resource, index)

    # -- public sources ----------------------------------------------------
    def iter_all_people(
        self, *, per_page: int = 100, where: Optional[dict] = None
    ) -> Iterator[Person]:
        """All people in the account (optionally filtered).

        ``where`` maps to Planning Center ``where[...]`` filters, e.g.
        ``{"status": "active"}``.
        """
        params = {"per_page": per_page, "include": _INCLUDES}
        for key, val in (where or {}).items():
            params[f"where[{key}]"] = val
        yield from self._people_from_pages(
            self._paginate(f"{self.base_url}/people", params=params)
        )

    def iter_list_people(self, list_id: str, *, per_page: int = 100) -> Iterator[Person]:
        """People belonging to a Planning Center List (the common case)."""
        params = {"per_page": per_page, "include": _INCLUDES}
        yield from self._people_from_pages(
            self._paginate(f"{self.base_url}/lists/{list_id}/people", params=params)
        )

    def find_people_by_name(self, name: str, *, per_page: int = 25) -> List[Person]:
        """Search people by name. Returns every match so callers can disambiguate.

        Planning Center's ``where[search_name]`` filter matches against first,
        last, and nickname, so a partial name like "Jane D" works.
        """
        params = {
            "per_page": per_page,
            "include": _INCLUDES,
            "where[search_name]": name,
        }
        return list(
            self._people_from_pages(
                self._paginate(f"{self.base_url}/people", params=params)
            )
        )

    def resolve_names(
        self, names: Iterable[str]
    ) -> Tuple[List[Person], List[str], Dict[str, List[Person]]]:
        """Resolve a list of names to people.

        Returns ``(matched, not_found, ambiguous)`` where ``ambiguous`` maps a
        queried name to its several candidates. Only unambiguous single matches
        land in ``matched`` — we never guess which person you meant.
        """
        matched: List[Person] = []
        not_found: List[str] = []
        ambiguous: Dict[str, List[Person]] = {}
        for raw in names:
            name = raw.strip()
            if not name:
                continue
            results = self.find_people_by_name(name)
            if not results:
                not_found.append(name)
            elif len(results) == 1:
                matched.append(results[0])
            else:
                # An exact full-name match wins over partial ones.
                exact = [
                    p for p in results if p.name.strip().lower() == name.lower()
                ]
                if len(exact) == 1:
                    matched.append(exact[0])
                else:
                    ambiguous[name] = results
        return matched, not_found, ambiguous

    def get_lists(self) -> List[dict]:
        """Return available Lists as ``[{"id", "name"}]`` to help discovery."""
        out = []
        for page in self._paginate(f"{self.base_url}/lists", params={"per_page": 100}):
            for res in page.get("data") or []:
                out.append(
                    {
                        "id": str(res.get("id")),
                        "name": str((res.get("attributes") or {}).get("name") or ""),
                    }
                )
        return out
