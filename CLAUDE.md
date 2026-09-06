# cc-zcrm-canvas-builder

## What this project is

A system to **generate Zoho CRM Canvas templates programmatically and deploy them into CRM**.

The workflow John wants: ask an agent for a canvas template for a given module → the agent
generates the Canvas JSON → the agent inserts it into Zoho CRM via the save API. Source of the
requirement is a screen recording walkthrough (see `canvas-resource-links.txt` for Zoho docs).

Not a one-off canvas. The point is repeatable template generation across modules.

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

Request/response envelope mapped and auth confirmed. **Blocked on sample size:** everything known
about the payload comes from a single simple Accounts canvas. John is providing more captures of
differently-configured canvases before geometry can be described or templates built.

**Do not generalise from one capture.** A sample shows what that canvas used, never what Canvas
supports. The geometry doc was written this way, was wrong, and is parked at
`docs/draft/geometry-rules.DRAFT.md`. See `mistakes.md`.

### Waiting on

More canvas captures covering, ideally: a responsive/multi-breakpoint canvas, one using
`autoheight`, one with percentage-width or otherwise non-fixed sizing, a different module, and a
visually complex layout. Each capture should be request + response where possible, saved to
`reference/captures/`.

### Unresolved layout questions

- What does `autoheight` actually do?
- When is `layoutstyle.field.width: "100%"` or a column `percent` honoured over the pixel `width`?
- What changes between the builder's Default Mode and Responsive Mode, and how are the two extra
  breakpoints implied by root `end_x: 4320` expressed?
- Does anything reflow, or is placement always explicit?

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
docs/canvas-json-structure.md            full structural spec of the Canvas JSON — READ THIS FIRST
output/<org-slug>-<org-id>/<Module>/     generated templates, one folder per org then module
reference/captures/                      parsed request + response payloads (JSON, diffable)
.env.example                             OAuth key names (real values go in gitignored .env)
save-zcrm-canvas-api-curl-request.txt    the original captured PUT (748 KB) — GITIGNORED, local
                                         only: carries a live session Cookie and x-zcsrf-token.
                                         Use the parsed copies in reference/captures/ instead.
save-zcrm-canvas-api-curl-response.json  the captured 200 OK response (19 KB)
canvas-1-example-visual.png              Canvas Preview screenshot of that same canvas
canvas-resource-links.txt                Zoho documentation URLs
mistakes.md                              running log of mistakes worth not repeating
```

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

**A related-list ID may appear at most ONCE per canvas.** Using the same related list in a custom
tab *and* on its own related-list tab is accepted by the save API (`code: SUCCESS`, every node
retained) but **crashes the Zoho builder** — it loads as a blank white screen with JS errors and
the canvas cannot be edited until restored. Verified 2026-09-06 when 13 duplicated IDs across 28
tabs bricked the Contacts canvas. `src/validate.py` now errors on this.

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
  per-canvas layout, so a second client org means a new base, not a rewrite.
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
   python/jq, do not read it.

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

## Environment

- Camco CRM org: **647376701**. Accounts module `2582206000000002177`, layout
  `2582206000000091029`, canvas view `2582206000057761014`.
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
