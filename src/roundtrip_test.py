"""Read-only round-trip validation against live Camco CRM.

For each captured canvas: GET the live view, compare it structurally against the
captured request body, and report what differs. Writes nothing to CRM.

The point is to answer: can we reconstruct a byte-faithful request body from what
the API gives us back? If yes, the deploy path is trustworthy.

    python src/roundtrip_test.py
"""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from zoho_auth import ZohoAuth, ZohoAuthError  # noqa: E402
from zoho_canvas import CanvasApiError, CanvasClient  # noqa: E402

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CAPTURES = PROJECT_ROOT / "reference" / "captures"

CASES = [
    ("c1  Main Account (Accounts)", "2582206000057761014",
     "accounts-main-account.payload.json"),
    ("c2  Canvas-template 2 (Accounts)", "2582206000076636840",
     "accounts-canvas-template-2.payload.json"),
    ("c3  canvas template 3 (Contacts)", "2582206000076641025",
     "contacts-canvas-template-3.payload.json"),
]


def walk(node, fn, depth=0, path="root"):
    if isinstance(node, dict):
        fn(node, depth, path)
        for i, child in enumerate(node.get("children") or []):
            walk(child, fn, depth + 1, f"{path}/{i}")


def profile(view: dict) -> dict:
    """Structural fingerprint, independent of key ordering."""
    types, themes, uids, keys = Counter(), Counter(), [], Counter()
    total = [0]
    maxdepth = [0]

    def visit(n, d, _p):
        total[0] += 1
        maxdepth[0] = max(maxdepth[0], d)
        types[n.get("type", "<root>")] += 1
        if n.get("theme"):
            themes[n["theme"]] += 1
        if "uniqueid" in n:
            uids.append(n["uniqueid"])
        for k in n:
            keys[k] += 1

    walk(view, visit)
    return {
        "nodes": total[0], "max_depth": maxdepth[0],
        "types": types, "themes": themes,
        "uniqueids": uids, "node_keys": keys,
    }


def cmp_counter(name, a: Counter, b: Counter) -> list[str]:
    out = []
    for k in sorted(set(a) | set(b)):
        if a.get(k, 0) != b.get(k, 0):
            out.append(f"      {name} {k!r}: captured={a.get(k,0)} live={b.get(k,0)}")
    return out


def unwrap(doc: dict) -> dict | None:
    """Both request bodies and GET responses use the canvas_view array envelope."""
    cv = doc.get("canvas_view")
    if isinstance(cv, list) and cv:
        return cv[0]
    return None


def main() -> int:
    try:
        auth = ZohoAuth.from_env()
    except ZohoAuthError as exc:
        print(f"AUTH FAIL: {exc}")
        return 1

    client = CanvasClient(auth)
    print(f"Target: {auth.api_host}  org {auth.org_id}\n")

    failures = 0
    for label, view_id, capfile in CASES:
        print("=" * 74)
        print(f"{label}\n  view_id {view_id}")

        cap_path = CAPTURES / capfile
        if not cap_path.exists():
            print(f"  SKIP: capture missing ({capfile})")
            continue

        captured = unwrap(json.loads(cap_path.read_text(encoding="utf-8")))

        try:
            live_doc = client.get_view(view_id)
        except CanvasApiError as exc:
            print(f"  GET FAILED: {exc}")
            failures += 1
            continue

        live = unwrap(live_doc)
        if live is None:
            print(f"  Unexpected GET shape. Top keys: {list(live_doc)}")
            failures += 1
            continue

        pc, pl = profile(captured), profile(live)

        print(f"  identity : name={live.get('name')!r} module="
              f"{(live.get('module') or {}).get('api_name')!r} "
              f"feature={live.get('feature')!r} state={live.get('state')!r}")
        print(f"  nodes    : captured={pc['nodes']}  live={pl['nodes']}  "
              f"{'MATCH' if pc['nodes']==pl['nodes'] else 'DIFFER'}")
        print(f"  depth    : captured={pc['max_depth']}  live={pl['max_depth']}")
        print(f"  uniqueid : captured={len(pc['uniqueids'])}  live={len(pl['uniqueids'])}")

        cs, ls = set(pc["uniqueids"]), set(pl["uniqueids"])
        if cs or ls:
            print(f"             captured ids still live: {len(cs & ls)}/{len(cs) or 0}"
                  f"   live-only: {len(ls - cs)}")

        diffs = (cmp_counter("type", pc["types"], pl["types"])
                 + cmp_counter("theme", pc["themes"], pl["themes"])
                 + cmp_counter("key", pc["node_keys"], pl["node_keys"]))
        if diffs:
            print("  structural differences:")
            for d in diffs[:25]:
                print(d)
            if len(diffs) > 25:
                print(f"      … and {len(diffs)-25} more")
        else:
            print("  structural differences: NONE")

        # Save the live copy as a rollback point.
        out = CAPTURES / f"live-{view_id}.json"
        out.write_text(json.dumps(live_doc, indent=1), encoding="utf-8")
        print(f"  saved    : reference/captures/{out.name}")

    print("=" * 74)
    print("Done. Nothing was written to CRM." if not failures
          else f"Done with {failures} failure(s). Nothing was written to CRM.")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
