# LLM Wiki

This repository uses `docs/wiki/` as its maintained, agent-facing knowledge
layer. Markdown posts, Hugo configuration, templates, and static assets remain
raw sources and are not rewritten by wiki maintenance.

- **Ingest:** read one source, update relevant wiki pages and cross-references,
  update `source-map.md` and `index.md`, then append to `log.md`.
- **Query:** start at `docs/wiki/index.md`, read relevant pages, and cite raw
  source paths.
- **Lint:** check citations, links, stale claims, conflicts, and orphan pages;
  refresh `wiki-health.md` and append to `log.md`.
- **Status:** report page count, recent log entries, open questions, health
  findings, and canonical memory file.
