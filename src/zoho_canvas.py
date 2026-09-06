"""Zoho CRM Canvas view API client.

Read and write canvas views. Deliberately read-biased: get_view() is safe to run
against live CRM, put_view() is not and refuses to run without an explicit
confirm flag.

Usage:
    from zoho_auth import ZohoAuth
    from zoho_canvas import CanvasClient

    client = CanvasClient(ZohoAuth.from_env())
    view = client.get_view("2582206000076636840")
"""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from pathlib import Path

from zoho_auth import ZohoAuth

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CAPTURES = PROJECT_ROOT / "reference" / "captures"


class CanvasApiError(RuntimeError):
    pass


class CanvasClient:
    def __init__(self, auth: ZohoAuth):
        self.auth = auth

    def _url(self, view_id: str) -> str:
        return f"{self.auth.api_host.rstrip('/')}/crm/v8/settings/canvas/views/{view_id}"

    def _request(self, method: str, view_id: str, body: bytes | None = None) -> dict:
        headers = dict(self.auth.auth_header())
        if body is not None:
            # Zoho expects text/plain even though the body is JSON.
            headers["Content-Type"] = "text/plain;charset=UTF-8"

        req = urllib.request.Request(
            self._url(view_id), data=body, method=method, headers=headers
        )
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                raw = resp.read().decode("utf-8")
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", "replace")[:1000]
            raise CanvasApiError(
                f"{method} {view_id} failed: HTTP {exc.code}. Response: {detail}"
            ) from exc
        except Exception as exc:
            raise CanvasApiError(f"{method} {view_id} failed: {exc}") from exc

        if not raw.strip():
            return {}
        try:
            return json.loads(raw)
        except json.JSONDecodeError as exc:
            raise CanvasApiError(f"Non-JSON response: {raw[:300]}") from exc

    # --- read ---------------------------------------------------------

    def get_view(self, view_id: str) -> dict:
        """Fetch a canvas view. Read-only, safe against live CRM."""
        return self._request("GET", view_id)

    def backup_view(self, view_id: str, label: str) -> Path:
        """GET a view and save it to reference/captures/ as a rollback point."""
        data = self.get_view(view_id)
        CAPTURES.mkdir(parents=True, exist_ok=True)
        path = CAPTURES / f"{label}.live-{view_id}.json"
        path.write_text(json.dumps(data, indent=1), encoding="utf-8")
        return path

    # --- write --------------------------------------------------------

    def put_view(self, view_id: str, payload: dict, *, i_understand_this_is_live: bool = False) -> dict:
        """Overwrite a canvas view. DESTRUCTIVE — replaces the whole canvas.

        There is no sandbox for this project, so this refuses to run unless the
        caller explicitly opts in, and it always takes a backup first.
        """
        if not i_understand_this_is_live:
            raise CanvasApiError(
                "put_view() overwrites a live canvas and needs "
                "i_understand_this_is_live=True. Take a backup_view() first."
            )
        self.backup_view(view_id, "pre-put-rollback")
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        return self._request("PUT", view_id, body)
