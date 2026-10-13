# Storage contract

GitHub stores generator code, tests, non-secret configuration and technical documentation only.
Google Drive stores manuscripts, source/evidence packets, generated illustrations, fonts with licenses,
PDF/PNG/JPG/PRN editions, QA reports, private canon, ledger revisions and puzzle solutions.
Do not commit edition-specific text, images or reports, including text embedded in authoring scripts.
Do not upload private files as public Actions artifacts or publish them on Pages.

Extract Drive materials outside the checkout. Set `PORANNA_PRASA_ASSETS` to the extracted
`assets` directory and optionally `PORANNA_PRASA_PILOTS` to `editions` for integration tests.
`--input`, `--private-state` and `--output` must point outside the checkout.
Drive folders remain owner-private. Credentials and folder IDs are runtime configuration,
never hard-coded in public source. Sync changed canon and revisions back to the same private
Drive location after an approved run; the offline generator does not perform Drive uploads.

Production `main` and automatic printing remain unchanged pending separate acceptance.
