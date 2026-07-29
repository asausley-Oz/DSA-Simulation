"""Command-line entry point.

Examples
--------
List your Planning Center Lists (to find a list id)::

    python -m planning_center_carehub.cli lists

Preview what would be created, without writing anything::

    python -m planning_center_carehub.cli sync --source list --list-id 123456 --dry-run

Generate the import CSV + worksheet for a list::

    python -m planning_center_carehub.cli sync --source list --list-id 123456
"""

from __future__ import annotations

import argparse
import sys
from typing import List

from .config import Config
from .carehub import FileCareHubClient, HttpCareHubClient
from .models import VisitRequest
from .planning_center import PlanningCenterClient, PlanningCenterError
from .state import StateStore
from .transform import to_visit_requests


def _client(cfg: Config) -> PlanningCenterClient:
    return PlanningCenterClient(cfg.pco_app_id, cfg.pco_secret)


def _read_names(cfg: Config) -> List[str]:
    """Names come from --name flags, a --names-file, or PCO_NAMES_FILE."""
    if cfg.names:
        return list(cfg.names)
    if cfg.names_file:
        with open(cfg.names_file, "r", encoding="utf-8") as fh:
            return [line.strip() for line in fh if line.strip() and not line.startswith("#")]
    return []


def _fetch_people(cfg: Config, pco: PlanningCenterClient):
    if cfg.source == "names":
        names = _read_names(cfg)
        if not names:
            raise SystemExit(
                "PCO_SOURCE=names requires names (--name 'Jane Doe' repeated, "
                "or --names-file people.txt)."
            )
        matched, not_found, ambiguous = pco.resolve_names(names)
        for name in not_found:
            print(f"  ! no Planning Center match for: {name}")
        for name, candidates in ambiguous.items():
            print(f"  ! '{name}' matched {len(candidates)} people — skipped:")
            for cand in candidates:
                contact = cand.email or cand.phone or "no contact"
                print(f"      id={cand.pco_id}  {cand.name}  ({contact})")
        if not_found or ambiguous:
            print(
                "  Resolve these by using a fuller name, or add them to a "
                "Planning Center List and use --source list."
            )
        return matched
    if cfg.source == "list":
        if not cfg.list_id:
            raise SystemExit(
                "PCO_SOURCE=list requires a list id (PCO_LIST_ID or --list-id). "
                "Run the 'lists' command to find one."
            )
        return list(pco.iter_list_people(cfg.list_id))
    if cfg.source == "all":
        where = {"status": cfg.status_filter} if cfg.status_filter else None
        return list(pco.iter_all_people(where=where))
    raise SystemExit(
        f"Unknown PCO_SOURCE '{cfg.source}' (use 'names', 'list', or 'all')."
    )


def cmd_lists(cfg: Config) -> int:
    pco = _client(cfg)
    lists = pco.get_lists()
    if not lists:
        print("No lists found in this Planning Center account.")
        return 0
    print(f"{'ID':<12} NAME")
    for item in lists:
        print(f"{item['id']:<12} {item['name']}")
    return 0


def cmd_sync(cfg: Config, dry_run: bool) -> int:
    pco = _client(cfg)
    people = _fetch_people(cfg, pco)
    print(f"Fetched {len(people)} person(s) from Planning Center.")

    visit_requests: List[VisitRequest] = to_visit_requests(
        people, request_type=cfg.request_type, priority=cfg.priority
    )

    state = StateStore(cfg.state_path)
    plan = state.plan(visit_requests)
    print(
        f"Plan: {len(plan.new)} new, {len(plan.changed)} changed, "
        f"{len(plan.unchanged)} unchanged."
    )

    if dry_run:
        for vr in plan.to_submit:
            print(f"  would create: {vr.name} ({vr.phone or vr.email or 'no contact'})")
        print("Dry run: nothing written.")
        return 0

    if not plan.to_submit:
        print("Nothing new to submit. Up to date.")
        return 0

    # Choose sink: direct HTTP only if explicitly configured, else files.
    if cfg.carehub_submit_url:
        headers = {}
        if cfg.carehub_auth_header:
            headers["Authorization"] = cfg.carehub_auth_header
        sink = HttpCareHubClient(cfg.carehub_submit_url, headers=headers)
        print(f"Submitting directly to {cfg.carehub_submit_url} ...")
    else:
        sink = FileCareHubClient(cfg.output_dir)

    result = sink.submit(plan.to_submit)
    print(result.detail)

    state.mark_submitted(result.submitted)
    state.save()
    print(f"State saved to {cfg.state_path}.")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="planning_center_carehub",
        description="Sync Planning Center people into CareHub visit requests.",
    )
    parser.add_argument(
        "--env", default=".env", help="Path to a .env file (default: .env)"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("lists", help="List your Planning Center Lists and their ids.")

    p_sync = sub.add_parser("sync", help="Create visit requests from PCO people.")
    p_sync.add_argument(
        "--source", choices=["names", "list", "all"], help="Override PCO_SOURCE"
    )
    p_sync.add_argument("--list-id", help="Override PCO_LIST_ID")
    p_sync.add_argument("--status", help="Override PCO_STATUS_FILTER (source=all)")
    p_sync.add_argument(
        "--name",
        action="append",
        dest="names",
        metavar="NAME",
        help="A person's name; repeat for several. Implies --source names.",
    )
    p_sync.add_argument(
        "--names-file",
        help="File with one name per line. Implies --source names.",
    )
    p_sync.add_argument(
        "--dry-run", action="store_true", help="Show the plan without writing."
    )
    return parser


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    cfg = Config.from_env(args.env)

    # CLI overrides win over env/.env.
    if getattr(args, "names", None):
        cfg.names = args.names
    if getattr(args, "names_file", None):
        cfg.names_file = args.names_file
    # Supplying names at all implies the names source, unless overridden.
    if (cfg.names or getattr(args, "names_file", None)) and not getattr(
        args, "source", None
    ):
        cfg.source = "names"
    if getattr(args, "source", None):
        cfg.source = args.source
    if getattr(args, "list_id", None):
        cfg.list_id = args.list_id
    if getattr(args, "status", None):
        cfg.status_filter = args.status

    try:
        if args.command == "lists":
            return cmd_lists(cfg)
        if args.command == "sync":
            return cmd_sync(cfg, dry_run=getattr(args, "dry_run", False))
    except PlanningCenterError as exc:
        print(f"Planning Center error: {exc}", file=sys.stderr)
        return 2
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
