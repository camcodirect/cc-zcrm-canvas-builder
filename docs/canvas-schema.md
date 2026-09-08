# Zoho CRM Canvas: schema and update reference

The single place to look before building or updating a Canvas view by API. It covers the update
workflow end to end, the request body schema, every observed attribute and where it lives, the
enumerations (types, themes, datatypes, class tokens, action ids, icons), and the rules that
keep a generated canvas openable in the Zoho editor.

**Evidence base.** 33 Zoho-authored payloads: 3 gallery templates and 30 consecutive editor saves
across three recorded sessions (`reference/ui-capture/round-1..3/`), plus Zoho's own preset JSON,
components palette and icon catalog (`reference/zoho-assets/`). Nothing here is inferred from a
single file. Where something has never been observed it is marked **unobserved**; do not emit it.

Three companion files:

- `docs/canvas-constructs.md`: full JSON of each construct as the editor emits it (cards, text,
  icons, fields, related lists, tabs, buttons, flex, grid, image, line, query lists).
- `docs/canvas-key-inventory.md`: machine-generated, every key in every slot with counts, host
  node kinds and most common values. Regenerate it, never hand-edit it.
- `docs/canvas-json-structure.md`: the original envelope/request/response notes (older; this file
  and constructs.md win where they disagree).

---

## 1. The update workflow

Canvas views are **update-only** in this project. Creating a view is done once in the UI; every
change after that is a full-body PUT.

```text
1. Profile the module        getLayouts(module) for fields + sections; GET related_lists for lists
2. Design                    HTML mockup at 1100 px, absolutely positioned (output/.../*.html)
3. Build                     src/build_*.py -> output/<org>/<Module>/<name>.json (+ .meta.json)
4. Validate                  src/validate.py   (schema, icons, action ids, table math)
5. Vocabulary audit          every type/theme/class/key/style in the body must exist in reference/
6. Rollback snapshot         GET the live view -> reference/captures/rollback-<view>-<stamp>.json
7. PUT                       replaces the whole canvas; response = SUCCESS + uniqueid list
8. GET back                  confirm node count / names; NOT sufficient on its own
9. OPEN IN THE EDITOR        the only real verification; a canvas can be valid to the API and
                             unopenable in the UI
10. If broken                python src/restore.py <rollback-file> --execute
```

### Endpoint

```text
GET  https://crm.zoho.com/crm/v8/settings/canvas/views?module=Contacts&feature=DetailView   list
GET  https://crm.zoho.com/crm/v8/settings/canvas/views/{view_id}                            read
PUT  https://crm.zoho.com/crm/v8/settings/canvas/views/{view_id}                            write
Authorization: Zoho-oauthtoken {access_token}      (Bearer also accepted)
Content-Type: text/plain;charset=UTF-8             (body is JSON regardless)
```

OAuth self-client, refresh-token grant, token cached to `.token-cache.json` (Zoho rate-limits the
refresh endpoint). Scope: `ZohoCRM.settings.canvas.ALL` plus read on fields/modules/layouts/
related_lists. Related lists: `GET /crm/v8/settings/related_lists?module={Module}`. Uploaded
images: `GET/POST /crm/v2.2/settings/canvas_files?feature=background_image`.

Other metadata the builders use, all over the same OAuth token (tested 2026-09-07):

```text
GET /crm/v8/settings/modules                                  module ids by api_name
GET /crm/v8/settings/layouts?module={Module}                  sections + fields (api_name, id, data_type)
GET /crm/v8/settings/custom_buttons?module={Module}           204 No Content when the module has none
GET /crm/v8/settings/blueprints?module={Module}               active blueprints and their driving field
GET /crm/v2/settings/canvas/views/components?feature=DetailView&module={Module}&layout_id={id}
                                                              the Elements palette: 401 NOT_ALLOWED over
                                                              OAuth; browser session only. Use the action
                                                              ids in the module's existing canvas instead.
```

### Response

```jsonc
{ "canvas_view": [ { "code": "SUCCESS", "status": "success", "message": "view updated successfully",
    "details": { "id": "<view_id>", "children": [ { "uniqueid": "…" }, … ] } } ] }
```

One `uniqueid` per node the server kept, flat, **not** in document order. The server prunes
typeless wrapper nodes that have no position and no children, so the count can be one or two
short of what was sent. Error response shape: **unobserved**.

### GET vs PUT body

A GET returns server-owned keys that must be **stripped** before sending the body back:
`componentid`, `created_by`, `created_time`, `modified_by`, `modified_time`, `generated_type`,
`is_default`, `profiles`, `share`, `source`. Keep `uniqueid`. A PUT body carries `action: "edit"`,
which GET omits. `src/noop_deploy.py:build_request_body` does exactly this.

---

## 2. Request envelope and root

```jsonc
{ "canvas_view": [ <view> ] }        // always an array with one element
```

| root key | required | value | notes |
|---|---|---|---|
| `name` | yes | string | shown in Setup → Canvas |
| `feature` | yes | `"DetailView"` | only value observed |
| `type` | yes | `"component"` in PUT; GET returns `"view"` | |
| `state` | yes | `"active"` | |
| `action` | PUT only | `"edit"` | |
| `module` | yes | `{ "id", "api_name" }` | |
| `layout` | yes | `{ "id" }` (GET adds `name`) | canvas is per layout |
| `related_to` | yes | see §3 | `null` members when unused |
| `ui` | yes | `{ value, canvas_rules, script_info }` | root box + rules |
| `children` | yes | node list | the layout tree |
| `uniqueid` | on update | string | root has one too |

Root `ui.value.position`: `{ start_x: 0, start_y: 0, width: W, end_x: 3*W, height: H, depth: 1 }`.
`end_x == 3 × width` on the root only (three responsive breakpoints; Responsive Mode payload is
**unobserved**). Observed widths: 1440 (Accounts template), 1100 (both Zoho gallery templates).
`ui.canvas_rules: []` and `ui.script_info: { "mapping": {}, "deleted": [] }` in every observed
payload; populated forms are **unobserved**.

---

## 3. `related_to` associations

Non-null only when the canvas places a Query or a lookup All-Fields tab.

```jsonc
"related_to": {
  "data_hub_associations": [ {                      // a saved Query used as a related list
      "connection_id": "<uuid>",
      "data_hub": { "name": "testq_query", "query_uuid": "<uuid>" },
      "name": "test query",
      "config": { "display_type": "related_list" } } ],
  "lookup_associations": [ {                        // an "All Fields - <Lookup>" tab
      "connection_id": "<uuid>",
      "parent_module_lookup_field": { "api_name": "Account_Name", "id": "2582206000000002493" },
      "child_module": { "api_name": "Accounts", "id": "2582206000000002177" } } ],
  "homepage_associations": null                     // unobserved
}
```

Nodes that use a connection reference it through a node-level `details` block (§4). The
`connection_id` is minted by the editor; how to obtain one by API is **unobserved**, so
query- and lookup-backed constructs currently have to be created in the UI and carried forward.

---

## 4. The node model

Every element of `children`, at any depth, is one node:

```jsonc
{
  "type": "component" | "field" | "relatedlist" | "action" | "button" | "link" | "section" |
          "row" | "table_cell" | "static_content" | "separator",
  "theme": "…",                 // layout engine / widget kind, on components and related lists
  "id": "…",                    // CRM entity id, system id, or absent
  "datatype": "…",              // fields, actions, links, buttons
  "ui": { … },                  // geometry + styling, see §5
  "children": [ … ],            // always present, [] when empty
  "uniqueid": "<uuid>",         // stable node identity, optional
  // situational:
  "tab_relatedlist_id": "…",    // on a tab body that hosts a related list
  "related_list": true,         // on a related-list card container
  "static_id": "…",             // on All-Fields sections (the CRM section name)
  "personality_name": "…",      // on some related lists (Emails)
  "details": { … }              // connection reference, see below
}
```

`details` shapes observed:

```jsonc
{ "connection_type": "data_hub_associations", "connection_id": "<uuid>" }            // query list
{ "connection_type": "data_hub_associations", "connection_id": "<uuid>", "path": "$.First_Name" }  // query column
{ "connection_type": "lookup_associations",   "connection_id": "<uuid>" }            // lookup all-fields tab
```

### Node kinds observed (type / theme)

| type | theme | what it is |
|---|---|---|
| component | Custom Layout | absolute container: card, tab body, related-list card, banner |
| component | Flex Layout | flex container (`property.flex`) |
| component | Grid Layout | grid container (`property.grid`) |
| component | Tab Layout | tab strip; also a nested tab group ("Sub Tab") |
| component | Table Layout | label/value rows |
| component | Static Text | literal text (may contain HTML) |
| component | Static Icon | icon from the catalog |
| component | Canvas Button | custom canvas button |
| component | Canvas Image | uploaded image (`$Image{id}`) |
| component | Line | horizontal/vertical rule |
| component | MERGEFIELD | inline button group |
| component | *(none)* | inner wrapper of MERGEFIELD (`zcanvas-row-seperator`, `position: {}`) |
| static_content | Custom Layout | title block of a related-list card (`zcanvas-title-editor`) |
| static_content | Custom Component | standalone heading wrapper (gallery template c1 only) |
| field | *(none)* | CRM field reference |
| relatedlist | Table Layout | Zoho-rendered list, `children: []` |
| relatedlist | Custom Layout | list with chosen column fields as children |
| relatedlist | Canvas Data Table | table preset with `table_cell` children |
| action | *(none)* | system action button (`id` from palette) |
| button | *(none)* | CRM custom button (numeric id) |
| link | *(none)* | custom link field |
| section | *(none)* | All-Fields section (`ui: {}`, `static_id`) |
| row | *(none)* | Table Layout row |
| table_cell | *(none)* | Canvas Data Table column |
| separator | *(none)* | spacer inside a MERGEFIELD |
| *(none)* | *(none)* | typeless styling wrappers inside All-Fields sections; pruned if empty |

---

## 5. The `ui` object and its slots

`ui` is a bag of named style slots. `value` is the node's own box; the rest style sub-parts.

| `ui.*` | on | contents |
|---|---|---|
| `value` | every node | `style`, `custom_style`, `position`, `class`, plus the keys in §6 |
| `field` | field, action, button, link, image | style of the value text / button face |
| `holder` | field, action, link | wrapper around label+value; `style.default.flex_direction` |
| `label` | field, table_cell | the field label |
| `icon` | action (⋯ buttons), link | `{ style, custom_style, class, icon }` |
| `image` | Canvas Image | `{ style: { default: { src: "$Image{id}" } } }` |
| `autoheight` | Static Text | bool; `true` grows the box to its text |
| `tab_item_title` | tab body | `{ class }`; `"zc-tabgroup"` marks a nested tab group |
| `allfieldstabstyle` | All Fields tab, lookup All-Fields tab | `{}` observed |
| `canvas_rules` | root, relatedlist | `[]` observed |
| `context` | relatedlist (Notes, Timeline, Closed Meetings) | list-type chrome: `notes_*`, `table_head/row/column/link` |
| `layoutstyle` | Canvas Data Table | `{ head: {"$height"}, row: {"$height"} }` |
| `header`, `row`, `row_odd`, `row_even` | Canvas Data Table | `{ style, custom_style }` |
| `column`, `column_odd`, `column_even` | table_cell | column striping |
| `field_odd`, `field_even` | field inside a data table | row striping |
| `static_column_value/label/header/column/column_odd/column_even` | Canvas Data Table | the fixed first column |
| `index` | wrappers inside All-Fields sections | integer column index |
| `sectionstyle`, `titlesection`, `datastyle`, `datastylefields`, `datastylerow`, `datastylelayout`, `datastyletable`, `inner`, `tagname`, `class`, `style`, `custom_style`, `position` | All-Fields section internals | machine-generated; copy from a capture, never hand-build |
| `script_info` | root | `{ mapping, deleted }` |

Every style slot has the shape `{ "style": { "<state>": { … } }, "custom_style": {}, "class": "" }`.
`style` is the theme/preset baseline, `custom_style` the user's overrides (an object, or `[]`
inside `custom_layoutstyle`).

---

## 6. `ui.value` keys

| key | type | on | meaning |
|---|---|---|---|
| `style` | `{state: {...}}` | all | inline CSS by state (§8) |
| `custom_style` | `{}` | all | user overrides |
| `position` | object | all but MERGEFIELD inner (`{}`) | geometry (§7) |
| `class` | string | all | space-separated Zoho class tokens (§10) |
| `zcode` | `{ "name": "section3" }` | containers, text, icons, images, lines, RL cards, tab strips | stable handle; `RL-<Label>` for related-list cards; spaces entity-encoded (`&#x20;`) |
| `value` | string | Static Text, separator (`""`) | the literal text; HTML allowed |
| `name` | string | tab body, Canvas Button | tab label / button label |
| `disabled` | `true` | related-list and All-Fields tab bodies | |
| `icon` | string | Static Icon, tab body | catalog icon name |
| `fixed` | bool | icons, images, lines, data-table cells | not user-movable |
| `related_list` | `true` | related-list card container | |
| `count` | string | related-list card container | rows to show |
| `recordcount` | string | relatedlist node | rows to show |
| `editorclass` | `"zcanvas-loading-component"` | related-list card container | |
| `layoutstyle` | object | Tab Layout, Table Layout | engine-level styles (§8) |
| `custom_layoutstyle` | object | Tab Layout | user overrides; arrays for `default/hover/active` |
| `scope` | `"default"` | Table Layout | |
| `property` | object | Flex/Grid containers and their items | §9 |
| `vertical` | bool | Line | orientation |

---

## 7. `position` and geometry

```jsonc
"position": { "start_x", "start_y", "end_x", "width", "height", "depth",
              "order"?, "min_top"?, "min_left"?, "over_top"?, "over_left"?, "_locked_"? }
```

Rules that held on every one of the 33 payloads:

- `end_x == start_x + width` on every node except the root, where `end_x == 3 × width`.
- Coordinates are **parent-relative**, except inside a `Canvas Data Table`, where a `table_cell` and
  its `field` share identical table-space coordinates.
- `depth` is z-order, not nesting level. 1 almost everywhere; banners use up to 10; the tab strip
  moves to 6 when set vertical.
- `order` sequences siblings: table rows stack (`start_y` = cumulative row heights), tab bodies do
  not (tab 0 has full height; every other tab sits at `start_y == its own height`, one layer).
- `min_top` / `min_left` are inner padding for children (tab bodies use 30/30; All Fields 10/20).
- `over_top` / `over_left` are negative pulls for deliberate overlap.
- `_locked_: "true"` (string) marks a locked box (banners).
- Children may extend past the parent's width; Zoho's own templates do it. Do not "fix" it.
- Table Layout: `layoutstyle.row.height` (`"29px"`) must equal each row's `position.height` (`29`).
- Root height should cover the lowest `start_y + height`.

Layout engines: absolute (`Custom Layout`) is the default; `Flex Layout` and `Grid Layout` reflow
their children (§9). `zc-fit-height-content` on a flex container and `autoheight: true` on Static
Text are the only content-driven heights observed.

---

## 8. Style system

**States** (keys under `style` / `custom_style` / `layoutstyle`):
`default`, `hover`, `active` (tab chips, buttons); tab-strip scopes `tabname`, `tabicon`,
`container`, `editor` (each holding its own `default/hover/active`); Table Layout scopes `field`,
`row`, `inner` (`inner: [{percent}]` is the column split); data-table `head`.

**Properties** (snake_case CSS; 40 observed): `background_color`, `background_image`,
`background_size`, `background_repeat`, `border`, `border_top/right/bottom/left`, `border_radius`,
`border_top_left_radius`, `border_top_right_radius`, `border_bottom_left_radius`,
`border_bottom_right_radius`, `box_shadow`, `color`, `font_size`, `font_family`, `line_height`,
`text_transform`, `vertical_align`, `flex_direction`, `padding`, `padding_top/right/bottom/left`,
`margin`, `margin_top/right/bottom/left`, `width`, `height`, `src` (image), `$height` (data-table
head/row), and the flags `_show_`, `_hide_`, `_section_version_`. `$inherited` appears only in
presets. `letter_spacing` and anything else not in this list is **unobserved**.

**Values.** Colours are `rgba(r, g, b, a)` / `rgb(r, g, b)` strings. `font_family` uses the codes
`r` regular, `m` medium, `s` semibold, `b` bold. `background_image` is a `linear-gradient(...)`,
`url(/crm/CRMClient/images/canvas/banner.png)`, or `url($Image{<canvas_file_id>})`. Flags are the
string `"true"`; `_section_version_` is the integer `1`.

**Class strings** may carry template expressions on mirror fields
(`{{if(hidedLookups[<id>],'hide','')}} {{getMirrorFieldClasses(...)}}`); never normalise them.

**Presets** (`reference/zoho-assets/*-preset.json`) are libraries of these blocks: text (7),
field (9, styling `value/holder/field/label`), section (25), tab (7), button (30,
`field.default/hover` + `field.class`), related list (6, `container/title/relatedlist/context`),
table (3).

---

## 9. `property` (Flex and Grid)

```jsonc
// flex container
"property": { "flex": { "default": { "direction": "column", "space_distribute": "_normal",
                                      "alignment": "topleft", "wrap": "nowrap" } } }
// freshly dropped, empty:  "property": { "flex": {} }
// flex item (any child of a Flex Layout)
"property": { "flex_item": { "default": { "h_stretch": false, "v_stretch": false, "align_self": "" } } }
// grid container
"property": { "grid": { "default": { "column_gap": "5px", "row_gap": "5px",
                                      "block_width_count": [ { "order": 11 } ],
                                      "block_height_px": "20px" } } }
```

`h_stretch: true` adds `zc-flex-self-column-horizontal-grow` to the item's class. Grid items are
**unobserved**.

---

## 10. Enumerations

### `datatype` (fields, actions, links)

`text`, `text-area`, `picklist`, `multiselectpicklist`, `boolean`, `number`, `bigint`, `date`,
`date-time`, `email`, `phone`, `website`, `twitter`, `lookup`, `multiselectlookup`,
`multi_module_lookup`, `user`, `multiselectuser`, `profileimage`, `tag`, `layout`, `link`,
`button`. These are canvas datatypes; the CRM `data_type` differs.

**CRM `data_type` → canvas `datatype`**, derived 2026-09-07 by joining every field node in the 33
Zoho-authored files against live layout metadata (counts are field placements that agreed; the
odd stray value in the join came from id collisions in related-list subtrees and is ignored):

| CRM `data_type` | canvas `datatype` | evidence |
|---|---|---|
| `text` | `text` (`tag` when the field is `Tag`) | 1790 / 73 |
| `textarea` | `text-area` | 85 |
| `email`, `phone`, `website` | same name | 71 / 214 / 114 |
| `picklist`, `multiselectpicklist` | `picklist` | 551 / 70 |
| `boolean` | `boolean` | 199 |
| `date` | `date` | 154 |
| `datetime` | `date-time` | 371 |
| `integer`, `double`, `currency`, `bigint` | `number` | 109 / 80 / 45 / 35 |
| `formula` (any return type) | `text` | 4 |
| `lookup` | `lookup` | 189 |
| `ownerlookup` | `user` | 192 |
| `multiuserlookup` | `multiselectuser` | 2 |
| `multiselectlookup` | `multiselectlookup` | 36 |
| `profileimage` | `profileimage` | 39 |

The table lives in code as `DATATYPE` in `src/build_proposals_v1.py`.

### Class tokens (52 observed)

| role | tokens |
|---|---|
| fields | `zcanvas-field`, `zc-rl-field`, `zcclinkvalue`, `zctextarea`, `zcbdrbox`, `zcmultimodulelookupfield`, `mirror_field_<id>` |
| alignment | `zc-ta-left`, `zc-ta-center`, `zc-ta-right`, `zcanvasuppercase` |
| containers | `zc-lsection`, `zc-list-component`, `zcautoratio`, `zclayout-table`, `zc-no-theme`, `zcanvas-editor`, `zcanvas-row`, `zcanvas-title-editor`, `zc_disabled`, `zcanvas-non-delete`, `zcnochange`, `zcrestricttable`, `zc-submodule-list` |
| tabs | `zc-tab-section`, `zc-tabrl-container`, `zc-tab-all-fields`, `zc-tab-lookup-all-fields`, `zc-tabgroup`, `zcanvas-horizantol-top`, `zcanvas-vertical-left`, `zcanvas-vertical-right`, `zcanvas-subtab-push`, `zcanvas-tab-splitnav`, `zcanvas-single-subtab` |
| buttons | `zccbutton`, `zccbuttonicon`, `zccbuttonnotext`, `zccrlaction`, `zc-only-icon`, `zccfieldicon`, `zc-restricted-icon`, `zcanvas-nav`, `zcanvas-no-img-default` |
| groups | `zc-merge-hright`, `zcanvas-row-seperator`, `zcanvas-seperator` |
| flex / grid | `zc-flex-component`, `zc-flex-direction-column`, `zc-fit-height-content`, `zc-flex-self-column-horizontal-grow`, `zcanvas-grid-container` |
| image | `zc-cover-Image`, `zclayout` |
| links | `zcclink` |

### Action ids

From the components palette for the module (`reference/zoho-assets/components-palette-contacts-detailview.json`, fetch per module):
`edit`, `clone`, `findandmerge`, `send_mail`, `delete`, `mail_merge`, `share`, `macro`, `callnow`,
`sendDM`, `meetnow`, `scheduleonlinemeeting`, `inviteClientPortal`, `data_enrichment`,
`askzia_contextual`, `navigate`, `back`, `print_preview`, `morebutton`, `reviewHistory`,
`locatemap`, `lock`, `cadence`, `create_client_script`, `cliq`. Editor-generated inside related-list
title bars: `moreRLActions<related_list_id>`, `ExpandView`, `newEvent`.

### System components placed as related lists

The palette's `system` entries are placed as `relatedlist` nodes with a string id:
`timeline` and `journeys` ("Interactions") observed. Others listed by the palette
(`stage_navigator`, `blueprint`, `upcoming_actions`, `upcoming_action`, `next_action`, `tag`,
`orchestrations`, `pathfinders`) and the `zia` entries are **unobserved**.

### Icons

231 names in `reference/zoho-assets/icon-catalog.txt`, case-sensitive and irregular
(`icon-Icon_task`, `icon-Icon_Calender`, `icon-Icon_Notes`, `icon-Icon_Location`). Anything else
is invalid. Used on `ui.value.icon` (Static Icon, tab body) and `ui.icon.icon` (action buttons).

### Related-list ids

`GET /crm/v8/settings/related_lists?module={Module}` → `id`, `display_label`, target `module`.
Entries with `module: null` (grouped / custom-function lists such as Drive Files, Zoho Projects,
Chronological View) can be placed but carry no fields. Field ids inside a related list belong to
the **related** module.

### `zcode.name` conventions

`section<n>`, `text<n>`, `icon<n>`, `image<n>`, `line<n>`, `grid<n>`, `tab<n>`, `flexNaN` (editor
quirk), `RL-<Display Label>` for related-list cards.

---

## 11. Tabs

The strip is a `Tab Layout`; each tab body is a child. Body kinds by `class` and extra keys:

| kind | class | node / ui extras |
|---|---|---|
| custom | `zc-tab-section` | |
| related list | `zc-tab-section zc-tabrl-container` | `tab_relatedlist_id`, value `disabled: true` |
| All Fields | `zc-tab-section zc-tab-all-fields zc-tabrl-container` | `disabled`, `ui.allfieldstabstyle: {}`, one `section` child per layout section |
| lookup All Fields | `zc-tab-section zc-tab-lookup-all-fields zc-tabrl-container` | `disabled`, `allfieldstabstyle: {}`, node `details.lookup_associations`, name `All Fields - <Lookup label>`, `children: []` |
| nested tab group | a `Tab Layout` child with class `zc-tab-section`, name, `tab_item_title.class: "zc-tabgroup"` | own `layoutstyle` / `custom_layoutstyle` |

Strip option tokens (Properties panel): orientation `zcanvas-horizantol-top` / `zcanvas-vertical-left`
/ `zcanvas-vertical-right`; navigation both sides `zcanvas-tab-splitnav`; sub-tab single expand
`zcanvas-single-subtab`; always `zcanvas-subtab-push`; hide/show via `style.default._hide_` /
`_show_`. Container styling lands in `layoutstyle.editor.default`.

---

## 12. `uniqueid`

- Stable identity minted by the server; preserved on every save (verified 217/217, 178/178, and a
  no-op PUT with 425/425 unchanged).
- Present on roughly half the nodes in the editor's own output (containers, rows, sections,
  actions, static text, related lists; usually not on fields or typeless wrappers).
- May be **duplicated within one payload**: cloning a card in the editor copies the ids (22
  duplicates in round-3). The server accepts it.
- Send what you have on updates, never fabricate, never treat absence as an error.

---

## 13. What the API checks versus what the editor needs

The save endpoint accepted every payload we have ever sent, including three that left the editor
on a blank or spinning screen. Treat `SUCCESS` as "stored", not "works". The gates that keep a
generated canvas openable:

1. Only shapes from `canvas-constructs.md` / `src/canvas_shapes.py`.
2. `src/validate.py`: envelope, `end_x` math, table row math, server-owned keys, known
   types/themes, icon names in the catalog, action ids in the palette. It passes all 33
   Zoho-authored files with zero findings; any new rule must keep that true.
3. The vocabulary audit in the deploy chain: every type, theme, class token, ui key, value key and
   style property in the body must appear somewhere in `reference/`.
4. Open it in the editor.

Known **unobserved** areas (do not emit): grid items, `system`/`zia` components other than
`timeline`/`journeys`, Responsive Mode, populated `canvas_rules`/`script_info`, error responses,
`homepage_associations`, a populated `custom_style` (the editor's Custom CSS box; `{}` in all 33
files), any toggle-switch rendering of a boolean (none exists; Zoho draws a checkbox).

**`lookup_associations.connection_id` is minted by the editor, client-side.** Settled 2026-09-07
by tracing the round-1 HAR: the first id (`00ce09e9-…`) appears fully formed in the editor's PUT
and in no earlier response. All four observed ids begin with `00`. `src/build_proposals_v1.py`
mints `"00" + uuid4()[2:]` the same way; the server stored it and the live GET returned it. Whether
the tab then *renders* the looked-up record is confirmed only in the editor.

---

## 14. Files

```text
src/canvas_shapes.py        builders that emit only observed shapes (use this)
src/base_template.py        legacy builders; two shapes the editor never produces; reference only
src/validate.py             gates 2 above
src/build_contacts_v3.py    current Contacts build (design v2, observed shapes)
src/noop_deploy.py          GET → strip → PUT → verify; build_request_body()
src/restore.py              put a rollback file back
src/evolve.py               one named change at a time on the live canvas
src/zoho_auth.py            OAuth refresh grant with disk cache
src/zoho_canvas.py          GET / backup / PUT client (PUT needs an explicit opt-in flag)
reference/ui-capture/       30 editor saves + responses, manifest in README
reference/zoho-assets/      presets, components palette, icon catalog
reference/captures/         gallery templates, rollbacks
docs/canvas-constructs.md   per-construct JSON
docs/canvas-key-inventory.md  generated key inventory
```
