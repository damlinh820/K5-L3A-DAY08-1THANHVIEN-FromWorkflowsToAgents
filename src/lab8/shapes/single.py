"""Shape B — one ReAct agent. Student work.

Use `lab8.runtime.run_react` with max_steps=8. `decide` may pick a read tool.
It must not call `issue_refund`. After the loop, the host validates the quote
and is the only writer.

A decide() that trusts ticket text over the order row will fail hidden claims
where the customer overstates the delay or cites a superseded clause.

Per-order cap: an order may already have been refunded by an earlier claim.
The read tool `lookup_refund_history` shows how much. The host still enforces
the cap, so pass the full quote to `durability.issue_refund`, not a net amount.

Caps: stop at 8 steps. Count model calls in the Budget so cost stays comparable.

Trace contract v1 (docs/contracts.md): return a trace_path to a JSON file written in this run,
{"run_id": <same run_id>, "events": [...]}, on every return path including early
ones. `lab8.trace.Trace` does this; your own tracer is fine if it matches.
"""

from __future__ import annotations

from lab8.db import connect
from lab8.durability import issue_refund
from lab8.mock_llm import complete
from lab8.runtime import run_react
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
    trace = Trace(make_run_id("single", claim_id, seed))
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
            conn, shape="single", claim_id=claim_id, seed=seed,
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

        # MockLLM supplies an untrusted delay hint. It may trigger another read,
        # but it never replaces the structured order or determines the quote.
        parsed = complete(budget, seed=seed, purpose="parse", prompt=claim["ticket"])
        delay_text = parsed.partition("=")[2]
        ticket_delay = int(delay_text) if delay_text.isdecimal() else None
        trace.add("ticket_parse", {"has_delay_hint": ticket_delay is not None})
        observations: dict = {}

        def decide(observation: dict) -> dict:
            last_tool = observation.get("last_tool")
            if last_tool:
                observations[last_tool] = observation["last_result"]
                trace.add("agent_observation", {"tool": last_tool})

            if "lookup_order" not in observations:
                action = {
                    "tool": "lookup_order",
                    "args": {"order_id": claim["order_id"], "principal_id": claim["principal_id"]},
                }
            elif not observations["lookup_order"]["visible"]:
                return {"final": {"status": "escalated"}}
            elif (
                ticket_delay is not None
                and ticket_delay != int(observations["lookup_order"]["order"]["delay_days"])
                and "lookup_policy" not in observations
            ):
                action = {"tool": "lookup_policy", "args": {}}
            elif "lookup_refund_history" not in observations:
                action = {
                    "tool": "lookup_refund_history",
                    "args": {"order_id": claim["order_id"], "principal_id": claim["principal_id"]},
                }
            else:
                return {"final": {"status": "ready"}}
            trace.add("agent_action", {"tool": action["tool"]})
            return action

        loop = run_react(
            conn, budget, observation={"claim": {"claim_id": claim_id}},
            decide=decide, max_steps=8, worker=True,
        )
        if loop["stopped"] != "final":
            return finish_run("failed", reason="step_cap")
        order_view = observations["lookup_order"]
        if not order_view["visible"]:
            return finish_run("escalated", reason=order_view["reason"])

        # The read loop cannot grant approval or write a refund. Code computes
        # the full quote from the authorized order after the loop has ended.
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
