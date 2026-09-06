"""Zoho OAuth access-token management.

Exchanges a long-lived refresh token for short-lived access tokens and caches them
in memory until shortly before they expire.

Credentials come from .env and are never logged. Zoho refresh tokens do not expire
unless revoked, so once .env is filled in this runs unattended.

Usage:
    from zoho_auth import ZohoAuth
    auth = ZohoAuth.from_env()
    headers = auth.auth_header()          # {"Authorization": "Zoho-oauthtoken …"}

Run directly to verify credentials without touching CRM data:
    python src/zoho_auth.py
"""

from __future__ import annotations

import json
import os
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path

# Refresh this many seconds before the token actually expires, so a request
# never goes out holding a token that dies in flight.
EXPIRY_MARGIN_SECONDS = 60

PROJECT_ROOT = Path(__file__).resolve().parent.parent


class ZohoAuthError(RuntimeError):
    """Raised when credentials are missing or Zoho rejects the token request."""


def load_dotenv(path: Path | None = None) -> dict[str, str]:
    """Minimal .env reader. No dependency on python-dotenv.

    Handles `KEY=value`, blank lines, `#` comments, `export ` prefixes and
    surrounding quotes. Does not do interpolation.
    """
    path = path or PROJECT_ROOT / ".env"
    values: dict[str, str] = {}
    if not path.exists():
        return values

    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[len("export "):].strip()
        if "=" not in line:
            continue
        key, _, val = line.partition("=")
        key = key.strip()
        val = val.strip()
        if len(val) >= 2 and val[0] == val[-1] and val[0] in ("'", '"'):
            val = val[1:-1]
        if key:
            values[key] = val
    return values


@dataclass
class ZohoAuth:
    client_id: str
    client_secret: str
    refresh_token: str
    accounts_host: str = "https://accounts.zoho.com"
    api_host: str = "https://crm.zoho.com"
    org_id: str = ""

    _access_token: str | None = field(default=None, repr=False, init=False)
    _expires_at: float = field(default=0.0, repr=False, init=False)
    _lock: threading.Lock = field(default_factory=threading.Lock, repr=False, init=False)

    def __repr__(self) -> str:  # never leak secrets via repr/logs
        return f"ZohoAuth(org_id={self.org_id!r}, api_host={self.api_host!r})"

    @classmethod
    def from_env(cls, env: dict[str, str] | None = None) -> "ZohoAuth":
        """Build from .env, falling back to real environment variables."""
        src = dict(load_dotenv())
        src.update({k: v for k, v in os.environ.items() if k.startswith("ZOHO_")})
        if env:
            src.update(env)

        missing = [
            k for k in ("ZOHO_CLIENT_ID", "ZOHO_CLIENT_SECRET", "ZOHO_REFRESH_TOKEN")
            if not src.get(k)
        ]
        if missing:
            raise ZohoAuthError(
                "Missing required credentials in .env: "
                + ", ".join(missing)
                + ". Copy .env.example to .env and fill it in."
            )

        return cls(
            client_id=src["ZOHO_CLIENT_ID"],
            client_secret=src["ZOHO_CLIENT_SECRET"],
            refresh_token=src["ZOHO_REFRESH_TOKEN"],
            accounts_host=src.get("ZOHO_ACCOUNTS_HOST") or "https://accounts.zoho.com",
            api_host=src.get("ZOHO_API_HOST") or "https://crm.zoho.com",
            org_id=src.get("ZOHO_ORG_ID", ""),
        )

    # --- token handling -------------------------------------------------

    @property
    def _is_valid(self) -> bool:
        return bool(self._access_token) and time.time() < self._expires_at

    def access_token(self, force_refresh: bool = False) -> str:
        """Return a live access token, refreshing if needed. Thread-safe."""
        with self._lock:
            if not force_refresh and self._is_valid:
                return self._access_token  # type: ignore[return-value]
            return self._refresh()

    def _refresh(self) -> str:
        """Exchange the refresh token for a new access token. Caller holds the lock."""
        url = f"{self.accounts_host.rstrip('/')}/oauth/v2/token"
        body = urllib.parse.urlencode({
            "refresh_token": self.refresh_token,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "refresh_token",
        }).encode("utf-8")

        req = urllib.request.Request(
            url,
            data=body,
            method="POST",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                payload = json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", "replace")[:500]
            raise ZohoAuthError(
                f"Token refresh failed: HTTP {exc.code}. Response: {detail}"
            ) from exc
        except Exception as exc:
            raise ZohoAuthError(f"Token refresh failed: {exc}") from exc

        # Zoho returns HTTP 200 with an "error" key on failure.
        if "error" in payload:
            raise ZohoAuthError(
                f"Token refresh rejected by Zoho: {payload['error']}. "
                "Check client id/secret, refresh token, and that "
                "ZOHO_ACCOUNTS_HOST matches the org's data centre."
            )

        token = payload.get("access_token")
        if not token:
            raise ZohoAuthError(f"No access_token in response. Keys: {list(payload)}")

        expires_in = int(payload.get("expires_in", 3600))
        self._access_token = token
        self._expires_at = time.time() + max(expires_in - EXPIRY_MARGIN_SECONDS, 0)
        return token

    # --- convenience ----------------------------------------------------

    def auth_header(self) -> dict[str, str]:
        """Authorization header for a Zoho CRM API call.

        Zoho uses the 'Zoho-oauthtoken' prefix, not 'Bearer'. Postman's OAuth 2.0
        helper is configured with a 'Bearer' prefix and also works; both are
        accepted by the CRM API.
        """
        return {"Authorization": f"Zoho-oauthtoken {self.access_token()}"}

    def expires_in(self) -> int:
        """Seconds until the cached token is considered stale. 0 if none."""
        return max(int(self._expires_at - time.time()), 0) if self._access_token else 0


def main() -> int:
    """Verify credentials by fetching a token. Prints no secrets."""
    try:
        auth = ZohoAuth.from_env()
    except ZohoAuthError as exc:
        print(f"FAIL: {exc}")
        return 1

    print(f"Config     : {auth}")
    print(f"Accounts   : {auth.accounts_host}")

    try:
        token = auth.access_token()
    except ZohoAuthError as exc:
        print(f"FAIL: {exc}")
        return 1

    print(f"Token      : OK (…{token[-6:]}, {len(token)} chars)")
    print(f"Expires in : {auth.expires_in()}s")
    print("Cached     : ", end="")
    t2 = auth.access_token()
    print("yes (no re-fetch)" if t2 == token else "no - unexpected re-fetch")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
