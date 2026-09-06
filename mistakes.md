# Mistakes

Running log of meaningful mistakes made on this project. Keep entries short. Only record
things that would actually cost time if repeated.

Format for each entry:

- **What went wrong**
- **Why it happened**
- **Rule going forward**

---

## 2026-09-04 — Assuming the captured cURL file contained the API response

- **What went wrong:** Started reasoning about `uniqueid` values seen in the screen recording as
  if they were part of the saved payload. They are not in
  `save-zcrm-canvas-api-curl-request.txt` at all.
- **Why it happened:** The video shows the DevTools Network panel, which displays both the
  request payload and the server response. The exported file is request-only.
- **Rule going forward:** The captured file is the **request** only. Any key seen in a DevTools
  Network panel must be confirmed to exist in the file (grep it) before treating it as something
  we have to generate.
- **Resolved 2026-09-04:** response captured. `uniqueid` is server-generated, returned as a flat
  list of one UUID per node, and **regenerated on every save** — two saves of the same canvas
  share none. Never send it, never diff on it.

---

## 2026-09-06 — Emitted 14 icon names that do not exist

- **What went wrong:** `build_contacts_v2.py` used 20 `icon-Icon_*` names. Only one had ever been
  observed; the other 19 were invented by analogy (`icon-Icon_Task`, `icon-Icon_Mail`,
  `icon-Icon_Calendar` ...). Checked against the 231-name icon font pulled from the HAR, 14 do not
  exist (the real ones are `icon-Icon_task`, `icon-Icon_Calender`, `icon-Icon_Notes`,
  `icon-Icon_Location`, and so on: irregular case, British-ish spellings). An unknown icon class is
  a strong candidate for the editor's JS failure.
- **Why it happened:** Icon names looked like a predictable scheme, so I produced plausible ones
  instead of looking for the catalog. The catalog was one grep of the editor's CSS away.
- **Rule going forward:** **Every enumerated value (icon name, action id, theme, class token) must
  come from an observed catalog, never from analogy.** `reference/zoho-assets/` now holds the icon
  catalog and the components palette; `validate.py` checks against both.

---

## 2026-09-06 — Diagnosed three canvas breakages by guessing; a UI capture settled it in one pass

- **What went wrong:** Three consecutive deploys broke the Zoho editor. Each time I diffed my
  payload against a working capture, found *a* difference, declared it the cause, fixed only that,
  and shipped 300-600 nodes of still-untested structure. Duplicate related lists, then the All
  Fields tab. Both explanations were wrong or incomplete, and John's canvas was unusable for hours.
- **Why it happened:** I was inferring an undocumented schema from static end-state captures. A
  finished canvas shows what one canvas contains; it cannot show which parts are *required*, which
  are cosmetic, or what the editor does when it builds them. I kept mistaking "a difference" for
  "the cause".
- **What actually settled it:** John recorded a browser session adding one construct at a time
  (HAR, 9 consecutive saves). Diffing consecutive saves gives the exact node shape the editor emits
  per construct — the real spec, in ~15 minutes, with no production breakage.
- **Rule going forward:** **When reverse-engineering an undocumented format, capture the tool
  producing it before inferring from its output.** Ask for a recorded session early. One capture of
  the authoring tool beats any number of static samples, and beats guessing on live data.

---

## 2026-09-06 — Two "structural rules" I asserted were both wrong

Both were invented to explain a breakage, then written into the docs as fact. The UI capture
disproved them.

- **"A related-list ID may appear at most once per canvas."** False. In the captured session Zoho
  itself added the same related list (`2582206000073572031`) twice, saved, and the editor kept
  working. Duplicates are legal. The validator rule enforcing this was removed.
- **"An empty All Fields tab hangs the editor."** Unverified. It was one of several differences and
  I picked it. The capture shows no evidence it matters on its own.
- **Rule going forward:** Do not write a rule into the docs from a single failed deploy. A
  difference between a broken payload and a working one is a *hypothesis*. Label it as one until
  something independent confirms it — ideally a capture of the tool, or a deliberate A/B.

---

## 2026-09-06 — Deployed a canvas that broke the Zoho builder UI (blank white screen)

- **What went wrong:** The generated Contacts v2 canvas was accepted by the API (`code: SUCCESS`,
  429/429 nodes retained) but the Canvas **builder** then loaded as a blank white screen with 9 JS
  errors. The canvas was unopenable and uneditable until restored from a rollback.
- **Root cause:** **The same related-list ID appeared in more than one place.** 13 of the 23 related
  lists were used twice or three times — once inside a custom composite tab (Overview, Engagement,
  Delivery, AI Insights) and again on their own dedicated related-list tab. 37 `relatedlist` nodes
  for 23 distinct IDs. Zoho's editor evidently keys internal state by related-list id, so the
  duplicates collide and the editor crashes on load.
- **Why it happened:** Two separate reasons compounded.
  (a) I treated "API returned SUCCESS" as "the canvas is good". The save endpoint validates far less
  than the editor requires. A canvas can be simultaneously valid to the API and fatally malformed
  to the UI.
  (b) I never opened the result in the builder after deploying. Every check I ran was a re-GET
  through the API, which by definition cannot catch a UI-side crash.
- **Rule going forward:**
  1. **A related-list ID may appear at most ONCE per canvas.** The validator now enforces this.
  2. **`SUCCESS` from the PUT is not verification.** After any structural deploy, open the canvas in
     the Zoho builder before calling it done, and say so explicitly rather than reporting API
     counts as if they were proof.
  3. Prefer adding a construct once and testing it, over shipping 429 nodes of untested new shapes
     in a single deploy. When this broke there were ~8 new node shapes in flight at once, which
     made the cause much harder to isolate than it needed to be.

---

## 2026-09-04 — Got `uniqueid` wrong twice, in opposite directions

- **What went wrong:** Claimed (a) `uniqueid` is never sent in a request and (b) it is regenerated
  on every save. Both false. Captures 2 and 3 send it on 40–43% of nodes, and every sent id comes
  back unchanged (217/217 and 178/178). It is a **stable node identity**.
- **Why it happened:** Capture 1 contained no `uniqueid`, so "never sent" looked obvious — but c1
  was the *first save of a newly built canvas*, the one case where there are no ids yet. Then the
  "regenerated" claim came from comparing c1's response against uniqueids glimpsed in a video
  frame of a **different canvas**. That is not a comparison of two saves of the same thing, and I
  presented it as one.
- **Rule going forward:** Before asserting a key is absent, ask whether the sample is a special
  case that would lack it anyway (first save, empty state, default config). And when claiming
  something changes between two runs, verify both runs are of the *same object* — otherwise the
  diff means nothing. This is the same generalise-from-one-sample failure as the geometry entry
  below; that makes three. Get a second capture before stating any rule about the payload.

---

## 2026-09-04 — Stated geometry "rules" from a single canvas

- **What went wrong:** Wrote `docs/geometry-rules.md` asserting that Canvas is "absolute
  positioning with fixed heights — no flow, no reflow, no content-driven sizing, no flexbox."
  That is a claim about the whole system, derived from one simple Accounts canvas. John flagged it
  as untrue. Doc is parked at `docs/draft/geometry-rules.DRAFT.md`.
- **Why it happened:** Confused "verified against the sample" with "verified". Every arithmetic
  check I ran passed, which felt like rigour, but they only ever confirmed what one canvas did —
  they could not reveal features that canvas doesn't use. Worse, contradicting evidence was
  already in front of me and I under-weighted it: `autoheight` as a node key,
  `layoutstyle.field.width: "100%"`, table columns sized by `percent`, and Responsive Mode in the
  builder UI. All of that points to relative sizing the doc denied.
- **Rule going forward:** **One capture describes one canvas, never the system.** Measurements from
  a single sample are "true of this payload" and must be written that way. Before asserting any
  general rule, ask what a canvas using the opposite approach would look like and whether the
  sample could even show it. Absence of a feature in one example is not evidence the feature does
  not exist — especially when unexplained keys (`autoheight`, `percent`, `over_top`) hint at it.
  Get several differently-configured captures before generalising.

---

## 2026-09-04 — Nearly treated field IDs as globally resolvable

- **What went wrong:** Started resolving all 152 id-bearing nodes against the Accounts field
  metadata. 51 did not resolve, and the first instinct was to call them "unknown".
- **Why it happened:** Fields nested inside a related-list tab look identical to host-module
  fields. Nothing in the node marks which module owns them — only the enclosing
  `tab_relatedlist_id` does.
- **Rule going forward:** ID resolution is **module-scoped per subtree**. Walk down from the
  related-list wrapper and resolve against that related module. A global resolver produces a
  canvas that saves fine and renders wrong.

---
