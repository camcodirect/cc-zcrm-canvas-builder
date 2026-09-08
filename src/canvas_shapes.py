"""Canvas node builders that emit ONLY shapes the Zoho editor itself emits.

Every builder here mirrors a node captured from the editor or from Zoho's own
gallery templates (see docs/canvas-constructs.md and reference/ui-capture/).
Nothing is invented. If a shape you need is not here, capture it first.

Supersedes base_template.py, which carried two shapes the editor never
produces (a static_content wrapper around every heading, and guessed icon
names) and is kept only for reference.
"""

from __future__ import annotations

import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
ASSETS = PROJECT_ROOT / "reference" / "zoho-assets"

ICON_CATALOG: set[str] = set(
    (ASSETS / "icon-catalog.txt").read_text(encoding="utf-8").split()
) if (ASSETS / "icon-catalog.txt").exists() else set()

# Zoho font-family codes: r regular, m medium, s semibold, b bold.
F_REG, F_MED, F_SEMI, F_BOLD = "r", "m", "s", "b"


# ------------------------------------------------------------------ tokens

BRIGHT = {
    "canvas_bg":   "rgba(245, 248, 252, 1)",
    "card_bg":     "rgba(255, 255, 255, 1)",
    "banner_from": "rgb(99, 102, 241)",
    "banner_mid":  "rgb(14, 165, 233)",
    "banner_to":   "rgb(20, 184, 166)",
    "text":        "rgba(15, 23, 42, 1)",
    "text_2":      "rgba(51, 65, 85, 1)",
    "text_muted":  "rgba(100, 116, 139, 1)",
    "text_invert": "rgba(255, 255, 255, 1)",
    "indigo":  "rgba(99, 102, 241, 1)",
    "sky":     "rgba(14, 165, 233, 1)",
    "teal":    "rgba(20, 184, 166, 1)",
    "violet":  "rgba(139, 92, 246, 1)",
    "amber":   "rgba(245, 158, 11, 1)",
    "rose":    "rgba(244, 63, 94, 1)",
    "emerald": "rgba(16, 185, 129, 1)",
    "hairline": "rgba(232, 237, 243, 1)",
    # John's rule (2026-09-07): corners 3px max anywhere; soften with shadow instead.
    "radius_card": "3px",
    "radius_chip": "2px",
    "radius_button": "3px",
    "shadow":      "0px 6px 20px 0px rgba(15, 23, 42, 0.06)",
    "font_body":    "13px",
    "font_heading": "14px",
    "font_micro":   "11px",
    "row_height":   29,
}


# ---------------------------------------------------------------- helpers

class _Names:
    """Sequential zcode names the way the editor assigns them (section1, text2 ...)."""

    def __init__(self):
        self.n: dict[str, int] = {}

    def __call__(self, prefix: str) -> dict:
        self.n[prefix] = self.n.get(prefix, 0) + 1
        return {"name": f"{prefix}{self.n[prefix]}"}


zc = _Names()


def position(x: int, y: int, w: int, h: int, *, depth: int = 1, **extra) -> dict:
    pos = {"start_x": x, "start_y": y, "end_x": x + w, "width": w, "height": h, "depth": depth}
    pos.update({k: v for k, v in extra.items() if v is not None})
    return pos


def _sub(style: dict | None = None, cls: str = "") -> dict:
    """A ui.holder / ui.field / ui.label sub-block."""
    return {"style": {"default": style or {}}, "custom_style": {}, "class": cls}


# ------------------------------------------------------------------- root

def root(name: str, module_id: str, module_api: str, layout_id: str,
         width: int, height: int, tokens: dict = BRIGHT) -> dict:
    return {
        "name": name,
        "ui": {
            "value": {
                "style": {"default": {"background_color": tokens["canvas_bg"]}},
                "custom_style": {},
                "position": {"start_x": 0, "start_y": 0, "end_x": width * 3,
                             "width": width, "height": height, "depth": 1},
                "class": "",
            },
            "canvas_rules": [],
            "script_info": {"mapping": {}, "deleted": []},
        },
        "feature": "DetailView",
        "type": "component",
        "state": "active",
        "action": "edit",
        "module": {"id": module_id, "api_name": module_api},
        "layout": {"id": layout_id},
        "related_to": {"data_hub_associations": None, "lookup_associations": None,
                       "homepage_associations": None},
        "children": [],
    }


# ------------------------------------------------------------- containers

def section(x: int, y: int, w: int, h: int, *, style: dict | None = None,
            min_top: int = 9, min_left: int = 5, depth: int = 1,
            locked: bool = False) -> dict:
    """A card. Editor shape: zc-lsection + _section_version_ + zcode."""
    st = {"_section_version_": 1}
    st.update(style or {})
    pos = position(x, y, w, h, depth=depth, min_top=min_top, min_left=min_left)
    if locked:
        pos["_locked_"] = "true"
    return {
        "type": "component",
        "ui": {"value": {"style": {"default": st}, "custom_style": {},
                         "position": pos, "class": "zc-lsection", "zcode": zc("section")}},
        "theme": "Custom Layout",
        "children": [],
    }


def card(x: int, y: int, w: int, h: int, *, tokens: dict = BRIGHT) -> dict:
    return section(x, y, w, h, style={
        "border": "none",
        "background_color": tokens["card_bg"],
        "border_radius": tokens["radius_card"],
        "box_shadow": tokens["shadow"],
    })


def banner(x: int, y: int, w: int, h: int, *, tokens: dict = BRIGHT) -> dict:
    """Header band, as in gallery template c2: zc-lsection, depth 10, locked."""
    return section(x, y, w, h, depth=10, min_top=28, min_left=29, locked=True, style={
        "border": "none",
        "background_image": (f"linear-gradient(115deg, {tokens['banner_from']} 0%, "
                             f"{tokens['banner_mid']} 55%, {tokens['banner_to']} 100%)"),
        "background_size": "cover",
        "border_radius": "0",
        "box_shadow": "none",
    })


# ------------------------------------------------------------ static text

def text(x: int, y: int, w: int, h: int, value: str, *, style: dict | None = None,
         cls: str = "", autoheight: bool = True) -> dict:
    """Static Text exactly as the editor writes it: bare, with zcode + autoheight."""
    return {
        "type": "component",
        "ui": {"value": {"style": {"default": style or {}}, "custom_style": {},
                         "position": position(x, y, w, h), "class": cls,
                         "zcode": zc("text"), "value": value},
               "autoheight": autoheight},
        "theme": "Static Text",
        "children": [],
    }


def heading(x: int, y: int, w: int, h: int, value: str, *, tokens: dict = BRIGHT,
            size: str | None = None, family: str = F_SEMI, colour: str | None = None) -> dict:
    return text(x, y, w, h, value, style={
        "padding": "0px", "background_color": "transparent",
        "font_size": size or tokens["font_heading"], "font_family": family,
        "color": colour or tokens["text"],
    })


def chip(x: int, y: int, w: int, h: int, value: str, *, bg: str, colour: str,
         tokens: dict = BRIGHT) -> dict:
    """Text preset #1 shape: a Static Text with background, radius and padding."""
    return text(x, y, w, h, value, autoheight=False, style={
        "background_color": bg, "border_radius": tokens.get("radius_chip", "2px"),
        "padding": "4px 10px 4px 10px",
        "font_size": tokens["font_micro"], "font_family": F_SEMI, "color": colour,
    })


def icon(x: int, y: int, name: str, *, size: int = 22, colour: str | None = None) -> dict:
    if ICON_CATALOG and name not in ICON_CATALOG:
        raise ValueError(f"icon {name!r} is not in reference/zoho-assets/icon-catalog.txt")
    st = {"font_size": f"{size}px"}
    if colour:
        st["color"] = colour
    return {
        "type": "component",
        "ui": {"value": {"style": {"default": st}, "custom_style": {},
                         "position": position(x, y, size + 4, size + 4),
                         "fixed": True, "class": "zc-ta-center",
                         "zcode": zc("icon"), "icon": name}},
        "theme": "Static Icon",
        "children": [],
    }


def line(x: int, y: int, w: int, *, vertical: bool = False) -> dict:
    return {
        "type": "component",
        "ui": {"value": {"style": {}, "custom_style": {},
                         "position": position(x, y, w, 3), "fixed": True, "class": "",
                         "zcode": zc("line"), "vertical": vertical}},
        "theme": "Line",
        "children": [],
    }


def separator(x: int, y: int, size: int = 10) -> dict:
    return {
        "type": "separator",
        "ui": {"value": {"style": {"default": {"padding": "5px"}}, "custom_style": {},
                         "position": position(x, y, size, size),
                         "class": "zcanvas-seperator", "value": ""}},
        "children": [],
    }


# ----------------------------------------------------------------- fields

def field(field_id: str, datatype: str, x: int, y: int, w: int, h: int, *,
          tokens: dict = BRIGHT, cls: str = "zcanvas-field", order: int | None = None,
          value_style: dict | None = None, label_style: dict | None = None,
          label_cls: str = "", stacked: bool = True) -> dict:
    holder = {"flex_direction": "column"} if stacked else {}
    return {
        "id": field_id, "datatype": datatype, "type": "field",
        "ui": {
            "value": {"style": {"default": {}}, "custom_style": {},
                      "position": position(x, y, w, h, order=order), "class": cls},
            "holder": _sub(holder),
            "field": _sub(value_style or {"font_size": tokens["font_body"], "color": tokens["text"]}),
            "label": _sub(label_style or {"font_size": tokens["font_body"],
                                          "color": tokens["text_muted"]}, label_cls),
        },
        "children": [],
    }


def field_table(x: int, y: int, w: int, rows: list[tuple[str, str]], *,
                tokens: dict = BRIGHT, label_pct: float = 42.0) -> dict:
    """Label/value table. Shape from gallery template c1; rows stack cumulatively."""
    rh = tokens["row_height"]
    children = []
    for i, (fid, dt) in enumerate(rows):
        children.append({
            "type": "row",
            "ui": {"value": {"position": position(0, i * rh, w, rh, order=i),
                             "style": {"default": {}}, "custom_style": {},
                             "class": "zcanvas-row"}},
            "children": [field(fid, dt, 0, 0, w, rh, tokens=tokens, order=0,
                               cls="zc-ta-left zcanvas-field", stacked=False,
                               value_style={"padding_left": "0px", "color": tokens["text"]},
                               label_style={"padding": "0px 0px 0px 0px",
                                            "color": tokens["text_muted"]})],
        })
    return {
        "type": "component",
        "ui": {"value": {
            "style": {"default": {"background_color": "rgba(0,0,0,0)"}},
            "custom_style": {},
            "position": position(x, y, w, len(rows) * rh + 24),
            "class": "zclayout-table zc-no-theme zcanvas-editor",
            "layoutstyle": {"field": {"width": "100%"}, "row": {"height": f"{rh}px"},
                            "inner": [{"percent": label_pct}]},
            "scope": "default",
        }},
        "theme": "Table Layout",
        "children": children,
    }


# ---------------------------------------------------------------- actions

# Observed class strings per system action id (gallery template c1 / editor).
_ACTION_CLASS = {
    "back":       "zcanvas-no-img-default zc-ta-center zccbutton zc-restricted-icon zcanvas-field",
    "navigate":   "zcanvas-no-img-default zccbutton zcanvas-nav zc-restricted-icon zcanvas-field zc-ta-center",
    "morebutton": "zcanvas-no-img-default zccbutton zc-only-icon zccbuttonicon zcanvas-field zc-ta-center",
}
_ACTION_DEFAULT_CLASS = "zcanvas-field zcanvas-no-img-default zccbutton zc-ta-center"


def action(action_id: str, x: int, y: int, w: int, h: int, *, style: dict | None = None,
           hover: dict | None = None, depth: int = 1) -> dict:
    st: dict = {"default": style or {}}
    if hover:
        st["hover"] = hover
    return {
        "id": action_id, "datatype": "button", "type": "action",
        "ui": {"value": {"style": st, "custom_style": {},
                         "position": position(x, y, w, h, depth=depth),
                         "class": _ACTION_CLASS.get(action_id, _ACTION_DEFAULT_CLASS)},
               "field": _sub()},
        "children": [],
    }


def button_group(x: int, y: int, w: int, buttons: list[dict]) -> dict:
    """MERGEFIELD: an inline row of actions. Observed in gallery templates c2/c3.

    buttons: [{"id": "send_mail", "w": 120, "style": {...}, "hover": {...}}, ...]
    """
    inner, cx = [], 0
    for i, b in enumerate(buttons):
        inner.append(action(b["id"], cx, 0, b["w"], 34, style=b.get("style"), hover=b.get("hover")))
        cx += b["w"]
        if i < len(buttons) - 1:
            inner.append(separator(cx, 12))
            cx += 10
    return {
        "type": "component",
        "ui": {"value": {"style": {"default": {}}, "custom_style": {},
                         "position": position(x, y, w, 34), "class": "zc-merge-hright"}},
        "theme": "MERGEFIELD",
        "children": [{
            "type": "component",
            "ui": {"value": {"style": {"default": {}}, "custom_style": {},
                             "class": "zcanvas-row-seperator", "position": {}}},
            "children": inner,
        }],
    }


# ---------------------------------------------------------- related lists

def related_list_card(rl_id: str, title: str, x: int, y: int, w: int, h: int, *,
                      tokens: dict = BRIGHT, recordcount: int = 10,
                      icon_name: str | None = None, accent: str | None = None,
                      inset: int = 18, title_top: int = 8, list_top: int = 52) -> dict:
    """The exact shape of a related-list tab card in gallery template c3 (Notes tab):

        component .zc-list-component.zcautoratio  related_list=true count editorclass
          static_content .zcanvas-title-editor        (title block)
            [Static Icon]  Static Text .zc_disabled autoheight=false
          relatedlist theme="Table Layout"  recordcount  children=[]   (Zoho renders it)

    Geometry is ours: the default metrics match the field cards (18px inset,
    22px icon at y=15, 14px semibold title, content from y=52) so related-list
    cards and field cards read as one system.
    """
    inner_w = w - inset * 2
    title_children = []
    tx = 0
    if icon_name:
        title_children.append(icon(0, 7, icon_name, size=22, colour=accent))
        tx = 32
    title_children.append({
        "type": "component",
        "ui": {"value": {"style": {"default": {"padding": "0px", "font_size": tokens["font_heading"],
                                               "font_family": F_SEMI, "color": tokens["text"]}},
                         "custom_style": {},
                         "position": position(tx, 9, inner_w - tx - 20, 22),
                         "class": "zc_disabled", "value": title},
               "autoheight": False},
        "theme": "Static Text",
        "children": [],
    })
    return {
        "type": "component",
        "ui": {"value": {
            "style": {"default": {"border": "none", "background_color": tokens["card_bg"],
                                  "border_radius": tokens["radius_card"],
                                  "box_shadow": tokens["shadow"]}},
            "custom_style": {},
            "position": position(x, y, w, h, min_top=30, min_left=30),
            "class": "zc-list-component zcautoratio",
            "zcode": {"name": f"RL-{title}"},
            "related_list": True,
            "count": str(recordcount),
            "editorclass": "zcanvas-loading-component",
        }},
        "theme": "Custom Layout",
        "related_list": True,
        "children": [
            {
                "type": "static_content",
                "ui": {"value": {"style": {"default": {}}, "custom_style": {},
                                 "position": position(inset, title_top, inner_w, 40, min_top=11, min_left=10),
                                 "class": "zcanvas-title-editor"}},
                "theme": "Custom Layout",
                "children": title_children,
            },
            {
                "id": rl_id, "type": "relatedlist",
                "ui": {"value": {"position": position(inset, list_top, inner_w, h - list_top - inset),
                                 "style": {}, "recordcount": str(recordcount)},
                       "canvas_rules": []},
                "theme": "Table Layout",
                "children": [],
            },
        ],
    }


# ------------------------------------------------------------------- tabs

def tab_strip(x: int, y: int, w: int, h: int, tabs: list[dict], *, tokens: dict = BRIGHT,
              depth: int = 1) -> dict:
    """Tab Layout as the editor creates it, with the accent styled on the active chip.

    tabs: [{"name": str, "relatedlist_id": str|None, "children": [...]}]
    Tab bodies share a layer: tab 0 full height, others at start_y == own height.
    """
    body_h = h - 48
    other_h = body_h // 2
    children = []
    for i, t in enumerate(tabs):
        val = {"style": {}, "custom_style": {},
               "position": position(0, 0 if i == 0 else other_h, w,
                                    body_h if i == 0 else other_h,
                                    order=i, min_top=30, min_left=30),
               "class": "zc-tab-section" + (" zc-tabrl-container" if t.get("relatedlist_id") else ""),
               "name": t["name"]}
        if t.get("relatedlist_id"):
            val["disabled"] = True
        node = {"type": "component",
                "ui": {"value": val, "tab_item_title": {"class": ""}},
                "theme": "Custom Layout",
                "children": t.get("children", [])}
        if t.get("relatedlist_id"):
            node["tab_relatedlist_id"] = t["relatedlist_id"]
        children.append(node)

    return {
        "type": "component",
        "ui": {"value": {
            "style": {}, "custom_style": {},
            "position": position(x, y, w, h, depth=depth),
            "class": "zcanvas-horizantol-top zcanvas-subtab-push",
            "zcode": {"name": "tab1"},
            "layoutstyle": {
                "default": {},
                "hover": {"color": tokens["text"], "border_bottom": f"3px solid {tokens['hairline']}"},
                "active": {"color": tokens["indigo"], "border_bottom": f"3px solid {tokens['indigo']}",
                           "font_family": F_SEMI},
                "tabname": {}, "tabicon": {},
                "container": {"default": {"background_color": tokens["card_bg"]}},
                "editor": {"default": {"background_color": "rgba(255,255,255,0)"}},
            },
            "custom_layoutstyle": {"default": [], "hover": [], "active": [],
                                   "tabname": {}, "tabicon": {}, "container": {}, "editor": {}},
        }},
        "theme": "Tab Layout",
        "children": children,
    }


def system_list_card(system_id: str, title: str, x: int, y: int, w: int, h: int, *,
                     tokens: dict = BRIGHT, recordcount: int = 5, **kw) -> dict:
    """A palette `system` component (timeline, journeys) placed as a related list.

    Identical to related_list_card; the id is the system string. Observed for
    `timeline` and `journeys` ("Interactions") only.
    """
    return related_list_card(system_id, title, x, y, w, h, tokens=tokens, recordcount=recordcount, **kw)


def lookup_all_fields_tab(name: str, connection_id: str, w: int, body_h: int, order: int) -> dict:
    """An "All Fields - <Lookup>" tab body (round-3 save 01).

    Requires a matching entry in root related_to.lookup_associations; the
    connection_id is minted by the editor, so carry it forward from a capture.
    """
    return {
        "type": "component",
        "ui": {"value": {"style": {}, "custom_style": {},
                         "position": position(14, 14, w - 15, body_h, min_top=10, min_left=20, order=order),
                         "class": "zc-tab-section zc-tab-lookup-all-fields zc-tabrl-container",
                         "name": name, "disabled": True},
               "allfieldstabstyle": {}, "tab_item_title": {"class": ""}},
        "theme": "Custom Layout",
        "details": {"connection_type": "lookup_associations", "connection_id": connection_id},
        "children": [],
    }


def flex_container(x: int, y: int, w: int, h: int, items: list[dict], *,
                   fit_height: bool = True, style: dict | None = None) -> dict:
    """Flex Layout (column). Each item gets property.flex_item and an order.

    Items keep their own position block; the editor writes one for flex items
    too. h_stretch=True on an item is expressed by passing it already carrying
    the zc-flex-self-column-horizontal-grow class.
    """
    cls = "zc-flex-component zc-flex-direction-column" + (" zc-fit-height-content" if fit_height else "")
    for i, it in enumerate(items):
        v = it["ui"]["value"]
        v["position"]["order"] = i
        grow = "zc-flex-self-column-horizontal-grow" in (v.get("class") or "")
        v["property"] = {"flex_item": {"default": {"h_stretch": grow, "v_stretch": False,
                                                    "align_self": ""}}}
    return {
        "type": "component",
        "ui": {"value": {"style": {"default": style or {"box_shadow": "none", "background_color": "transparent",
                                                        "border": "none", "padding": "5px"}},
                         "custom_style": {},
                         "position": position(x, y, w, h, min_top=5, min_left=5),
                         "class": cls,
                         "property": {"flex": {"default": {"direction": "column",
                                                            "space_distribute": "_normal",
                                                            "alignment": "topleft", "wrap": "nowrap"}}}}},
        "theme": "Flex Layout",
        "children": items,
    }


def grid_container(x: int, y: int, w: int, h: int, *, column_gap: str = "5px",
                   row_gap: str = "5px", block_height_px: str = "20px",
                   style: dict | None = None) -> dict:
    """Grid Layout container. Only the EMPTY grid has been observed; grid items
    are unobserved, so this builder takes no children."""
    return {
        "type": "component",
        "ui": {"value": {"style": {"default": style or {"border": "1px solid rgb(215, 226, 237)",
                                                        "background_color": "rgba(248, 250, 255, 1)",
                                                        "box_shadow": "none", "border_radius": "10px"}},
                         "custom_style": {},
                         "position": position(x, y, w, h),
                         "class": "zcanvas-grid-container",
                         "zcode": zc("grid"),
                         "property": {"grid": {"default": {"column_gap": column_gap, "row_gap": row_gap,
                                                            "block_width_count": [{"order": 11}],
                                                            "block_height_px": block_height_px}}}}},
        "theme": "Grid Layout",
        "children": [],
    }


def canvas_image(canvas_file_id: str, x: int, y: int, w: int, h: int) -> dict:
    """An uploaded image (POST canvas_files?feature=background_image returns the id)."""
    ref = f"$Image{{{canvas_file_id}}}"
    return {
        "type": "component",
        "ui": {"value": {"style": {"default": {"background_image": f"url({ref})"}}, "custom_style": {},
                         "position": position(x, y, w, h), "fixed": True,
                         "class": "zcanvas-field zcbdrbox zc-cover-Image", "zcode": zc("image")},
               "field": {"style": {"default": {"background_image": "none"}}, "custom_style": {}, "class": ""},
               "image": {"style": {"default": {"src": ref}}}},
        "theme": "Canvas Image",
        "children": [],
    }


def canvas_button(label: str, x: int, y: int, w: int, h: int, *, style: dict | None = None,
                  hover: dict | None = None) -> dict:
    """Custom canvas button (Elements panel). Button presets go in field.default/hover."""
    st: dict = {"default": style or {}}
    if hover:
        st["hover"] = hover
    return {
        "type": "component",
        "ui": {"value": {"style": {"default": {}}, "custom_style": {},
                         "position": position(x, y, w, h),
                         "class": "zcanvas-field zcanvas-no-img-default zc-ta-center zccbutton",
                         "name": label},
               "field": {"style": st, "custom_style": {}, "class": ""}},
        "theme": "Canvas Button",
        "children": [],
    }


def all_fields_tab(reference_payload: Path) -> dict:
    """Lift the machine-generated All Fields tab from a Zoho-authored capture.

    It needs zc-tab-all-fields, disabled, allfieldstabstyle and one section per
    layout section with a deep generated subtree; copying is the only safe way.
    """
    src = json.loads(reference_payload.read_text(encoding="utf-8"))["canvas_view"][0]
    found = []

    def walk(n):
        if isinstance(n, dict):
            v = (n.get("ui") or {}).get("value") if isinstance(n.get("ui"), dict) else None
            if isinstance(v, dict) and v.get("name") == "All Fields":
                found.append(n)
            for c in (n.get("children") or []):
                walk(c)
    walk(src)
    if not found:
        raise RuntimeError("All Fields tab not found in reference capture")
    tab = json.loads(json.dumps(found[0]))

    def strip(n):
        if isinstance(n, dict):
            n.pop("uniqueid", None)
            n.pop("componentid", None)
            for c in (n.get("children") or []):
                strip(c)
    strip(tab)
    return tab
