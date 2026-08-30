See `CLAUDE.md`, `docs/wiki/index.md`, and `llm-wiki/index.md`.

<!-- AI-WORK-CONTEXT:START -->
## Work tracking and knowledge routing

For material implementation, research, or planning, load `.ai/kaneo/PROJECT.md`
and `.ai/kaneo/RUNTIME_RULES.md`. Before changing files, automatically start
one idempotent managed leaf:

```powershell
.\.ai\kaneo\manage.ps1 start --outcome "<one verifiable outcome>" --area "<knowledge area>" --apply
```

Keep returned `leaf_id`; finish it with exact changed paths and validation
evidence. Read-only questions do not create Kaneo work.
<!-- AI-WORK-CONTEXT:END -->

For cross-repository questions, use:

```powershell
.\.ai\knowledge.ps1 resolve-context --task "<question>"
```

For material work, `.ai/kaneo/manage.ps1` will automatically start one idempotent managed leaf
and finish it with validation evidence. Local posts, Hugo configuration, and maintained wiki
pages remain canonical.
