# Architecture

> source: `hugo.toml`, `run.cmd`, `.gitignore`, `README.md`

This is a Hugo static-site repository. `hugo.toml` defines the base URL,
English/Russian languages, author metadata, taxonomies, navigation, analytics,
theme selection, and custom CSS. The active theme is `hugo-clarity`; `diary` is
retained as a commented alternative. (`hugo.toml`)

Content is stored under `content/posts/en/` and `content/posts/ru/`, with
translation keys linking corresponding language versions. Images used by posts
are kept under `static/attachments/image/`. (`content/posts/en/`; `content/posts/ru/`)

`run.cmd` starts a draft-enabled local server with `hugo server -D`. Generated
`public/`, Hugo resource cache, and build logs are ignored. (`run.cmd`;
`.gitignore`)
