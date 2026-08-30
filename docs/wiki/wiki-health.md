# Wiki health

> source: `docs/wiki/index.md`, repository inventory on 2026-08-30

## Current findings

- Core wiki pages are linked from `index.md`.
- Core pages have source declarations and source-backed claims.
- Article and concept pages are linked; no known orphan wiki page remains.
- Spelling, language-output, and bibliography questions are recorded in
  [Open questions](open-questions.md). Kaneo provisioning is complete and
  read-back-confirmed.
- Central catalog validation is ready now that committed repository card
  `ba5a3f2` and local root mapping exist.

## Recommended next check

Run central catalog validation after committing integration files, then use
`.ai/kaneo/manage.ps1 health` before material article work.
