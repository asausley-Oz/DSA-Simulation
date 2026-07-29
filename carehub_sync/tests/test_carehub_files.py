import csv
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from planning_center_carehub.carehub import FileCareHubClient
from planning_center_carehub.models import VisitRequest


def test_file_client_writes_csv_and_worksheet(tmp_path):
    sink = FileCareHubClient(str(tmp_path))
    reqs = [
        VisitRequest(source_pco_id="1", name="Jane Doe", phone="555", notes="hi"),
        VisitRequest(source_pco_id="2", name="John Roe", email="j@x.com"),
    ]
    result = sink.submit(reqs)
    assert len(result.submitted) == 2

    assert os.path.exists(sink.csv_path)
    with open(sink.csv_path, newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    assert len(rows) == 2
    assert rows[0]["name"] == "Jane Doe"
    assert rows[0]["source_pco_id"] == "1"

    with open(sink.worksheet_path, encoding="utf-8") as fh:
        text = fh.read()
    assert "Jane Doe" in text
    assert "John Roe" in text
    assert "[ ]" in text  # checkbox present
