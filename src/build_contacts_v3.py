"""Contacts canvas, design v2, rebuilt from observed shapes only (v3 payload).

Every node comes from canvas_shapes.py, which mirrors what the Zoho editor
emits. Icon names are checked against the icon catalog at build time.

    python src/build_contacts_v3.py            # build + validate
    python src/build_contacts_v3.py --deploy   # PUT to canvas 3, then STOP and
                                               # open it in the editor before
                                               # calling it working
"""

from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from canvas_shapes import (BRIGHT, F_SEMI, action, all_fields_tab, banner, button_group,  # noqa: E402
                           card, chip, field, field_table, heading, icon, line,
                           related_list_card, root, tab_strip, text)
from validate import validate  # noqa: E402

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = PROJECT_ROOT / "output" / "camco-647376701" / "Contacts"
REFERENCE = PROJECT_ROOT / "reference" / "captures" / "contacts-canvas-template-3.payload.json"

VIEW_ID = "2582206000076641025"
MODULE_ID = "2582206000000002179"
LAYOUT_ID = "2582206000000091033"
T = BRIGHT

W, BANNER_H, TABS_H, GAP = 1100, 154, 44, 22

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

RL = {
    "notes": "2582206000000003801", "cadences": "2582206000053584109",
    "chrono": "2582206000050213037", "open_meet": "2582206000025002869",
    "open_tasks": "2582206000025002867", "emails": "2582206000000015214",
    "attachments": "2582206000000003799", "invited": "2582206000000062003",
    "transcripts": "2582206000015911007", "closed_meet": "2582206000025002875",
    "closed_tasks": "2582206000025002873", "rel_account": "2582206000006579837",
    "proposals": "2582206000008479131", "visits": "2582206000012628057",
    "drive": "2582206000035599501", "projects": "2582206000056715127",
    "resources": "2582206000057036296", "buyers": "2582206000066075610",
    "linked_inq": "2582206000072748167", "referred_by": "2582206000072748178",
    "ai_extract": "2582206000073572031", "ai_items": "2582206000073543022",
    "timeline": "timeline",
}

# Every icon here is checked against the 231-name catalog at build time.
IC = {
    "profile": "icon-Icon_Customerprofile", "location": "icon-Icon_Location",
    "notes": "icon-Icon_Notes", "info": "icon-Icon_Info", "task": "icon-Icon_task",
    "meeting": "icon-Icon_Meeting", "mail": "icon-Icon_Mail", "status": "icon-Icon_Status",
    "quotes": "icon-Icon_Quotes", "files": "icon-Icon_Files", "folder": "icon-Icon_Folder",
    "attach": "icon-Icon_Attachment", "contacts": "icon-Icon_Contacts",
    "accounts": "icon-Icon_Accounts", "zia": "icon-Icon_zia", "clock": "icon-Icon_Clock",
    "calendar": "icon-Icon_Calender", "globe": "icon-Icon_globe", "docs": "icon-Icon_Documents",
    "card": "icon-Icon_Datacard", "people": "icon-Icon_people", "tag": "icon-Icon_Tag",
}

RL_TABS = [
    ("Notes",              RL["notes"],        IC["notes"],    "indigo"),
    ("Closed Tasks",       RL["closed_tasks"], IC["task"],     "teal"),
    ("Attachments",        RL["attachments"],  IC["attach"],   "sky"),
    ("Related Account",    RL["rel_account"],  IC["accounts"], "sky"),
    ("Related Buyers",     RL["buyers"],       IC["contacts"], "rose"),
    ("Linked Contact",     RL["linked_inq"],   IC["people"],   "violet"),
    ("Referred By",        RL["referred_by"],  IC["people"],   "teal"),
    ("Chronological View", RL["chrono"],       IC["clock"],    "indigo"),
    ("SalesIQ Visits",     RL["visits"],       IC["globe"],    "amber"),
    ("Timeline",           RL["timeline"],     IC["clock"],    "sky"),
]


def titled_card(x, y, w, h, title, icon_name, accent, body):
    c = card(x, y, w, h, tokens=T)
    c["children"] = [icon(18, 15, icon_name, size=22, colour=T[accent]),
                     heading(50, 17, w - 90, 22, title, tokens=T), *body]
    return c


def rows_card(x, y, w, h, title, icon_name, accent, rows):
    return titled_card(x, y, w, h, title, icon_name, accent,
                       [field_table(18, 52, w - 36, rows, tokens=T)])


def kpi(x, y, w, h, fid_dt, accent):
    """Tile with a coloured left edge; the field's own label is the caption."""
    c = card(x, y, w, h, tokens=T)
    c["ui"]["value"]["style"]["default"]["border_left"] = f"4px solid {T[accent]}"
    c["children"] = [field(*fid_dt, 14, 12, w - 30, 48, tokens=T,
                           label_cls="zcanvasuppercase",
                           label_style={"font_size": T["font_micro"], "color": T["text_muted"],
                                        "font_family": F_SEMI},
                           value_style={"font_size": "17px", "font_family": F_SEMI,
                                        "color": T["text"]})]
    return c


def rl_card(x, y, w, h, title, rl_id, icon_name, accent, count=10):
    return related_list_card(rl_id, title, x, y, w, h, tokens=T, recordcount=count,
                             icon_name=icon_name, accent=T[accent])


# ----------------------------------------------------------------- panes

def pane_overview():
    half = (W - GAP * 3) // 2
    q = (W - GAP * 5) // 4
    return [
        kpi(GAP, 18, q, 76, F["lead_src"], "indigo"),
        kpi(GAP * 2 + q, 18, q, 76, F["owner"], "sky"),
        kpi(GAP * 3 + q * 2, 18, q, 76, F["last_act"], "emerald"),
        kpi(GAP * 4 + q * 3, 18, q, 76, F["modified"], "amber"),

        rows_card(GAP, 120, half, 300, "About This Contact", IC["profile"], "indigo",
                  [F["email"], F["phone"], F["mobile"], F["account"],
                   F["reports_to"], F["lead_src"], F["opt_out"]]),
        rows_card(GAP * 2 + half, 120, half, 300, "Mailing Address", IC["location"], "teal",
                  [F["street"], F["city"], F["state"], F["zip"], F["country"]]),

        titled_card(GAP, 440, half, 206, "Description & Tags", IC["notes"], "emerald",
                    [field(*F["desc"], 18, 52, half - 36, 90, tokens=T,
                           cls="zcanvas-field zctextarea"),
                     field(*F["tag"], 18, 150, half - 36, 30, tokens=T)]),
        rows_card(GAP * 2 + half, 440, half, 206, "System Information", IC["info"], "violet",
                  [F["created_by"], F["created"], F["modified_by"], F["last_act"]]),

        rl_card(GAP, 666, half, 248, "Open Tasks", RL["open_tasks"], IC["task"], "sky", 5),
        rl_card(GAP * 2 + half, 666, half, 248, "Open Meetings", RL["open_meet"], IC["meeting"], "rose", 5),
        rl_card(GAP, 934, half, 222, "Recent Emails", RL["emails"], IC["mail"], "amber", 5),
        rl_card(GAP * 2 + half, 934, half, 222, "Cadences", RL["cadences"], IC["status"], "indigo", 5),
    ]


def pane_engagement():
    third = (W - GAP * 4) // 3
    stats = [("24", "Emails exchanged", "sky"), ("7", "Meetings held", "rose"),
             ("92%", "Response rate", "emerald")]
    tiles = []
    for i, (big, label, accent) in enumerate(stats):
        c = card(GAP + i * (third + GAP), 18, third, 92, tokens=T)
        c["ui"]["value"]["style"]["default"]["border_left"] = f"4px solid {T[accent]}"
        c["children"] = [
            text(14, 12, third - 30, 16, label.upper(), autoheight=False,
                 style={"padding": "0px", "background_color": "transparent",
                        "font_size": T["font_micro"], "font_family": F_SEMI,
                        "color": T["text_muted"]}),
            text(14, 32, third - 30, 34, big, autoheight=False,
                 style={"padding": "0px", "background_color": "transparent",
                        "font_size": "26px", "font_family": "b", "color": T["text"]}),
        ]
        tiles.append(c)

    tl = card(738, 136, 340, 360, tokens=T)
    entries = [("Email replied", "Aug 28 · Contract redlines"),
               ("Meeting held", "Aug 21 · Technical review"),
               ("Proposal sent", "Aug 15 · Phase 2"),
               ("Cadence started", "Aug 01 · Renewal nurture"),
               ("Contact created", "Mar 23 · Infotelligent")]
    tl_children = [icon(18, 15, IC["clock"], size=22, colour=T["indigo"]),
                   heading(50, 17, 250, 22, "Activity Timeline", tokens=T)]
    for i, (head, meta) in enumerate(entries):
        y = 56 + i * 56
        tl_children += [
            text(18, y, 300, 17, head, autoheight=False,
                 style={"padding": "0px", "background_color": "transparent",
                        "font_size": "12.5px", "font_family": F_SEMI, "color": T["text"]}),
            text(18, y + 18, 300, 16, meta, autoheight=False,
                 style={"padding": "0px", "background_color": "transparent",
                        "font_size": "11.5px", "color": T["text_muted"]}),
        ]
        if i < len(entries) - 1:
            tl_children.append(line(18, y + 44, 300))
    tl["children"] = tl_children

    return tiles + [
        rl_card(GAP, 136, 700, 360, "Closed Meetings", RL["closed_meet"], IC["meeting"], "rose"),
        tl,
        rl_card(GAP, 516, 1056, 330, "Invited Meetings", RL["invited"], IC["calendar"], "emerald"),
    ]


def pane_delivery():
    half = (W - GAP * 3) // 2
    return [
        rl_card(GAP, 18, half, 300, "Proposals", RL["proposals"], IC["quotes"], "violet", 8),
        rl_card(GAP * 2 + half, 18, half, 300, "Zoho Projects", RL["projects"], IC["files"], "teal", 8),
        rl_card(GAP, 338, half, 250, "Resources", RL["resources"], IC["docs"], "sky", 8),
        rl_card(GAP * 2 + half, 338, half, 250, "Drive Files", RL["drive"], IC["folder"], "amber", 8),
    ]


def pane_ai():
    half = (W - GAP * 3) // 2
    summary = card(GAP, 18, 1056, 150, tokens=T)
    summary["children"] = [
        icon(18, 15, IC["zia"], size=22, colour=T["violet"]),
        heading(50, 17, 400, 22, "AI Summary", tokens=T),
        text(18, 52, 1020, 60,
             "Static preview copy. Canvas static text is literal, so this reads the same on "
             "every record until it is wired to a field.",
             style={"padding": "0px", "background_color": "transparent",
                    "font_size": "13.5px", "color": T["text_2"]}),
        chip(18, 118, 110, 22, "PREVIEW", bg="rgba(224, 231, 255, 1)", colour="rgba(55, 48, 163, 1)"),
    ]
    return [
        summary,
        rl_card(GAP, 188, half, 290, "AI Meeting Extractions", RL["ai_extract"], IC["zia"], "indigo", 8),
        rl_card(GAP * 2 + half, 188, half, 290, "AI Meeting Items", RL["ai_items"], IC["zia"], "emerald", 8),
        rl_card(GAP, 498, 1056, 200, "Transcripts", RL["transcripts"], IC["docs"], "sky", 8),
    ]


def build() -> dict:
    view = root("Contacts Canvas v3", MODULE_ID, "Contacts", LAYOUT_ID, W, 1420, tokens=T)

    b = banner(0, 0, W, BANNER_H, tokens=T)
    white = {"border": "none", "background_color": T["text_invert"], "color": T["indigo"],
             "border_radius": "10px", "font_family": F_SEMI}
    ghost = {"border": "1px solid rgba(255, 255, 255, 0.42)",
             "background_color": "rgba(255, 255, 255, 0.18)", "color": T["text_invert"],
             "border_radius": "10px"}
    b["children"] = [
        action("back", 22, 16, 34, 30, style={"border": "none", "background_color": "rgba(255,255,255,0)",
                                             "color": T["text_invert"]}),
        field(*F["image"], 30, 32, 80, 80, tokens=T, cls="zcbdrbox zcanvas-field"),
        field(*F["full_name"], 126, 36, 460, 32, tokens=T, stacked=False,
              value_style={"font_size": "23px", "font_family": F_SEMI, "color": T["text_invert"]},
              label_style={"font_size": "0px", "color": "rgba(255,255,255,0)"}),
        field(*F["title"], 126, 70, 460, 20, tokens=T, stacked=False,
              value_style={"font_size": "13px", "color": "rgba(255, 255, 255, 0.86)"},
              label_style={"font_size": "0px", "color": "rgba(255,255,255,0)"}),
        field(*F["account"], 126, 92, 460, 20, tokens=T, cls="zcanvas-field zcclinkvalue", stacked=False,
              value_style={"font_size": "13px", "font_family": F_SEMI, "color": T["text_invert"]},
              label_style={"font_size": "0px", "color": "rgba(255,255,255,0)"}),
        button_group(736, 42, 336, [
            {"id": "send_mail", "w": 120, "style": white,
             "hover": {"background_color": "rgba(238, 242, 255, 1)", "color": T["indigo"]}},
            {"id": "edit", "w": 86, "style": ghost},
            {"id": "morebutton", "w": 40, "style": ghost},
        ]),
        action("navigate", 1032, 42, 40, 34, style=ghost),
    ]
    view["children"].append(b)

    tabs = [{"name": "Overview", "children": pane_overview()},
            {"name": "Engagement", "children": pane_engagement()},
            {"name": "Delivery", "children": pane_delivery()},
            {"name": "AI Insights", "children": pane_ai()}]
    for label, rl_id, ic, accent in RL_TABS:
        tabs.append({"name": label, "relatedlist_id": rl_id,
                     "children": [rl_card(GAP, 24, W - GAP * 2, 640, label, rl_id, ic, accent)]})

    strip = tab_strip(0, BANNER_H, W, 1254, tabs, tokens=T)
    af = all_fields_tab(REFERENCE)
    body_h = 1254 - 48
    af["ui"]["value"]["position"].update({
        "start_x": 0, "start_y": body_h // 2, "end_x": W, "width": W, "height": body_h // 2,
        "depth": 1, "order": len(strip["children"])})
    strip["children"].append(af)
    view["children"].append(strip)
    return {"canvas_view": [view]}


def main() -> int:
    body = build()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUT_DIR / "contacts-v3.json"
    out.write_text(json.dumps(body, indent=1), encoding="utf-8")
    (OUT_DIR / "contacts-v3.meta.json").write_text(json.dumps({
        "canvas_view_id": VIEW_ID, "module": {"id": MODULE_ID, "api_name": "Contacts"},
        "layout": {"id": LAYOUT_ID}, "org_id": "647376701",
        "design_source": "output/camco-647376701/Contacts/contacts-design-v2.html",
        "generated_by": "src/build_contacts_v3.py",
        "shapes": "src/canvas_shapes.py (observed shapes only)",
    }, indent=1), encoding="utf-8")

    n, rl, tabs = [0], [0], []

    def count(x):
        if isinstance(x, dict):
            n[0] += 1
            if x.get("type") == "relatedlist":
                rl[0] += 1
            nm = ((x.get("ui") or {}).get("value") or {}).get("name") if isinstance(x.get("ui"), dict) else None
            if nm:
                tabs.append(nm)
            for c in (x.get("children") or []):
                count(c)
    count(body["canvas_view"][0])
    print(f"Built {out.relative_to(PROJECT_ROOT)}: {n[0]} nodes, {len(tabs)} tabs, {rl[0]} related lists")

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
    rb = PROJECT_ROOT / "reference" / "captures" / f"rollback-{VIEW_ID}-{stamp}.json"
    rb.write_text(json.dumps(client.get_view(VIEW_ID), indent=1), encoding="utf-8")
    print(f"\nRollback: reference/captures/{rb.name}")
    try:
        resp = client.put_view(VIEW_ID, body, i_understand_this_is_live=True)
    except CanvasApiError as exc:
        print(f"PUT FAILED: {exc}")
        return 1
    cv = resp.get("canvas_view", [{}])[0]
    print(f"PUT {cv.get('code')} {cv.get('status')}  uniqueids returned: "
          f"{len(cv.get('details', {}).get('children', []))}")
    print("\nNOT VERIFIED until opened in the editor:")
    print(f"  https://crm.zoho.com/crm/org647376701/settings/modules/Contacts/layouts/{LAYOUT_ID}"
          f"/canvas/{VIEW_ID}/edit?feature=DetailView")
    print(f"  restore: python src/restore.py reference/captures/{rb.name} --execute")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
