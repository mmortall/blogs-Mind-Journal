# Mind Journal Wiki

> source: `README.md`, `hugo.toml`, `docs/llm-wiki.md`, `content/posts/en/`, `content/posts/ru/`

Mind Journal is a separate Hugo publication for political philosophy and
related articles. Its central theme is **Sytrism**: a proposed governance model
that combines human institutions, artificial intelligence, and cyber-networks
or direct-democratic collective intelligence.

## Read this when

- Understanding project purpose: [Project overview](project-overview.md)
- Changing Hugo structure or publication behavior: [Architecture](architecture.md)
- Checking current content and integration state: [Current status](current-status.md)
- Finding raw source coverage: [Source map](source-map.md)
- Reviewing the central concept: [Sytrism](concepts/sytrism.md)
- Finding article coverage and translations: [Articles](features/articles.md)
- Resolving wording or source gaps: [Open questions](open-questions.md)
- Checking agent instructions: [Agents map](agents-map.md)
- Maintaining wiki quality: [Wiki health](wiki-health.md)
- Reviewing prior maintenance: [Log](log.md)

## Boundaries

- `content/` is raw editorial source and remains authoritative for article text.
- `docs/wiki/` is an LLM-maintained synthesis with source paths on important
  claims.
- The central Cerebro catalog owns cross-repository routing; Mind Journal owns
  its local content and Hugo configuration.
- Mind Journal is related to `staraban-blogs` in the central catalog but is a
  separate editorial project.
