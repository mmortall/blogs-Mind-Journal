# Kaneo and Knowledge Binding

| Field | Value |
|---|---|
| State | `configured` |
| Repository | `Mind-Journal-HUGO` |
| Knowledge card | `.ai/knowledge.yaml` |
| Space ID | `repo:content:mind-journal` |
| API endpoint | `https://admin.polyquantlabs.xyz/kaneo/api` |
| MCP endpoint | `https://admin.polyquantlabs.xyz/kaneo/api/mcp` |
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
