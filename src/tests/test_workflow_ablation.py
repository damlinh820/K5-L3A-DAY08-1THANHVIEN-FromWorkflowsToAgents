"""Paired R4 experiment: removing drafting must preserve financial behavior."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from bonus.workflow_no_draft import run_claim as run_without_draft
from lab8.db import connect, init_store
from lab8.durability import InjectedCrash
from lab8.shapes.workflow import run_claim as run_with_draft
from tests.conftest import CLAIMS, WORLD


def _money_state(path):
    conn = connect(path)
    try:
        return {
            "ledger": [dict(r) for r in conn.execute("SELECT * FROM refund_ledger ORDER BY claim_id")],
            "audit": [dict(r) for r in conn.execute("SELECT * FROM audit_events ORDER BY audit_key")],
            "checkpoints": [dict(r) for r in conn.execute("SELECT * FROM checkpoints ORDER BY claim_id, step")],
        }
    finally:
        conn.close()


def _fresh_pair(tmp_path):
    paths = (tmp_path / "with_draft.sqlite", tmp_path / "without_draft.sqlite")
    for path in paths:
        init_store(path, WORLD, CLAIMS).close()
    return paths


def _assert_same_decision(left, right):
    for field in ("claim_id", "seed", "status", "proposal_amount", "refund_effects",
                  "committed_audit_count", "error_reason", "tool_calls"):
        assert getattr(left, field) == getattr(right, field), field
    assert left.shape == "workflow"
    assert right.shape == "workflow_no_draft"
    assert left.run_id != right.run_id
    assert left.model_calls == 1
    assert right.model_calls == right.input_tokens == right.output_tokens == 0
    assert right.cost_estimate < left.cost_estimate
    original_trace = json.loads(Path(left.trace_path).read_text(encoding="utf-8"))
    variant_trace = json.loads(Path(right.trace_path).read_text(encoding="utf-8"))
    assert sum(event["kind"] == "draft" for event in original_trace["events"]) == 1
    assert [event for event in original_trace["events"] if event["kind"] != "draft"] == variant_trace["events"]


@pytest.mark.parametrize("claim_id", [claim["claim_id"] for claim in CLAIMS])
@pytest.mark.parametrize("seed", [11, 22, 33, 44, 55])
def test_removing_draft_preserves_public_decisions_and_entire_money_state(tmp_path, monkeypatch, claim_id, seed):
    monkeypatch.chdir(tmp_path)
    original_db, variant_db = _fresh_pair(tmp_path)
    original = run_with_draft(claim_id, seed=seed, store_path=str(original_db))
    variant = run_without_draft(claim_id, seed=seed, store_path=str(variant_db))
    _assert_same_decision(original, variant)
    assert _money_state(original_db) == _money_state(variant_db)


@pytest.mark.parametrize("point", ["before_effect", "after_effect_before_checkpoint", "after_checkpoint"])
def test_removing_draft_preserves_crash_and_resume_effects(tmp_path, monkeypatch, point):
    monkeypatch.chdir(tmp_path)
    original_db, variant_db = _fresh_pair(tmp_path)
    for runner, path in ((run_with_draft, original_db), (run_without_draft, variant_db)):
        with pytest.raises(InjectedCrash, match=point):
            runner("C-012", seed=11, store_path=str(path), crash_at=point)
    assert _money_state(original_db) == _money_state(variant_db)
    original = run_with_draft("C-012", seed=11, store_path=str(original_db))
    variant = run_without_draft("C-012", seed=11, store_path=str(variant_db))
    _assert_same_decision(original, variant)
    assert _money_state(original_db) == _money_state(variant_db)
    assert len(variant.refund_effects) == variant.committed_audit_count == 1
