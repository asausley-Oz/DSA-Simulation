import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from planning_center_carehub import cli
from planning_center_carehub.models import Person


class StubPCO:
    """Stands in for PlanningCenterClient so the CLI runs without network."""

    def __init__(self, *a, **kw):
        pass

    def resolve_names(self, names):
        people = [
            Person(pco_id=str(i), first_name=n.split()[0], last_name=n.split()[-1],
                   phone=f"555-000{i}")
            for i, n in enumerate(names, 1)
        ]
        return people, [], {}


def test_sync_by_name_writes_files_then_is_idempotent(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(cli, "_client", lambda cfg: StubPCO())
    monkeypatch.setenv("PCO_APP_ID", "x")
    monkeypatch.setenv("PCO_SECRET", "y")
    monkeypatch.setenv("OUTPUT_DIR", str(tmp_path / "out"))
    monkeypatch.setenv("STATE_PATH", str(tmp_path / "out" / "state.json"))

    argv = [
        "sync",
        "--env", str(tmp_path / "nonexistent.env"),
        "--name", "Jane Doe",
        "--name", "John Roe",
    ]
    # --env is a top-level flag, so put it before the subcommand.
    argv = ["--env", str(tmp_path / "nonexistent.env"), "sync",
            "--name", "Jane Doe", "--name", "John Roe"]

    assert cli.main(argv) == 0
    out = capsys.readouterr().out
    assert "Fetched 2 person(s)" in out
    assert "2 new" in out

    csv_path = tmp_path / "out" / "carehub_visit_requests.csv"
    assert csv_path.exists()
    content = csv_path.read_text()
    assert "Jane Doe" in content and "John Roe" in content

    # Second identical run must not re-emit anyone.
    assert cli.main(argv) == 0
    out2 = capsys.readouterr().out
    assert "0 new" in out2
    assert "Nothing new to submit" in out2


def test_dry_run_writes_nothing(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(cli, "_client", lambda cfg: StubPCO())
    monkeypatch.setenv("PCO_APP_ID", "x")
    monkeypatch.setenv("PCO_SECRET", "y")
    out_dir = tmp_path / "out"
    monkeypatch.setenv("OUTPUT_DIR", str(out_dir))
    monkeypatch.setenv("STATE_PATH", str(out_dir / "state.json"))

    argv = ["--env", str(tmp_path / "none.env"), "sync", "--name", "Jane Doe", "--dry-run"]
    assert cli.main(argv) == 0
    out = capsys.readouterr().out
    assert "would create: Jane Doe" in out
    assert not (out_dir / "carehub_visit_requests.csv").exists()
