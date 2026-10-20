"""Conservative local CLI estimates, including unresolved transport usage."""
from __future__ import annotations

import json
import math
import re
from pathlib import Path

IDLE_TRANSPORT_ERROR = "API Error: Stream idle timeout - partial response received"


def _valid_cost(value):
    if type(value) not in (int, float) or value < 0:
        return False
    try:
        return math.isfinite(value)
    except OverflowError:
        return False


def _uncertain_idle_transport(raw):
    return (isinstance(raw, dict) and raw.get("is_error") is True
            and raw.get("result") == IDLE_TRANSPORT_ERROR and not raw.get("modelUsage"))


def cost_accounting(root, config):
    """Read attempts and validated deferrals without rewriting saved evidence."""
    from transport_defer import deferred_transport_batches
    from interruption_defer import interrupted_batches

    root = Path(root)
    budget = config.get("max_call_budget_usd")
    if not _valid_cost(budget):
        raise RuntimeError("A finite nonnegative per-call estimate reserve is required")
    # Validate every saved deferral even when no unknown attempt would use it.
    deferred = deferred_transport_batches(root)
    interrupted = interrupted_batches(root)
    reported_costs = []
    uncertain = {}
    for request in sorted(root.glob("provider*/*.request.json")):
        raw_path = request.with_name(request.name.removesuffix(".request.json") + ".raw.json")
        try:
            raw = json.loads(raw_path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            raw = None
        reported = raw.get("total_cost_usd") if isinstance(raw, dict) else None
        valid_reported = _valid_cost(reported)
        if valid_reported:
            reported_costs.append(reported)
        if not valid_reported or _uncertain_idle_transport(raw):
            uncertain[str(request.relative_to(root))] = raw

    reviewed = set()
    for entry in deferred:
        batch = entry.get("batch") if isinstance(entry, dict) else None
        if not isinstance(batch, str) or not re.fullmatch(r"batch_\d{5}", batch):
            raise RuntimeError("Invalid reviewed transport deferral batch")
        request_name = f"provider/{batch}.request.json"
        # A reviewed base-provider idle failure cannot clear a different request.
        if request_name in uncertain and _uncertain_idle_transport(uncertain[request_name]):
            reviewed.add(request_name)

    reviewed_interruptions = set()
    for entry in interrupted:
        request_name = f"provider/{entry['batch']}.request.json"
        # Init-only interruption validation pins a missing raw result.  It cannot
        # confer review credit to another provider directory or completed call.
        if request_name in uncertain and uncertain[request_name] is None:
            reviewed_interruptions.add(request_name)
    if reviewed & reviewed_interruptions:
        raise RuntimeError("A provider attempt cannot have two different usage deferrals")

    unknown = len(uncertain)
    reported_total = sum(reported_costs)
    reserve = unknown * budget
    if not math.isfinite(reported_total) or not math.isfinite(reserve) or not math.isfinite(reported_total + reserve):
        raise RuntimeError("Local CLI estimate totals must remain finite")
    return {
        "incremental_cli_estimate_usd": reported_total,
        "calls_without_final_cost": unknown,
        "reviewed_deferred_transport_calls_without_final_cost": len(reviewed),
        "reviewed_deferred_interruption_calls_without_final_cost": len(reviewed_interruptions),
        "unreviewed_calls_without_final_cost": unknown - len(reviewed) - len(reviewed_interruptions),
        "conservative_cli_estimate_reserved_usd": reported_total + reserve,
        "unknown_cli_estimate_reserve_usd": reserve,
        "uncertain_usage_attempts": list(uncertain),
        "uncertain_usage_estimates_not_invoices": True,
    }


def unreviewed_cost_count(root, config, status):
    """Keep older unresolved counts conservative and derive review credit afresh."""
    cached_unknown = status.get("calls_without_final_cost") if isinstance(status, dict) else None
    if type(cached_unknown) is not int or cached_unknown < 0:
        raise RuntimeError("Cached unresolved cost count must be a nonnegative integer")
    ledger = cost_accounting(root, config)
    return max(0, max(cached_unknown, ledger["calls_without_final_cost"])
               - ledger["reviewed_deferred_transport_calls_without_final_cost"]
               - ledger["reviewed_deferred_interruption_calls_without_final_cost"])
