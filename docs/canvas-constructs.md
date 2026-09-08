# Canvas constructs, as the Zoho editor emits them

**Evidence base.** Two recorded editor sessions (25 consecutive saves, one construct added per
save), Zoho's own preset JSON served to the editor, and the three gallery templates. Everything
below is what the editor actually writes, not an inference from a finished canvas. Sources:

- `reference/ui-capture/round-1/` and `round-2/`: the 25 PUT bodies and their responses
- `reference/zoho-assets/`: presets (text, field, section, tab, button, related list, table),
  four ReusableViews, the components palette, and the 231-name icon catalog
- `reference/captures/`: the three gallery templates

Companion to `canvas-json-structure.md` (envelope, request, response). This file is the
per-construct shape reference for the builders.

---

## 1. Layout engines

Canvas has three container layout modes. The earlier claim that it is purely absolute was wrong.

| Theme | Class | Children positioned by |
|---|---|---|
| `Custom Layout` | `zc-lsection`, `zc-list-component`, `zc-tab-section` | absolute `position` (pixels, parent-relative) |
| `Flex Layout` | `zc-flex-component zc-flex-direction-column` | flex; children carry `property.flex_item` and `order` |
| `Grid Layout` | `zcanvas-grid-container` | grid; container carries `property.grid` |

Absolute is the default and covers every gallery template. Flex and Grid are opt-in from the
Elements panel. Within an absolute container the arithmetic from `geometry-rules.DRAFT.md` has held
across all 25 saves: `end_x == start_x + width` on every non-root node, root `end_x == 3 × width`.

### Flex container

```jsonc
{ "type": "component", "theme": "Flex Layout",
  "ui": { "value": {
    "style": { "default": { "box_shadow": "none", "background_color": "transparent",
                            "border": "none", "padding": "5px" } },
    "custom_style": {},
    "position": { "start_x": 535, "start_y": 621, "end_x": 1029, "width": 494, "height": 866,
                  "depth": 1, "min_top": 5, "min_left": 5 },
    "class": "zc-flex-component zc-flex-direction-column zc-fit-height-content",
    "property": { "flex": { "default": {
        "direction": "column", "space_distribute": "_normal",
        "alignment": "topleft", "wrap": "nowrap" } } }
  } },
  "children": [ /* items */ ] }
```

A freshly dropped, empty flex container has `"property": {"flex": {}}` and `zcode.name` of
`flexNaN` (an editor quirk; keep it if copying). `zc-fit-height-content` makes the container grow
to its children. That is the first observed content-driven height in Canvas.

### Flex item

Any child of a Flex Layout gains:

```jsonc
"property": { "flex_item": { "default": { "h_stretch": false, "v_stretch": false, "align_self": "" } } }
```

and `position.order`. `h_stretch: true` adds class `zc-flex-self-column-horizontal-grow` on the
item. Items still carry a full `position` block; the editor writes it, so keep it.

### Grid container

```jsonc
{ "type": "component", "theme": "Grid Layout",
  "ui": { "value": {
    "style": { "default": { "border": "1px solid rgb(215, 226, 237)",
                            "background_color": "rgba(248, 250, 255, 1)",
                            "box_shadow": "none", "border_radius": "10px" } },
    "custom_style": {},
    "position": { "start_x": 621, "start_y": 243, "end_x": 1073, "width": 452, "height": 357, "depth": 1 },
    "class": "zcanvas-grid-container",
    "zcode": { "name": "grid1" },
    "property": { "grid": { "default": {
        "column_gap": "5px", "row_gap": "5px",
        "block_width_count": [ { "order": 11 } ],
        "block_height_px": "20px" } } }
  } },
  "children": [] }
```

Only an empty grid was captured. Grid item shape is **unobserved**.

---

## 2. Containers and cards

### Card (Elements panel, "section")

One `Custom Layout` component with class `zc-lsection`. Children sit directly inside it. The
editor stamps `_section_version_: 1` into `style.default` and gives it a `zcode.name`.

```jsonc
{ "type": "component", "theme": "Custom Layout",
  "ui": { "value": {
    "style": { "default": { "_section_version_": 1 } },
    "custom_style": {},
    "position": { "start_x": 390, "start_y": 748, "end_x": 808, "width": 418, "height": 168,
                  "depth": 1, "min_top": 9, "min_left": 5 },
    "class": "zc-lsection",
    "zcode": { "name": "section11" } } },
  "children": [ /* fields, static text, ... */ ] }
```

Section presets (`section-preset.json`, 25 styles) are all variations of `border`,
`background_color`, `border_radius`, `box_shadow`, `background_image` in `style.default`.

### Static text

Sits **directly** inside a container. The editor does not wrap it. `value` may contain HTML.

```jsonc
{ "type": "component", "theme": "Static Text",
  "ui": {
    "value": {
      "style": { "default": { "background_color": "rgba(239, 177, 22, 1)" } },
      "custom_style": {},
      "position": { "start_x": 5, "start_y": 9, "end_x": 409, "width": 404, "height": 38, "depth": 1 },
      "class": "",
      "zcode": { "name": "text1" },
      "value": "<span style=\"font-family: Zoho_Puvi_ExtraBold;\">CARD TITLE</span>" },
    "autoheight": true },
  "children": [] }
```

`autoheight: true` lets the text box grow to its content. Related-list card titles use
`autoheight: false` with class `zc_disabled` (not user-editable). The `static_content` +
`zcanvas-title-editor` wrapper does exist, but only as the **title block of a related-list card**
(see §4). Gallery template c1 also uses a `static_content`/`Custom Component` wrapper for
standalone headings; both forms are accepted, the bare form is what the editor produces today.

Text presets (`text-preset.json`) are seven `style.default` blocks: chips with background and
radius, gradient banner text, outlined text, and three grey headings (22/18/15px, `font_family: b`).

### Static icon

```jsonc
{ "type": "component", "theme": "Static Icon",
  "ui": { "value": {
    "style": {}, "custom_style": {},
    "position": { "start_x": 97, "start_y": 77, "end_x": 111, "width": 14, "height": 14, "depth": 1 },
    "fixed": true, "class": "zc-ta-center",
    "zcode": { "name": "icon1" },
    "icon": "icon-Icon_Fiber" } },
  "children": [] }
```

**`icon` must be one of the 231 names in `reference/zoho-assets/icon-catalog.txt`.** Names are
case-sensitive and irregular (`icon-Icon_Calender`, `icon-Icon_Notes`, `icon-Icon_task`,
`icon-Icon_Location`). Colour and size go in `style.default.color` / `font_size`. Names observed in
real canvases: `dot_three`, `plus`, `Back`, `Fiber`, `Status`, `Money`, `Customerprofile`,
`Dollar`, `Calender`, `Clock`, `Account`.

### Line

```jsonc
{ "type": "component", "theme": "Line",
  "ui": { "value": { "style": {}, "custom_style": {},
    "position": { "start_x": 384, "start_y": 821, "end_x": 525, "width": 141, "height": 3, "depth": 1 },
    "fixed": true, "class": "", "zcode": { "name": "line1" }, "vertical": false } },
  "children": [] }
```

### Image

Uploaded through `POST /crm/v2.2/settings/canvas_files?feature=background_image`, which returns
`{file_id, id}`. The canvas references the numeric `id` through the `$Image{...}` macro.

```jsonc
{ "type": "component", "theme": "Canvas Image",
  "ui": {
    "value": { "style": { "default": { "background_image": "url($Image{2582206000076736002})" } },
               "custom_style": {},
               "position": { "start_x": 111, "start_y": 798, "end_x": 231, "width": 120, "height": 120, "depth": 1 },
               "fixed": true, "class": "zcanvas-field zcbdrbox zc-cover-Image",
               "zcode": { "name": "image1" } },
    "field": { "style": { "default": { "background_image": "none" } }, "custom_style": {}, "class": "" },
    "image": { "style": { "default": { "src": "$Image{2582206000076736002}" } } } },
  "children": [] }
```

`GET /crm/v2.2/settings/canvas_files?feature=background_image` lists the org's uploaded files.

### Separator

```jsonc
{ "type": "separator",
  "ui": { "value": { "style": { "default": { "padding": "5px" } }, "custom_style": {},
    "position": { "start_x": 190, "start_y": 11, "end_x": 200, "width": 10, "height": 10, "depth": 1 },
    "class": "zcanvas-seperator", "value": "" } },
  "children": [] }
```

---

## 3. Fields

A field dropped into a card:

```jsonc
{ "id": "2582206000000002489", "datatype": "text", "type": "field",
  "ui": {
    "value": { "style": { "default": {} }, "custom_style": {},
               "position": { "start_x": 18, "start_y": 59, "end_x": 154, "width": 136, "height": 39, "depth": 1 } },
    "holder": { "style": { "default": { "flex_direction": "column" } }, "custom_style": {}, "class": "" },
    "field":  { "style": {}, "custom_style": {}, "class": "" },
    "label":  { "style": {}, "custom_style": {}, "class": "" } },
  "children": [] }
```

`holder` is the label+value wrapper, `field` the value, `label` the label. `flex_direction:
column` stacks label over value; `column-reverse` puts the value first. Field presets
(`field-preset.json`, nine styles) restyle those three sub-parts plus `value`. Some preset entries
carry `"$inherited": true`, an editor hint that the sub-part inherits the parent style.

Fields inside a related list add class `zc-rl-field` and resolve against the **related** module.

**Boolean fields** carry nothing beyond `datatype: "boolean"` in any of the 33 files: no class, no
style. Zoho renders its own checkbox. There is no toggle-switch element in Canvas.

**`custom_style`** (the editor's Custom CSS box) is present on every slot and empty in every
observed file. Its populated shape is unknown; do not emit it. One recorded save with a single
custom CSS property would settle it.

### Query-backed fields (Data Hub)

A related list built from a saved Query has no `id`. It and its fields carry `details`:

```jsonc
{ "type": "relatedlist", "theme": "Custom Layout",
  "ui": { "value": { "style": { "default": {} }, "custom_style": {},
    "position": { "start_x": 30, "start_y": 80, "end_x": 320, "width": 290, "height": 144,
                  "depth": 1, "min_top": 13, "min_left": 17 },
    "class": "zcanvas-non-delete" }, "canvas_rules": [] },
  "details": { "connection_id": "00803ee3-…", "connection_type": "data_hub_associations" },
  "children": [
    { "datatype": "text", "type": "field",
      "details": { "connection_id": "00803ee3-…", "connection_type": "data_hub_associations",
                   "path": "$.First_Name" }, "ui": { /* as a normal rl field */ }, "children": [] } ] }
```

and the root `related_to.data_hub_associations` becomes non-null:

```jsonc
"related_to": { "data_hub_associations": [ {
    "config": { "display_type": "related_list" },
    "connection_id": "00803ee3-…",
    "data_hub": { "name": "testq query", "query_uuid": "7679d2e3-…" },
    "name": "test query" } ],
  "homepage_associations": null, "lookup_associations": null }
```

The `zcode.name` for that card was `RL-testq&#x20;query`: spaces in zcode names are HTML-entity
encoded.

---

## 4. Related lists

Three renderings, all with `type: "relatedlist"` and `id` = the related-list id from
`GET /crm/v8/settings/related_lists?module=…` (or the literal `timeline`).

### a) Full list inside a tab (`Table Layout`, empty children)

```jsonc
{ "id": "2582206000000003801", "type": "relatedlist", "theme": "Table Layout",
  "ui": { "value": { "position": { … }, "style": {}, "recordcount": "10" },
          "context": { "notes_footer": {}, "notes_title": {}, "notes_content": {},
                       "notes_separator": {}, "notes_link": {} },
          "canvas_rules": [] },
  "children": [] }
```

Zoho renders its own table. `context` keys are list-type specific (Notes has `notes_*`;
Timeline and Closed Meetings carry `context` too; Emails carries `personality_name` at node
level).

### b) Card with chosen columns (`Custom Layout` with field children)

The Elements panel produces this 9-node shape when you drop a related list. Structure:

```text
component  .zc-list-component  theme=Custom Layout  related_list=true  count="5"
           zcode.name="RL-<Display Label>"  editorclass="zcanvas-loading-component"
  static_content  .zcanvas-title-editor  theme=Custom Layout        (the title block)
    component  Static Text  .zc_disabled  value="<Display Label>"  autoheight=false
    action  id="moreRLActions<rl_id>"  datatype=button             (the ⋯ button, ui.icon = icon-Icon_dot_three)
  relatedlist  id=<rl_id>  theme=Custom Layout  .zcanvas-non-delete  recordcount="5"
    field ×N   .zcanvas-field .zc-rl-field  (columns; ids belong to the related module)
```

Both the card and the `relatedlist` node carry `related_list: true` (card) / `recordcount`
(list). `count` on the card and `recordcount` on the list are strings. The `moreRLActions` action
has `ui.holder`, `ui.field` and `ui.icon` sub-blocks and the long class
`zcanvas-field zcanvas-no-img-default zc-ta-center zccbutton zccrlaction zc-rl-field zccbuttonicon zccbuttonnotext zc-only-icon`.

`relatedlist-preset.json` holds six card presets; each is `{container, title, relatedlist,
context}` where `context.table_head / table_column / table_row / table_link` style the list
chrome. Preset 1 and 5 have an empty `relatedlist.children` (Zoho renders columns); 2, 3, 4, 6
carry explicit field children.

### c) Data table (`Canvas Data Table`)

```text
relatedlist  id=<rl_id>  theme=Canvas Data Table  .zc-submodule-list  recordcount="5"
  ui.layoutstyle = { head: {"$height": "40px"}, row: {"$height": "40px"} }
  ui.{row, header, row_odd, row_even, static_column_*} style blocks
  table_cell ×N   (one per column; position in TABLE space)
    field  (same coordinates as its table_cell; ui.field_odd / ui.field_even)
```

`table-preset.json` has three table presets with `style.rows[]` striping and per-column
`label_cells` / `value_cells` styling.

**Duplicates are legal.** The editor itself placed the same related list twice (once as a card,
once as a data table) and saved without complaint.

---

## 5. Tabs

### New tab strip

```jsonc
{ "type": "component", "theme": "Tab Layout",
  "ui": { "value": {
    "style": {}, "custom_style": {},
    "position": { "start_x": 35, "start_y": 1082, "end_x": 1190, "width": 1155, "height": 300, "depth": 1 },
    "class": "zcanvas-horizantol-top zcanvas-subtab-push",
    "zcode": { "name": "tab1" },
    "layoutstyle":        { "default": {}, "hover": {}, "active": {}, "tabname": {}, "tabicon": {}, "container": {}, "editor": {} },
    "custom_layoutstyle": { "default": [], "hover": [], "active": [], "tabname": {}, "tabicon": {}, "container": {}, "editor": {} } } },
  "children": [
    { "type": "component", "theme": "Custom Layout",
      "ui": { "value": { "style": {}, "custom_style": {},
                "position": { "start_x": 0, "start_y": 0, "end_x": 1155, "width": 1155, "height": 255,
                              "depth": 1, "min_top": 66, "min_left": 97, "order": 0 },
                "class": "zc-tab-section", "name": "Unnamed Tab" },
              "tab_item_title": { "class": "" } },
      "children": [] } ] }
```

Note `custom_layoutstyle` uses **arrays** for `default/hover/active` and objects for the rest.
The `layoutstyle` states are: `default`, `hover`, `active` (the tab chip), `tabname`, `tabicon`,
`container` (the strip), `editor` (the tab body panel).

### Tab body

`class` distinguishes body kinds:

| Tab kind | class | extra keys |
|---|---|---|
| custom | `zc-tab-section` | |
| related list | `zc-tab-section zc-tabrl-container` | node: `tab_relatedlist_id`; value: `disabled: true` |
| All Fields | `zc-tab-section zc-tab-all-fields zc-tabrl-container` | value: `disabled: true`; ui: `allfieldstabstyle: {}`; children: one `section` per layout section |

Tab bodies share a layer. Tab 0 gets the full height; every other tab sits at
`start_y == its own height`. Held on all 5 strips observed.

### Properties panel → class tokens (round 2, saves 1 to 9)

| Panel control | Tokens on the Tab Layout `class` |
|---|---|
| Orientation: horizontal top | `zcanvas-horizantol-top` (Zoho's spelling) |
| Orientation: vertical left | `zcanvas-vertical-left` |
| Orientation: vertical right | `zcanvas-vertical-right` |
| Tab navigation: both sides | + `zcanvas-tab-splitnav` |
| Sub tab action: single expand | + `zcanvas-single-subtab` |
| always present | `zcanvas-subtab-push` |
| hide / show toggle | `style.default._hide_: "true"` or `_show_: "true"` |

Switching to vertical bumped the strip's `depth` from 1 to 6. Styling the tab container writes
`layoutstyle.editor.default` (`margin`, `padding`, `border_radius`, `box_shadow`,
`background_color`). Tab presets (`tab-preset.json`, seven) fill `default/hover/active` for the
chip and `container`/`editor` for the frame.

---

## 6. Buttons and actions

### Custom button (Elements panel)

```jsonc
{ "type": "component", "theme": "Canvas Button",
  "ui": { "value": { "style": { "default": {} }, "custom_style": {},
    "position": { "start_x": 153, "start_y": 66, "end_x": 244, "width": 91, "height": 33, "depth": 1 },
    "class": "zcanvas-field zcanvas-no-img-default zc-ta-center zccbutton", "name": "Button" },
    "field": { "style": {}, "custom_style": {}, "class": "" } },
  "children": [] }
```

Button presets (`button-preset.json`, 30) are `field.default` / `field.hover` style pairs plus a
`field.class` list. A CRM custom button (from Setup) is `type: "button"` with a numeric id
instead.

### System action

```jsonc
{ "id": "data_enrichment", "datatype": "button", "type": "action",
  "ui": { "value": { "style": { "default": {} }, "custom_style": {},
    "position": { "start_x": 315, "start_y": 1071, "end_x": 438, "width": 123, "height": 33, "depth": 2 },
    "class": "zcanvas-no-img-default zc-ta-center zccbutton" },
    "field": { "style": {}, "custom_style": {}, "class": "" } },
  "children": [] }
```

**Valid `id` values come from the components palette**
(`reference/zoho-assets/components-palette-contacts-detailview.json`). Available on Contacts
DetailView: `edit`, `clone`, `findandmerge`, `send_mail`, `delete`, `mail_merge`, `share`,
`macro`, `callnow`, `sendDM`, `meetnow`, `scheduleonlinemeeting`, `inviteClientPortal`,
`data_enrichment`, `askzia_contextual`, `navigate`, `back`, `print_preview`, `morebutton`,
`reviewHistory`, `locatemap`, `lock`, `cadence`, `create_client_script`, `cliq`. Plus the
generated `moreRLActions<related_list_id>`. The palette also lists `system` components
(`stage_navigator`, `blueprint`, `timeline`, `tag`, `upcoming_actions`, …) and `zia` components;
their node shapes are unobserved. Fetch the palette per module; availability differs.

### MERGEFIELD (inline button group)

```text
component  theme=MERGEFIELD  .zc-merge-hright   position: normal
  component  .zcanvas-row-seperator   position: {}        ← empty position is legal here
    action / separator / action ...
```

---

## 7. `uniqueid`

Present on 219 of 467 nodes in the editor's own save. Containers, rows, sections, actions,
static text and related lists carry it; most `field` nodes and all typeless wrappers do not. So:
send it when you have it (updates), never fabricate it, and do not treat its absence as an error.
The server returns one per node it kept and preserves every one you sent.

---

## 8. Style vocabulary additions (beyond `canvas-json-structure.md` §6)

Properties: `margin`, `margin_right`, `background_size`, `letter_spacing` (**unobserved, avoid**),
`_show_`, `_hide_`, `_section_version_`, `$height` (table head/row), `$inherited` (presets only).
Values: `font_family` codes `r m s b`; `background_image` may be a `linear-gradient(...)`, a
`url(/crm/CRMClient/images/canvas/banner.png)`, or `url($Image{id})`.

Class strings may contain **template expressions** on mirror fields:
`{{if(hidedLookups[<id>],'hide','')}} {{getMirrorFieldClasses('<a>_<b>',lookupFieldIdsWithHiddenRecord)}}`.
Never normalise or dedupe class strings.

---

## 9. Round-3 additions (lookup All-Fields, system lists, nested tab groups)

### Lookup All-Fields tab

"All Fields - Account Name": shows the looked-up record's fields. The editor creates it empty; the
server fills it at render. It needs a `lookup_associations` entry in root `related_to` (§ schema
doc) and a `details` reference on the tab body.

```jsonc
{ "type": "component", "theme": "Custom Layout",
  "ui": { "value": { "style": {}, "custom_style": {},
            "position": { "start_x": 14, "start_y": 14, "end_x": 1099, "width": 1085, "height": 480,
                          "depth": 1, "min_top": 10, "min_left": 20, "order": 3 },
            "class": "zc-tab-section zc-tab-lookup-all-fields zc-tabrl-container",
            "name": "All Fields - Broker Company Name", "disabled": true },
          "allfieldstabstyle": {}, "tab_item_title": { "class": "" } },
  "details": { "connection_type": "lookup_associations", "connection_id": "0065650d-…" },
  "children": [] }
```

The `connection_id` is **minted by the editor in the browser**, not issued by the server: in the
round-1 HAR it appears fully formed in the first PUT that carries the tab and in no response
before it. Every observed id starts with `00`. A builder can mint its own (`"00" + uuid4()[2:]`,
see `src/build_proposals_v1.py`); the server accepted and returned one on Proposals 2026-09-07.
The tab name follows the editor's pattern `All Fields - <lookup field label>`.

### System components as related lists

Palette `system` entries are placed exactly like a related list, with a string id. Observed:
`timeline`, `journeys` (label "Interactions"). The tab body has `tab_relatedlist_id: "journeys"`
and the card holds `relatedlist` `id: "journeys"`, theme `Table Layout`, `children: []`.

### Nested tab group ("Sub Tab")

A `Tab Layout` placed as a child of the strip, with `class: "zc-tab-section"`, a `name`, its own
`layoutstyle` / `custom_layoutstyle`, and `tab_item_title.class: "zc-tabgroup"`. It arrives at
2 × 2 px and grows when tabs are added inside it (contents **unobserved**).

### Other round-3 facts

- Canvas Image gained the class token `zclayout` on re-save (`zcanvas-field zcbdrbox zc-cover-Image zclayout`).
- Cloning a card duplicates its `uniqueid`s within the payload; the server accepts that.
- `related_to.lookup_associations[]` = `{ connection_id, parent_module_lookup_field: {api_name, id}, child_module: {api_name, id} }`.

---

## 10. Still unobserved

- Grid item shape (only an empty grid was captured)
- `system` and `zia` palette components (`blueprint`, `stage_navigator`, `zia_score`, …)
- Responsive Mode payload (root `end_x == 3 × width` is the only trace)
- Populated `canvas_rules` / `script_info`
- Error responses from the save endpoint
- Populated `custom_style` (Custom CSS); the components palette for any module but Contacts
  (endpoint is browser-session only, 401 over OAuth)
- An All Fields tab for any module but Contacts (the editor generates it; the one on file is
  Contacts-shaped and cannot be reused elsewhere)
