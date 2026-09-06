"""No-op deploy test: GET a live canvas, strip server-owned keys, PUT it back unchanged.

The safest possible first write. If the canvas is identical afterwards, the
request-body construction is proven correct against live CRM.

Sequence:
  1. GET the live canvas, save it as a rollback file
  2. Build a request body from it (strip server-owned keys, keep uniqueid)
  3. PUT that body
  4. GET again and verify nothing changed

    python src/noop_deploy.py <view_id> [--execute]

Without --execute it does everything except the PUT (dry run).
"""

from __future__ import annotations

import json
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from zoho_auth import ZohoAuth, ZohoAuthError  # noqa: E402
from zoho_canvas import CanvasApiError, CanvasClient  # noqa: E402

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CAPTURES = PROJECT_ROOT / "reference" / "captures"

# Keys the server owns. They come back on a GET but must not be sent in a PUT.
# `uniqueid` is deliberately NOT in this list — it is a stable node identity and
# must be preserved on updates.
SERVER_KEYS_VIEW = {
    "componentid", "created_by", "created_time", "modified_by", "modified_time",
    "generated_type", "is_default", "profiles", "share", "source",
}
SERVER_KEYS_NODE = {"componentid"}


def strip_node(node: dict) -> dict:
    out = {k: v for k, v in node.items() if k not in SERVER_KEYS_NODE}
    if "children" in out:
        out["children"] = [strip_node(c) for c in (out["children"] or [])]
    return out


def build_request_body(live_doc: dict) -> dict:
    view = live_doc["canvas_view"][0]
    cleaned = {k: v for k, v in view.items() if k not in SERVER_KEYS_VIEW | SERVER_KEYS_NODE}
    cleaned["children"] = [strip_node(c) for c in (cleaned.get("children") or [])]
    # `action` appears in captured requests but not in GETs.
    cleaned.setdefault("action", "edit")
    return {"canvas_view": [cleaned]}


def fingerprint(view: dict) -> dict:
    """Content fingerprint that ignores sibling order and server keys."""
    nodes = []

    def walk(n):
        if isinstance(n, dict):
            nodes.append(n)
            for c in (n.get("children") or []):
                walk(c)
    walk(view)

    return {
        "nodes": len(nodes),
        "uniqueids": Counter(n["uniqueid"] for n in nodes if "uniqueid" in n),
        "field_ids": Counter(n["id"] for n in nodes
                             if n.get("type") == "field" and n.get("id")),
        "types": Counter(n.get("type") for n in nodes),
        "themes": Counter(n.get("theme") for n in nodes if n.get("theme")),
        "tab_names": Counter(
            (n.get("ui") or {}).get("value", {}).get("name")
            for n in nodes
            if isinstance(n.get("ui"), dict)
            and isinstance(n["ui"].get("value"), dict)
            and n["ui"]["value"].get("name")
        ),
    }


def compare(a: dict, b: dict) -> list[str]:
    issues = []
    for key in ("uniqueids", "field_ids", "types", "themes", "tab_names"):
        lost, gained = a[key] - b[key], b[key] - a[key]
        if lost:
            issues.append(f"{key}: LOST {sum(lost.values())} -> {dict(list(lost.items())[:5])}")
        if gained:
            issues.append(f"{key}: GAINED {sum(gained.values())} -> {dict(list(gained.items())[:5])}")
    return issues


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    execute = "--execute" in sys.argv
    if not args:
        print(__doc__)
        return 2
    view_id = args[0]

    try:
        auth = ZohoAuth.from_env()
    except ZohoAuthError as exc:
        print(f"AUTH FAIL: {exc}")
        return 1
    client = CanvasClient(auth)

    print(f"Canvas   : {view_id}")
    print(f"Mode     : {'EXECUTE (will PUT)' if execute else 'DRY RUN (no PUT)'}\n")

    # 1. GET + rollback
    print("[1/4] GET live canvas")
    try:
        before_doc = client.get_view(view_id)
    except CanvasApiError as exc:
        print(f"  FAILED: {exc}")
        return 1
    before = before_doc["canvas_view"][0]
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    rollback = CAPTURES / f"rollback-{view_id}-{stamp}.json"
    rollback.write_text(json.dumps(before_doc, indent=1), encoding="utf-8")
    fp_before = fingerprint(before)
    print(f"  name={before.get('name')!r} module="
          f"{(before.get('module') or {}).get('api_name')!r}")
    print(f"  nodes={fp_before['nodes']} uniqueids={sum(fp_before['uniqueids'].values())} "
          f"fields={sum(fp_before['field_ids'].values())}")
    print(f"  rollback saved: reference/captures/{rollback.name}")

    # 2. build body
    print("\n[2/4] Build request body from live state")
    body = build_request_body(before_doc)
    fp_body = fingerprint(body["canvas_view"][0])
    print(f"  nodes={fp_body['nodes']} uniqueids={sum(fp_body['uniqueids'].values())} "
          f"fields={sum(fp_body['field_ids'].values())}")
    issues = compare(fp_before, fp_body)
    if issues:
        print("  ABORT - body does not match live state before sending:")
        for i in issues:
            print(f"    {i}")
        return 1
    print("  body content matches live state exactly")

    out = CAPTURES / f"noop-body-{view_id}-{stamp}.json"
    out.write_text(json.dumps(body, indent=1), encoding="utf-8")
    print(f"  body saved: reference/captures/{out.name}")

    if not execute:
        print("\n[3/4] SKIPPED (dry run)")
        print("[4/4] SKIPPED (dry run)")
        print("\nDry run complete. Nothing written. Re-run with --execute to PUT.")
        return 0

    # 3. PUT
    print("\n[3/4] PUT")
    try:
        resp = client.put_view(view_id, body, i_understand_this_is_live=True)
    except CanvasApiError as exc:
        print(f"  FAILED: {exc}")
        print(f"  Canvas unchanged. Rollback available: {rollback.name}")
        return 1
    cv = resp.get("canvas_view", [{}])[0]
    print(f"  code={cv.get('code')} status={cv.get('status')} message={cv.get('message')!r}")
    print(f"  returned uniqueids: {len(cv.get('details', {}).get('children', []))}")

    # 4. verify
    print("\n[4/4] GET again and verify")
    after_doc = client.get_view(view_id)
    after = after_doc["canvas_view"][0]
    fp_after = fingerprint(after)
    print(f"  nodes={fp_after['nodes']} uniqueids={sum(fp_after['uniqueids'].values())} "
          f"fields={sum(fp_after['field_ids'].values())}")

    issues = compare(fp_before, fp_after)
    print()
    if issues:
        print("MISMATCH - canvas changed:")
        for i in issues:
            print(f"  {i}")
        print(f"\nRestore from: reference/captures/{rollback.name}")
        return 1

    print("PASS - canvas is unchanged after the round trip.")
    print("  uniqueids preserved :", sum(fp_after['uniqueids'].values()))
    print("  field refs preserved:", sum(fp_after['field_ids'].values()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
