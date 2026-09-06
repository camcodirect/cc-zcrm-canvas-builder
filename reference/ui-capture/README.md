# UI capture: what the Zoho Canvas editor actually sends

Two recorded browser sessions in the Contacts canvas editor (`2582206000076641025`), one
construct added per save. `save-NN.json` is the PUT body, `resp-NN.json` the response. The raw
HARs are gitignored (they carry a live session cookie); these extracted bodies are clean.

Diff consecutive saves to see exactly what one editor action adds. `docs/canvas-constructs.md`
is derived from these files.

## round-1 (2026-09-06 21:43 to 21:47)

| save | what was done in the editor | nodes |
|---|---|---|
| 00 | Save with no changes (baseline of the gallery template) | 429 |
| 01 | Add a card to Overview: `zc-lsection` + 2 fields + Static Text title | 431 |
| 02 | Add a new tab strip ("Unnamed Tab") | 433 |
| 03 | Add a Static Icon and a Canvas Button into the new tab | 434 |
| 04 | Add a field; the icon was removed | 442 |
| 05 | Add a related list (Resources) as a card with 4 column fields | 458 |
| 06 | Add AI Meeting Extractions twice: as a card and as a Canvas Data Table | 460 |
| 07 | Add two fields to the banner | 466 |
| 08 | Add six system actions (delete, sendDM, inviteClientPortal, data_enrichment, askzia_contextual, clone) | 467 |

## round-2 (2026-09-06 21:52 to 21:58)

| save | what was done in the editor | nodes |
|---|---|---|
| 00 | Baseline (continues from round 1; data_enrichment removed) | 465 |
| 01 | Rename tab to "cc tab 1"; orientation → vertical left (`zcanvas-vertical-left`, depth 6) | 464 |
| 02 | Save, no change | 464 |
| 03 | Orientation → vertical right | 464 |
| 04 | Orientation → horizontal top; style the tab container (`layoutstyle.editor`) | 464 |
| 05 | Tab navigation → both sides (`zcanvas-tab-splitnav`) | 464 |
| 06 | Sub tab action → single expand (`zcanvas-single-subtab`) | 464 |
| 07 | Tab navigation → same side | 464 |
| 08 | Hide toggle (`style.default._hide_`) | 464 |
| 09 | Show toggle (`style.default._show_`) | 464 |
| 10 | Field dropped into the tab | 465 |
| 11 | Empty Flex Layout | 466 |
| 12 | Empty Grid Layout | 468 |
| 13 | Flex Layout holding a related-list card and a Table Layout (flex items) | 469 |
| 14 | Canvas Image (uploaded via canvas_files) | 469 |
| 15 | Line, plus a Query-backed related list ("testq query", data_hub_associations) | 476 |

## round-3 (2026-09-06 23:31 to 23:32)

Baseline is "canvas template 3" at 499 nodes (a reverted copy of the round-2 end state, not the
v3 deploy).

| save | what was done in the editor | nodes |
|---|---|---|
| 00 | Baseline save | 499 |
| 01 | Three lookup All-Fields tabs: Broker Company Name, Related Buyer Contact, Account Name (`zc-tab-lookup-all-fields`, `details.lookup_associations`, root `related_to.lookup_associations`) | 504 |
| 02 | Related-list tab "Drive Files related to Accounts" (a `module: null` list) | 509 |
| 03 | System component "Interactions" as a related list (`id: "journeys"`), plus a nested "Sub Tab" tab group (`zc-tabgroup`) | 515 |

## Findings that corrected earlier assumptions

- The same related list may appear more than once (round-1 save 06).
- Static Text sits directly inside a container; no `static_content` wrapper needed.
- Canvas has Flex and Grid layout engines, not only absolute positioning.
- `uniqueid` is absent from about half the nodes in the editor's own output.
- Icon names must come from the 231-name catalog in `reference/zoho-assets/icon-catalog.txt`.
