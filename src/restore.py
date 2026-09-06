"""Restore a canvas from a rollback capture.

    python src/restore.py <rollback-file> [--execute]

Strips server-owned keys from the saved GET and PUTs it back. Dry run by default.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from noop_deploy import build_request_body, fingerprint  # noqa: E402
from zoho_auth import ZohoAuth  # noqa: E402
from zoho_canvas import CanvasApiError, CanvasClient  # noqa: E402

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    execute = "--execute" in sys.argv
    if not args:
        print(__doc__)
        return 2

    path = Path(args[0])
    if not path.is_absolute():
        path = PROJECT_ROOT / path
    doc = json.loads(path.read_text(encoding="utf-8"))
    view = doc["canvas_view"][0]

    # The canvas id is in the filename: rollback-<viewid>-<stamp>.json
    view_id = path.stem.split("-")[1]

    fp = fingerprint(view)
    print(f"Restore source : {path.name}")
    print(f"  canvas       : {view_id}")
    print(f"  name         : {view.get('name')!r}")
    print(f"  nodes        : {fp['nodes']}  uniqueids {sum(fp['uniqueids'].values())}"
          f"  fields {sum(fp['field_ids'].values())}")

    body = build_request_body(doc)
    print(f"  body nodes   : {fingerprint(body['canvas_view'][0])['nodes']}")

    if not execute:
        print("\nDry run. Re-run with --execute to restore.")
        return 0

    client = CanvasClient(ZohoAuth.from_env())
    try:
        resp = client.put_view(view_id, body, i_understand_this_is_live=True)
    except CanvasApiError as exc:
        print(f"PUT FAILED: {exc}")
        return 1

    cv = resp.get("canvas_view", [{}])[0]
    print(f"\nPUT  code={cv.get('code')} status={cv.get('status')}")

    after = client.get_view(view_id)["canvas_view"][0]
    fa = fingerprint(after)
    print(f"     live nodes {fa['nodes']}  name {after.get('name')!r}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
