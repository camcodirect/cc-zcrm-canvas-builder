# output/

Generated Canvas templates, ready to PUT into Zoho CRM.

## Structure

```text
output/
  <org-slug>-<org-id>/
    <ModuleApiName>/
      <canvas-name>.json          the request body — {"canvas_view":[{…}]}
      <canvas-name>.meta.json     deploy metadata (canvas view id, layout id, target)
      <canvas-name>.preview.html  HTML mockup for visual review (optional)
```

Example:

```text
output/
  camco-647376701/
    Accounts/
      main-account.json
      main-account.meta.json
      main-account.preview.html
```

## Conventions

- **Org folder** is `<slug>-<org-id>`. The ID is what the API cares about and never collides;
  the slug keeps it readable. Camco production is `camco-647376701`.
- **Module folder** uses the exact CRM **API name**, case-sensitive (`Accounts`, `Deals`,
  `Proposals`) — not the display label. This is what `getFields(module)` expects.
- **File name** is a kebab-case slug of the canvas `name` field (`"Main Account"` →
  `main-account.json`).

## The `.meta.json` sidecar

The canvas view ID is a deploy parameter, not part of the payload, so it lives beside it:

```jsonc
{
  "canvas_view_id": "2582206000057761014",   // PUT target — required
  "module": { "id": "2582206000000002177", "api_name": "Accounts" },
  "layout": { "id": "2582206000000091029" },
  "org_id": "647376701",
  "source": "reference/captures/accounts-main-account.payload.json",
  "generated": "2026-09-04"
}
```

Keeping it separate means the `.json` file is exactly the request body and can be sent as-is.

## Rules

- These are **generated artifacts**. Edit the template definition, regenerate — do not hand-patch
  a file here.
- **Never put credentials in this folder.** They belong in `.env`.
- Before deploying over an existing canvas, save the current live version to
  `reference/captures/` first. There is no sandbox — every deploy hits live CRM.
