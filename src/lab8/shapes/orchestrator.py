"""Shape C — orchestrator plus read-only investigators. Student work.

1. Build a handoff with `lab8.handoff.make_handoff`. Allowed tools are read-only.
   Never put parent_secret, raw headers, or the full claim row into facts.
2. `lab8.runtime.run_readonly_investigators` runs those tools.
3. The orchestrator quotes from the investigator's order view and calls
   `durability.issue_refund`. Investigators have no write registry.
   Pass the full quote; the host subtracts earlier refunds on the same order.
   `lookup_refund_history` is a read-only tool you may hand to an investigator.
4. Trace the sanitized handoff, not the parent context.

An LLM summary of the parent context is not a sanitizer. Use the allowlist.

Trace contract v1 (docs/contracts.md): return a trace_path to a JSON file written in this run,
{"run_id": <same run_id>, "events": [...]}, on every return path including early
ones. `lab8.trace.Trace` does this; your own tracer is fine if it matches.
"""

from __future__ import annotations

import json

from lab8.db import connect
from lab8.durability import issue_refund
from lab8.handoff import make_handoff
from lab8.mock_llm import complete
from lab8.runtime import run_readonly_investigators
from lab8.schemas import Budget, RunResult, make_run_id
from lab8.shapes.common import finish
from lab8.tools import compute_compensation, get_claim_view, tool_cost
from lab8.trace import Trace


def run_claim(
    claim_id: str,
    *,
    seed: int,
    store_path: str,
    crash_at: str | None = None,
) -> RunResult:
    budget = Budget()
    trace = Trace(make_run_id("orchestrator", claim_id, seed))
    conn = connect(store_path)

    def finish_run(
        status: str, proposal: int = 0, reason: str | None = None
    ) -> RunResult:
        trace.add("decision", {"status": status, "proposal_amount": proposal})
        reply = complete(
            budget, seed=seed, purpose="draft",
            prompt=f"status={status}; proposal_vnd={proposal}",
        )
        trace.add("draft", {"text": reply})
        return finish(
            conn, shape="orchestrator", claim_id=claim_id, seed=seed,
            status=status, proposal_amount=proposal, budget=budget,
            trace=trace, error_reason=reason,
        )

    try:
        budget.add_tool(tool_cost())
        claim = get_claim_view(conn, claim_id)
        trace.add("claim_lookup", {"found": claim["found"]})
        if not claim["found"]:
            return finish_run("failed", reason="unknown_claim")
        if not claim.get("order_id"):
            return finish_run("needs_info", reason="missing_order_id")

        # The worker receives only a typed task and read capabilities. Neither
        # the parent's ticket/context nor write tools cross this boundary.
        handoff = make_handoff(
            request_id=f"REQ-{claim_id}", claim_id=claim_id,
            task="check_order_scope_current_policy_and_refund_history",
            facts={},
            allowed_tools=["lookup_order", "lookup_policy", "lookup_refund_history"],
        )
        trace.add("handoff", handoff)
        acknowledgement = complete(
            budget, seed=seed, purpose="peer",
            prompt=json.dumps(handoff, ensure_ascii=False, sort_keys=True),
        )
        trace.add("investigator_ack", {"text": acknowledgement})
        investigated = run_readonly_investigators(
            conn, budget, handoff, principal_id=claim["principal_id"],
        )
        order_view = investigated["tools"]["lookup_order"]
        trace.add("investigator", {"order_visible": order_view["visible"]})
        if not order_view["visible"]:
            return finish_run("escalated", reason=order_view["reason"])

        # The coordinator quotes from the authorized worker view, then alone
        # calls the host. Prior refunds are subtracted by the host, not here.
        budget.add_tool(tool_cost())
        quote = compute_compensation(conn, order_view["order"])
        proposal = int(quote["amount_vnd"])
        trace.add("quote", {"amount_vnd": proposal})
        if proposal <= 0:
            return finish_run("denied", reason=quote["reason"])

        trace.add("refund_requested", {"proposal_amount": proposal})
        trace.write()
        outcome = issue_refund(conn, claim_id, proposal, crash_at=crash_at)
        trace.add("refund_outcome", {
            "ok": outcome["ok"], "conflict": outcome["conflict"],
        })
        if not outcome["ok"]:
            status = "failed" if outcome["conflict"] else "denied"
            return finish_run(status, proposal, outcome["reason"])
        return finish_run("resolved", proposal)
    finally:
        conn.close()
