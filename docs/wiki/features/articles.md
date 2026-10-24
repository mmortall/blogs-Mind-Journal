# Articles

> source: `content/posts/en/`, `content/posts/ru/`, `content/posts/uk/`, `hugo.toml`

The repository currently contains eight posts in each of three languages
(English, Russian, Ukrainian). Translation sets are linked with a shared
`translationKey` in front matter. (`content/posts/en/`; `content/posts/ru/`;
`content/posts/uk/`)

| Theme | `translationKey` | Date | English source |
|---|---|---|---|
| Sytrism as governance | `sytrizm-new-form-of-government` | 2025-09 | `content/posts/en/Sytrism as a new form of government.en.md` |
| Sytrism and Fresco | `sytrizm-fresco-compare` | 2025-09 | `content/posts/en/Sytrizm and the ideas of Jacques Fresco.en.md` |
| Direct democracy | `direct-democracy` | 2025-09 | `content/posts/en/Direct democracy.en.md` |
| Political systems | `about-the-essence-of-any-political-system` | 2025-09 | `content/posts/en/About the essence of any political system.en.md` |
| Institutional linchpin | `about-a-possible-linchpin` | 2025-09 | `content/posts/en/About a possible linchpin for Sightrism.en.md` |
| The Venus Project, critical reappraisal | `venus-project-critical-reappraisal` | 2026-08-30 | `content/posts/en/The Venus Project - a critical reappraisal.en.md` |
| Future design network map | `future-network-map` | 2026-08-30 | `content/posts/en/Future design network map.en.md` |
| How to govern large groups | `governance-of-large-groups` | 2026-09-01 | `content/posts/en/How to Govern Large Groups - Eight Problems Instead of One Button.en.md` |

Russian and Ukrainian files sit in `content/posts/ru/` (`*.ru.md`) and
`content/posts/uk/` (`*.uk.md`) with the same keys.

## Governance research article

`governance-of-large-groups` is the public, plain-language digest of the
governance research in `docs/wiki/research/`. It is published in all three
languages, has `toc: true`, and carries six chapter illustrations stored in
`static/attachments/image/` (`governance-eight-problems.png`,
`governance-feedback-loop.png`, `governance-institutions-comparison.png`,
`governance-culture-ritual.png`, `governance-evidence-limits.png`,
`governance-diagnostic.png`). Structure: six chapters, eight coordination tasks,
real cases, a diagnostic scheme, a summary, and an evidence-limits section.
(`content/posts/*/*governance*`; `static/attachments/image/`; git commits
`424b381`, `71c5d45`, `ca71889`, `2b16cea`)

- Image paths use the project's relative form. Root-relative `/attachments/...`
  links bypass `baseURL` and break on GitHub Pages, so do not switch to them.
  (`hugo.toml`; build check recorded in `log.md`)
- The article is a reader-facing derivative. The 20 Russian drafts in
  `docs/wiki/research/articles/` remain the evidence layer and are not copied
  into `content/posts/` yet. (`docs/wiki/research/articles/publication-audit.md`)

The older posts still have no separate bibliography. The governance article
lists eight sources inline and defers the rest to the research dossiers.
(`content/posts/en/How to Govern Large Groups - Eight Problems Instead of One Button.en.md`)
