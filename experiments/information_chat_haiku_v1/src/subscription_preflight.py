"""Read included Claude quota without model calls or billing-setting changes.

The existing OAuth credential stays in memory and is sent only to Anthropic's
first-party usage endpoint. It is never printed, persisted, or used for inference.
"""
from __future__ import annotations

import json
import math
import os
import subprocess
import tempfile
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

from run_expansion import dump, file_sha, load, stamp
from run_haiku import SAFE_ENV

USAGE_URL = "https://api.anthropic.com/api/oauth/usage"
LAST_PREFLIGHT_FILE = "LAST_SUBSCRIPTION_PREFLIGHT.json"


def _retry_after_seconds(value):
    """Keep only a finite, nonnegative numeric delay from Retry-After."""
    if not isinstance(value, str):
        return None
    try:
        number = float(value.strip())
    except ValueError:
        return None
    if not math.isfinite(number) or number < 0:
        return None
    return int(number) if number.is_integer() else number


class SubscriptionPreflightHTTPError(RuntimeError):
    """A usage-endpoint failure is distinct from a model or quota rejection."""

    def __init__(self, http_status, retry_after_seconds=None):
        self.http_status = http_status if type(http_status) is int and 100 <= http_status <= 599 else None
        self.retry_after_seconds = retry_after_seconds
        status = str(self.http_status) if self.http_status is not None else "unknown"
        super().__init__(f"Read-only subscription usage endpoint HTTP {status}; no inference attempted")


def validate_subscription_preflight(path, config):
    try:
        evidence = load(path)
        checked = datetime.fromisoformat(evidence["checked_at_utc"])
        if checked.tzinfo is None:
            raise ValueError("Timestamp must include a timezone")
        age = (datetime.now(timezone.utc) - checked).total_seconds()
        account = evidence["account"]
        usage = evidence["usage"]
        primary, extra = usage["five_hour"], usage["extra_usage"]
        if not isinstance(primary, dict) or not isinstance(extra, dict):
            raise ValueError("Included quota and extra-usage state must both be known")
        used = primary["utilization"]
        if evidence.get("read_only") is not True or not -30 <= age <= 300:
            raise ValueError("A fresh read-only quota check is required")
        expected = {"loggedIn": True, "authMethod": "claude.ai", "apiProvider": "firstParty",
                    "subscriptionType": "enterprise", "orgName": config["expected_org_name"]}
        if any(account.get(key) != value for key, value in expected.items()):
            raise ValueError("Unexpected subscription account; no fallback")
        if isinstance(used, bool) or not isinstance(used, (int, float)) or not 0 <= used < 100:
            raise ValueError("Included quota unavailable or unknown")
        if "locked_reason" not in primary or primary["locked_reason"]:
            raise ValueError("Included quota is locked or unknown")
        if extra.get("is_enabled") is not False:
            raise ValueError("Extra usage must be explicitly disabled")
        for key, window in usage.items():
            if not key.startswith("seven_day") or window is None:
                continue
            if not isinstance(window, dict):
                raise ValueError("Weekly quota is unknown")
            used = window.get("utilization")
            if isinstance(used, bool) or not isinstance(used, (int, float)) or not 0 <= used < 100 or window.get("locked_reason"):
                raise ValueError("Weekly quota unavailable or locked")
    except (OSError, ValueError, KeyError, TypeError) as exc:
        raise RuntimeError("Subscription-only continuation preflight failed: " + str(exc)) from None
    return evidence


def _capture_subscription_preflight(config, root):
    env = {key: value for key, value in os.environ.items() if key in SAFE_ENV}
    with tempfile.TemporaryDirectory(prefix="haiku-quota-readonly-") as temporary:
        auth = subprocess.run(["claude", "auth", "status", "--json"], cwd=temporary, env=env,
                              text=True, capture_output=True, timeout=30)
    if auth.returncode:
        raise RuntimeError("Could not verify the existing Claude subscription")
    identity = json.loads(auth.stdout)
    expected = {"loggedIn": True, "authMethod": "claude.ai", "apiProvider": "firstParty",
                "subscriptionType": "enterprise", "orgName": config["expected_org_name"]}
    if any(identity.get(key) != value for key, value in expected.items()):
        raise RuntimeError("School subscription is not available; no fallback")
    credential = subprocess.run(["security", "find-generic-password", "-s", "Claude Code-credentials", "-w"],
                                text=True, capture_output=True, timeout=15)
    if credential.returncode:
        raise RuntimeError("Existing subscription credential unavailable; no login or purchase attempted")
    try:
        token = json.loads(credential.stdout)["claudeAiOauth"]["accessToken"]
        class NoRedirect(urllib.request.HTTPRedirectHandler):
            def redirect_request(self, req, fp, code, msg, headers, newurl):
                return None
        request = urllib.request.Request(USAGE_URL, headers={"Authorization": "Bearer " + token,
            "anthropic-beta": "oauth-2025-04-20", "Accept": "application/json"}, method="GET")
        with urllib.request.build_opener(NoRedirect()).open(request, timeout=20) as response:
            usage = json.load(response)
    except urllib.error.HTTPError as exc:
        retry_after = _retry_after_seconds(exc.headers.get("Retry-After") if exc.headers else None)
        raise SubscriptionPreflightHTTPError(exc.code, retry_after) from None
    except Exception as exc:
        raise RuntimeError(f"Read-only subscription usage check failed ({type(exc).__name__}); no inference attempted") from None
    finally:
        credential = None
        token = None
    evidence = {"checked_at_utc": stamp(), "read_only": True, "endpoint": USAGE_URL,
        "account": {key: identity.get(key) for key in ["loggedIn", "authMethod", "apiProvider", "subscriptionType", "orgName"]},
        "usage": {key: value for key, value in usage.items()
                  if key in {"five_hour", "extra_usage"} or key.startswith("seven_day")},
        "model_calls": 0, "billing_settings_changed": False, "credentials_saved": False}
    name = "check_" + evidence["checked_at_utc"].replace(":", "").replace("+", "_") + ".json"
    path = root / "SUBSCRIPTION_PREFLIGHT" / name
    dump(path, evidence)
    validate_subscription_preflight(path, config)
    return path


def capture_subscription_preflight(config, root):
    """Always check afresh, recording failure before older evidence can be reused."""
    marker = root / LAST_PREFLIGHT_FILE
    dump(marker, {"state": "checking", "started_at_utc": stamp()})
    try:
        path = _capture_subscription_preflight(config, root)
        evidence = load(path)
        dump(marker, {"state": "verified", "checked_at_utc": evidence["checked_at_utc"],
                      "evidence_file": str(path.relative_to(root)), "evidence_sha256": file_sha(path)})
        return path
    except Exception as exc:
        failed = {"state": "failed", "failed_at_utc": stamp(), "error_type": type(exc).__name__}
        if isinstance(exc, SubscriptionPreflightHTTPError):
            if exc.http_status is not None:
                failed["http_status"] = exc.http_status
            if exc.retry_after_seconds is not None:
                failed["retry_after_seconds"] = exc.retry_after_seconds
        dump(marker, failed)
        raise


def ensure_subscription_preflight(config, root):
    """Reuse only the latest marked, unchanged, fresh, verified quota check."""
    try:
        interval = config.get("campaign", {}).get("quota_check_interval_seconds", 120)
        if isinstance(interval, bool) or not isinstance(interval, (int, float)) or not math.isfinite(interval):
            raise ValueError("Invalid quota check interval")
        maximum_age = min(120, interval)
        marker = load(root / LAST_PREFLIGHT_FILE)
        if marker.get("state") != "verified":
            raise ValueError("The latest quota check was not verified")
        relative = marker["evidence_file"]
        if not isinstance(relative, str) or Path(relative).is_absolute():
            raise ValueError("Invalid quota evidence path")
        path = root / relative
        if path.resolve().parent != (root / "SUBSCRIPTION_PREFLIGHT").resolve():
            raise ValueError("Quota evidence must remain in its private directory")
        if file_sha(path) != marker["evidence_sha256"]:
            raise ValueError("Quota evidence changed")
        evidence = validate_subscription_preflight(path, config)
        if marker.get("checked_at_utc") != evidence["checked_at_utc"]:
            raise ValueError("Quota evidence timestamp differs from its verified marker")
        age = (datetime.now(timezone.utc) - datetime.fromisoformat(evidence["checked_at_utc"])).total_seconds()
        if -30 <= age <= maximum_age:
            return path
    except (RuntimeError, OSError, ValueError, KeyError, TypeError, AttributeError):
        pass
    return capture_subscription_preflight(config, root)
