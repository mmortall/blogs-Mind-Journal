# Kaneo and Knowledge Binding

| Field | Value |
|---|---|
| State | `configured` |
| Repository | `Mind-Journal-HUGO` |
| Knowledge card | `.ai/knowledge.yaml` |
| Space ID | `repo:content:mind-journal` |
| API endpoint | `https://admin.polyquantlabs.xyz/kaneo/api` |
| MCP endpoint | Separate host-only channel; repository workflow uses local REST wrapper |
| Workspace | `content creation and blogging` |
| Workspace ID | `gnETouELw7tAd34p5WREq79HDQg07xk3` |
| Project name | `Mind Journal - Philosophy & Articles` |
| Project ID | `ji0wvag33gbpawnxd9nkan0s` |
| Adoption mode | `Managed` |

Kaneo owns execution state. Repository content, Hugo configuration, and the
LLM Wiki remain canonical. Authentication uses `KANEO_API_KEY` plus Cloudflare
Access service credentials; secret values are never stored here.

The project was created and read back from configured content workspace on
2026-08-30. Use central workflow instructions in
`docs/wiki/systems/kaneo-workflow.md`.

## Portable REST runtime

Use `https://admin.polyquantlabs.xyz/kaneo/api` on every machine.
Do not discover localhost, Docker, MCP, or another server.
`manage.ps1` uses bundled standard-library client in `.ai/kaneo/runtime`.
Central checkout is not required for Kaneo. Python 3.11+ is required;
set `KANEO_PYTHON` when automatic interpreter selection is unsuitable.
Set `KANEO_API_KEY`, `CF_ACCESS_CLIENT_ID`, and `CF_ACCESS_CLIENT_SECRET`
in machine/user/process environment. Missing credentials are authentication
configuration failure, not absence of Kaneo. Never commit credential values.
Knowledge routing remains separate and uses `KNOWLEDGE_ROOT_PLATFORM`.
