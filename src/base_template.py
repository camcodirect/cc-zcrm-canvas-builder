"""Camco org base template — branding tokens and node builders.

Two layers, deliberately separate:

  TOKENS  — colour, type and spacing for one org. Swap this for a new client.
  builders — geometry-aware node constructors that emit valid Canvas JSON.

Everything here emits the observed Canvas vocabulary only. No invented class
tokens, no invented style properties. See docs/canvas-json-structure.md.

Brand source: Camco site palette (assets/css/immersive.css) adapted from its
dark theatrical scheme to a light CRM working surface. Signal red is kept as the
accent; the near-black becomes text rather than background.
"""

from __future__ import annotations


# --- design tokens ------------------------------------------------------

CAMCO = {
    "name": "camco",
    "org_id": "647376701",

    # Surfaces. CRM detail pages are light working surfaces, so the site's
    # near-black is used for text, not background.
    "canvas_bg":   "rgba(244, 241, 234, 1)",   # --bone, warm page ground
    "card_bg":     "rgba(255, 255, 255, 1)",
    "banner_from": "rgb(11, 10, 9)",           # --ink
    "banner_to":   "rgb(124, 29, 29)",         # --signal-deep

    # Type
    "text":        "rgba(28, 25, 23, 1)",      # --ink-3
    "text_muted":  "rgba(109, 103, 95, 1)",    # between --ash-dim and --ink-4
    "text_invert": "rgba(244, 241, 234, 1)",   # --bone

    # Accent
    "signal":      "rgba(220, 38, 38, 1)",     # --signal
    "signal_hot":  "rgba(239, 68, 68, 1)",     # --signal-hot
    "success":     "rgba(52, 211, 153, 1)",    # --success

    # Lines
    "hairline":    "rgba(28, 25, 23, 0.12)",

    # Metrics — all values observed in Zoho's own gallery templates
    "radius_card":  "13px",
    "radius_pill":  "99px",
    "pad_card":     "20px",
    "font_body":    "14px",
    "font_label":   "14px",
    "font_heading": "16px",
    "font_title":   "18px",
    "shadow":       "0px 2px 2px 0px rgba(0, 0, 0, 0.12)",
    "row_height":   29,
}

# Bright modern palette — the approved design v2. Indigo/sky/teal banner on a
# cool near-white ground, white cards, rotating accent colours per card.
BRIGHT = {
    "name": "bright",
    "org_id": "647376701",

    "canvas_bg":   "rgba(245, 248, 252, 1)",   # slate-50-ish page ground
    "card_bg":     "rgba(255, 255, 255, 1)",
    "banner_from": "rgb(99, 102, 241)",        # indigo-500
    "banner_mid":  "rgb(14, 165, 233)",        # sky-500
    "banner_to":   "rgb(20, 184, 166)",        # teal-500

    "text":        "rgba(15, 23, 42, 1)",      # slate-900
    "text_2":      "rgba(51, 65, 85, 1)",      # slate-700
    "text_muted":  "rgba(100, 116, 139, 1)",   # slate-500
    "text_faint":  "rgba(203, 213, 225, 1)",   # slate-300
    "text_invert": "rgba(255, 255, 255, 1)",

    # accent rotation
    "indigo":  "rgba(99, 102, 241, 1)",
    "sky":     "rgba(14, 165, 233, 1)",
    "teal":    "rgba(20, 184, 166, 1)",
    "violet":  "rgba(139, 92, 246, 1)",
    "amber":   "rgba(245, 158, 11, 1)",
    "rose":    "rgba(244, 63, 94, 1)",
    "emerald": "rgba(16, 185, 129, 1)",
    "signal":  "rgba(99, 102, 241, 1)",        # primary = indigo

    "hairline":    "rgba(232, 237, 243, 1)",
    "row_line":    "rgba(244, 247, 250, 1)",

    # On the coloured banner a white pill reads better than a saturated fill.
    "primary_btn_bg": "rgba(255, 255, 255, 1)",
    "primary_btn_fg": "rgba(99, 102, 241, 1)",
    "radius_btn":     "10px",

    "radius_card":  "14px",
    "radius_tile":  "12px",
    "radius_pill":  "99px",
    "pad_card":     "18px",
    "font_body":    "13px",
    "font_label":   "13px",
    "font_heading": "14px",
    "font_title":   "23px",
    "font_kpi":     "17px",
    "font_big":     "26px",
    "font_micro":   "11px",
    "shadow":       "0px 6px 20px 0px rgba(15, 23, 42, 0.06)",
    "row_height":   29,
}

# Zoho font-family codes: r regular, m medium, s semibold, b bold.
F_REG, F_MED, F_SEMI, F_BOLD = "r", "m", "s", "b"


# --- geometry helper ----------------------------------------------------

def position(x: int, y: int, w: int, h: int, *, depth: int = 1, **extra) -> dict:
    """Build a position block. Enforces end_x == start_x + width."""
    pos = {
        "start_x": x, "start_y": y, "end_x": x + w,
        "width": w, "height": h, "depth": depth,
    }
    pos.update({k: v for k, v in extra.items() if v is not None})
    return pos


# --- node builders ------------------------------------------------------

def root(name: str, module_id: str, module_api: str, layout_id: str,
         width: int, height: int, tokens: dict = CAMCO) -> dict:
    """The canvas_view root. end_x is 3x width (responsive breakpoints)."""
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
        "related_to": {"data_hub_associations": None,
                       "lookup_associations": None,
                       "homepage_associations": None},
        "children": [],
    }


def banner(x: int, y: int, w: int, h: int, *, zcode: str = "section1",
           tokens: dict = CAMCO, depth: int = 10) -> dict:
    """Full-width gradient header band. depth 10 keeps it above the tabs."""
    mid = tokens.get("banner_mid")
    stops = (f"{tokens['banner_from']} 0%, {mid} 55%, {tokens['banner_to']} 100%"
             if mid else
             f"{tokens['banner_from']} 0%, {tokens['banner_to']} 100%")
    return {
        "type": "component",
        "ui": {"value": {
            "style": {"default": {
                "border": "none",
                "background_image": f"linear-gradient(115deg, {stops})",
                "background_size": "cover",
                "border_radius": "0",
                "box_shadow": "none",
            }},
            "custom_style": {},
            "position": position(x, y, w, h, depth=depth, min_top=28, min_left=29),
            "class": "zc-lsection",
            "zcode": {"name": zcode},
        }},
        "theme": "Custom Layout",
        "children": [],
    }


def card(x: int, y: int, w: int, h: int, *, tokens: dict = CAMCO,
         shadow: bool = True, list_component: bool = False) -> dict:
    """Rounded white card. The dominant container in Zoho's gallery templates."""
    return {
        "type": "component",
        "ui": {"value": {
            "style": {"default": {
                "border": "none",
                "background_color": tokens["card_bg"],
                "border_radius": tokens["radius_card"],
                "padding": tokens["pad_card"],
                "box_shadow": tokens["shadow"] if shadow else "none",
            }},
            "custom_style": {},
            "position": position(x, y, w, h),
            "class": "zc-list-component" if list_component else "zc-lsection",
        }},
        "theme": "Custom Layout",
        "children": [],
    }


def heading(x: int, y: int, w: int, h: int, text: str, *,
            tokens: dict = CAMCO, uppercase: bool = False) -> dict:
    """Static text. The ONLY node type whose literal text lives in the payload."""
    return {
        "type": "static_content",
        "ui": {"value": {
            "style": {},
            "custom_style": {},
            "position": position(x, y, w, h, min_left=10, min_top=11),
            "class": "zcanvas-title-editor",
        }},
        "theme": "Custom Component",
        "children": [{
            "type": "component",
            "ui": {
                "autoheight": False,
                "value": {
                    "style": {"default": {
                        "padding": "0px",
                        "background_color": "transparent",
                        "color": tokens["text"],
                        "font_size": tokens["font_heading"],
                        "font_family": F_SEMI,
                    }},
                    "position": position(0, 0, w, h),
                    "class": "zcanvasuppercase" if uppercase else "zc_disabled",
                    "value": text,
                },
            },
            "theme": "Static Text",
            "children": [],
        }],
    }


def field(field_id: str, datatype: str, x: int, y: int, w: int, h: int, *,
          tokens: dict = CAMCO, order: int | None = None,
          css: str = "zcanvas-field") -> dict:
    """A CRM field reference. Label and value are resolved by Zoho from the ID."""
    return {
        "id": field_id,
        "datatype": datatype,
        "type": "field",
        "ui": {
            "value": {
                "style": {"default": {}},
                "custom_style": {},
                "position": position(x, y, w, h, order=order),
                "class": css,
            },
            "field": {"style": {"default": {
                "font_size": tokens["font_body"],
                "color": tokens["text"],
                "padding_left": "0px",
            }}, "custom_style": {}, "class": ""},
            "label": {"style": {"default": {
                "font_size": tokens["font_label"],
                "color": tokens["text_muted"],
                "padding": "0px 0px 0px 0px",
            }}, "custom_style": {}, "class": ""},
        },
        "children": [],
    }


def field_table(x: int, y: int, w: int, rows: list[tuple[str, str]], *,
                tokens: dict = CAMCO, label_pct: float = 42.0) -> dict:
    """A label/value table. Rows stack cumulatively — verified in all captures.

    rows: list of (field_id, datatype).
    """
    rh = tokens["row_height"]
    children = []
    for i, (fid, dt) in enumerate(rows):
        children.append({
            "type": "row",
            "ui": {"value": {
                "position": position(0, i * rh, w, rh, order=i),
                "style": {"default": {}},
                "custom_style": {},
                "class": "zcanvas-row",
            }},
            "children": [field(fid, dt, 0, 0, w, rh,
                               tokens=tokens, order=0,
                               css="zc-ta-left zcanvas-field")],
        })
    # Table height exceeds the row sum; the captures show header/padding overhead.
    height = len(rows) * rh + 24
    return {
        "type": "component",
        "ui": {"value": {
            "style": {"default": {"background_color": "rgba(0,0,0,0)"}},
            "custom_style": {},
            "position": position(x, y, w, height),
            "class": "zclayout-table zc-no-theme zcanvas-editor",
            "layoutstyle": {
                "field": {"width": "100%"},
                "row": {"height": f"{rh}px"},
                "inner": [{"percent": label_pct}],
            },
            "scope": "default",
        }},
        "theme": "Table Layout",
        "children": children,
    }


def tab_strip(x: int, y: int, w: int, h: int, tabs: list[dict], *,
              tokens: dict = CAMCO, zcode: str = "tab1", depth: int = 4) -> dict:
    """Horizontal tab strip.

    Tab bodies do NOT stack: tab 0 gets the full height, every other tab sits at
    start_y == its own height, sharing one layer. Verified across all captures.

    tabs: [{"name": str, "relatedlist_id": str|None, "children": [...]}]
    """
    body_h = h - 48          # strip chrome, measured at 45-48px in the captures
    other_h = body_h // 2
    children = []
    for i, t in enumerate(tabs):
        val = {
            "style": {},
            "custom_style": {},
            "position": position(0, 0 if i == 0 else other_h, w,
                                 body_h if i == 0 else other_h,
                                 order=i, min_top=30, min_left=30),
            "class": ("zc-tab-section" if not t.get("relatedlist_id")
                      else "zc-tab-section zc-tabrl-container"),
            "name": t["name"],
        }
        if t.get("disabled"):
            val["disabled"] = True
        node = {
            "type": "component",
            "ui": {"value": val, "tab_item_title": {"class": ""}},
            "theme": "Custom Layout",
            "children": t.get("children", []),
        }
        if t.get("relatedlist_id"):
            node["tab_relatedlist_id"] = t["relatedlist_id"]
            node["related_list"] = True
        children.append(node)

    return {
        "type": "component",
        "ui": {"value": {
            "style": {"default": {}},
            "custom_style": {},
            "position": position(x, y, w, h, depth=depth),
            "class": "zcanvas-horizantol-top zcanvas-subtab-push",
            "zcode": {"name": zcode},
            "layoutstyle": {
                "default": {"border_bottom": "4px solid rgba(255, 255, 255, 0)",
                            "border_top": "0px solid transparent"},
                "hover": {"background_color": "rgba(28, 25, 23, 0.06)",
                          "color": tokens["text"],
                          "font_size": tokens["font_body"],
                          "font_family": F_REG,
                          "border_bottom": "4px solid rgba(255, 255, 255, 0)"},
                "active": {"background_color": "rgba(255, 255, 255, 0)",
                           "color": tokens["signal"],
                           "border_bottom": f"4px solid {tokens['signal']}",
                           "padding_left": "12px", "padding_right": "12px",
                           "padding_top": "12px", "padding_bottom": "8px",
                           "font_family": F_MED, "border_radius": "0"},
                "container": {"default": {"margin_top": "0px"}},
                "editor": {"default": {
                    "padding": "0px",
                    "background_color": "rgba(255, 255, 255, 0)",
                    "margin_top": "16px",
                    "border_radius": "0px",
                    "box_shadow": "none"}},
                "tabname": {
                    "default": {"padding": "0px", "font_family": F_MED},
                    "hover": {"padding": "0px", "color": tokens["text"],
                              "background_color": "transparent",
                              "font_size": tokens["font_body"]},
                    "active": {"padding": "0px", "color": tokens["signal"],
                               "background_color": "transparent",
                               "font_size": tokens["font_body"],
                               "font_family": F_SEMI}},
                "tabicon": {},
            },
        }},
        "theme": "Tab Layout",
        "children": children,
    }


def action(action_id: str, x: int, y: int, w: int, h: int, *,
           tokens: dict = CAMCO, primary: bool = False) -> dict:
    """A system action button: back, edit, reviewHistory, morebutton, navigate."""
    if primary:
        # On a coloured banner a white "primary" reads better than a saturated
        # fill; palettes can opt in with primary_btn_bg / primary_btn_fg.
        bg = tokens.get("primary_btn_bg", tokens["signal"])
        fg = tokens.get("primary_btn_fg", tokens["text_invert"])
        style = {"default": {"border": "none",
                             "background_color": bg,
                             "color": fg,
                             "border_radius": tokens.get("radius_btn",
                                                         tokens["radius_pill"])},
                 "hover": {"background_color": tokens.get("signal_hot", bg),
                           "border": "none",
                           "color": fg}}
    else:
        style = {"default": {"border": "none",
                             "background_color": "rgba(255,255,255,0)",
                             "color": tokens["text_invert"],
                             "border_radius": "0"}}
    return {
        "id": action_id,
        "datatype": "button",
        "type": "action",
        "ui": {
            "value": {"style": style, "custom_style": {},
                      "position": position(x, y, w, h),
                      "class": "zcanvas-field zcanvas-no-img-default "
                               "zccbutton zc-ta-center"},
            "field": {"style": {"default": {}}, "custom_style": {}, "class": ""},
        },
        "children": [],
    }


def related_list(rl_id: str, x: int, y: int, w: int, h: int, *,
                 recordcount: str | int = 10, context: dict | None = None) -> dict:
    """A full related list rendered by Zoho's own table.

    theme="Table Layout" with empty children = let Zoho render the default list.
    This is the shape Zoho's gallery templates use for a whole-tab related list.
    """
    val = {
        "position": position(x, y, w, h),
        "style": {},
        "recordcount": str(recordcount),
    }
    node = {
        "id": rl_id,
        "type": "relatedlist",
        "ui": {"value": val, "canvas_rules": []},
        "theme": "Table Layout",
        "children": [],
    }
    if context:
        node["ui"]["context"] = context
    return node


def related_list_card(rl_id: str, x: int, y: int, w: int, h: int, title: str, *,
                      tokens: dict = CAMCO, recordcount: int = 10,
                      icon: str | None = None,
                      icon_colour: str | None = None,
                      zcode: str | None = None) -> dict:
    """A titled card wrapping a related list — the gallery-template idiom.

    Structure (matches Zoho's own output):
      component .zc-list-component  (rounded card, related_list=True)
        static_content .zcanvas-title-editor -> Static Text (the title)
        relatedlist theme="Table Layout"
    """
    inner_w = w - 60
    children = []
    if icon:
        children.append({
            "type": "component",
            "ui": {"value": {
                "style": {"default": {"color": icon_colour or tokens["signal"],
                                      "font_size": "22px"}},
                "custom_style": {},
                "position": position(30, 30, 26, 26),
                "fixed": True,
                "class": "zc-ta-center",
                "zcode": {"name": f"icon_{icon}"},
                "icon": icon,
            }},
            "theme": "Static Icon",
            "children": [],
        })
    title_x = 64 if icon else 30
    children.append({
        "type": "static_content",
        "ui": {"value": {
            "style": {"default": {}}, "custom_style": {},
            "position": position(title_x, 30, inner_w - (title_x - 30), 40,
                                 min_top=11, min_left=10),
            "class": "zcanvas-title-editor",
        }},
        "theme": "Custom Layout",
        "children": [{
            "type": "component",
            "ui": {
                "value": {
                    "style": {"default": {
                        "padding": "0px",
                        "font_size": tokens["font_heading"],
                        "font_family": F_MED,
                        "color": tokens["text"],
                    }},
                    "custom_style": {},
                    "position": position(10, 11, inner_w - 40, 19),
                    "class": "zc_disabled",
                    "value": title,
                },
                "autoheight": False,
            },
            "theme": "Static Text",
            "children": [],
        }],
    })
    children.append(related_list(rl_id, 30, 80, inner_w, h - 110,
                                 recordcount=recordcount))

    return {
        "type": "component",
        "ui": {"value": {
            "style": {"default": {
                "border": "none",
                "background_color": tokens["card_bg"],
                "border_radius": tokens["radius_card"],
                "box_shadow": tokens["shadow"],
            }},
            "custom_style": {},
            "position": position(x, y, w, h, min_top=30, min_left=30),
            "class": "zc-list-component zcautoratio",
            "zcode": {"name": zcode or f"RL-{title}"},
            "related_list": True,
            "count": str(recordcount),
            "editorclass": "zcanvas-loading-component",
        }},
        "theme": "Custom Layout",
        "related_list": True,
        "children": children,
    }


def text_block(x: int, y: int, w: int, h: int, text: str, *,
               tokens: dict = CAMCO, size: str | None = None,
               colour: str | None = None, family: str = F_REG,
               uppercase: bool = False, letter_spacing: str | None = None) -> dict:
    """A free static-text node. The only way to put literal words on a canvas."""
    style = {
        "padding": "0px",
        "background_color": "transparent",
        "font_size": size or tokens["font_body"],
        "font_family": family,
        "color": colour or tokens["text"],
    }
    if letter_spacing:
        style["letter_spacing"] = letter_spacing
    return {
        "type": "static_content",
        "ui": {"value": {
            "style": {}, "custom_style": {},
            "position": position(x, y, w, h, min_left=0, min_top=0),
            "class": "zcanvas-title-editor",
        }},
        "theme": "Custom Component",
        "children": [{
            "type": "component",
            "ui": {"autoheight": False, "value": {
                "style": {"default": style},
                "custom_style": {},
                "position": position(0, 0, w, h),
                "class": "zcanvasuppercase" if uppercase else "zc_disabled",
                "value": text,
            }},
            "theme": "Static Text",
            "children": [],
        }],
    }


def kpi_tile(x: int, y: int, w: int, h: int, label: str, accent: str, *,
             tokens: dict = CAMCO, value_field: tuple[str, str] | None = None,
             value_text: str | None = None, detail: str | None = None,
             big: bool = False) -> dict:
    """White tile with a coloured left edge, an uppercase label and a value.

    The accent stripe is border_left on the tile itself — cheaper than a
    separate node and observed working in the earlier showcase deploy.
    """
    children = [
        text_block(14, 12, w - 30, 16, label, tokens=tokens,
                   size=tokens["font_micro"], colour=tokens["text_muted"],
                   family=F_SEMI, uppercase=True, letter_spacing="0.5px"),
    ]
    vy = 30
    if value_field:
        children.append(field(*value_field, 14, vy, w - 30, 24, tokens=tokens))
    elif value_text is not None:
        children.append(text_block(
            14, vy, w - 30, 30 if big else 24, value_text, tokens=tokens,
            size=tokens["font_big"] if big else tokens["font_kpi"],
            family=F_BOLD if big else F_SEMI))
    if detail:
        children.append(text_block(14, vy + (32 if big else 26), w - 30, 16,
                                   detail, tokens=tokens,
                                   size=tokens["font_micro"],
                                   colour=tokens["text_muted"]))
    return {
        "type": "component",
        "ui": {"value": {
            "style": {"default": {
                "border": "none",
                "border_left": f"4px solid {accent}",
                "background_color": tokens["card_bg"],
                "border_radius": tokens["radius_tile"],
                "box_shadow": tokens["shadow"],
            }},
            "custom_style": {},
            "position": position(x, y, w, h),
            "class": "zc-lsection",
        }},
        "theme": "Custom Layout",
        "children": children,
    }


def icon_chip(x: int, y: int, name: str, bg: str, size: int = 26) -> dict:
    """A rounded coloured square holding a Zoho icon — the card-header chip."""
    return {
        "type": "component",
        "ui": {"value": {
            "style": {"default": {
                "color": "rgba(255, 255, 255, 1)",
                "background_color": bg,
                "border_radius": "8px",
                "font_size": "13px",
            }},
            "custom_style": {},
            "position": position(x, y, size, size),
            "fixed": True,
            "class": "zc-ta-center",
            "zcode": {"name": f"icon_{name}"},
            "icon": name,
        }},
        "theme": "Static Icon",
        "children": [],
    }


def titled_card(x: int, y: int, w: int, h: int, title: str, *,
                tokens: dict = CAMCO, icon: str | None = None,
                accent: str | None = None, count: str | None = None,
                body: list | None = None) -> dict:
    """White rounded card with an icon chip, a title, and optional count pill."""
    accent = accent or tokens["signal"]
    children = []
    tx = 18
    if icon:
        children.append(icon_chip(18, 15, icon, accent))
        tx = 53
    children.append(text_block(tx, 18, w - tx - 60, 20, title, tokens=tokens,
                               size=tokens["font_heading"], family=F_SEMI))
    if count is not None:
        children.append(text_block(w - 56, 19, 38, 18, count, tokens=tokens,
                                   size=tokens["font_micro"],
                                   colour=tokens["text_muted"], family=F_SEMI))
    children.extend(body or [])
    return {
        "type": "component",
        "ui": {"value": {
            "style": {"default": {
                "border": "none",
                "background_color": tokens["card_bg"],
                "border_radius": tokens["radius_card"],
                "box_shadow": tokens["shadow"],
            }},
            "custom_style": {},
            "position": position(x, y, w, h),
            "class": "zc-lsection",
        }},
        "theme": "Custom Layout",
        "children": children,
    }


def timeline(x: int, y: int, w: int, entries: list[tuple[str, str]], *,
             tokens: dict = CAMCO, accent: str | None = None,
             step: int = 46) -> dict:
    """Vertical event rail. Each entry is (headline, meta).

    The rail is a 2px left border on a tall thin component; each dot is a small
    bordered circle. Static — Canvas cannot bind these to live activity.
    """
    accent = accent or tokens["signal"]
    nodes = []
    for i, (head, meta) in enumerate(entries):
        ey = i * step
        nodes.append({
            "type": "component",
            "ui": {"value": {
                "style": {"default": {
                    "background_color": tokens["card_bg"],
                    "border": f"2px solid {accent}",
                    "border_radius": "50%",
                }},
                "custom_style": {},
                "position": position(0, ey + 2, 10, 10),
                "class": "zc-lsection",
            }},
            "theme": "Custom Layout",
            "children": [],
        })
        nodes.append(text_block(22, ey, w - 30, 17, head, tokens=tokens,
                                size="12.5px", family=F_SEMI))
        nodes.append(text_block(22, ey + 18, w - 30, 16, meta, tokens=tokens,
                                size="11.5px", colour=tokens["text_muted"]))
    return {
        "type": "component",
        "ui": {"value": {
            "style": {"default": {
                "border": "none",
                "border_left": f"2px solid {tokens['hairline']}",
                "background_color": "rgba(0,0,0,0)",
            }},
            "custom_style": {},
            "position": position(x, y, w, max(len(entries) * step, step)),
            "class": "zc-lsection",
        }},
        "theme": "Custom Layout",
        "children": nodes,
    }


def chip(x: int, y: int, w: int, text: str, *, tokens: dict = CAMCO,
         bg: str | None = None, colour: str | None = None,
         h: int = 24) -> dict:
    """A rounded pill — used for tags and status labels. Static text."""
    return {
        "type": "component",
        "ui": {"value": {
            "style": {"default": {
                "background_color": bg or "rgba(241, 245, 249, 1)",
                "border": "none",
                "border_radius": tokens["radius_pill"],
            }},
            "custom_style": {},
            "position": position(x, y, w, h),
            "class": "zc-lsection",
        }},
        "theme": "Custom Layout",
        "children": [text_block(0, 4, w, 16, text, tokens=tokens,
                                size="11.5px", family=F_SEMI,
                                colour=colour or tokens["text_2"])],
    }


def separator(x: int, y: int, size: int = 10) -> dict:
    return {
        "type": "separator",
        "ui": {"value": {
            "style": {"default": {"padding": "5px"}},
            "custom_style": {},
            "position": position(x, y, size, size),
            "class": "zcanvas-seperator",
            "value": "",
        }},
        "children": [],
    }
