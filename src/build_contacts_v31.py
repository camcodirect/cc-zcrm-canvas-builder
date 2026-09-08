"""Contacts canvas v3.1: v3 plus the constructs learned from the round-3 capture.

Adds, before the All Fields tab:
  - "Interactions"  a palette `system` component placed as a related list (id "journeys")
  - three "All Fields - <Lookup>" tabs (Account Name, Broker Company Name,
    Related Buyer Contact), with their `details.lookup_associations` references
    and the matching root `related_to.lookup_associations` entries

The lookup connection ids were minted by the editor during the round-3
recording and are read from that capture, not typed in. Whether they survived
the v3 PUT (which wrote lookup_associations: null) is unknown; if the tabs come
up empty in the editor, recreate them there.

    python src/build_contacts_v31.py            # build + validate
    python src/build_contacts_v31.py --deploy
"""

from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import build_contacts_v3 as v3  # noqa: E402
from canvas_shapes import (BRIGHT, all_fields_tab, lookup_all_fields_tab,  # noqa: E402
                           system_list_card, tab_strip)
from validate import validate  # noqa: E402

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = PROJECT_ROOT / "output" / "camco-647376701" / "Contacts"
ROUND3 = PROJECT_ROOT / "reference" / "ui-capture" / "round-3" / "save-03.json"
T = BRIGHT
W, BANNER_H, GAP = v3.W, v3.BANNER_H, v3.GAP
STRIP_H = 1254
BODY_H = STRIP_H - 48


def lookup_tabs_from_capture() -> tuple[list[dict], list[dict]]:
    """(lookup_associations for related_to, [{name, connection_id}]) from round-3."""
    view = json.loads(ROUND3.read_text(encoding="utf-8"))["canvas_view"][0]
    assoc = view["related_to"]["lookup_associations"]
    tabs = []

    def walk(n):
        if isinstance(n, dict):
            d = n.get("details") or {}
            if d.get("connection_type") == "lookup_associations":
                tabs.append({"name": n["ui"]["value"]["name"],
                             "connection_id": d["connection_id"]})
            for c in (n.get("children") or []):
                walk(c)
    walk(view)
    ids = {a["connection_id"] for a in assoc}
    tabs = [t for t in tabs if t["connection_id"] in ids]
    return assoc, tabs


def build() -> dict:
    body = v3.build()
    view = body["canvas_view"][0]
    view["name"] = "Contacts Canvas v3.1"

    strip = view["children"][-1]
    assert strip.get("theme") == "Tab Layout"
    af = strip["children"].pop()                       # All Fields, re-appended last
    assert af["ui"]["value"]["name"] == "All Fields"

    # Interactions: system component as a related list, same card as Timeline.
    strip["children"].append({
        "type": "component",
        "ui": {"value": {"style": {}, "custom_style": {},
                         "position": {"start_x": 0, "start_y": BODY_H // 2, "end_x": W,
                                      "width": W, "height": BODY_H // 2, "depth": 1,
                                      "min_top": 30, "min_left": 30,
                                      "order": len(strip["children"])},
                         "class": "zc-tab-section zc-tabrl-container",
                         "name": "Interactions", "disabled": True},
               "tab_item_title": {"class": ""}},
        "theme": "Custom Layout",
        "tab_relatedlist_id": "journeys",
        "children": [system_list_card("journeys", "Interactions", GAP, 24, W - GAP * 2, 640,
                                      tokens=T, recordcount=5)],
    })

    # Lookup All-Fields tabs + their root associations, from the round-3 capture.
    assoc, lookup_tabs = lookup_tabs_from_capture()
    for t in lookup_tabs:
        strip["children"].append(
            lookup_all_fields_tab(t["name"], t["connection_id"], W, BODY_H // 2,
                                  order=len(strip["children"])))
    view["related_to"]["lookup_associations"] = assoc

    af["ui"]["value"]["position"]["order"] = len(strip["children"])
    strip["children"].append(af)
    return body


def main() -> int:
    body = build()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUT_DIR / "contacts-v3.1.json"
    out.write_text(json.dumps(body, indent=1), encoding="utf-8")
    (OUT_DIR / "contacts-v3.1.meta.json").write_text(json.dumps({
        "canvas_view_id": v3.VIEW_ID, "module": {"id": v3.MODULE_ID, "api_name": "Contacts"},
        "layout": {"id": v3.LAYOUT_ID}, "org_id": "647376701",
        "generated_by": "src/build_contacts_v31.py", "extends": "src/build_contacts_v3.py",
        "lookup_connections_from": "reference/ui-capture/round-3/save-03.json",
    }, indent=1), encoding="utf-8")

    view = body["canvas_view"][0]
    n = [0]; tabs = []

    def count(x):
        if isinstance(x, dict):
            n[0] += 1
            nm = ((x.get("ui") or {}).get("value") or {}).get("name") if isinstance(x.get("ui"), dict) else None
            if nm:
                tabs.append(nm)
            for c in (x.get("children") or []):
                count(c)
    count(view)
    print(f"Built {out.relative_to(PROJECT_ROOT)}: {n[0]} nodes, {len(tabs)} tabs")
    print("  tabs:", tabs)
    print("  lookup_associations:", [a["parent_module_lookup_field"]["api_name"]
                                     for a in view["related_to"]["lookup_associations"]])

    errors, warnings = validate(body)
    print(f"  validation: {len(errors)} errors, {len(warnings)} warnings")
    for e in errors[:20]:
        print(f"    ERROR {e}")
    for w in warnings[:10]:
        print(f"    WARN  {w}")
    if errors:
        return 1
    if "--deploy" not in sys.argv:
        print("\nNot deployed. Re-run with --deploy.")
        return 0

    from zoho_auth import ZohoAuth
    from zoho_canvas import CanvasApiError, CanvasClient
    client = CanvasClient(ZohoAuth.from_env())
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    rb = PROJECT_ROOT / "reference" / "captures" / f"rollback-{v3.VIEW_ID}-{stamp}.json"
    rb.write_text(json.dumps(client.get_view(v3.VIEW_ID), indent=1), encoding="utf-8")
    print(f"\nRollback: reference/captures/{rb.name}")
    try:
        resp = client.put_view(v3.VIEW_ID, body, i_understand_this_is_live=True)
    except CanvasApiError as exc:
        print(f"PUT FAILED: {exc}")
        return 1
    cv = resp.get("canvas_view", [{}])[0]
    print(f"PUT {cv.get('code')} {cv.get('status')}  uniqueids returned: "
          f"{len(cv.get('details', {}).get('children', []))}")
    after = client.get_view(v3.VIEW_ID)["canvas_view"][0]
    print(f"     live: {after.get('name')!r}, lookup_associations kept: "
          f"{len(after.get('related_to', {}).get('lookup_associations') or [])}")
    print("\nNOT VERIFIED until opened in the editor:")
    print(f"  https://crm.zoho.com/crm/org647376701/settings/modules/Contacts/layouts/{v3.LAYOUT_ID}"
          f"/canvas/{v3.VIEW_ID}/edit?feature=DetailView")
    print(f"  restore: python src/restore.py reference/captures/{rb.name} --execute")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
