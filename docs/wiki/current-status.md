# Current status

> source: `README.md`, `hugo.toml`, `content/posts/en/`, `content/posts/ru/`, `content/posts/uk/`, `run.cmd`

- Local content contains eight posts in each of English, Russian and Ukrainian.
  Five date from September 2025; three (Venus Project, future network map,
  governance of large groups) from 2026-08-30 to 2026-09-01.
  (`content/posts/en/`; `content/posts/ru/`; `content/posts/uk/`)
- The article set covers Sytrism, Jacques Fresco, direct democracy, political
  systems, a proposed institutional “linchpin”, the Venus Project, a future
  design map, and the governance-of-large-groups digest. See
  [Articles](features/articles.md).
- Hugo configuration defines English, Russian and Ukrainian. The governance
  article is live in all three with TOC and six illustrations; the last
  content commit is `2b16cea`, deployed by GitHub Actions to the configured
  GitHub Pages URL. (`hugo.toml`; `git log`)
- Governance research: 20 Russian drafts, 363 bibliography records and 163
  evidence rows are in `docs/wiki/research/`. Kaneo tasks #77–#82 (empirical
  pilots) stay open. (`docs/wiki/research/governance-of-groups.md`;
  `docs/wiki/research/evidence-matrix.md`)
- Code blocks: `static/css/custom.css` overrides the theme's white-on-light
  fenced-code colours (commit `805f569`). (`static/css/custom.css`)
- Cerebro integration files and local wiki are now prepared and committed in
  `ba5a3f2`. Central catalog registration is ready for validation.
- Kaneo is bound to dedicated `Mind Journal - Philosophy & Articles` project
  (`ji0wvag33gbpawnxd9nkan0s`) in content workspace. Project creation and GET
  read-back passed on 2026-08-30. Repo-local lifecycle is in `.ai/kaneo/`.
