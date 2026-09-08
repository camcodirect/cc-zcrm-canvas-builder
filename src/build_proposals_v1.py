"""Proposals canvas v1 for Camco (design: output/camco-647376701/Proposals/proposals-v1.preview.html).

Every field is resolved by api_name against the live Standard layout at build
time; nothing numeric is hardcoded except the canvas view id, which is the
deploy target. Related lists are resolved by display label. Every node comes
from canvas_shapes.py (observed shapes only).

    python src/build_proposals_v1.py            # profile live, build, validate, audit
    python src/build_proposals_v1.py --deploy   # + rollback GET, PUT, re-GET; then
                                                #   open it in the editor before
                                                #   calling it working
"""

from __future__ import annotations

import json
import sys
import urllib.parse
import urllib.request
import uuid
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from canvas_shapes import (BRIGHT, F_SEMI, banner, button_group, card, field, field_table,  # noqa: E402
                           heading, icon, lookup_all_fields_tab, related_list_card, root,
                           section, system_list_card, tab_strip, text)
from validate import validate  # noqa: E402
from zoho_auth import ZohoAuth  # noqa: E402

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = PROJECT_ROOT / "output" / "camco-647376701" / "Proposals"
REFERENCE_DIRS = [PROJECT_ROOT / "reference" / "captures", PROJECT_ROOT / "reference" / "ui-capture"]

ORG_ID = "647376701"
MODULE = "Proposals"
LAYOUT_NAME = "Standard"
VIEW_ID = "2582206000076741077"          # deploy target, the only hardcoded id
CANVAS_NAME = "Proposals Canvas v1"

T = dict(BRIGHT)
W, BANNER_H, GAP = 1100, 206, 22

# CRM data_type -> canvas datatype, derived by joining every field node in the
# 33 Zoho-authored captures against live layout metadata (2026-09-07).
DATATYPE = {
    "text": "text", "textarea": "text-area", "email": "email", "phone": "phone",
    "website": "website", "picklist": "picklist", "multiselectpicklist": "picklist",
    "boolean": "boolean", "date": "date", "datetime": "date-time",
    "integer": "number", "double": "number", "currency": "number", "bigint": "number",
    "formula": "text", "lookup": "lookup", "ownerlookup": "user",
    "multiuserlookup": "multiselectuser", "multiselectlookup": "multiselectlookup",
    "profileimage": "profileimage",
}
DATATYPE_BY_API = {"Tag": "tag"}     # Tag is data_type text in the layout, `tag` in the canvas

IC = {
    "info": "icon-Icon_Info", "dollar": "icon-Icon_Dollar", "docs": "icon-Icon_Documents",
    "notes": "icon-Icon_Notes", "status": "icon-Icon_Status", "outline": "icon-Icon_Info_outline",
    "tag": "icon-Icon_Tag", "task": "icon-Icon_task", "meeting": "icon-Icon_Meeting",
    "clock": "icon-Icon_Clock", "money": "icon-Icon_Money", "calendar": "icon-Icon_Calender",
    "profile": "icon-Icon_Customerprofile", "attach": "icon-Icon_Attachment", "mail": "icon-Icon_Mail",
}


# ----------------------------------------------------------------- profile

class Profile:
    """Live module profile: never cached to disk (CLAUDE.md, Step 0)."""

    def __init__(self, auth: ZohoAuth):
        self.auth = auth
        mods = self._get("/crm/v8/settings/modules")["modules"]
        mod = next(m for m in mods if m["api_name"] == MODULE)
        self.module_id = mod["id"]
        layouts = self._get("/crm/v8/settings/layouts", {"module": MODULE})["layouts"]
        lay = next(L for L in layouts if L["name"] == LAYOUT_NAME)
        self.layout_id = lay["id"]
        self.fields: dict[str, dict] = {}
        for s in lay["sections"]:
            for f in s["fields"]:
                self.fields[f["api_name"]] = f
        rls = self._get("/crm/v8/settings/related_lists", {"module": MODULE})["related_lists"]
        self.related: dict[str, dict] = {r["display_label"]: r for r in rls}
        accounts = next(m for m in mods if m["api_name"] == "Accounts")
        self.accounts_module_id = accounts["id"]

    def _get(self, path, params=None):
        url = f"{self.auth.api_host}{path}" + (("?" + urllib.parse.urlencode(params)) if params else "")
        req = urllib.request.Request(url, headers=self.auth.auth_header())
        with urllib.request.urlopen(req, timeout=60) as r:
            raw = r.read().decode("utf-8")
        return json.loads(raw) if raw.strip() else {}

    def f(self, api_name: str) -> tuple[str, str]:
        fd = self.fields[api_name]
        dt = DATATYPE_BY_API.get(api_name) or DATATYPE[fd["data_type"]]
        return fd["id"], dt

    def rl(self, label: str) -> str:
        return self.related[label]["id"]


# ----------------------------------------------------------------- helpers

def titled_card(x, y, w, h, title, icon_name, accent, body):
    c = card(x, y, w, h, tokens=T)
    c["children"] = [icon(18, 15, icon_name, size=22, colour=T[accent]),
                     heading(50, 17, w - 90, 22, title, tokens=T), *body]
    return c


def rows_card(x, y, w, h, title, icon_name, accent, rows, *, label_pct=42.0, extra=()):
    return titled_card(x, y, w, h, title, icon_name, accent,
                       [field_table(18, 52, w - 36, rows, tokens=T, label_pct=label_pct), *extra])


def hint(x, y, w, value):
    return text(x, y, w, 34, value, style={"padding": "0px", "background_color": "transparent",
                                          "font_size": "12px", "color": T["text_muted"]})


def textarea(fid_dt, x, y, w, h):
    return field(*fid_dt, x, y, w, h, tokens=T, cls="zcanvas-field zctextarea",
                 label_cls="zcanvasuppercase",
                 label_style={"font_size": T["font_micro"], "font_family": F_SEMI, "color": T["text_muted"]},
                 value_style={"font_size": T["font_body"], "color": T["text_2"]})


def kpi(x, y, w, h, fid_dt, accent):
    c = card(x, y, w, h, tokens=T)
    c["ui"]["value"]["style"]["default"]["border_left"] = f"4px solid {T[accent]}"
    c["children"] = [field(*fid_dt, 14, 12, w - 30, 48, tokens=T, label_cls="zcanvasuppercase",
                           label_style={"font_size": T["font_micro"], "color": T["text_muted"],
                                        "font_family": F_SEMI},
                           value_style={"font_size": "17px", "font_family": F_SEMI, "color": T["text"]})]
    return c


def stat_tile(x, y, w, h, fid_dt, *, hero=False):
    """Header stat tile: a glass section holding one stacked field."""
    if hero:
        st = {"border": "1px solid rgba(255, 255, 255, 0.92)", "background_color": "rgba(255, 255, 255, 0.92)",
              "border_radius": T["radius_chip"], "box_shadow": "none"}
        label = {"font_size": T["font_micro"], "font_family": F_SEMI, "color": T["text_muted"]}
        value = {"font_size": "18px", "font_family": F_SEMI, "color": T["indigo"]}
    else:
        st = {"border": "1px solid rgba(255, 255, 255, 0.34)", "background_color": "rgba(255, 255, 255, 0.16)",
              "border_radius": T["radius_chip"], "box_shadow": "none"}
        label = {"font_size": T["font_micro"], "font_family": F_SEMI, "color": "rgba(255, 255, 255, 0.82)"}
        value = {"font_size": "15px", "font_family": F_SEMI, "color": T["text_invert"]}
    s = section(x, y, w, h, style=st)
    s["children"] = [field(*fid_dt, 14, 8, w - 28, 42, tokens=T, label_cls="zcanvasuppercase",
                           label_style=label, value_style=value)]
    return s


def rl_card(p: Profile, x, y, w, h, label, icon_name, accent, count=5, *, rl_id=None, title=None):
    return related_list_card(rl_id or p.rl(label), title or label, x, y, w, h, tokens=T,
                             recordcount=count, icon_name=icon_name, accent=T[accent])


# ------------------------------------------------------------------ header

def header(p: Profile) -> dict:
    b = banner(0, 0, W, BANNER_H, tokens=T)
    hidden = {"font_size": "0px", "color": "rgba(255,255,255,0)"}
    white = {"border": "none", "background_color": T["text_invert"], "color": T["indigo"],
             "border_radius": T["radius_button"], "font_family": F_SEMI}
    ghost = {"border": "1px solid rgba(255, 255, 255, 0.42)", "background_color": "rgba(255, 255, 255, 0.18)",
             "color": T["text_invert"], "border_radius": T["radius_button"]}
    b["children"] = [
        field(*p.f("Name"), 30, 42, 600, 34, tokens=T, stacked=False,
              value_style={"font_size": "24px", "font_family": F_SEMI, "color": T["text_invert"]},
              label_style=hidden),
        # Status pill: the picklist value styled like a button (34px, 3px radius).
        field(*p.f("Proposal_Status"), 644, 42, 140, 34, tokens=T, stacked=False,
              cls="zcanvas-field zc-ta-center",
              value_style={"background_color": "rgba(255, 255, 255, 0.92)", "color": "rgba(67, 56, 202, 1)",
                           "border_radius": T["radius_button"], "font_size": T["font_micro"],
                           "font_family": F_SEMI, "padding": "9px 14px 9px 14px"},
              label_style=hidden),
        button_group(794, 42, 276, [
            {"id": "mail_merge", "w": 130, "style": white,
             "hover": {"background_color": "rgba(238, 242, 255, 1)", "color": T["indigo"]}},
            {"id": "edit", "w": 86, "style": ghost},
            {"id": "morebutton", "w": 40, "style": ghost},
        ]),
        stat_tile(30, 134, 250, 58, p.f("Est_Total_Cost"), hero=True),
        stat_tile(292, 134, 185, 58, p.f("Billing_Method")),
        stat_tile(489, 134, 185, 58, p.f("Payment_Terms")),
        stat_tile(686, 134, 185, 58, p.f("Proposal_Date")),
        stat_tile(883, 134, 185, 58, p.f("Acceptance_Date")),
    ]
    return b


# ------------------------------------------------------------------- panes

THIRD, HALF = 337, 517          # (1100 - 4*22) // 3, (1100 - 3*22) // 2
X3 = (GAP, GAP * 2 + THIRD, GAP * 3 + THIRD * 2)       # 22, 381, 740
X2 = (GAP, GAP * 2 + HALF)                            # 22, 561


def pane_overview(p: Profile):
    f = p.f
    return [
        rows_card(X3[0], 18, THIRD, 310, "Proposal Details", IC["info"], "indigo",
                  [f("Related_Account"), f("Related_Contact"), f("Prepared_For"), f("Email_To"),
                   f("Company_Name"), f("DBA"), f("Proposal_Date"), f("Acceptance_Date")], label_pct=50),
        rows_card(X3[1], 18, THIRD, 310, "Billing & Delivery", IC["dollar"], "teal",
                  [f("Billing_Method"), f("Billable_Rate"), f("Payment_Terms"),
                   f("Billing_Timeline"), f("Delivery_Timeline")], label_pct=50,
                  extra=[hint(18, 216, THIRD - 36, "Pricing detail for each billing method is on the Pricing tab.")]),
        rows_card(X3[2], 18, THIRD, 310, "Signature & Invoicing", IC["docs"], "emerald",
                  [f("zsign_doc_id"), f("zsign_request_id"), f("zdoc_signed_datetime"),
                   f("zbooks_initial_invoice_id"), f("initial_invoice_sent")], label_pct=50,
                  extra=[hint(18, 216, THIRD - 36, "Workflow keys written by the Deluge automations. Read-only in practice.")]),

        titled_card(X3[0], 350, 696, 221, "Project Description", IC["notes"], "sky",
                    [textarea(f("Brief_Project_Description"), 18, 52, 696 - 36, 221 - 70)]),
        rows_card(X3[2], 350, THIRD, 221, "Proposal Controls", IC["status"], "violet",
                  [f("Send_Client_Intake"), f("Exclude_NDA"), f("Exclude_Price_Breakdown"),
                   f("Share_With_Frank"), f("Share_With")], label_pct=50),

        titled_card(X3[0], 593, 696, 192, "Special Terms", IC["outline"], "amber",
                    [textarea(f("Proposal_Specific_Notes"), 18, 52, 696 - 36, 192 - 70)]),
        rows_card(X3[2], 593, THIRD, 192, "Tags & Status", IC["tag"], "rose",
                  [f("Tag"), f("Record_Status__s"), f("Locked__s"), f("Currency")], label_pct=50),

        rl_card(p, X2[0], 807, HALF, 250, "Open Tasks", IC["task"], "sky"),
        rl_card(p, X2[1], 807, HALF, 250, "Open Meetings", IC["meeting"], "rose"),
    ]


def pane_pricing(p: Profile):
    f = p.f
    q = 247
    xs = (22, 291, 560, 829)
    fixed = titled_card(X2[1], 338, HALF, 230, "Fixed Pricing", IC["dollar"], "emerald",
                        [field_table(18, 52, HALF - 36, [f("Fixed_Price")], tokens=T),
                         textarea(f("Fixed_Pricing_Notes"), 18, 90, HALF - 36, 230 - 108)])
    return [
        kpi(xs[0], 18, q, 76, f("Billing_Method"), "indigo"),
        kpi(xs[1], 18, q, 76, f("Est_Total_Cost"), "emerald"),
        kpi(xs[2], 18, q, 76, f("Initial_Invoice_Amount"), "sky"),
        kpi(xs[3], 18, q, 76, f("Payment_Terms"), "amber"),
        rows_card(X2[0], 116, HALF, 200, "Hourly", IC["clock"], "indigo",
                  [f("Estimated_Project_Hours"), f("Billable_Rate"), f("Est_Total_Cost"),
                   f("Est_Total_Cost_override")]),
        rows_card(X2[1], 116, HALF, 200, "Hour Blocks", IC["money"], "sky",
                  [f("Initial_Block_Size"), f("Initial_Invoice_Amount"), f("Initial_Invoice_Amount_override")]),
        rows_card(X2[0], 338, HALF, 230, "Retainer", IC["calendar"], "violet",
                  [f("Fixed_Retainer_Amount"), f("Is_Recurring"), f("Max_Hour_Allocation"),
                   f("Billing_Frequency"), f("Retainer_Effective_Rate")]),
        fixed,
        hint(22, 586, 1056, "All four pricing blocks are always shown. Canvas has no per-record conditional "
                            "sections; only the block matching Billing Method will carry values."),
    ]


def pane_activity(p: Profile):
    return [
        rl_card(p, 22, 18, 1056, 420, "ChronologicalView", IC["clock"], "indigo", 10, title="Chronological View"),
        rl_card(p, X2[0], 460, HALF, 260, "Closed Tasks", IC["task"], "teal"),
        rl_card(p, X2[1], 460, HALF, 260, "Closed Meetings", IC["meeting"], "rose"),
    ]


def pane_record(p: Profile):
    f = p.f
    return [
        rows_card(X3[0], 18, THIRD, 250, "System Information", IC["info"], "violet",
                  [f("Created_By"), f("Created_Time"), f("Modified_By"), f("Modified_Time"),
                   f("Last_Activity_Time"), f("ID_String")], label_pct=50),
        rows_card(X3[1], 18, THIRD, 250, "Ownership & Sharing", IC["profile"], "indigo",
                  [f("Owner"), f("Share_With_Frank"), f("Share_With")], label_pct=50),
        rows_card(X3[2], 18, THIRD, 250, "Currency", IC["money"], "amber",
                  [f("Currency"), f("Exchange_Rate")], label_pct=50),
        rl_card(p, 22, 290, 1056, 250, "Locking Information", IC["status"], "rose"),
    ]


RL_TABS = [  # (display label as tab name, related-list label, icon, accent)
    ("Notes", "Notes", IC["notes"], "indigo"),
    ("Attachments", "Attachments", IC["attach"], "sky"),
    ("Emails", "Emails", IC["mail"], "amber"),
    ("Checklists", "Checklists", IC["task"], "teal"),
    ("Cadences", "Cadences", IC["status"], "violet"),
]


# -------------------------------------------------------------------- build

def mint_connection_id() -> str:
    """Lookup-association id. The editor mints these client-side (they appear
    fully formed in its first PUT, never in a prior response); all four observed
    begin with "00", so match that."""
    return "00" + str(uuid.uuid4())[2:]


def build(p: Profile) -> dict:
    view = root(CANVAS_NAME, p.module_id, MODULE, p.layout_id, W, 1340, tokens=T)
    view["children"].append(header(p))

    body_h = 1079
    strip_h = body_h + 48
    tabs = [{"name": "Overview", "children": pane_overview(p)},
            {"name": "Pricing", "children": pane_pricing(p)},
            {"name": "Activity", "children": pane_activity(p)},
            {"name": "Record", "children": pane_record(p)}]
    strip = tab_strip(0, BANNER_H, W, strip_h, tabs, tokens=T)

    # Related Account: Zoho's lookup All-Fields tab on the Related_Account lookup.
    conn = mint_connection_id()
    ra_id, _ = p.f("Related_Account")
    strip["children"].append(lookup_all_fields_tab("All Fields - Related Account", conn, W, body_h // 2,
                                                   order=len(strip["children"])))
    view["related_to"]["lookup_associations"] = [{
        "connection_id": conn,
        "parent_module_lookup_field": {"api_name": "Related_Account", "id": ra_id},
        "child_module": {"api_name": "Accounts", "id": p.accounts_module_id},
    }]

    def rl_tab(name, rl_id, card_node):
        return {"type": "component",
                "ui": {"value": {"style": {}, "custom_style": {},
                                 "position": {"start_x": 0, "start_y": body_h // 2, "end_x": W, "width": W,
                                              "height": body_h // 2, "depth": 1, "min_top": 30, "min_left": 30,
                                              "order": len(strip["children"])},
                                 "class": "zc-tab-section zc-tabrl-container", "name": name, "disabled": True},
                       "tab_item_title": {"class": ""}},
                "theme": "Custom Layout", "tab_relatedlist_id": rl_id, "children": [card_node]}

    strip["children"].append(rl_tab("Timeline", "timeline",
                                    system_list_card("timeline", "Timeline", GAP, 24, W - GAP * 2, 640,
                                                     tokens=T, recordcount=10, icon_name=IC["clock"],
                                                     accent=T["indigo"])))
    for name, label, ic, accent in RL_TABS:
        strip["children"].append(rl_tab(name, p.rl(label),
                                        rl_card(p, GAP, 24, W - GAP * 2, 640, label, ic, accent, 10, title=name)))
    view["children"].append(strip)
    return {"canvas_view": [view]}


# -------------------------------------------------------------------- audit

def vocabulary(doc) -> dict[str, set]:
    """Class tokens, style keys, themes, types, datatypes, icons used in a payload."""
    v = {"class": set(), "style": set(), "theme": set(), "type": set(), "datatype": set(), "icon": set()}

    def walk(n):
        if isinstance(n, dict):
            if n.get("theme"):
                v["theme"].add(n["theme"])
            if n.get("type"):
                v["type"].add(n["type"])
            if n.get("datatype"):
                v["datatype"].add(n["datatype"])
            ui = n.get("ui") if isinstance(n.get("ui"), dict) else {}
            for slot in ui.values():
                if isinstance(slot, dict):
                    cls = slot.get("class")
                    if isinstance(cls, str):
                        v["class"].update(cls.split())
                    st = slot.get("style")
                    if isinstance(st, dict):
                        for state in st.values():
                            if isinstance(state, dict):
                                v["style"].update(state.keys())
                    if isinstance(slot.get("icon"), str):
                        v["icon"].add(slot["icon"])
            for c in n.get("children") or []:
                walk(c)
    walk(doc["canvas_view"][0])
    return v


def audit(doc) -> dict[str, set]:
    seen = {k: set() for k in ("class", "style", "theme", "type", "datatype", "icon")}
    for d in REFERENCE_DIRS:
        for f in d.rglob("*.json"):
            if f.name.startswith(("rollback-", "pre-put", "live-", "noop-", "edited-")):
                continue
            try:
                ref = json.loads(f.read_text(encoding="utf-8"))
            except Exception:
                continue
            if "canvas_view" not in ref or not isinstance(ref["canvas_view"][0], dict) \
                    or "children" not in ref["canvas_view"][0]:
                continue
            for k, s in vocabulary(ref).items():
                seen[k] |= s
    # Icons: the catalog (pulled from Zoho's own CSS) is the authority, not the
    # handful of names the gallery canvases happen to use.
    from canvas_shapes import ICON_CATALOG
    seen["icon"] |= ICON_CATALOG
    mine = vocabulary(doc)
    return {k: mine[k] - seen[k] for k in mine}


# --------------------------------------------------------------------- main

def main() -> int:
    auth = ZohoAuth.from_env()
    p = Profile(auth)
    print(f"Profiled {MODULE}: module {p.module_id}, layout {LAYOUT_NAME} {p.layout_id}, "
          f"{len(p.fields)} fields, {len(p.related)} related lists")

    body = build(p)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUT_DIR / "proposals-v1.json"
    out.write_text(json.dumps(body, indent=1), encoding="utf-8")
    (OUT_DIR / "proposals-v1.meta.json").write_text(json.dumps({
        "canvas_view_id": VIEW_ID, "module": {"id": p.module_id, "api_name": MODULE},
        "layout": {"id": p.layout_id, "name": LAYOUT_NAME}, "org_id": ORG_ID,
        "design_source": "output/camco-647376701/Proposals/proposals-v1.preview.html",
        "generated_by": "src/build_proposals_v1.py", "generated": datetime.now().isoformat(timespec="seconds"),
        "lookup_associations": body["canvas_view"][0]["related_to"]["lookup_associations"],
    }, indent=1), encoding="utf-8")

    n, rl, tabs, fields = [0], [0], [], []

    def count(x):
        if isinstance(x, dict):
            n[0] += 1
            if x.get("type") == "relatedlist":
                rl[0] += 1
            if x.get("type") == "field":
                fields.append(x["id"])
            nm = ((x.get("ui") or {}).get("value") or {}).get("name") if isinstance(x.get("ui"), dict) else None
            if nm:
                tabs.append(nm)
            for c in (x.get("children") or []):
                count(c)
    count(body["canvas_view"][0])
    print(f"Built {out.relative_to(PROJECT_ROOT)}: {n[0]} nodes, {len(tabs)} tabs, {rl[0]} related lists, "
          f"{len(fields)} field placements ({len(set(fields))} distinct)")
    print("  tabs:", tabs)

    errors, warnings = validate(body)
    print(f"  validation: {len(errors)} errors, {len(warnings)} warnings")
    for e in errors[:20]:
        print(f"    ERROR {e}")
    for w in warnings[:10]:
        print(f"    WARN  {w}")
    unseen = audit(body)
    total = sum(len(s) for s in unseen.values())
    print(f"  vocabulary audit vs Zoho-authored files: {total} unobserved values")
    for k, s in unseen.items():
        if s:
            print(f"    {k}: {sorted(s)}")
    if errors or total:
        print("\nNot deployed: fix the above first.")
        return 1
    if "--deploy" not in sys.argv:
        print("\nNot deployed. Re-run with --deploy.")
        return 0

    from zoho_canvas import CanvasApiError, CanvasClient
    client = CanvasClient(auth)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    rb = PROJECT_ROOT / "reference" / "captures" / f"rollback-{VIEW_ID}-{stamp}.json"
    live = client.get_view(VIEW_ID)
    rb.write_text(json.dumps(live, indent=1), encoding="utf-8")
    print(f"\nRollback: reference/captures/{rb.name}  (was {live['canvas_view'][0].get('name')!r})")
    try:
        resp = client.put_view(VIEW_ID, body, i_understand_this_is_live=True)
    except CanvasApiError as exc:
        print(f"PUT FAILED: {exc}")
        return 1
    cv = resp.get("canvas_view", [{}])[0]
    print(f"PUT {cv.get('code')} {cv.get('status')} {cv.get('message')!r}  uniqueids returned: "
          f"{len(cv.get('details', {}).get('children', []))}")
    after = client.get_view(VIEW_ID)["canvas_view"][0]
    la = after.get("related_to", {}).get("lookup_associations") or []
    print(f"     live: {after.get('name')!r}, lookup_associations kept: {len(la)}")
    print("\nNOT VERIFIED until opened in the editor:")
    print(f"  https://crm.zoho.com/crm/org{ORG_ID}/settings/modules/CustomModule6/layouts/{p.layout_id}"
          f"/canvas/{VIEW_ID}/edit?feature=DetailView")
    print(f"  restore: python src/restore.py reference/captures/{rb.name} --execute")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
