# cc-zcrm-canvas-builder

## What this project is

A system to **generate Zoho CRM Canvas templates programmatically and deploy them into CRM**.

The workflow John wants: ask an agent for a canvas template for a given module → the agent
generates the Canvas JSON → the agent inserts it into Zoho CRM via the save API. Source of the
requirement is a screen recording walkthrough (see `canvas-resource-links.txt` for Zoho docs).

Not a one-off canvas. The point is repeatable template generation across modules.

## Sibling project: the zcrm-canvas plugin

This project is being turned into a shareable Claude Code plugin at
**`e:\claude-projects\zcrm-canvas`** (its own git repo, installable by marketplace). Design spec:
`docs/superpowers/specs/2026-09-07-zcrm-canvas-skill-design.md`. The split of roles:

- **This repo is the evidence base and Camco's history.** Captures, HARs, rollbacks, the
  Camco builders, and the docs derived from them live here and stay here. Nothing under
  `reference/` or `output/` is ever copied into the plugin; the plugin's tests read this checkout
  through `ZCRM_EVIDENCE_DIR` when they need it.
- **The plugin is where new canvases get built** once it exists. It carries the ported code
  (`auth`, `api`, `shapes`, `validate`, the compiler), the derived assets (icon catalog, presets,
  `vocabulary.json`), the default theme, and the references.

**Parity rule.** When functionality changes here, carry the change to the plugin where it makes
sense, in the same session, and say so in the final message. Concretely:

- A new or changed builder in `src/canvas_shapes.py` → the plugin's `shapes.py`.
- A new validator rule, or a calibration fix, in `src/validate.py` → the plugin's `validate.py`
  (and re-run the 33-file calibration there).
- A new observed construct, class token, style key, icon, action id or datatype mapping → the
  plugin's `vocabulary.json`, its catalog or palette under `assets/`, and its `references/` copy
  of `canvas-schema.md` / `canvas-constructs.md`.
- A new design rule or a change to the header conventions, card metrics or corner rule →
  `references/design-rules.md` and `themes/default.json`.
- A new endpoint, endpoint limit or auth quirk → `api.py` / `auth.py` and the endpoint table in
  the plugin's `canvas-schema.md`.
- A workflow change (Step 0, the mockup round, deploy gates) → `SKILL.md` and the matching
  `commands/*.md`.

What does **not** go across: Camco ids, Camco captures, per-canvas builders
(`build_contacts_*.py`, `build_proposals_v1.py`), rollbacks, the HARs, anything in `.env`.
Those are this org's data; the plugin gets a spec in `examples/` at most, labelled as an
example. If the plugin folder does not exist yet or is mid-build, note the parity item in the
final message instead of guessing at its layout.

## Scope (settled 2026-09-04)

- **Update only.** PUT to an existing canvas view. Creating canvases via POST is out of scope.
  The **canvas view ID must be a parameter** of the deploy call, not hardcoded.
- **Target: Camco org `647376701`, Accounts module.** No sandbox exists and John does not want
  one — work against the live Camco org, carefully.
- The captured Accounts canvas is a **structural sample**, not the design standard. Real canvases
  will differ over time.
- **Build an org-level base template** carrying branding and colour scheme, with per-canvas
  layouts on top. Camco first; the design must allow other client orgs later.
- **Styling should stay flexible/parameterised** rather than locked to a fixed house style.

## Status

Pipeline proven end to end (OAuth, GET, PUT, restore).

**Live on Proposals canvas `2582206000076741077` (2026-09-07 12:46): "Proposals Canvas v1"**, built
by `src/build_proposals_v1.py`: 263 nodes, 11 tabs (Overview, Pricing, Activity, Record, a lookup
All-Fields tab on Related_Account, Timeline, 5 related-list tabs). Fields resolve by api_name
against the live Standard layout at build time; nothing numeric is hardcoded but the view id.
Design mockup: `output/camco-647376701/Proposals/proposals-v1.preview.html`. Rollback:
`reference/captures/rollback-2582206000076741077-20260907-124655.json` (the Zoho starter
"Proposal Canvas 1"). **Editor check pending.** Two facts settled while building it:
the editor mints `lookup_associations.connection_id` client-side (it appears fully formed in the
first PUT, never in a prior response), so the builder mints one; and the components palette
endpoint (`/crm/v2/settings/canvas/views/components`) is browser-session only, 401 over OAuth, so
the header uses only action ids Zoho itself placed on this module (`mail_merge`, `edit`,
`morebutton`). Corners are 3px max everywhere (John's rule, now in `BRIGHT`).

**Live on Contacts canvas `2582206000076641025` (2026-09-06 20:07): "Contacts Canvas v3.1"**, built
by `src/build_contacts_v31.py` on top of `build_contacts_v3.py`: 511 nodes, 19 tabs (4 composite,
10 related-list, Interactions via `journeys`, 3 lookup All-Fields tabs, All Fields). The server
kept the 3 `lookup_associations` connection ids from the round-3 recording. Rollback:
`reference/captures/rollback-2582206000076641025-20260906-200727.json`. Editor check pending at
the time of writing; do not build on it until John confirms it opens.

Structural knowledge now rests on a real evidence base, not one capture:

- **25 consecutive editor saves** in two recorded sessions, one construct added per save
  (`reference/ui-capture/`, manifest in its README). Diffing consecutive saves gives the exact node
  shape the editor emits per construct.
- **Zoho's own preset JSON and catalogs** served to the editor (`reference/zoho-assets/`): text,
  field, section, tab, button, related-list and table presets, four ReusableViews, the components
  palette (valid action ids), and the 231-name icon catalog.
- The three gallery templates (`reference/captures/`).

**`docs/canvas-constructs.md` is the per-construct spec.** Read it before writing any builder code.

**Method rule.** When a structure is undocumented, capture the tool that produces it (a recorded
editor session) before inferring from its output. Three deploys broke the editor because rules were
inferred from static end states; one 15-minute capture settled all of them. Every enumerated value
(icon name, action id, theme, class token) must come from an observed catalog, never from analogy:
14 of 20 guessed icon names did not exist.

### What the captures answered

- Canvas has **three container engines**: absolute (`Custom Layout`), `Flex Layout`, `Grid Layout`.
  Flex items reflow (`property.flex_item`, `zc-fit-height-content`). The old "purely absolute" claim
  was wrong; within absolute containers the geometry arithmetic held on all 25 saves.
- `autoheight: true` on Static Text grows the box to its content.
- The same related list may appear more than once (the editor itself did it).
- Static Text sits directly inside a container; no wrapper needed.
- `uniqueid` is absent from about half the nodes in the editor's own output.
- Query-backed related lists exist (`details.connection_id`, root `related_to.data_hub_associations`).

### Still unobserved

- Grid item shape; `system` and `zia` palette components (`blueprint`, `zia_score`, ...)
- Responsive Mode payload; populated `canvas_rules` / `script_info`; error responses
- **Populated `custom_style`** (the editor's Custom CSS box). Every node carries the slot, and in
  all 33 Zoho-authored files it is `{}`. Do not emit it until one save with a custom CSS
  property has been captured; that single save would settle the shape.
- **A toggle switch.** There is none. Boolean fields carry only `datatype: "boolean"` and Zoho
  renders its own checkbox. Mockups must show a checkbox, not a switch (John asked, 2026-09-07).
- **Which specific deviation broke the editor in the v2 deploys.** Invalid icon names are the
  leading candidate. The rebuild should emit only observed shapes and be opened in the editor
  before it is called working.

## Pipeline status — write path VALIDATED 2026-09-04

A no-op deploy has been executed successfully against live Camco CRM.

`src/noop_deploy.py <view_id> [--execute]` — GETs a canvas, strips server-owned keys, PUTs it
back unchanged, then GETs again and verifies. Run against c3 (Contacts, `2582206000076641025`):

```text
PUT  -> code=SUCCESS status=success "view updated successfully", 425 uniqueids returned
after -> 425 nodes, 425 uniqueids, 154 field refs
        uniqueid set identical to before, 0 changed
```

This proves end to end: OAuth → GET → build request body → PUT → verify. The body-construction
rules below are correct against the real API, not just against captures.

**Server-owned keys — strip these from a GET before PUTting it back:**
`componentid`, `created_by`, `created_time`, `modified_by`, `modified_time`, `generated_type`,
`is_default`, `profiles`, `share`, `source`. Keep `uniqueid`. Add `action: "edit"`, which appears
in captured requests but not in GET responses.

## Layout

```text
docs/canvas-schema.md                    THE reference: update workflow, full body schema, every attribute, enumerations
docs/canvas-constructs.md                per-construct JSON as the editor emits it
docs/canvas-key-inventory.md             generated: every key in every slot, counts, hosts, sample values
docs/canvas-json-structure.md            envelope, request/response, vocabulary (older; constructs.md wins)
reference/ui-capture/                    25 editor saves, one construct per save, plus manifest
reference/zoho-assets/                   Zoho presets, components palette, 231-name icon catalog
src/                                     the builder: auth, canvas client, validator, templates
output/<org-slug>-<org-id>/<Module>/     generated templates, one folder per org then module
reference/captures/                      parsed request + response payloads (JSON, diffable)
.env.example                             OAuth key names (real values go in gitignored .env)
canvas-1-example-visual.png              Canvas Preview screenshot of canvas 1
canvas-resource-links.txt                Zoho documentation URLs
mistakes.md                              running log of mistakes worth not repeating
```

**`reference/captures/` holds two kinds of file.** Keep the distinction — cleanup depends on it.

*Reference payloads* are the three original captures and their responses. They are the evidence
this project's structural rules were derived from, they cannot be regenerated, and
`src/roundtrip_test.py` reads the `.payload.json` three by name:

```text
accounts-main-account.{payload,response}.json          c1 — Accounts "Main Account"
accounts-canvas-template-2.{payload,response}.json     c2 — Accounts, 368 nodes
contacts-canvas-template-3.{payload,response}.json     c3 — Contacts, 305 nodes
```

*Rollback snapshots* (`rollback-<view_id>-<timestamp>.json`) are written automatically before
every PUT. Keep the most recent one or two per view as a restore point and delete the rest — they
pile up fast and older ones are superseded the moment a newer deploy succeeds. Restore with
`python src/restore.py <rollback-file> --execute`.

Anything named `live-*.json`, `noop-body-*`, `edited-body-*` or `pre-put-rollback.*` is a
regenerable build artifact. Delete freely.

**Raw browser captures are gitignored and local only** —
`save-zcrm-canvas-api-curl-request.txt`, `canvas-template-request-2.txt` and
`canvas-template-request-3.txt` each carry a live session Cookie / `x-zcsrf-token`. The
credential-free parsed payloads above are what the code actually reads; use those.

## The essential facts

**Endpoint.** `PUT https://crm.zoho.com/crm/v8/settings/canvas/views/{id}` with
`Content-Type: text/plain;charset=UTF-8` (body is JSON regardless). The PUT **replaces the whole
canvas** — there is no partial update. Always capture current state before writing.

**Auth is OAuth 2.0, confirmed working.** Use `Authorization: Zoho-oauthtoken {token}` — that is
Zoho's own scheme name. Zoho also accepts `Authorization: Bearer {token}`, which is what Postman's
OAuth2 helper emits and what the original capture showed, so both work; prefer `Zoho-oauthtoken`
when hand-rolling the header. The session cookies and `x-zcsrf-token` / `x-murphy-*` headers in the
original browser capture are **not needed** — build against OAuth, ignore them.

Verified 2026-09-04 against live Camco with a self-client refresh token: the refresh grant mints an
access token (1 h life) and `GET /crm/v8/settings/canvas/views/2582206000057761014` returns `200`
with `name: "Main Account"`, `feature: DetailView`, `state: active`. Credentials are in `.env`.
The token grants `ZohoCRM.modules.ALL` + `ZohoCRM.settings.ALL` (plus org/users/bulk/notifications/
coql/search), which is far broader than the builder needs — `modules.ALL` includes record DELETE
across every module of the live org. Canvas work only requires `ZohoCRM.settings.canvas.ALL` plus
read on fields/modules/layouts/related_lists; consider a narrower second token for the deploy path.

The token endpoint reports `api_domain: https://www.zohoapis.com`, but the canvas call is confirmed
working against `crm.zoho.com`. Both hosts serve it; `ZOHO_API_HOST` stays `crm.zoho.com`.

**The response is an acknowledgement, not an echo.** It returns `code: "SUCCESS"`,
`message: "view updated successfully"`, `details.id`, and a flat list of `uniqueid` UUIDs — roughly
one per node sent (506 of 507 in c2; 425 of 427 in c3; the shortfall is nodes with empty
`position: {}`). The list is **not** in document order.

**`uniqueid` is a STABLE node identity — send it on updates.** Verified across c2 and c3: every
`uniqueid` sent came back unchanged (217/217 and 178/178, zero lost), and the server minted new
UUIDs only for nodes that arrived without one. c1 sent none because it was a first save of a
newly-built canvas; c2/c3 are re-saves and echo the existing IDs.

Practical rule for this update-only project: **GET the live canvas first, carry its `uniqueid`s
onto the matching nodes, then PUT.** Omitting them makes Zoho treat every node as new, which
risks orphaning node identity that `script_info.mapping` and canvas rules may depend on.

*(Two earlier conclusions here were wrong — "never sent" and "regenerated every save". Both came
from a single capture. See `mistakes.md`.)*

**Positioning.** Every node carries
`position {start_x, start_y, end_x, width, height, depth, order?, min_top?, min_left?, _locked_?}`.
Whether pixel placement is the *only* layout mode is **still unresolved** — see the unresolved
questions above. Root width is **not fixed**: 1440 in c1, 1100 in c2/c3. The one reliable
arithmetic across all three captures is `end_x == start_x + width` on every node except the root,
and root `end_x == 3 × root width`.

**Fields are ID references, not definitions.** A field node is just
`{id, datatype, type, ui:{position, class, style}}`. No api_name, no label — Zoho resolves both
from the CRM field ID at render. So templates must key on **api_name** and resolve IDs at build
time, or they work in exactly one org.

**Field IDs are module-scoped per subtree.** Fields inside a related-list tab belong to the
*related* module. Verified: the four fields under the Proposals tab resolve against `Proposals`,
not `Accounts`. A global ID resolver will silently produce a broken canvas.

**Two ID conventions.** System actions use string IDs (`back`, `edit`, `reviewHistory`,
`morebutton`, `navigate`, `timeline`) and are org-independent. Everything else uses numeric CRM
IDs and must be remapped per org.

**Only `static_content` holds literal text.** Everything else visible on screen (field labels,
custom button labels, link text, related-list names) lives in CRM, not the payload.
`"Basic Info"` is stored title case and uppercased by the `zcanvasuppercase` CSS class.

## Hard constraints discovered by breaking things

**Retracted:** an earlier version of this section said a related-list id may appear only once per
canvas. The recorded editor session disproved it (Zoho placed one list twice and saved fine). It
was a guess dressed as a rule; see `mistakes.md`.

**Enumerated values come from catalogs.** `icon` names must be in
`reference/zoho-assets/icon-catalog.txt`; action ids must be in the components palette (or the
editor-generated `moreRLActions<id>`, `ExpandView`, `newEvent`). `src/validate.py` errors on both,
and is calibrated to pass every one of the 29 Zoho-authored files under `reference/`. Any new
validator rule must pass those files first; if it fires on Zoho's output, the rule is wrong.

**A `SUCCESS` response is not verification.** The save endpoint validates far less than the editor
requires, so a canvas can be valid to the API and fatally malformed to the UI. Re-GETting through
the API cannot detect a UI-side crash. **After any structural deploy, open the canvas in the Zoho
builder before reporting it as working.**

**Restoring:** `python src/restore.py reference/captures/rollback-<viewid>-<stamp>.json --execute`
takes a saved GET, strips the server-owned keys and PUTs it back. Rollbacks are written
automatically before every deploy.

## Working rules

- **Read `docs/canvas-json-structure.md` before touching canvas JSON.** It has the full node-type
  schema, the 35-token CSS class vocabulary, the style property list, and the composite structures
  (Tab Layout, Table Layout).
- **Never invent class tokens or style properties.** Reuse the observed vocabulary. Zoho's typo
  `zcanvas-horizantol-top` is real — keep it.
- **There is no sandbox — every deploy hits live Camco CRM.** Before any PUT, GET the current
  canvas and save it to `reference/captures/` so there is a rollback. Get an explicit go-ahead
  for the first deploy of any canvas.
- **Profile the module before designing.** Fields, layouts, layout membership, sections, and the
  related-list inventory, fetched live. See "Step 0" under Design workflow. A canvas designed
  without knowing what the module offers is guesswork.
- **Resolve IDs from live CRM, never hardcode them** in a template.
- **Canvas view ID is always a parameter**, never baked into a template. It lives in the
  `.meta.json` sidecar next to each generated file, not in the payload.
- **Generated templates go to `output/<org-slug>-<org-id>/<ModuleApiName>/`.** Module folders use
  the exact case-sensitive CRM API name. Camco production is `camco-647376701`. See
  `output/README.md`.
- Files under `output/` are **generated artifacts** — regenerate them, never hand-patch.
- Keep branding (colours, fonts, spacing) in an **org-level base template** separate from the
  per-canvas layout, so a second client org means a new base, not a rewrite. The Camco base is
  `BRIGHT` in `src/canvas_shapes.py`.
- **Corners 3px max, everywhere.** John: "I do not like the rounded look. But it can be used
  subtly to soften." Cards, tiles and buttons 3px, chips and pills 2px, soften with `box_shadow`.
  `BRIGHT` carries `radius_card`, `radius_chip`, `radius_button`; never hardcode a larger radius.
- **One set of card metrics.** Every card, related-list card included: 18px inset, icon 22px at
  y=15, title 14px semibold at x=50/y=17, content from y=52, rows 29px. Things that share a role
  share exact metrics; John flags anything that "sticks out like a sore thumb".
- **Header conventions (settled on Proposals, 2026-09-07).** Record name left at 24px; the status
  picklist as a pill with the button metrics (34px tall, same top as the buttons, 3px radius);
  actions right-aligned as one group ending at the same right edge as the content below; a row of
  stat tiles under it with a solid white hero tile for the one number that matters. No back arrow,
  no record image, no navigator button, no subtitle lines: John removed all of them. Lookups and
  contact details go in a details card, not the header.
- **Only `action` ids Zoho has itself placed on that module** go in a header. The palette
  endpoint is browser-session only (401 over OAuth), so the ids in the module's existing canvas
  (`GET` it first) are the observed set. On Proposals that is `mail_merge`, `edit`, `morebutton`,
  `back`, `navigate`.
- **Credentials live in `.env` only** — never in a template, capture, doc, commit, or chat
  message. `.gitignore` already excludes it. `.env.example` holds the key names and no values.
- Log meaningful mistakes in `mistakes.md`.

## Design workflow

### Step 0 — profile the module before designing anything

**Never start a canvas design from a field list someone handed you, or from what a previous canvas
happened to use.** Before any mockup or JSON, build a picture of everything the module can show,
so the design is a deliberate choice out of the full set rather than an accident of what was
convenient to look up.

Fetch live from CRM every time. **Do not cache module profiles to disk** — CRM schemas drift
(fields added, deleted and recreated with new IDs, sections renamed, related lists added), and a
stale profile silently produces a broken canvas. The cost of re-fetching is small next to
deploying a canvas built on IDs that no longer resolve.

Scope is **the module plus one level of relationships**:

**Three calls cover it** (resolved and tested 2026-09-06 against live Accounts):

1. **Fields, layouts, layout membership and sections — all from `getLayouts(module)`.**
   One call. Each field nested under its section carries `api_name`, `id`, `field_label`,
   `data_type`, `custom_field`, `section_id`, `required` and `visible`, so layout membership is
   implicit in the nesting. **A separate `getFields` call is redundant for the primary module.**
   Output exceeds the tool token cap (306 KB for Accounts) and lands in a file — parse it with
   python/jq, do not read it. The same data comes from
   `GET /crm/v8/settings/layouts?module={Module}` through `src/zoho_auth.py`, which is what the
   builders use (`Profile` in `src/build_proposals_v1.py`): no MCP round trip, no file, resolved
   by `api_name` at build time on every run. Also fetch `GET /crm/v8/settings/modules` for the
   module id, and `/crm/v8/settings/custom_buttons?module=` (204 = none) and
   `/crm/v8/settings/blueprints?module=` so the design knows what actions and process exist.

   A field existing on the module does not mean it is on the layout the canvas targets, and
   placing an off-layout field fails silently. Reading fields *through* the layout removes that
   whole class of error, because anything you can see is by definition on the layout.

   The section structure is the CRM's own answer to how this data groups. Work with it or
   deliberately depart from it, but do not ignore it.

2. **Related-list inventory — `GET /crm/v8/settings/related_lists?module={Module}`**, via the
   OAuth client in `src/zoho_auth.py`. There is **no MCP tool for this**; the Camco server has
   no related-lists metadata call. Each entry gives `id`, `display_label` and the target
   `module` api_name.

   Note that some related lists have `module: null` — grouped and `custom_function` types like
   ChronologicalView, Google Drive Files and Zoho Projects. They have no target module, so
   nothing resolves against them and a canvas cannot place fields from them.

3. **Fields on a related module — `getFields(relatedModule)`, only when the design actually
   places them.** Do not pre-fetch fields for all twenty-odd related modules. When the layout
   calls for showing columns from Proposals, fetch Proposals then. Fields inside a related-list
   subtree resolve against the *related* module, never the primary one.

**Do not reach for the `DI_ZCRM` or `ISS_ZCRN` MCP servers.** They point at different orgs
(Decker and ISS) and have some tools Camco lacks, which makes them tempting and wrong.

The point is comprehension, not collection. State plainly, before designing, what data the module
makes available and what the design will and will not use. If a whole category of data is being
left off the canvas, that is a decision worth naming rather than an omission.

### Then mock it

Design is done as a **free-form HTML mockup first**, for John to inspect visually, then converted
to Canvas JSON. HTML is a real design surface here, not just a preview.

Canvas is absolute-positioned with fixed-height boxes, so some HTML will not convert. Expected
sticking points: flexbox and percentage reflow, overlapping / z-stacked elements, inline text flow
inside a field, and content-driven height. **When something will not map, say so and propose the
nearest Canvas-representable alternative — never silently approximate.** John's instruction is to
mock freely and work through walls as they come up.

Note the preview limit: field labels and values live in CRM, not the payload, so a mockup shows
layout, spacing, colour and structure — not real record data.

**How the mockup round works (settled on Proposals, 2026-09-07).**

- The mockup is a fixed 1100px page with every box absolute-positioned at the **same
  coordinates the Canvas JSON will use**, so conversion is one-to-one and nothing is
  re-designed in the builder. Labels are the live CRM labels; values are marked as examples.
- Publish it as a private Artifact and give John the link. He reviews screenshots with
  annotations (arrows, circles, yellow highlights) and sends changes one screenshot at a time.
  Republish to the **same URL** each round; several short rounds are normal (five on Proposals).
- Mockup fonts: Zoho Puvi is what CRM renders and cannot be loaded from Google Fonts, so use
  Segoe UI as the stand-in and say so in the page note. Do not pick a display face.
- Show Zoho-rendered things as Zoho renders them: booleans as checkboxes, related lists as a
  dashed "rendered by Zoho" box, a lookup All-Fields tab as the linked record's sections.
- Only after John says "deploy" does any builder code get written. Save the mockup next to the
  output as `<canvas>.preview.html`; it is the design source named in `.meta.json`.

## Environment

- Camco CRM org: **647376701**. Accounts module `2582206000000002177`, layout
  `2582206000000091029`, canvas view `2582206000057761014`. Proposals module
  `2582206000008466209` (`CustomModule6`), layout `Standard` `2582206000008466208`, canvas view
  `2582206000076741077`. Proposals has no custom buttons and one active blueprint on
  `Proposal_Status`.
- The **Camco ZCRM MCP** resolves schema metadata. John expanded its permissions **2026-09-06**;
  it now has `getModules`, `getModuleByApiName`, `getLayouts`, `getLayoutById`, `getFields`,
  `getFieldsWithID` and `executeCOQLQuery`. It also carries substantial **write** tools against
  the live org (`createFields`, `updateLayout`, `createRecords`/`deleteRecords`, bulk jobs,
  functions, workflow rules) — there is no sandbox, so treat those with care.
- It still has **no related-lists metadata tool**. Use
  `GET /crm/v8/settings/related_lists?module={Module}` through `src/zoho_auth.py`.
- Two schema gotchas, both found by testing rather than reading:
  `getModuleByApiName` does **not** accept the `include` parameter the DI server has (it takes
  `fields` and `include_inner_details`); `fields: ["related_lists"]` returns `PATTERN_NOT_MATCHED`,
  and `include_inner_details: "related_lists"` is accepted but changes nothing. Related lists
  never come back from that call.
- `getFields` and `getLayouts` output both exceed the tool token cap and get written to a file —
  parse with python/jq rather than reading.
- **Accounts baseline, verified live 2026-09-06:** one layout (`Standard`,
  `2582206000000091029`), 12 sections, 125 fields on the layout, 23 related lists. The module and
  layout IDs above still resolve.

## Maintenance

**Parity with the plugin.** See "Sibling project" near the top: any change to the working code,
the observed vocabulary, the design rules or the workflow here is carried to
`e:\claude-projects\zcrm-canvas` in the same session where it makes sense, and the final
message names what was carried and what was deliberately left behind.

**Keep this file and `docs/canvas-json-structure.md` current.** Both describe an undocumented
Zoho payload derived from a single capture, so they go stale quietly and dangerously.

Update them when any of the following happens:

- A new capture is taken (new module, an error response) — fold in whatever it reveals and note
  what is still unobserved.
- A generated canvas is rejected by the API — record the error shape and the payload difference
  that caused it. Error responses are still unobserved and are the biggest remaining gap.
- A new node type, theme, class token, or style property is observed.
- The project structure changes.

At the start of a session, sanity-check that the IDs above still resolve. Zoho changes IDs when
fields are deleted and recreated. If something no longer resolves, fix the doc before building on it.
