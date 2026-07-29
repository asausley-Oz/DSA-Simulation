import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from planning_center_carehub.models import VisitRequest
from planning_center_carehub.state import StateStore


def vr(pco_id, phone="555"):
    return VisitRequest(source_pco_id=pco_id, name=f"P{pco_id}", phone=phone)


def test_all_new_first_run(tmp_path):
    store = StateStore(str(tmp_path / "state.json"))
    plan = store.plan([vr("1"), vr("2")])
    assert len(plan.new) == 2
    assert not plan.changed and not plan.unchanged
    assert len(plan.to_submit) == 2


def test_unchanged_after_submit(tmp_path):
    path = str(tmp_path / "state.json")
    store = StateStore(path)
    reqs = [vr("1"), vr("2")]
    store.mark_submitted(store.plan(reqs).to_submit)
    store.save()

    store2 = StateStore(path)
    plan = store2.plan(reqs)
    assert len(plan.unchanged) == 2
    assert not plan.to_submit


def test_changed_detected(tmp_path):
    path = str(tmp_path / "state.json")
    store = StateStore(path)
    store.mark_submitted(store.plan([vr("1", phone="555")]).to_submit)
    store.save()

    store2 = StateStore(path)
    plan = store2.plan([vr("1", phone="999")])
    assert len(plan.changed) == 1
    assert len(plan.to_submit) == 1
