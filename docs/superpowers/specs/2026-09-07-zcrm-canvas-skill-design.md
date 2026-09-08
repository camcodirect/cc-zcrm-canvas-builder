# zcrm-canvas: a shareable Claude Code plugin for Zoho CRM Canvas templates

Design spec, 2026-09-07. Turns the cc-zcrm-canvas-builder project into a plugin anyone can
install, point at their own Zoho CRM org, and use to design, build and deploy Canvas detail
views the way this project does it.

## 1. Purpose and scope

The plugin gives Claude a fixed, safe workflow for Canvas work:

```text
profile a module  ->  design a mockup with the user  ->  build JSON  ->  deploy  ->  editor check
```

plus a learning path (`learn`) so the plugin's knowledge of the undocumented Canvas format grows
from recorded editor sessions instead of guesses.

In scope: DetailView canvases, update-only (PUT to an existing canvas view), any org, any module.
Out of scope, unchanged from the project: creating canvases (POST), other canvas features
(list view, home page), Custom CSS, Blueprint / Stage / Zia components, anything not yet observed.

Users talk to Claude; they do not hand-write files. Every file format below is chosen for the
compiler and for diffs, not for hand authoring.

## 2. Distribution and layout

A Claude Code plugin in its own git repository, installed through a marketplace entry.

```text
zcrm-canvas/
  .claude-plugin/plugin.json          name, version, description
  README.md                           install, one-time org setup, the one manual step
  skills/zcrm-canvas/
    SKILL.md                          the method and safety rules; short; points at references
    references/
      canvas-schema.md                envelope, root, slots, enumerations (from this project)
      canvas-constructs.md            per-construct JSON as the editor emits it
      design-rules.md                 header conventions, card metrics, corner rule, theme schema
      spec-format.md                  the canvas spec schema with the Proposals example
      learning.md                     how to record a session and what `learn` does with it
  commands/
    canvas-profile.md
    canvas-design.md
    canvas-build.md
    canvas-deploy.md
    canvas-restore.md
    canvas-theme.md
    canvas-learn.md
  scripts/zcrm_canvas/                Python 3.10+, stdlib only
    __init__.py
    auth.py                           OAuth refresh grant, token cache (zoho_auth.py)
    api.py                            canvas GET/PUT, metadata GETs (zoho_canvas.py + Profile)
    shapes.py                         observed node builders (canvas_shapes.py)
    theme.py                          theme loading, defaults, org default resolution
    spec.py                           spec loading and validation against the live profile
    layout.py                         grid -> absolute coordinates
    compile_html.py                   spec -> mockup
    compile_json.py                   spec -> canvas_view payload
    validate.py                       structural validator + catalog checks
    audit.py                          vocabulary audit against assets/vocabulary.json
    learn.py                          HAR -> saves, diffs, vocabulary and construct report
    cli.py                            `python -m zcrm_canvas <command> ...`
  assets/
    icon-catalog.txt                  231 names from Zoho's CSS
    presets/*.json                    text, field, section, tab, button, related-list, table
    components-palette-contacts.json  the one palette we have; per-module palettes are browser-only
    vocabulary.json                   every class token, style key, theme, type, datatype, ui key
                                      observed across the 33 Zoho-authored files (derived, small)
  themes/
    default.json                      the plugin default: this project's rules and palette
  examples/
    contacts.spec.json                the shipped example: Contacts, standard fields and
                                      related lists only, so it validates in any org
    contacts.preview.html             what it compiles to
```

Proposals is a Camco custom module, so it is not the example; it is the golden test input
(§10) and lives under `tests/fixtures/` as a spec, not under `examples/`.

Nothing org-specific ships except the example spec, which is labelled as an example. The 33
capture files and the HARs stay in this project as the evidence base; the plugin carries what is
derived from them.

## 3. Configuration: orgs, credentials, themes

Per-user, outside any project, so the plugin works from any directory:

```text
~/.zcrm-canvas/
  orgs/
    camco/
      org.json          { "org_id": "647376701", "api_host": "https://crm.zoho.com",
                          "accounts_host": "https://accounts.zoho.com",
                          "default_theme": "camco-bright" }
      credentials.env   ZOHO_CLIENT_ID / ZOHO_CLIENT_SECRET / ZOHO_REFRESH_TOKEN (mode 600)
      themes/
        camco-bright.json
        camco-dark.json
      captures/         rollbacks and profile-free captures for this org
```

- The active org is `--org <slug>`, else `ZCRM_CANVAS_ORG`, else the only org configured, else
  ask.
- Credentials are never read from a project directory and never written anywhere else. The
  README recommends a token scoped to `ZohoCRM.settings.canvas.ALL` plus read on
  modules/layouts/related_lists/custom_buttons/blueprints, not `modules.ALL`.
- Generated output goes to the current working directory under
  `output/<org-slug>-<org-id>/<ModuleApiName>/`, same convention as today, so a consulting
  project keeps its canvases with the project.

### Themes

A theme is a JSON token file. The plugin ships `themes/default.json`, which is this project's
`BRIGHT` palette plus the design rules John set:

```jsonc
{
  "name": "default",
  "colors": { "canvas_bg": "…", "card_bg": "…", "banner_from": "…", "banner_mid": "…",
              "banner_to": "…", "text": "…", "text_2": "…", "text_muted": "…",
              "text_invert": "…", "accents": { "indigo": "…", "sky": "…", "teal": "…",
              "violet": "…", "amber": "…", "rose": "…", "emerald": "…" }, "hairline": "…" },
  "radius": { "card": "3px", "chip": "2px", "button": "3px" },     // 3px max, enforced
  "shadow": "0px 6px 20px 0px rgba(15, 23, 42, 0.06)",
  "type":   { "body": "13px", "heading": "14px", "micro": "11px", "name": "24px" },
  "metrics":{ "canvas_width": 1100, "gap": 22, "row_height": 29, "card_inset": 18,
              "card_title_y": 15, "card_content_y": 52, "icon_size": 22,
              "banner_height": 206, "button_height": 34, "stat_tile_height": 58 },
  "header": { "style": "gradient-stats" }                          // the one header layout in v1
}
```

An org can hold any number of themes. `org.json.default_theme` names the one `design` uses
unless `--theme` says otherwise. A theme that omits a key inherits it from `default.json`.
`theme.py` refuses any radius above 3px; that rule is the plugin's, not a preference.

## 4. The canvas spec

The single source both the mockup and the JSON compile from. JSON, because the scripts are
stdlib-only and users never hand-write it. Claude writes and edits it during `design`.

```jsonc
{
  "spec_version": 1,
  "name": "Proposals Canvas v1",
  "module": "Proposals",                 // api_name; ids resolved at build time
  "layout": "Standard",                  // layout name; id resolved at build time
  "theme": "camco-bright",               // optional; org default otherwise
  "header": {
    "name_field": "Name",
    "status_field": "Proposal_Status",   // optional; rendered as the pill
    "actions": ["mail_merge", "edit", "morebutton"],   // must be in the module's observed set
    "stats": [ { "field": "Est_Total_Cost", "hero": true }, { "field": "Billing_Method" },
               { "field": "Payment_Terms" }, { "field": "Proposal_Date" },
               { "field": "Acceptance_Date" } ]
  },
  "tabs": [
    { "name": "Overview", "rows": [
        { "cards": [
            { "title": "Proposal Details", "icon": "info", "accent": "indigo", "span": 1,
              "fields": ["Related_Account", "Related_Contact", "Prepared_For", "Email_To",
                         "Company_Name", "DBA", "Proposal_Date", "Acceptance_Date"] },
            { "title": "Billing & Delivery", "icon": "dollar", "accent": "teal", "span": 1,
              "fields": ["Billing_Method", "Billable_Rate", "Payment_Terms",
                         "Billing_Timeline", "Delivery_Timeline"],
              "note": "Pricing detail for each billing method is on the Pricing tab." },
            { "title": "Signature & Invoicing", "icon": "docs", "accent": "emerald", "span": 1,
              "fields": ["zsign_doc_id", "zsign_request_id", "zdoc_signed_datetime",
                         "zbooks_initial_invoice_id", "initial_invoice_sent"] } ] },
        { "cards": [
            { "title": "Project Description", "icon": "notes", "accent": "sky", "span": 2,
              "textarea": "Brief_Project_Description" },
            { "title": "Proposal Controls", "icon": "status", "accent": "violet", "span": 1,
              "fields": ["Send_Client_Intake", "Exclude_NDA", "Exclude_Price_Breakdown",
                         "Share_With_Frank", "Share_With"] } ] },
        { "cards": [
            { "title": "Open Tasks", "icon": "task", "accent": "sky", "span": 1,
              "related_list": "Open Tasks", "count": 5 },
            { "title": "Open Meetings", "icon": "meeting", "accent": "rose", "span": 1,
              "related_list": "Open Meetings", "count": 5 } ] } ] },
    { "name": "Pricing", "rows": [
        { "kpis": [ { "field": "Billing_Method", "accent": "indigo" }, "…" ] },
        "…" ] },
    { "name": "Related Account", "lookup_all_fields": "Related_Account" },
    { "name": "Timeline", "system_list": "timeline" },
    { "name": "Notes", "related_list": "Notes" }
  ]
}
```

Card kinds, one per card: `fields` (label/value table), `textarea` (one text-area field),
`related_list`, `system_list`, `kpi` row, `note` (static text), and `raw` (a hand-built node from
`shapes.py`, the escape hatch for constructs the spec does not express yet). Tab kinds:
`rows` (composite), `related_list`, `system_list`, `lookup_all_fields`.

Icons are named by short key (`info`, `dollar`, `task`, …) mapped to catalog names in
`design-rules.md`; a raw `icon-Icon_*` name is allowed and checked against the catalog.

`spec.py` validates a spec against the live profile before anything compiles: every field must be
on the named layout, every related list must exist by display label, every action id must appear
in the module's existing canvas or the shipped palette, every icon must be in the catalog. It
reports all problems at once, with the nearest matching api_name for each miss.

## 5. The compiler

`layout.py` turns rows and spans into absolute coordinates using the theme metrics:

- A row is `gap`-padded; a card with `span: n` out of the row's total spans gets its share of
  `canvas_width - gap * (cards + 1)`. Three spans of 1 give 337px; 2 + 1 gives 696 + 337; 1 + 1
  gives 517 + 517. The same numbers as the Proposals mockup.
- Card height comes from content: title block plus `row_height` per field plus padding; a
  textarea card takes an explicit `height` or a default; related-list cards take `height`
  or a default by `count`. Cards in a row share the row's tallest height.
- Rows stack with `gap`. The tab body height is the tallest tab; the strip is body + 48; the root
  is banner + strip.

`compile_html.py` and `compile_json.py` consume the same placed tree. The HTML uses the theme
tokens and the same coordinates, with the conventions settled on Proposals: Segoe UI as the
stand-in for Zoho Puvi, booleans as checkboxes, related lists as a "rendered by Zoho" box, a
lookup tab as the linked record's sections, example values marked as examples, a tab switcher
and a legend of what was left off and why. The JSON uses `shapes.py` only; `compile_json.py`
never writes a node literal itself.

Field datatypes come from the CRM `data_type` → canvas `datatype` table already in
`canvas-schema.md` §10. Related-list cards use the Table Layout form (Zoho renders columns).
`lookup_all_fields` mints `"00" + uuid4()[2:]` and writes the matching `related_to`
entry.

## 6. Commands

Each command is a `commands/*.md` prompt that calls `python -m zcrm_canvas …` for anything
mechanical and reserves Claude for judgment. Stop points are explicit.

### `/canvas profile <Module> [--org]`

Runs `profile`: modules, layouts (fields by section, api_name, data_type), related lists, custom
buttons, blueprints, and the action ids and related-list ids in every existing DetailView canvas
on the module. Prints a structured summary and nothing is cached to disk. Claude then states
what the module offers and what a design could leave off, and stops.

### `/canvas design <Module> <view_id> [--theme] [--from spec]`

1. Profiles (or reuses the profile from this turn).
2. Captures the target canvas to `~/.zcrm-canvas/orgs/<org>/captures/` as the first rollback
   and reads its action ids: that is the observed action set for the header.
3. Drafts `output/<org>/<Module>/<slug>.spec.json` from the profile, the theme and the design
   rules (header shape, one card per layout section as the starting point, related lists in
   sensible tabs, everything not used listed under "left off").
4. Compiles the mockup, publishes it as a private Artifact, gives the link, and **stops**.
5. Each later round: apply the user's changes to the spec, recompile, republish to the same URL,
   stop. The command never proceeds to build on its own.

### `/canvas build <spec>`

Validates the spec against the live profile, compiles JSON, runs `validate.py` and `audit.py`,
writes `<slug>.json`, `<slug>.meta.json` (view id, module and layout ids, theme, spec path,
generated time), and refreshes `<slug>.preview.html`. Zero errors and zero unobserved values
or it does not write the JSON. No network write.

### `/canvas deploy <spec|json> [--yes]`

Requires the user's go-ahead in the same conversation turn; without `--yes` the command asks
and stops. Then: GET the live canvas and save the timestamped rollback, PUT, GET again, compare
node count and `uniqueid` retention, print the editor URL and the restore command, and say in
plain words that it is not verified until opened in the editor.

### `/canvas restore <rollback>`

The existing restore path: strip server-owned keys, PUT, re-GET.

### `/canvas theme [create|set-default|show] …`

`create` walks the user through a short set of questions (palette from a brand colour or two,
gradient or flat banner, corner radius up to 3px, fonts sizes) and writes
`orgs/<org>/themes/<name>.json`. `set-default` writes `org.json.default_theme`. `show` prints the
resolved tokens with inheritance from `default.json`.

### `/canvas learn <file.har> [--label]`

The method rule as a tool. See §8.

## 7. Safety rules, and where each one lives

| Rule | Enforced by |
|---|---|
| Rollback GET before every PUT | `api.put_view` refuses without a rollback path it wrote itself in this process |
| Explicit go-ahead before a deploy | `/canvas deploy` prompt; `--yes` only when the user said so |
| No node literals outside `shapes.py` | `compile_json.py` code review rule; `audit.py` catches strays |
| Enumerated values from catalogs only | `validate.py` (icons, action ids), `spec.py` |
| Radius 3px max | `theme.py` |
| Credentials never in a project or output | `auth.py` reads only `~/.zcrm-canvas/orgs/<org>/credentials.env` or env vars |
| SUCCESS is not verification | `deploy` output text; SKILL.md |
| Profiles never cached | `profile` writes nothing; `spec.py` re-profiles on every build |
| Module-scoped field ids | `spec.py` resolves related-module fields against that module (v1 only places Zoho-rendered related lists, so this is a guard, not a feature) |

## 7a. The mistakes log

`references/mistakes.md` ships inside the plugin. It is seeded from this project's
`mistakes.md` with every entry that still applies to the plugin (the catalog rule, capture the
tool before inferring from its output, `SUCCESS` is not verification, one sample is not a rule,
module-scoped field ids, duplicate related lists are legal, the `uniqueid` reversals) in the
same three-part format: what went wrong, why, rule going forward.

`SKILL.md` requires two things of every session:

1. Read `references/mistakes.md` before doing anything else.
2. When a deploy breaks the editor, a test that should have caught something did not, or the
   user corrects the same point twice, write an entry before moving on. Entries are short and
   only for things that would cost time if repeated.

Where the entry is written depends on who is running it. An installed plugin is a cached copy
and edits to it are lost on update, so new entries go to `mistakes.md` in the user's working
project, which `SKILL.md` also reads if present. Entries made while developing the plugin in
its own repo go straight into `references/mistakes.md` and ship with the next version. Other
users' entries reach the shipped file by pull request.

## 8. Learning from a recorded session

`learn.py` takes a HAR of the Canvas editor, one construct added per save (the procedure in
`learning.md`, which is this project's README for `reference/ui-capture/`):

1. Extract every `PUT …/settings/canvas/views/<id>` body and response, in order, plus any
   preset, palette or catalog assets the editor fetched (new icon CSS, a palette for a module we
   lack).
2. Diff consecutive saves and print, per save, the added subtree with its full JSON.
3. Extend `assets/vocabulary.json` with any new class tokens, style keys, themes, types,
   datatypes and ui keys, marked with the session label and date; extend the icon catalog and
   palettes the same way.
4. Report what is new against `canvas-constructs.md` and hand Claude the diffs, so the
   documentation and, if warranted, a new `shapes.py` builder are written from evidence.
5. Write the extracted saves to `~/.zcrm-canvas/learned/<label>/` so nothing from the HAR (which
   carries session cookies) is ever copied into the plugin repo or a project.

`learn` never edits `shapes.py` on its own; it produces the evidence and the report. Adding a
builder is a code change with a test.

## 9. What moves from this project

| This project | Plugin |
|---|---|
| `src/zoho_auth.py` | `scripts/zcrm_canvas/auth.py`, org-aware |
| `src/zoho_canvas.py` + `Profile` in `build_proposals_v1.py` | `api.py` |
| `src/canvas_shapes.py` | `shapes.py`, tokens read from a theme object |
| `src/validate.py` | `validate.py`, unchanged rules |
| vocabulary audit in `build_proposals_v1.py` | `audit.py` + `assets/vocabulary.json` |
| `build_proposals_v1.py` panes | `tests/fixtures/proposals.spec.json` (golden test input) |
| Contacts v3.1 design, redone through the plugin | `examples/contacts.spec.json` (standard fields only) |
| `docs/canvas-schema.md`, `docs/canvas-constructs.md` | `references/` |
| CLAUDE.md working rules, design workflow, header conventions, corner rule | `SKILL.md`, `references/design-rules.md`, `themes/default.json` |
| `reference/ui-capture/README.md` procedure | `references/learning.md` |
| `reference/zoho-assets/` | `assets/` |
| `restore.py` | `cli.py restore` |

This project keeps the captures, the HARs and the Camco builders as the evidence base and the
history. New Camco canvases are built with the plugin.

## 10. Testing

- **Golden compile.** `tests/fixtures/proposals.spec.json` compiles to JSON that matches the
  deployed `proposals-v1.json` in the evidence base node for node (ignoring the minted
  connection id and zcode counters). This proves the spec expresses everything the
  hand-written builder did. It is a test, not an example: Proposals is a Camco custom module.
- **First live deploy is Contacts.** Contacts is a standard module every org has. The plugin's
  first end-to-end run is a fresh Contacts design through the real `design` loop on Camco's
  Contacts canvas `2582206000076641025` (which has a known-good rollback and predates the
  corner rule anyway). The approved spec, trimmed to standard fields and related lists, becomes
  `examples/contacts.spec.json`. The spec validator must report every Camco-only field it drops.
- **Validator calibration.** `validate.py` and `audit.py` pass all 33 Zoho-authored files with
  zero findings, run from this repo against the plugin's copies before each release.
- **Layout arithmetic.** Unit tests on `layout.py`: `end_x == start_x + width` everywhere, rows
  never overlap, spans fill the width to the pixel for 1+1, 1+1+1, 2+1, 4×1.
- **Spec validation.** A spec naming a missing field, an unknown related list, an unobserved
  action id, a bad icon and a 14px radius produces five findings and no output.
- **No-op deploy.** The existing round trip (GET, strip, PUT, GET, compare) against a scratch
  canvas the user names, as the smoke test for a new org.

## 11. Open points, none blocking

- A second header layout (flat, no gradient) will be wanted by someone; `header.style` is in the
  theme so it can be added without touching specs.
- Custom CSS stays unobserved until someone records one save with it; `learn` is how that
  arrives.
- The plugin has one palette file (Contacts). Other modules' palettes are browser-only; the
  observed action set from the module's own canvas is the working rule until a `learn` session
  captures another palette.
