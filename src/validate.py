"""Structural validation for a generated canvas_view payload.

Checks the invariants that held across all three real captures. Run this on any
generated body before it goes near the API.

    python src/validate.py <path-to-body.json>
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

# Observed vocabulary. Anything outside these is flagged for review rather than
# rejected outright - the captures are a sample, not the full spec.
KNOWN_TYPES = {"component", "field", "section", "row", "action", "static_content",
               "relatedlist", "link", "table_cell", "button", "separator", "view"}
KNOWN_THEMES = {"Custom Layout", "Custom Component", "Static Text", "Static Icon",
                "Tab Layout", "Table Layout", "Canvas Data Table", "MERGEFIELD"}
SERVER_KEYS = {"componentid", "created_by", "created_time", "modified_by",
               "modified_time", "generated_type", "is_default", "profiles",
               "share", "source"}


def validate(doc: dict) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    cv = doc.get("canvas_view")
    if not isinstance(cv, list) or not cv:
        return ["root: missing canvas_view array"], []
    view = cv[0]

    for key in ("name", "feature", "module", "layout", "children"):
        if key not in view:
            errors.append(f"root: missing required key {key!r}")

    rp = ((view.get("ui") or {}).get("value") or {}).get("position") or {}
    if rp:
        w, ex = rp.get("width"), rp.get("end_x")
        if w and ex and ex != w * 3:
            errors.append(f"root: end_x should be 3x width, got {ex} vs {w}*3={w*3}")

    max_bottom = [0]

    def walk(node, path="root", parent_pos=None, in_datatable=False):
        if not isinstance(node, dict):
            return

        t = node.get("type")
        if t and t not in KNOWN_TYPES:
            warnings.append(f"{path}: unknown type {t!r}")
        th = node.get("theme")
        if th and th not in KNOWN_THEMES:
            warnings.append(f"{path}: unknown theme {th!r}")

        for k in node:
            if k in SERVER_KEYS:
                errors.append(f"{path}: server-owned key {k!r} must not be sent")

        if "children" not in node:
            errors.append(f"{path}: missing children (use [] when empty)")

        val = (node.get("ui") or {}).get("value")
        pos = val.get("position") if isinstance(val, dict) else None

        if isinstance(pos, dict) and pos:
            sx, sy = pos.get("start_x"), pos.get("start_y")
            w, h, ex = pos.get("width"), pos.get("height"), pos.get("end_x")

            # The root is exempt: it uses end_x == 3*width for the responsive
            # breakpoints, checked separately above.
            if path != "root" and None not in (sx, w, ex) and sx + w != ex:
                errors.append(
                    f"{path}: end_x != start_x+width ({sx}+{w}={sx+w}, got {ex})")

            if pos.get("depth") is None:
                warnings.append(f"{path}: position has no depth")

            # NOTE: no containment check. Zoho's own gallery templates (c2, c3)
            # routinely place children past the parent's width - related-list
            # cards especially - and those canvases render correctly. Overflow
            # is therefore legal, not a defect, so flagging it produces only
            # false positives. Data-table cells also repeat parent coordinates
            # in table space by design (see docs §3).

            if path == "root" and None not in (sy, h):
                pass
            elif None not in (sy, h) and parent_pos is None:
                max_bottom[0] = max(max_bottom[0], sy + h)

        nxt = in_datatable or node.get("theme") == "Canvas Data Table"
        for i, c in enumerate(node.get("children") or []):
            walk(c, f"{path}/{i}", pos if isinstance(pos, dict) and pos else parent_pos, nxt)

    walk(view)

    # A related-list id may appear at most once in a canvas. Duplicates are
    # accepted by the save API but crash the Zoho builder UI - it loads as a
    # blank white screen and the canvas becomes uneditable. Verified 2026-09-06.
    rl_ids: dict[str, int] = {}
    tab_rl_ids: dict[str, int] = {}

    def check_related(node, path="root"):
        if isinstance(node, dict):
            if node.get("type") == "relatedlist" and node.get("id"):
                rl_ids[node["id"]] = rl_ids.get(node["id"], 0) + 1
            if node.get("tab_relatedlist_id"):
                t = node["tab_relatedlist_id"]
                tab_rl_ids[t] = tab_rl_ids.get(t, 0) + 1
            for i, c in enumerate(node.get("children") or []):
                check_related(c, f"{path}/{i}")
    check_related(view)

    for rid, n in rl_ids.items():
        if n > 1:
            errors.append(
                f"related-list id {rid} used {n} times - must appear at most once "
                "(duplicates blank-screen the Zoho builder)")
    for rid, n in tab_rl_ids.items():
        if n > 1:
            errors.append(f"tab_relatedlist_id {rid} used {n} times - must be unique")

    # Table Layout: layoutstyle.row.height must match each row's position.height
    def check_tables(node, path="root"):
        if isinstance(node, dict):
            if node.get("theme") == "Table Layout":
                val = (node.get("ui") or {}).get("value") or {}
                ls = val.get("layoutstyle") or {}
                declared = (ls.get("row") or {}).get("height")
                if declared:
                    want = int(str(declared).replace("px", ""))
                    run = 0
                    for i, row in enumerate(node.get("children") or []):
                        rp2 = (((row.get("ui") or {}).get("value") or {})
                               .get("position") or {})
                        if rp2.get("height") not in (None, want):
                            errors.append(
                                f"{path}/{i}: row height {rp2.get('height')} != "
                                f"layoutstyle.row.height {want}")
                        if rp2.get("start_y") not in (None, run):
                            errors.append(
                                f"{path}/{i}: row start_y {rp2.get('start_y')} != "
                                f"cumulative {run}")
                        run += rp2.get("height") or want
            for i, c in enumerate(node.get("children") or []):
                check_tables(c, f"{path}/{i}")
    check_tables(view)

    return errors, warnings


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    doc = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    errors, warnings = validate(doc)

    print(f"Validating {sys.argv[1]}")
    print(f"  errors  : {len(errors)}")
    for e in errors[:30]:
        print(f"    ERROR {e}")
    print(f"  warnings: {len(warnings)}")
    for w in warnings[:30]:
        print(f"    WARN  {w}")
    if not errors and not warnings:
        print("  clean")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
