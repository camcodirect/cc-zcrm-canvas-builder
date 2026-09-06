# Canvas geometry rules — DRAFT, DO NOT RELY ON

> **Status: parked 2026-09-04. Not validated. Do not build against this file.**
>
> Every observation here comes from **exactly one canvas** — a simple Accounts detail view. That
> is a sample size of one, and John has correctly pushed back that it is not enough to describe
> how Canvas geometry actually works. More captures of differently-configured canvases are needed
> before any of this can be stated as a rule.
>
> **What is probably still true** (arithmetic measured within the sample, unlikely to change):
> the `end_x = start_x + width` invariant, the `Canvas Data Table` cell/field coordinate
> duplication, the cumulative row stacking in that table, `depth` not tracking nesting level.
> Even these are "true of this canvas", not "true of Canvas".
>
> **What was wrong and is now removed:** the claim that Canvas is purely absolute positioning with
> fixed heights and no flow or reflow. Contradicting evidence was visible in the sample and I
> failed to weigh it — `autoheight` exists as a node key, `layoutstyle.field.width` is `"100%"`,
> table columns are sized by `percent`, and the builder has a Responsive Mode. Canvas clearly has
> some relative/derived sizing. Its rules are unknown.
>
> Re-derive the whole document once more captures exist. See `mistakes.md`.

---

## 1. The model

**UNKNOWN — previously overstated.** The sample canvas positions everything with explicit
`start_x` / `start_y` / `width` / `height`, so absolute placement is clearly *available*. Whether
it is the *only* mode is contradicted by the evidence above and must be established from more
captures.

Open: what does `autoheight` do; when is `width: "100%"` or a `percent` honoured over the pixel
`width`; what changes between Default and Responsive mode; whether anything reflows.

```jsonc
"position": {
  "start_x": 28, "start_y": 159,   // top-left, relative to parent (see §3)
  "end_x": 346,                    // MUST equal start_x + width (see §2)
  "width": 318, "height": 347,     // fixed
  "depth": 1,                      // z-order, NOT nesting level (see §6)
  "order": 0,                      // sequence among siblings (see §5)
  "min_top": 30, "min_left": 30,   // inner padding for children (see §7)
  "over_top": -39, "over_left": 0  // negative pull, overlaps the previous box
}
```

`start_x`, `start_y`, `end_x`, `width`, `height`, `depth` appear on all 202 positioned nodes.
`order` on 113, `min_top` 22, `min_left` 21, `over_top`/`over_left` 1 each.

---

## 2. The `end_x` invariant

```
end_x == start_x + width
```

Verified across all 202 positioned nodes. **Exactly one exception — the root:**

```jsonc
"position": { "start_x": 0, "width": 1440, "end_x": 4320, "height": 2229, "depth": 1 }
```

4320 = 3 × 1440, the three responsive breakpoints. Only the root does this. Every descendant must
satisfy the invariant, and a generator should assert it before sending.

There is no `end_y`. Vertical extent is `start_y + height`, never stored.

---

## 3. Coordinate space: parent-relative, with one exception

Child coordinates are **relative to the parent's box**, so a child at `start_x: 0` sits at the
parent's left edge, not the canvas's.

**Exception — `Canvas Data Table` cells.** Inside a related list themed `Canvas Data Table`, a
`table_cell` and its `field` child carry **identical** coordinates, and those are in *table* space,
not cell space:

```jsonc
{ "type": "table_cell", "ui": {"value": {"position": {"start_x": 90, "width": 200, "height": 41}}},
  "children": [
    { "type": "field", "ui": {"value": {"position": {"start_x": 90, "width": 200, "height": 41}}} }
  ] }
```

Verified on all 4 occurrences: identical in every case, zero differing. The field does **not** reset
to `start_x: 0`. Columns therefore accumulate across the table (90 → 290 → 490 → 690), which reads as
"overflowing the parent" if you check containment naively. It is correct.

Everywhere else, treat a child that extends past its parent's width as a bug.

---

## 4. Canvas dimensions

| | |
|---|---|
| Root width | **1440** |
| Root height | 2229 in the capture — set it to the actual content extent |
| Root `end_x` | 4320 (3 × 1440) |

Root height is not magic; it must cover the lowest `start_y + height` of the content. Compute it
last, from the finished tree.

---

## 5. `order` — sequencing siblings

`order` is a 0-based index among siblings. It appears in two contexts and means something different
in each:

**Table rows — order matches vertical stacking.** Rows in a `Table Layout` stack cumulatively:

```
order=0  start_y=0    height=29
order=1  start_y=29   height=29
order=2  start_y=58   height=29
…
order=8  start_y=232  height=29
```

`start_y` of row *n* = Σ heights of rows 0..n-1. Verified exactly across all 9 rows.

**Tabs — order sequences, but tabs do NOT stack.** Only one tab body is visible at a time, so they
share a layer. In the capture, tab 0 sits at `start_y: 0` and **every other tab sits at
`start_y: 352`** — the same value, not accumulating:

```
order=0  General        start=(0,0)    1038x705
order=1  Zoho Finance   start=(0,352)  1038x352
order=2  Resources      start=(0,352)  1038x352
order=3  Proposals      start=(0,352)  1038x352
order=4  Zoho Projects  start=(0,352)  1038x352
order=5  All Fields     start=(0,352)  1038x352
```

Do not compute cumulative offsets for tab children. Give the first tab its own geometry and every
subsequent tab the same shared offset. `order` alone determines the visible sequence in the tab strip.

---

## 6. `depth` is z-order, not nesting

`depth` is 1 on nearly every node regardless of how deeply nested it is. Measured by nesting level:

```
level 0 -> [1]        level 3 -> [1]
level 1 -> [1, 2]     level 4 -> [1]
level 2 -> [1, 2]     level 5 -> [1]
                      level 6 -> [1]
```

Level 6 nodes still carry `depth: 1`. Use `1` by default; `2` appears on the Tab Layout containers
that need to sit above sibling content. **Do not set `depth` to the nesting level** — that is the
obvious wrong inference.

---

## 7. `min_top` / `min_left` and `over_top` / `over_left`

`min_top` / `min_left` are **inner offsets applied to a container's children** — effectively
padding. Tab bodies overwhelmingly use `min_top: 30, min_left: 30`; the All Fields tab uses
`10 / 20`. A child inside such a container starts at that inset (the list component inside a tab
body sits at `start_x: 30, start_y: 30`).

`over_top` / `over_left` are **negative pulls** that let a box overlap the one before it. Only one
occurrence: the first Tab Layout has `over_top: -39`, lifting the tab strip to sit flush against
the section above. Use sparingly and only when a deliberate overlap is wanted.

---

## 8. Composite geometry

### Table Layout

```
component theme="Table Layout"  (width W, height H)
  ui.value.layoutstyle = { row: {height: "29px"},
                           field: {width: "100%"},
                           inner: [{percent: 42.038216560509554}] }
  └── row (start_y = cumulative, height = row height, order = index)
        └── field (start_x 0, width = row width)
```

- Row height is set in **two places** and they must agree: `layoutstyle.row.height` (a CSS string,
  `"29px"`) and each row's `position.height` (a number, `29`).
- `layoutstyle.inner[].percent` sets the label/value column split — 42.04% in the capture.
- **Table height exceeds the sum of row heights**: 347 vs 261 (9 × 29), a difference of 86 for
  header and padding. Do not compute table height as just the row sum.

### Tab Layout

```
component theme="Tab Layout"  (the strip + bodies)
  └── component theme="Custom Layout"   <- one per tab
        ui.value.name  = "Zoho Finance"   (the tab label)
        position.order = 1                (sequence)
        position.min_top / min_left = 30  (body padding)
```

Tab bodies are all the same width as the Tab Layout (1038). Heights vary; the first tab is tallest
(705) and the rest share 352. See §5 for why they do not stack.

### Section (`zc-lsection`)

Plain absolutely-positioned containers. The capture's three top-level sections:

```
header   start=(0,0)    1440x78
left col start=(0,78)   368x1551
right    start=(368,78) 1072x40
```

These **do** tile without overlap — a header band across the full width, then two columns beneath it.

---

## 9. Generator checklist

Assert all of these before sending a payload:

1. `end_x == start_x + width` on every node except the root.
2. Root `width == 1440`, root `end_x == 4320`.
3. Every child fits inside its parent — **except** `Canvas Data Table` cell/field pairs (§3).
4. Table rows: `start_y` = cumulative sum of prior row heights; `order` = index.
5. Table `layoutstyle.row.height` (string, `"29px"`) matches row `position.height` (number, `29`).
6. Tab children share a layer — do not accumulate their `start_y`.
7. `depth` defaults to 1; never set it from nesting level.
8. Root height covers the maximum `start_y + height` in the tree.
9. No two siblings overlap unless `over_top` / `over_left` is deliberate.
10. Node count sent == `len(details.children)` in the response (see `canvas-json-structure.md` §10).

---

## 10. Known gaps

- **Responsive breakpoints.** Root `end_x` of 4320 implies three widths, but the capture only ever
  describes one. How the other two are expressed is unobserved.
- **Height overhead constants.** The table's 86px of header/padding was measured on one table. It
  may be theme-dependent.
- **Whether Zoho validates geometry on write.** Unknown — every capture so far is a success path,
  so we do not know if a malformed box is rejected or silently rendered wrong.
