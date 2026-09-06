# Zoho CRM Canvas JSON — structural reference

Everything here is derived from one real capture: `reference/captures/accounts-main-account.payload.json`
(the parsed body of `save-zcrm-canvas-api-curl-request.txt`), cross-referenced against live Camco
CRM metadata via the Camco ZCRM MCP.

**Scope warning — read this before trusting anything below.** This documents what **one** 736 KB
Accounts canvas contains. It is an observed vocabulary, not Zoho's published schema — Zoho does not
document the Canvas view body.

A single capture shows what that canvas *used*. It cannot show what Canvas *supports*. Treat every
statement here as "true of this payload" rather than "true of Canvas", and never conclude a feature
is absent just because this sample lacks it. Anything marked *unobserved* has not been seen and
must not be assumed to work.

**Update 2026-09-06.** The evidence base is now much wider than one capture: two recorded editor
sessions (25 consecutive saves, one construct per save), Zoho's own preset JSON, and three gallery
templates. The per-construct shapes the editor emits, the three layout engines (absolute, Flex,
Grid), the tab-strip option tokens, the icon catalog and the action-id palette are documented in
**`docs/canvas-constructs.md`**, which supersedes this file wherever the two disagree. Geometry
within absolute containers held across all 25 saves; see `docs/draft/geometry-rules.DRAFT.md`.

Two claims previously made in this file were wrong and are corrected below: "a related-list id
may appear at most once" (the editor itself places one twice) and "an empty All Fields tab hangs
the editor" (unverified).

---

## 1. The request

```
PUT https://crm.zoho.com/crm/v8/settings/canvas/views/{canvas_view_id}
Authorization: Zoho-oauthtoken {oauth_access_token}
Content-Type: text/plain;charset=UTF-8
```

Body is JSON despite the `text/plain` content type. Preserve that header exactly.

**Auth is OAuth 2.0 — confirmed working.** `Zoho-oauthtoken` is Zoho's own scheme name and is what
hand-written clients should send. Zoho also accepts `Bearer`, which is what Postman's OAuth2 helper
emits — John's Postman request against the Camco org uses `Bearer` with auto-refresh and returns
`200 OK`. Both are valid; prefer `Zoho-oauthtoken`.

The original browser capture used session cookies (`Cookie` + `x-zcsrf-token` + `x-crm-org` +
`x-requested-with`), but **those are not required** — do not build against them.

Verified 2026-09-04 with a self-client refresh token against live Camco: the refresh grant returns a
1-hour access token, and `GET /crm/v8/settings/canvas/views/2582206000057761014` responds `200` with
`name: "Main Account"`, `feature: DetailView`, `state: active`. The token endpoint advertises
`api_domain: https://www.zohoapis.com`, but `crm.zoho.com` serves the canvas call — both hosts work.

The GET response uses the same `canvas_view` array envelope documented in §2, so a rollback capture
can be diffed directly against a generated request body.

The `x-murphy-*`, `x-client-subversion`, `x-static-version` and `x-crm-ref-id` headers in the
original capture are telemetry/build-pinning. The Postman request succeeds without reproducing
the browser session, so treat all of them as droppable.

`{canvas_view_id}` is the canvas being overwritten and **must be a parameter of the deploy step** —
the generator has to accept it per call.

The PUT **replaces the entire canvas view**. There is no partial update. This project is
**update-only**; creating a new canvas via POST is out of scope and its shape is unobserved.

---

## 2. Root envelope

```jsonc
{
  "canvas_view": [                 // always an array; one element observed
    {
      "name": "Main Account",      // canvas name shown in the builder
      "feature": "DetailView",     // the canvas surface
      "type": "component",
      "state": "active",
      "action": "edit",
      "module": { "id": "2582206000000002177", "api_name": "Accounts" },
      "layout": { "id": "2582206000000091029" },
      "related_to": {
        "data_hub_associations": null,
        "lookup_associations": null,
        "homepage_associations": null
      },
      "ui": {
        "value": {
          "style": { "default": { "background_color": "rgba(233, 238, 242, 1)" } },
          "custom_style": {},
          "position": { "start_x": 0, "start_y": 0, "end_x": 4320,
                        "width": 1440, "height": 2229, "depth": 1 },
          "class": ""
        },
        "canvas_rules": [],
        "script_info": { "mapping": {}, "deleted": [] }
      },
      "children": [ /* the layout tree */ ]
    }
  ]
}
```

Root canvas is **1440 × 2229**. Note `end_x` is 4320 (3 × 1440) on the root only — the other
two viewport widths for responsive mode. Every descendant uses `end_x = start_x + width`.

`canvas_rules` (empty here) and `script_info` are where Canvas Rules and Client Script bindings
would live. Both unobserved in populated form.

---

## 3. The universal node shape

Every node in `children` is:

```jsonc
{
  "type":     "...",        // required — see §4
  "ui":       { ... },      // required — geometry + styling
  "children": [ ... ],      // required, [] when empty
  "id":       "...",        // when the node references a CRM entity
  "datatype": "...",        // for field/action/link/button
  "theme":    "..."         // for layout-bearing components
}
```

Observed counts in the capture: 120 `field`, 29 `component`, 11 `section`, 9 `row`, 8 `action`,
7 `static_content`, 7 `relatedlist`, 5 `link`, 4 `table_cell`, 1 `button`. Max nesting depth 6.

### `ui` sub-keys

`ui.value` is the node's own box. The others style sub-parts of the rendered widget:

| `ui.*` key | Appears on | Styles |
|---|---|---|
| `value` | all | the node box itself |
| `field` | field, action, link, button | the value text |
| `holder` | field, action, link | the wrapper |
| `label` | field, table_cell | the field label |
| `index` | table internals | column index |
| `header`, `row`, `row_odd`, `row_even` | relatedlist, table_cell | table chrome |
| `column`, `column_odd`, `column_even` | table_cell | column striping |
| `field_odd`, `field_even` | field in tables | row striping |
| `layoutstyle` | Tab/Table Layout | the layout container (**carries states — see §6**) |
| `sectionstyle`, `titlesection`, `datastyle*` | All-Fields sections | generated section chrome |
| `tab_item_title` | tab child | the tab's label chip |
| `autoheight` | component | bool |
| `canvas_rules` | relatedlist, root | per-node rules |
| `context` | relatedlist | context binding |
| `icon` | action, link | icon spec |

---

## 4. Node types

### `field` — a CRM field reference
The single most important shape. It is **a pointer, not a definition**:

```jsonc
{
  "id": "2582206000000002425",     // CRM field ID
  "datatype": "text",
  "type": "field",
  "ui": {
    "value": { "style": {"default":{}}, "custom_style": {},
               "position": {...}, "class": "zcanvas-field" },
    "field": { "style": {"default":{"font_size":"18px"}}, "custom_style": {}, "class": "" },
    "holder": { ... },             // optional
    "label":  { ... }              // optional
  },
  "children": []
}
```

**No API name. No label text.** Zoho resolves both from the field ID at render time. This is why
the generator must map api_name → ID at build time (§8).

`datatype` observed: `text` (39), `picklist` (12), `number` (10), `boolean` (10), `button` (9),
`date-time` (8), `text-area` (6), `website` (6), `date` (6), `user` (5), `link` (5), `lookup` (3),
`profileimage`, `phone`, `tag`, `multiselectuser`.

These are **canvas datatypes, not CRM data_types** and they do not map 1:1. Observed divergences:

| canvas `datatype` | CRM `data_type` |
|---|---|
| `number` | `currency` or `double` |
| `text` | `text` or `formula` |
| `text-area` | `textarea` |
| `user` | `ownerlookup` |
| `multiselectuser` | `multiuserlookup` |
| `date-time` | `datetime` |
| `tag` | `text` |

11 field nodes carry no `datatype` at all (they sit inside generated All-Fields sections).

### `component` — container
Carries `theme`, and optionally `zcode`. Themes observed: `Custom Layout` (20), `Static Text` (5),
`Tab Layout` (2), `Table Layout` (1). Related-list tab wrappers add `tab_relatedlist_id` and
`related_list: true`.

### `section` — All-Fields section
`{id, type:"section", static_id, ui:{}, children:[]}`. Note `ui` is an **empty object** on all 11.
These are the auto-generated sections of the "All Fields" tab; `static_id` ties back to the CRM
layout section.

### `row` / `table_cell` — table internals
`row` holds fields inside a Table Layout. `table_cell` appears in Canvas Data Table related lists.

### `action` — system or related-list button
Two ID conventions, and this distinction matters for portability:

- **String IDs, org-independent:** `back`, `edit`, `reviewHistory`, `morebutton`, `navigate`
- **Composite:** `moreRLActions<relatedlist_id>`

### `button` — custom CRM button
Numeric CRM ID (`2582206000047549161` = "Setup Account Resources"). Label lives in CRM.

### `link` — a link-type field rendered as a link
Numeric field IDs. The five in the left column resolve to Drive URL, Miro Board Url, Coda Url,
Internal Cliq Channel ID and GitHub Repo Url.

### `static_content` — literal text
The only node type whose text is stored in the payload:

```jsonc
{ "type": "static_content", "theme": "Custom Component",
  "ui": { "value": { "position": {...}, "class": "zcanvas-title-editor" } },
  "children": [
    { "type": "component", "theme": "Static Text",
      "ui": { "value": { "value": "Zoho Finance",      // <-- the literal text
                         "class": "zc_disabled", "position": {...},
                         "style": {"default":{"padding":"0px",
                                   "background_color":"transparent"}} },
              "autoheight": false },
      "children": [] } ] }
```

All five literals in the capture: `Basic Info`, `Zoho Finance`, `Attachments`, `Notes`, `Timeline`.
`Basic Info` renders as "BASIC INFO" purely via the `zcanvasuppercase` class — **stored title case**.

### `relatedlist` — an embedded related list
`{id, type:"relatedlist", theme, personality_name?, ui:{canvas_rules, value:{recordcount?}, …}}`.
Themes: `Table Layout` (5), `Canvas Data Table`, `Custom Layout`. Related-list IDs observed:
`2582206000034507893`, `…34711647`, `…08473114` (Proposals), `…56715125`, `…00003779`,
`…00003781`, and the literal `timeline`.

---

## 5. Positioning

> **Caveat.** The keys below are what the sample uses. Whether pixel positioning is Canvas's only
> layout mode is **unresolved** — `autoheight`, `width: "100%"` and `percent` columns suggest not.
> Do not treat this section as the layout model. See `docs/draft/geometry-rules.DRAFT.md`.

Every box in the sample carries explicit coordinates:

```jsonc
"position": {
  "start_x": 28, "start_y": 159,     // top-left, relative to parent
  "end_x": 346,                      // = start_x + width
  "width": 318, "height": 347,
  "depth": 1,                        // z-order / nesting depth
  "order": 0,                        // sequence within tabs and rows
  "min_top": 30, "min_left": 30,     // minimum offsets
  "over_top": -39, "over_left": 0    // negative overlap pull
}
```

`start_x`/`start_y`/`end_x`/`width`/`height`/`depth` appear on all 202 positioned nodes.
`order` on 113, `min_top` on 22, `min_left` on 21, `over_*` on 1 each.

The one arithmetic relation that holds throughout the sample is `end_x == start_x + width`, with
the root as the sole exception (`end_x` 4320 = 3 × 1440, implying three responsive breakpoints —
themselves unobserved).

**Open:** how `autoheight`, percentage widths and Responsive Mode interact with these numbers.
Until that is known, do not assume "generate a canvas" reduces to computing pixel coordinates.

---

## 6. Styling

Three independent mechanisms, all of which can apply to one node.

**a) `style` / `custom_style` — inline CSS, keyed by state.**
States observed: `default` (654 uses), plus `hover` and `active` (on Tab Layout `layoutstyle`),
and `row` / `field` / `head` as table scopes. `custom_style` is the user's overrides;
`style` is the theme's baseline. Property names are **snake_case CSS**:

```
vertical_align  color  flex_direction  font_size  border_radius  padding
background_color  font_family  padding_left  border  width  height
padding_right  padding_top  padding_bottom  box_shadow  background_image
margin_left  margin_top  border_right  border_left  border_bottom  border_top
line_height  text_transform  border_top_left_radius  border_top_right_radius
border_bottom_left_radius  border_bottom_right_radius  $height
```

`font_family` uses single-letter codes: `r` regular, `b` bold, `s` semibold, `m` medium.
Colors are `rgba(...)` / `rgb(...)` strings. `$height` (with the `$`) appears in table headers.

**b) `class` — Zoho's CSS class vocabulary.** 35 distinct tokens, space-separated. Reuse these;
do not invent new ones:

| Token | Meaning |
|---|---|
| `zcanvas-field` | any field (119 uses — near-universal) |
| `zcanvas-row` | table row |
| `zclayout-table` | table layout container |
| `zc-lsection` | layout section |
| `zc-tab-section` | one tab's body |
| `zc-tabrl-container` | tab body holding a related list |
| `zc-tab-all-fields` | the All Fields tab |
| `zc-list-component` | list component |
| `zcanvas-title-editor` | static-text wrapper |
| `zcanvas-horizantol-top` | horizontal tabs, top *(Zoho's typo, keep it)* |
| `zcanvas-subtab-push` | sub-tab push behaviour |
| `zc-ta-left` / `zc-ta-center` | text align |
| `zcanvasuppercase` | uppercase transform |
| `zctextarea` | textarea field |
| `zcclink` / `zcclinkvalue` | link / link value |
| `zccbutton` / `zccbuttonicon` / `zccbuttonnotext` | button variants |
| `zc-only-icon` / `zccfieldicon` | icon-only |
| `zccrlaction` | related-list action |
| `zc-rl-field` | field inside a related list |
| `zcanvas-no-img-default` | suppress default image |
| `zc-restricted-icon` / `zcrestricttable` | permission-restricted |
| `zc_disabled` | disabled/static |
| `zcbdrbox` | bordered box |
| `zcnochange` / `zcanvas-non-delete` | locked from edit/delete |
| `zc-no-theme` | theme suppressed |
| `zcanvas-editor` | editor context |
| `zcanvas-nav` | navigation control |
| `zc-submodule-list` | submodule list |

**c) `theme` — the layout engine.** `Custom Layout`, `Tab Layout`, `Table Layout`,
`Static Text`, `Custom Component`, `Canvas Data Table`.

---

## 7. Composite structures

### Table Layout (the "Basic Info" block)
```
component theme="Table Layout" class="zclayout-table zc-no-theme zcanvas-editor"
  ui.value.layoutstyle = { field:{width:"100%"}, row:{height:"29px"},
                           inner:[{percent: 42.038216560509554}] }
  ui.value.scope = "default"
  └── row  (class "zcanvas-row", position.order 0..n)
        └── field
```
`layoutstyle.inner[].percent` sets column widths; `layoutstyle.row.height` the row height.

### Tab Layout (the GENERAL / Zoho Finance / … strip)
```
component theme="Tab Layout" zcode={name:"tab1"}
          class="zcanvas-horizantol-top zcanvas-subtab-push"
  ui.value.layoutstyle = { default:{}, hover:{}, active:{},
                           container:{default:{}}, editor:{default:{}},
                           tabname:{default:{}, hover:{}, active:{}}, tabicon:{} }
  └── component theme="Custom Layout"            <- one per tab
        ui.value.name     = "Zoho Finance"       <- the tab label
        ui.value.order    = 1                    <- tab sequence (in position)
        ui.value.icon     = "icon-Icon_plus"     <- optional
        ui.value.disabled = true                 <- optional
        ui.value.class    = "zc-tab-section zc-tabrl-container"
        tab_relatedlist_id = "2582206000008473114"
        related_list = true
        ui.tab_item_title = { class: "" }
```
The tab's **label is `ui.value.name`**, and its order comes from `position.order`.
The active-tab green (`rgba(0, 176, 80, 1)`) lives in `layoutstyle.active.background_color`.

### `zcode.name` — stable node handles
`section1`, `section2`, `section3`, `text1`, `tab1`, and for related-list tabs the convention
**`RL-<TabName>`**: `RL-Zoho Finance`, `RL-Resources`, `RL-Proposals`, `RL-Zoho Projects`,
`RL-Attachments`, `RL-Notes`, `RL-Timeline`.

---

## 8. ID resolution (verified against live CRM)

All 101 field-node IDs in the capture resolve cleanly against Camco org `647376701` using
`getFields(module)` from the Camco ZCRM MCP. Confirmed examples:

| Canvas node ID | api_name | Label | CRM data_type |
|---|---|---|---|
| `2582206000000002425` | `Account_Name` | Account Name | text |
| `2582206000005007003` | `Record_Image` | Account Image | profileimage |
| `2582206000006579833` | `primary_contact` | Primary Contact | lookup |
| `2582206000037048011` | `Next_Step` | Next Step | textarea |
| `2582206000039860734` | `Last_Invoice_Amount` | Last Invoice Amount | currency |
| `2582206000039860845` | `Total_Outstanding` | Total Outstanding | formula |

**Critical rule: fields inside a related-list tab belong to the related module, not the host
module.** The four field IDs under the Proposals tab do not exist in Accounts; they resolve
against `Proposals`:

| ID | api_name | Label |
|---|---|---|
| `2582206000008466934` | `Name` | Proposals Name |
| `2582206000008473589` | `Billable_Rate` | Billable Rate |
| `2582206000008473517` | `Payment_Terms` | Payment Terms |
| `2582206000008473993` | `Proposal_Status` | Proposal Status |

So the ID resolver must be **module-scoped per subtree**, not global.

Of the 152 id-bearing nodes: 101 resolve as Accounts fields, 4 as Proposals fields, and the
remaining 47 are non-field references (5 string system actions, 11 layout sections via
`static_id`, 7 related lists, 5 links, 1 custom button, plus `moreRLActions*` composites).

---

## 9. What is NOT in the payload

Do not expect to find, or to be able to set, these here:

- Field labels and API names (resolved from field ID)
- Custom button labels — "Setup Account Resources" is only ID `2582206000047549161`
- Related-list names — "Proposals" as a *tab* label is `ui.value.name`, but the list itself is an ID
- Link display text — "GDrive", "Miro", "Books", "Github", "Coda" all come from CRM
- Picklist values, mandatory flags, field-level permissions
- `uniqueid` — server-generated, never sent. See §10.

---

## 10. The response

Captured in `reference/captures/accounts-main-account.response.json` (19 KB). It is a pure
acknowledgement — it does **not** echo the canvas back:

```jsonc
{
  "canvas_view": [
    {
      "code": "SUCCESS",
      "message": "view updated successfully",
      "status": "success",
      "details": {
        "id": "2582206000057761014",          // the canvas view id
        "children": [                          // FLAT list, not a tree
          { "uniqueid": "6d42362a-6172-44e2-a68c-5bd4f8380b54" },
          { "uniqueid": "ca789e9c-c55d-491e-a3f6-0905875c8d35" }
          // … 372 total
        ]
      }
    }
  ]
}
```

Verified across all three captures (c1 request-only had no ids; c2 and c3 have request + response):

| | request nodes | `uniqueid` sent | returned | sent ids kept | new ids minted |
|---|---|---|---|---|---|
| c1 | 372 | 0 | 372 | — | 372 |
| c2 | 507 | 217 | 506 | **217 / 217** | 289 |
| c3 | 427 | 178 | 425 | **178 / 178** | 247 |

- **`uniqueid` IS sent on updates.** c2 and c3 both include it on 40–43% of nodes. c1 sent none
  because it was the first save of a newly-built canvas.
- **It is a stable identity, not an ephemeral handle.** Every id sent came back unchanged, zero
  lost. The server mints a new UUID only for a node that arrives without one.
- Returned count is ~one per node (506/507, 425/427). The shortfall is nodes carrying an empty
  `position: {}`.
- The list is **flat and NOT in document order** — shared ids come back in a different relative
  sequence than they were sent. Do not match by index.
- Which nodes carry one: all `component`, `action`, `row`, `section`, `relatedlist`,
  `static_content`, `separator` — but only *some* `field` nodes (49 of 178 in c2).

**Consequences for the generator (update-only project):**

1. **GET the live canvas first and carry its `uniqueid`s onto the matching nodes before PUT.**
   Omitting them makes Zoho treat every node as new, risking loss of node identity that
   `script_info.mapping` and canvas rules may reference.
2. Match nodes by tree position/content when transplanting ids — **not** by index into the
   response list, which is unordered.
3. Use the count as a post-deploy sanity check, allowing for the empty-`position` shortfall.
4. Check `code == "SUCCESS"` and `status == "success"`. Error-response shape is still unobserved.

> **Correction history.** This section previously claimed `uniqueid` was never sent and was
> regenerated on every save. Both were wrong, inferred from c1 alone. The "zero overlap" evidence
> came from comparing two *different* canvases, not two saves of one. See `mistakes.md`.

### Round-trip verification (live GET vs captured request)

`src/roundtrip_test.py` GETs each canvas from live CRM and diffs it against the captured request.
Run 2026-09-04 against Camco — **all three canvases round-trip cleanly**:

| | captured nodes | live nodes | sent ids still live | field refs lost | field refs gained |
|---|---|---|---|---|---|
| c1 | 372 | 372 | n/a (sent none) | 0 | 0 |
| c2 | 507 | 506 | **217 / 217** | **0** | **0** |
| c3 | 427 | 425 | **178 / 178** | **0** | **0** |

Two behaviours to know before generating payloads:

1. **The server prunes empty wrapper nodes.** The 1–2 node shortfall is typeless nodes carrying no
   position and no children, e.g. `{"ui":{"value":{"style":{"default":{}}},"index":3},"children":[]}`.
   Harmless, but it means node counts will not match exactly after a save.
2. **The server reorders related-list sibling cards.** Nodes appear at different sibling indices in
   the GET than in the request, while the content multiset is identical (field-id counts match
   exactly in both directions). **Never match nodes by tree path across a save** — match on
   `uniqueid`, or on content.

The GET adds server-owned keys not present in a request: `componentid` (on nearly every node),
`uniqueid`, plus view-level `created_by`, `created_time`, `modified_by`, `modified_time`,
`generated_type`, `is_default`, `profiles`, `share`, `source`. The request-only key is `action`.
A generated request body should carry none of the server-owned keys except `uniqueid`.

---

## 11. Open questions

1. What does an **error** response look like (bad field ID, malformed geometry, bad canvas id)?
   Everything captured so far is a success path.
2. Are `canvas_rules` / `script_info` populated forms needed, and what is their schema?
   Both are empty in the capture.
3. Do `theme` values beyond the six observed exist, and does Zoho validate the `class` vocabulary
   on write or accept anything?
