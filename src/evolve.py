"""Incremental canvas evolution — one verified change at a time.

The from-scratch generator produced canvases the API accepted but the Zoho
editor could not open. Three deploys, three different structural requirements
discovered the hard way. This tool takes the opposite approach: start from the
canvas that is live and working, apply ONE named change, deploy, and stop so a
human can confirm the editor still opens.

    python src/evolve.py list                    # what steps exist
    python src/evolve.py <step>                  # dry run: show the diff
    python src/evolve.py <step> --execute        # apply it

Every step is a pure function: live canvas view in, mutated view out. It must
not add or remove nodes unless that is the explicit point of the step, and the
diff is printed before anything is sent.
"""

from __future__ import annotations

import json
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from noop_deploy import build_request_body  # noqa: E402
from validate import validate  # noqa: E402
from zoho_auth import ZohoAuth  # noqa: E402
from zoho_canvas import CanvasApiError, CanvasClient  # noqa: E402

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CAPTURES = PROJECT_ROOT / "reference" / "captures"
VIEW_ID = "2582206000076641025"


# --------------------------------------------------------------- helpers

def walk(node, fn, path="root"):
    if isinstance(node, dict):
        fn(node, path)
        for i, c in enumerate(node.get("children") or []):
            walk(c, fn, f"{path}/{i}")


def value_of(node) -> dict | None:
    ui = node.get("ui")
    if not isinstance(ui, dict):
        return None
    v = ui.get("value")
    return v if isinstance(v, dict) else None


def profile(view) -> dict:
    types, themes, uids, names, texts = Counter(), Counter(), [], [], []
    total = [0]

    def visit(n, _p):
        total[0] += 1
        types[n.get("type")] += 1
        if n.get("theme"):
            themes[n["theme"]] += 1
        if "uniqueid" in n:
            uids.append(n["uniqueid"])
        v = value_of(n)
        if v:
            if v.get("name"):
                names.append(v["name"])
            if n.get("theme") == "Static Text" and v.get("value"):
                texts.append(v["value"])
    walk(view, visit)
    return {"nodes": total[0], "types": types, "themes": themes,
            "uniqueids": uids, "tabs": names, "texts": texts}


def diff_profiles(before: dict, after: dict) -> list[str]:
    out = []
    if before["nodes"] != after["nodes"]:
        out.append(f"node count {before['nodes']} -> {after['nodes']}")
    lost = set(before["uniqueids"]) - set(after["uniqueids"])
    if lost:
        out.append(f"uniqueids LOST: {len(lost)}")
    for key in ("types", "themes"):
        for k in sorted(set(before[key]) | set(after[key]), key=str):
            b, a = before[key].get(k, 0), after[key].get(k, 0)
            if b != a:
                out.append(f"{key[:-1]} {k}: {b} -> {a}")
    if before["tabs"] != after["tabs"]:
        out.append(f"tabs {before['tabs']} -> {after['tabs']}")
    return out


# ----------------------------------------------------------------- steps
# Each takes the live canvas_view dict and mutates it in place.

def step_rename(view: dict) -> str:
    """Rename the canvas. Smallest possible change - proves the loop works."""
    old = view.get("name")
    view["name"] = "Contacts v2"
    return f"name {old!r} -> {view['name']!r}"


def step_banner(view: dict) -> str:
    """Restyle the header band to the bright indigo/sky/teal gradient."""
    notes = []

    def visit(n, path):
        v = value_of(n)
        if not v:
            return
        st = (v.get("style") or {}).get("default") or {}
        # The header band is the full-width section at the top of the canvas.
        p = v.get("position") or {}
        if (n.get("theme") == "Custom Layout"
                and p.get("start_y") == 0 and (p.get("width") or 0) >= 700
                and ("background_image" in st or "background_color" in st)):
            before = st.get("background_image") or st.get("background_color")
            st["background_image"] = ("linear-gradient(115deg, "
                                      "rgb(99, 102, 241) 0%, "
                                      "rgb(14, 165, 233) 55%, "
                                      "rgb(20, 184, 166) 100%)")
            st["background_size"] = "cover"
            st.pop("background_color", None)
            v.setdefault("style", {})["default"] = st
            notes.append(f"{path}: banner {str(before)[:44]} -> indigo/sky/teal")
    walk(view, visit)
    return "; ".join(notes) if notes else "NO BANNER MATCHED - nothing changed"


def step_page_bg(view: dict) -> str:
    """Set the canvas page ground to the cool near-white."""
    v = value_of(view)
    st = (v.get("style") or {}).get("default") or {}
    before = st.get("background_color")
    st["background_color"] = "rgba(245, 248, 252, 1)"
    v.setdefault("style", {})["default"] = st
    return f"page background {before!r} -> {st['background_color']!r}"


STEPS = {
    "rename":  step_rename,
    "banner":  step_banner,
    "page-bg": step_page_bg,
}


# ------------------------------------------------------------------ main

def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    execute = "--execute" in sys.argv

    if not args or args[0] == "list":
        print("Steps:")
        for name, fn in STEPS.items():
            doc = (fn.__doc__ or "").strip().splitlines()[0]
            print(f"  {name:10} {doc}")
        print("\nRun one:  python src/evolve.py <step> [--execute]")
        return 0

    step = args[0]
    if step not in STEPS:
        print(f"Unknown step {step!r}. Try: {', '.join(STEPS)}")
        return 2

    client = CanvasClient(ZohoAuth.from_env())
    live = client.get_view(VIEW_ID)
    view = live["canvas_view"][0]

    before = profile(view)
    print(f"Live canvas : {view.get('name')!r}  {before['nodes']} nodes")
    print(f"Step        : {step}")

    body = build_request_body(live)
    note = STEPS[step](body["canvas_view"][0])
    after = profile(body["canvas_view"][0])

    print(f"Change      : {note}")

    structural = diff_profiles(before, after)
    print("Structural  :", "; ".join(structural) if structural else "none (styling only)")

    errors, warnings = validate(body)
    print(f"Validation  : {len(errors)} errors, {len(warnings)} warnings")
    for e in errors[:10]:
        print(f"   ERROR {e}")
    if errors:
        return 1

    if not execute:
        print("\nDry run. Re-run with --execute to apply.")
        return 0

    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    rb = CAPTURES / f"rollback-{VIEW_ID}-{stamp}.json"
    rb.write_text(json.dumps(live, indent=1), encoding="utf-8")
    print(f"\nRollback    : reference/captures/{rb.name}")

    try:
        resp = client.put_view(VIEW_ID, body, i_understand_this_is_live=True)
    except CanvasApiError as exc:
        print(f"PUT FAILED  : {exc}")
        return 1

    cv = resp.get("canvas_view", [{}])[0]
    print(f"PUT         : {cv.get('code')} {cv.get('status')}")

    check = profile(client.get_view(VIEW_ID)["canvas_view"][0])
    print(f"Live now    : {check['nodes']} nodes")
    print("\n>>> Open the editor and confirm it still works before the next step:")
    print("    https://crm.zoho.com/crm/org647376701/settings/modules/Contacts"
          f"/layouts/2582206000000091033/canvas/{VIEW_ID}/edit?feature=DetailView")
    print(f"\n    If broken: python src/restore.py reference/captures/{rb.name} --execute")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
