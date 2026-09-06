"""Apply targeted edits to a live canvas, addressed by uniqueid.

Nodes are addressed by `uniqueid` rather than tree path, because the server
reorders sibling cards across saves (see docs/canvas-json-structure.md §10).

    python src/edit_canvas.py <view_id> [--execute]

Edits are declared in EDITS below. Dry run by default: it shows the before/after
for each edit and writes nothing until --execute.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from noop_deploy import build_request_body, compare, fingerprint  # noqa: E402
from zoho_auth import ZohoAuth, ZohoAuthError  # noqa: E402
from zoho_canvas import CanvasApiError, CanvasClient  # noqa: E402

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CAPTURES = PROJECT_ROOT / "reference" / "captures"

# --- the edits to apply -------------------------------------------------
# Each entry: uniqueid -> {"set": {dotted.path.in.ui.value: new_value}}
EDITS: dict[str, dict] = {
    # Static Text "Other Info" -> "Contact Details"
    "ca657ade-4e31-492c-af1f-e7fc84d4df2a": {"set": {"value": "Contact Details"}},
    # Tab "Overview" -> "Summary"
    "f5eb0a28-0b29-42d0-83db-2b8a3fbb7e2f": {"set": {"name": "Summary"}},
}


def index_by_uniqueid(view: dict) -> dict[str, dict]:
    out: dict[str, dict] = {}

    def walk(n):
        if isinstance(n, dict):
            if "uniqueid" in n:
                out[n["uniqueid"]] = n
            for c in (n.get("children") or []):
                walk(c)
    walk(view)
    return out


def apply_edit(node: dict, spec: dict) -> list[str]:
    """Apply one edit spec to ui.value. Returns human-readable change lines."""
    changes = []
    val = node.setdefault("ui", {}).setdefault("value", {})
    for key, new in spec.get("set", {}).items():
        target = val
        parts = key.split(".")
        for p in parts[:-1]:
            target = target.setdefault(p, {})
        old = target.get(parts[-1])
        target[parts[-1]] = new
        changes.append(f"ui.value.{key}: {old!r} -> {new!r}")
    return changes


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

    print(f"Canvas : {view_id}")
    print(f"Mode   : {'EXECUTE' if execute else 'DRY RUN'}")
    print(f"Edits  : {len(EDITS)}\n")

    print("[1/4] GET live canvas")
    try:
        before_doc = client.get_view(view_id)
    except CanvasApiError as exc:
        print(f"  FAILED: {exc}")
        return 1
    before = before_doc["canvas_view"][0]
    fp_before = fingerprint(before)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    rollback = CAPTURES / f"rollback-{view_id}-{stamp}.json"
    rollback.write_text(json.dumps(before_doc, indent=1), encoding="utf-8")
    print(f"  name={before.get('name')!r} nodes={fp_before['nodes']}")
    print(f"  rollback: reference/captures/{rollback.name}")

    print("\n[2/4] Build body and apply edits")
    body = build_request_body(before_doc)
    idx = index_by_uniqueid(body["canvas_view"][0])

    missing = [u for u in EDITS if u not in idx]
    if missing:
        print("  ABORT - uniqueid(s) not found in canvas:")
        for u in missing:
            print(f"    {u}")
        return 1

    for uid, spec in EDITS.items():
        for line in apply_edit(idx[uid], spec):
            print(f"  {uid[:8]}  {line}")

    # Structure must be untouched: only values changed.
    fp_body = fingerprint(body["canvas_view"][0])
    struct = [i for i in compare(fp_before, fp_body)
              if not i.startswith("tab_names")]
    if struct:
        print("  ABORT - edits changed structure, not just values:")
        for i in struct:
            print(f"    {i}")
        return 1
    print("  structure unchanged (only the targeted values differ)")

    out = CAPTURES / f"edited-body-{view_id}-{stamp}.json"
    out.write_text(json.dumps(body, indent=1), encoding="utf-8")
    print(f"  body saved: reference/captures/{out.name}")

    if not execute:
        print("\n[3/4] SKIPPED (dry run)\n[4/4] SKIPPED (dry run)")
        print("\nDry run complete. Re-run with --execute to apply.")
        return 0

    print("\n[3/4] PUT")
    try:
        resp = client.put_view(view_id, body, i_understand_this_is_live=True)
    except CanvasApiError as exc:
        print(f"  FAILED: {exc}")
        print(f"  Canvas unchanged. Rollback: {rollback.name}")
        return 1
    cv = resp.get("canvas_view", [{}])[0]
    print(f"  code={cv.get('code')} status={cv.get('status')}")

    print("\n[4/4] Verify the edits landed")
    after = client.get_view(view_id)["canvas_view"][0]
    aidx = index_by_uniqueid(after)
    ok = True
    for uid, spec in EDITS.items():
        node = aidx.get(uid)
        if node is None:
            print(f"  {uid[:8]}  MISSING after save")
            ok = False
            continue
        val = (node.get("ui") or {}).get("value", {})
        for key, want in spec.get("set", {}).items():
            got = val
            for p in key.split("."):
                got = got.get(p) if isinstance(got, dict) else None
            mark = "OK " if got == want else "FAIL"
            if got != want:
                ok = False
            print(f"  {mark} {uid[:8]}  ui.value.{key} = {got!r}")

    fp_after = fingerprint(after)
    print(f"\n  nodes={fp_after['nodes']} uniqueids={sum(fp_after['uniqueids'].values())} "
          f"fields={sum(fp_after['field_ids'].values())}")
    lost = fp_before["uniqueids"] - fp_after["uniqueids"]
    if lost:
        print(f"  WARNING: {sum(lost.values())} uniqueid(s) lost")
        ok = False
    else:
        print("  all uniqueids preserved")

    print()
    print("PASS - edits applied and verified." if ok
          else f"FAILED. Restore from reference/captures/{rollback.name}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
