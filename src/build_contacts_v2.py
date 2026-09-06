"""Build the approved design v2 for the Contacts canvas.

Direct translation of output/camco-647376701/Contacts/contacts-design-v2.html.
Coordinates match the mockup 1:1 (1100 px wide, absolute positioning).

Four custom composite tabs (Overview, Engagement, Delivery, AI Insights) then a
related-list tab for each related module on Contacts.

    python src/build_contacts_v2.py            # build + validate
    python src/build_contacts_v2.py --deploy   # also PUT to canvas 3
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from base_template import (BRIGHT, F_BOLD, F_REG, F_SEMI, action, banner,  # noqa: E402
                           chip, field, field_table, kpi_tile, position,
                           related_list, related_list_card, root, separator,
                           tab_strip, text_block, timeline, titled_card)
from validate import validate  # noqa: E402

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = PROJECT_ROOT / "output" / "camco-647376701" / "Contacts"

VIEW_ID = "2582206000076641025"
MODULE_ID = "2582206000000002179"
LAYOUT_ID = "2582206000000091033"
T = BRIGHT

W = 1100
BANNER_H = 154
TABS_H = 44
BODY_TOP = BANNER_H + TABS_H          # 198, matches the mockup

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

# Every related list on Contacts, from the live settings/related_lists API.
RL = {
    "notes":        "2582206000000003801",
    "cadences":     "2582206000053584109",
    "chrono":       "2582206000050213037",
    "open_meet":    "2582206000025002869",
    "open_tasks":   "2582206000025002867",
    "emails":       "2582206000000015214",
    "attachments":  "2582206000000003799",
    "invited":      "2582206000000062003",
    "transcripts":  "2582206000015911007",
    "chrono_hist":  "2582206000050213063",
    "closed_meet":  "2582206000025002875",
    "closed_tasks": "2582206000025002873",
    "rel_account":  "2582206000006579837",
    "proposals":    "2582206000008479131",
    "visits":       "2582206000012628057",
    "drive":        "2582206000035599501",
    "locking":      "2582206000033362132",
    "projects":     "2582206000056715127",
    "resources":    "2582206000057036296",
    "contacts":     "2582206000066075427",
    "buyers":       "2582206000066075610",
    "linked_inq":   "2582206000072748167",
    "referred_by":  "2582206000072748178",
    "ai_extract":   "2582206000073572031",
    "ai_items":     "2582206000073543022",
    "timeline":     "timeline",
}

# Related-list tabs, in strip order, each with its own accent + icon.
RL_TABS = [
    ("Notes",                RL["notes"],        "icon-Icon_notes",    "indigo"),
    ("Open Tasks",           RL["open_tasks"],   "icon-Icon_Task",     "sky"),
    ("Open Meetings",        RL["open_meet"],    "icon-Icon_Meeting",  "rose"),
    ("Emails",               RL["emails"],       "icon-Icon_Mail",     "amber"),
    ("Proposals",            RL["proposals"],    "icon-Icon_Quotes",   "violet"),
    ("Closed Tasks",         RL["closed_tasks"], "icon-Icon_Task",     "teal"),
    ("Closed Meetings",      RL["closed_meet"],  "icon-Icon_Meeting",  "emerald"),
    ("Invited Meetings",     RL["invited"],      "icon-Icon_Calendar", "indigo"),
    ("Cadences",             RL["cadences"],     "icon-Icon_Cadence",  "emerald"),
    ("Attachments",          RL["attachments"],  "icon-Icon_attach",   "sky"),
    ("Resources",            RL["resources"],    "icon-Icon_document", "teal"),
    ("Zoho Projects",        RL["projects"],     "icon-Icon_Project",  "violet"),
    ("Drive Files",          RL["drive"],        "icon-Icon_folder",   "amber"),
    ("Transcripts",          RL["transcripts"],  "icon-Icon_document", "sky"),
    ("AI Meeting Extractions", RL["ai_extract"], "icon-Icon_Zia",      "indigo"),
    ("AI Meeting Items",     RL["ai_items"],     "icon-Icon_Zia",      "emerald"),
    ("Related Account",      RL["rel_account"],  "icon-Icon_Accounts", "sky"),
    ("Related Buyers",       RL["buyers"],       "icon-Icon_Contacts", "rose"),
    ("Linked Contact",       RL["linked_inq"],   "icon-Icon_Link",     "violet"),
    ("Referred By",          RL["referred_by"],  "icon-Icon_Link",     "teal"),
    ("Chronological View",   RL["chrono"],       "icon-Icon_History",  "indigo"),
    ("SalesIQ Visits",       RL["visits"],       "icon-Icon_website",  "amber"),
    ("Timeline",             RL["timeline"],     "icon-Icon_History",  "sky"),
]


def rows_card(x, y, w, h, title, icon, accent, rows, *, count=None, top=50):
    """Card whose body is a label/value Table Layout."""
    return titled_card(x, y, w, h, title, tokens=T, icon=icon,
                       accent=T[accent], count=count,
                       body=[field_table(18, top, w - 36, rows, tokens=T)])


def rl_card(x, y, w, h, title, rl_id, icon, accent, count=None):
    """Card wrapping a live related list."""
    return titled_card(x, y, w, h, title, tokens=T, icon=icon,
                       accent=T[accent], count=count,
                       body=[related_list(rl_id, 18, 50, w - 36, h - 66,
                                          recordcount=count or 10)])


# ---------------------------------------------------------------- panes

def pane_overview() -> list:
    return [
        kpi_tile(22, 18, 256, 76, "Lifecycle", T["indigo"], tokens=T,
                 value_field=F["lead_src"], detail="Lead source"),
        kpi_tile(290, 18, 256, 76, "Contact Owner", T["sky"], tokens=T,
                 value_field=F["owner"]),
        kpi_tile(558, 18, 256, 76, "Last Activity", T["emerald"], tokens=T,
                 value_field=F["last_act"]),
        kpi_tile(826, 18, 252, 76, "Modified", T["amber"], tokens=T,
                 value_field=F["modified"]),

        rows_card(22, 120, 528, 300, "About This Contact",
                  "icon-Icon_Customerprofile", "indigo",
                  [F["email"], F["phone"], F["mobile"], F["account"],
                   F["reports_to"], F["lead_src"], F["opt_out"]]),
        rows_card(566, 120, 512, 300, "Mailing Address", "icon-Icon_location",
                  "teal",
                  [F["street"], F["city"], F["state"], F["zip"], F["country"]]),

        titled_card(22, 440, 528, 206, "Description & Tags", tokens=T,
                    icon="icon-Icon_notes", accent=T["emerald"],
                    body=[field(*F["desc"], 18, 50, 492, 68, tokens=T,
                                css="zcanvas-field zctextarea"),
                          field(*F["tag"], 18, 126, 492, 26, tokens=T)]),
        rows_card(566, 440, 512, 206, "System Information", "icon-Icon_Setup",
                  "violet",
                  [F["created_by"], F["created"], F["modified_by"],
                   F["last_act"]]),

        rl_card(22, 666, 528, 248, "Open Tasks", RL["open_tasks"],
                "icon-Icon_Task", "sky", count=5),
        rl_card(566, 666, 512, 248, "Open Meetings", RL["open_meet"],
                "icon-Icon_Meeting", "rose", count=5),
        rl_card(22, 934, 528, 222, "Recent Emails", RL["emails"],
                "icon-Icon_Mail", "amber", count=5),
        rl_card(566, 934, 512, 222, "Cadences", RL["cadences"],
                "icon-Icon_Cadence", "indigo", count=5),
    ]


def pane_engagement() -> list:
    return [
        kpi_tile(22, 18, 344, 92, "Emails Exchanged", T["sky"], tokens=T,
                 value_text="24", detail="12 sent  ·  12 received", big=True),
        kpi_tile(378, 18, 344, 92, "Meetings Held", T["rose"], tokens=T,
                 value_text="7", detail="Last Aug 21", big=True),
        kpi_tile(734, 18, 344, 92, "Response Rate", T["emerald"], tokens=T,
                 value_text="92%", detail="Across all outreach", big=True),

        rl_card(22, 136, 700, 360, "Email History", RL["emails"],
                "icon-Icon_Mail", "sky", count=10),

        titled_card(738, 136, 340, 360, "Activity Timeline", tokens=T,
                    icon="icon-Icon_History", accent=T["indigo"],
                    body=[timeline(24, 56, 292, [
                        ("Email replied", "Aug 28 · Contract redlines"),
                        ("Meeting held", "Aug 21 · Technical review"),
                        ("Proposal sent", "Aug 15 · Phase 2"),
                        ("Cadence started", "Aug 01 · Renewal nurture"),
                        ("Contact created", "Mar 23 · Infotelligent"),
                    ], tokens=T, accent=T["indigo"], step=46)]),

        rl_card(22, 516, 1056, 330, "All Meetings", RL["closed_meet"],
                "icon-Icon_Meeting", "rose", count=10),
    ]


def pane_delivery() -> list:
    return [
        rl_card(22, 18, 528, 300, "Proposals", RL["proposals"],
                "icon-Icon_Quotes", "violet", count=8),
        rl_card(566, 18, 512, 300, "Zoho Projects", RL["projects"],
                "icon-Icon_Project", "teal", count=8),
        rl_card(22, 338, 528, 250, "Resources", RL["resources"],
                "icon-Icon_document", "sky", count=8),
        rl_card(566, 338, 512, 250, "Checklists", RL["attachments"],
                "icon-Icon_attach", "emerald", count=8),
        rl_card(22, 608, 1056, 190, "Drive Files", RL["drive"],
                "icon-Icon_folder", "amber", count=8),
    ]


def pane_ai() -> list:
    summary = ("Static preview copy. Canvas static text is literal, so this "
               "reads the same on every record until it is wired to a field.")
    return [
        titled_card(22, 18, 1056, 150, "AI Summary", tokens=T,
                    icon="icon-Icon_Zia", accent=T["violet"],
                    body=[text_block(18, 52, 1020, 60, summary, tokens=T,
                                     size="13.5px", colour=T["text_2"])]),
        rl_card(22, 188, 528, 290, "AI Meeting Extractions", RL["ai_extract"],
                "icon-Icon_Zia", "indigo", count=8),
        rl_card(566, 188, 512, 290, "AI Meeting Items", RL["ai_items"],
                "icon-Icon_Zia", "emerald", count=8),
        rl_card(22, 498, 1056, 200, "Transcripts", RL["transcripts"],
                "icon-Icon_document", "sky", count=8),
    ]


def build() -> dict:
    view = root("Contacts Canvas v2", MODULE_ID, "Contacts", LAYOUT_ID,
                W, BODY_TOP + 1210, tokens=T)

    b = banner(0, 0, W, BANNER_H, tokens=T)
    b["children"] = [
        action("back", 22, 16, 34, 30, tokens=T),
        field(*F["image"], 30, 32, 80, 80, tokens=T,
              css="zcbdrbox zcanvas-field"),
        field(*F["full_name"], 126, 36, 460, 32, tokens=T),
        field(*F["title"], 126, 69, 460, 20, tokens=T),
        field(*F["account"], 126, 90, 460, 20, tokens=T,
              css="zcanvas-field zcclinkvalue"),
        action("send_mail", 736, 42, 120, 34, tokens=T, primary=True),
        separator(862, 52),
        action("edit", 876, 42, 86, 34, tokens=T),
        separator(968, 52),
        action("morebutton", 982, 42, 40, 34, tokens=T),
        action("navigate", 1032, 42, 40, 34, tokens=T),
    ]
    view["children"].append(b)

    tabs = [
        {"name": "Overview",    "children": pane_overview()},
        {"name": "Engagement",  "children": pane_engagement()},
        {"name": "Delivery",    "children": pane_delivery()},
        {"name": "AI Insights", "children": pane_ai()},
    ]
    for label, rl_id, icon, accent in RL_TABS:
        tabs.append({
            "name": label,
            "relatedlist_id": rl_id,
            "children": [rl_card(22, 24, 1056, 640, label, rl_id, icon,
                                 accent, count=10)],
        })
    tabs.append({"name": "All Fields", "children": []})

    view["children"].append(
        tab_strip(0, BANNER_H, W, 1254, tabs, tokens=T, depth=4))
    return {"canvas_view": [view]}


def main() -> int:
    body = build()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUT_DIR / "contacts-v2.json"
    out.write_text(json.dumps(body, indent=1), encoding="utf-8")
    (OUT_DIR / "contacts-v2.meta.json").write_text(json.dumps({
        "canvas_view_id": VIEW_ID,
        "module": {"id": MODULE_ID, "api_name": "Contacts"},
        "layout": {"id": LAYOUT_ID},
        "org_id": "647376701",
        "design_source": "output/camco-647376701/Contacts/contacts-design-v2.html",
        "generated_by": "src/build_contacts_v2.py",
    }, indent=1), encoding="utf-8")

    n, rls, tabs_n = [0], [0], [0]

    def count(x):
        if isinstance(x, dict):
            n[0] += 1
            if x.get("type") == "relatedlist":
                rls[0] += 1
            if x.get("ui", {}).get("value", {}).get("name"):
                tabs_n[0] += 1
            for c in (x.get("children") or []):
                count(c)
    count(body["canvas_view"][0])

    print(f"Built {out.relative_to(PROJECT_ROOT)}")
    print(f"  nodes {n[0]}   tabs {tabs_n[0]}   related lists {rls[0]}")

    errors, warnings = validate(body)
    print(f"  validation: {len(errors)} errors, {len(warnings)} warnings")
    for e in errors[:20]:
        print(f"    ERROR {e}")
    for w in warnings[:8]:
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

    after = client.get_view(VIEW_ID)["canvas_view"][0]
    m, arl, names = [0], [0], []

    def c2(x):
        if isinstance(x, dict):
            m[0] += 1
            if x.get("type") == "relatedlist":
                arl[0] += 1
            nm = x.get("ui", {}).get("value", {}).get("name")
            if nm:
                names.append(nm)
            for ch in (x.get("children") or []):
                c2(ch)
    c2(after)
    print(f"     live nodes {m[0]}   related lists {arl[0]}   tabs {len(names)}")
    print(f"     name {after.get('name')!r}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
