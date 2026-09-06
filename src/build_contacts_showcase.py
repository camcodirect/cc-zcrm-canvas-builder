"""Build a maximal Contacts canvas — a showcase of every construct we understand.

Exercises: gradient banner with depth stacking, profile image, MERGEFIELD button
group, separators, Static Icons, rounded cards, label/value tables, related-list
cards on the Overview tab, full related lists on their own tabs, and system
actions.

    python src/build_contacts_showcase.py            # write + validate the body
    python src/build_contacts_showcase.py --deploy   # also PUT it to c3

Output: output/camco-647376701/Contacts/contacts-showcase.json
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from base_template import (CAMCO, F_MED, F_SEMI, action, banner, card,  # noqa: E402
                           field, field_table, heading, position,
                           related_list_card, root, separator, tab_strip)
from validate import validate  # noqa: E402

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = PROJECT_ROOT / "output" / "camco-647376701" / "Contacts"

VIEW_ID = "2582206000076641025"
MODULE_ID = "2582206000000002179"
LAYOUT_ID = "2582206000000091033"
T = CAMCO

W = 1100
BANNER_H = 190
GAP = 24

# --- Contacts fields (verified live via Camco ZCRM MCP) -----------------
F = {
    "image":       ("2582206000005007005", "profileimage"),
    "full_name":   ("2582206000000002529", "text"),
    "title":       ("2582206000000002499", "text"),
    "email":       ("2582206000000002497", "email"),
    "phone":       ("2582206000000002503", "phone"),
    "mobile":      ("2582206000000002511", "phone"),
    "account":     ("2582206000000002493", "lookup"),
    "reports_to":  ("2582206000006278003", "lookup"),
    "owner":       ("2582206000000002485", "user"),
    "lead_src":    ("2582206000000002487", "picklist"),
    "opt_out":     ("2582206000000014171", "boolean"),
    "tag":         ("2582206000000242039", "tag"),
    "desc":        ("2582206000000002553", "text-area"),
    "street":      ("2582206000000002533", "text"),
    "city":        ("2582206000000002537", "text"),
    "state":       ("2582206000000002541", "text"),
    "zip":         ("2582206000000002545", "text"),
    "country":     ("2582206000000002549", "text"),
    "created_by":  ("2582206000000002521", "user"),
    "modified_by": ("2582206000000002523", "user"),
    "created":     ("2582206000000002525", "date-time"),
    "modified":    ("2582206000000002527", "date-time"),
    "last_act":    ("2582206000000052005", "date-time"),
}

# Related lists available on Contacts, harvested from the original c3 capture.
RL = {
    "notes":      "2582206000000003801",
    "meetings":   "2582206000025002875",
    "emails":     "2582206000000015214",
    "connected":  "2582206000063944585",
    "checklists": "2582206000002573009",
    "timeline":   "timeline",
    "open_meet":  "2582206000025002867",
    "cadences":   "2582206000000062003",
    "tasks":      "2582206000025002869",
    "invited":    "2582206000053584109",
}


def static_icon(x: int, y: int, name: str, colour: str, size: int = 22) -> dict:
    return {
        "type": "component",
        "ui": {"value": {
            "style": {"default": {"color": colour, "font_size": f"{size}px"}},
            "custom_style": {},
            "position": position(x, y, size + 4, size + 4),
            "fixed": True,
            "class": "zc-ta-center",
            "zcode": {"name": f"icon_{name}"},
            "icon": name,
        }},
        "theme": "Static Icon",
        "children": [],
    }


def button_group(x: int, y: int, w: int, buttons: list[tuple[str, bool]]) -> dict:
    """MERGEFIELD wrapper — Zoho's construct for an inline row of buttons."""
    inner, cx = [], 0
    for i, (aid, primary) in enumerate(buttons):
        bw = 120 if primary else 44
        inner.append(action(aid, cx, 0, bw, 34, tokens=T, primary=primary))
        cx += bw
        if i < len(buttons) - 1:
            inner.append(separator(cx, 12))
            cx += 10
    return {
        "type": "component",
        "ui": {"value": {
            "style": {"default": {}}, "custom_style": {},
            "position": position(x, y, w, 34),
            "class": "zc-merge-hright",
        }},
        "theme": "MERGEFIELD",
        "children": [{
            "type": "component",
            "ui": {"value": {
                "style": {"default": {}}, "custom_style": {},
                "class": "zcanvas-row-seperator",
                "position": {},
            }},
            "children": inner,
        }],
    }


def titled_card(x, y, w, h, icon, colour, title, body):
    """Card with an icon + heading, then content."""
    c = card(x, y, w, h, tokens=T, list_component=True)
    c["children"] = [
        static_icon(20, 20, icon, colour),
        heading(54, 18, w - 90, 30, title, tokens=T),
        *body,
    ]
    return c


def stat_tile(x, y, w, h, fid_dt, label, colour):
    """A small KPI-style tile: coloured left border, label, single field."""
    return {
        "type": "component",
        "ui": {"value": {
            "style": {"default": {
                "border": "none",
                "border_left": f"4px solid {colour}",
                "background_color": "rgba(255, 255, 255, 1)",
                "border_radius": "8px",
                "padding": "12px",
                "box_shadow": "none",
            }},
            "custom_style": {},
            "position": position(x, y, w, h),
            "class": "zc-lsection",
        }},
        "theme": "Custom Layout",
        "children": [
            heading(12, 8, w - 30, 20, label, tokens=T),
            field(*fid_dt, 12, 32, w - 30, 24, tokens=T),
        ],
    }


def build() -> dict:
    view = root("Contacts Showcase", MODULE_ID, "Contacts", LAYOUT_ID,
                W, 1780, tokens=T)

    # --- banner --------------------------------------------------------
    b = banner(0, 0, W, BANNER_H, tokens=T)
    b["children"] = [
        action("back", 22, 20, 38, 30, tokens=T),
        field(*F["image"], 30, 56, 88, 88, tokens=T,
              css="zcbdrbox zcanvas-field"),
        field(*F["full_name"], 136, 62, 430, 32, tokens=T),
        field(*F["title"], 136, 98, 430, 22, tokens=T),
        field(*F["account"], 136, 124, 430, 22, tokens=T,
              css="zcanvas-field zcclinkvalue"),
        button_group(W - 372, 60, 342,
                     [("send_mail", True), ("edit", True), ("morebutton", False)]),
        action("navigate", W - 104, 20, 70, 30, tokens=T),
    ]
    view["children"].append(b)

    # --- Overview tab ---------------------------------------------------
    half = (W - GAP * 3) // 2
    third = (W - GAP * 4) // 3

    about_rows = [F["email"], F["phone"], F["mobile"], F["account"],
                  F["reports_to"], F["lead_src"], F["owner"], F["opt_out"]]
    address_rows = [F["street"], F["city"], F["state"], F["zip"], F["country"]]
    system_rows = [F["created_by"], F["created"], F["modified_by"],
                   F["modified"], F["last_act"]]

    overview = [
        # KPI strip across the top
        stat_tile(GAP, 20, third, 72, F["lead_src"], "Lead Source", T["signal"]),
        stat_tile(GAP * 2 + third, 20, third, 72, F["owner"], "Owner",
                  "rgba(12, 148, 174, 1)"),
        stat_tile(GAP * 3 + third * 2, 20, third, 72, F["last_act"],
                  "Last Activity", T["success"]),

        # Detail cards
        titled_card(GAP, 112, half, 330, "icon-Icon_Customerprofile", T["signal"],
                    "About This Contact",
                    [field_table(20, 62, half - 44, about_rows, tokens=T)]),
        titled_card(GAP * 2 + half, 112, half, 330, "icon-Icon_location",
                    "rgba(12, 148, 174, 1)", "Mailing Address",
                    [field_table(20, 62, half - 44, address_rows, tokens=T)]),

        titled_card(GAP, 462, half, 250, "icon-Icon_notes", T["success"],
                    "Description & Tags",
                    [field(*F["desc"], 20, 62, half - 44, 100, tokens=T,
                           css="zcanvas-field zctextarea"),
                     field(*F["tag"], 20, 174, half - 44, 26, tokens=T)]),
        titled_card(GAP * 2 + half, 462, half, 250, "icon-Icon_dashboard",
                    "rgba(240, 163, 48, 1)", "System Information",
                    [field_table(20, 62, half - 44, system_rows, tokens=T)]),

        # Related-list cards side by side
        related_list_card(RL["open_meet"], GAP, 732, half, 330,
                          "Open Meetings", tokens=T, recordcount=5,
                          icon="icon-Icon_Meeting", icon_colour=T["signal"]),
        related_list_card(RL["tasks"], GAP * 2 + half, 732, half, 330,
                          "Open Tasks", tokens=T, recordcount=5,
                          icon="icon-Icon_Task",
                          icon_colour="rgba(12, 148, 174, 1)"),
        related_list_card(RL["cadences"], GAP, 1082, half, 300,
                          "Cadences", tokens=T, recordcount=5,
                          icon="icon-Icon_Cadence", icon_colour=T["success"]),
        related_list_card(RL["invited"], GAP * 2 + half, 1082, half, 300,
                          "Invited Meetings", tokens=T, recordcount=5,
                          icon="icon-Icon_Calendar",
                          icon_colour="rgba(240, 163, 48, 1)"),
    ]

    # --- tabs -----------------------------------------------------------
    tab_body_w = W
    tabs = [{"name": "Overview", "children": overview}]

    full_tabs = [
        ("Notes", RL["notes"], "icon-Icon_notes", 10),
        ("Closed Meetings", RL["meetings"], "icon-Icon_Meeting", 10),
        ("Emails", RL["emails"], "icon-Icon_Mail", 10),
        ("Connected Records", RL["connected"], "icon-Icon_Link", 10),
        ("Checklists", RL["checklists"], "icon-Icon_Checklist", 10),
        ("Timeline", RL["timeline"], "icon-Icon_History", 10),
    ]
    for name, rl_id, icon, rc in full_tabs:
        tabs.append({
            "name": name,
            "relatedlist_id": rl_id,
            "children": [related_list_card(
                rl_id, GAP, 24, tab_body_w - GAP * 2, 700, name,
                tokens=T, recordcount=rc, icon=icon, icon_colour=T["signal"])],
        })

    tabs.append({"name": "All Fields", "children": []})

    view["children"].append(
        tab_strip(0, BANNER_H + 6, W, 1560, tabs, tokens=T, depth=4))

    return {"canvas_view": [view]}


def main() -> int:
    body = build()

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUT_DIR / "contacts-showcase.json"
    out.write_text(json.dumps(body, indent=1), encoding="utf-8")
    (OUT_DIR / "contacts-showcase.meta.json").write_text(json.dumps({
        "canvas_view_id": VIEW_ID,
        "module": {"id": MODULE_ID, "api_name": "Contacts"},
        "layout": {"id": LAYOUT_ID},
        "org_id": "647376701",
        "generated_by": "src/build_contacts_showcase.py",
    }, indent=1), encoding="utf-8")

    n = [0]

    def count(x):
        if isinstance(x, dict):
            n[0] += 1
            for c in (x.get("children") or []):
                count(c)
    count(body["canvas_view"][0])

    print(f"Built {out.relative_to(PROJECT_ROOT)}")
    print(f"  nodes: {n[0]}")

    errors, warnings = validate(body)
    print(f"  validation: {len(errors)} errors, {len(warnings)} warnings")
    for e in errors[:20]:
        print(f"    ERROR {e}")
    for w in warnings[:10]:
        print(f"    WARN  {w}")
    if errors:
        return 1

    if "--deploy" not in sys.argv:
        print(f"\nNot deployed. Re-run with --deploy to PUT to {VIEW_ID}.")
        return 0

    from datetime import datetime

    from zoho_auth import ZohoAuth
    from zoho_canvas import CanvasApiError, CanvasClient

    client = CanvasClient(ZohoAuth.from_env())
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    rb = PROJECT_ROOT / "reference" / "captures" / f"rollback-{VIEW_ID}-{stamp}.json"
    rb.write_text(json.dumps(client.get_view(VIEW_ID), indent=1), encoding="utf-8")
    print(f"\nRollback: reference/captures/{rb.name}")

    try:
        resp = client.put_view(VIEW_ID, body, i_understand_this_is_live=True)
    except CanvasApiError as exc:
        print(f"PUT FAILED: {exc}")
        return 1

    cv = resp.get("canvas_view", [{}])[0]
    print(f"PUT  code={cv.get('code')} status={cv.get('status')}")
    print(f"     uniqueids returned: {len(cv.get('details', {}).get('children', []))}")

    after = client.get_view(VIEW_ID)["canvas_view"][0]
    m = [0]
    rls = []

    def c2(x):
        if isinstance(x, dict):
            m[0] += 1
            if x.get("type") == "relatedlist":
                rls.append(x.get("id"))
            for ch in (x.get("children") or []):
                c2(ch)
    c2(after)
    print(f"     live nodes: {m[0]}  relatedlist nodes: {len(rls)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
