# Integrated Kaneo Runtime Rules

For material work, run `manage.ps1 health`, then
`manage.ps1 start --outcome "..." --area "..." --apply` before edits. Finish
only after canonical output and validation exist:
`manage.ps1 finish --task-id "<leaf_id>" --changed "<path>" --validation "<check> — <result>" --apply`.

Reuse named work and stable managed markers. Do not invent IDs, create sibling
relations, or mirror Kaneo hierarchy into research knowledge. Kaneo owns task
state; this repository owns articles, Hugo files, and maintained Wiki pages.

## Mandatory Kaneo channel and task contract

For material implementation, research, or planning work in this repository,
use the repository-local REST wrapper. This is the only normal Kaneo task
lifecycle.

- Run `.\.ai\kaneo\manage.ps1 health` before remote work.
- Start with `.\.ai\kaneo\manage.ps1 start --outcome "<one independently verifiable result>" --apply`.
- Save returned `leaf_id` and finish that same leaf with `manage.ps1 finish`.
- `--outcome` is both task title and `goal`; make it observable and specific.
  Managed start also persists `acceptanceCriteria`; never create a task with
  missing goal or acceptance criteria.
- Reuse existing managed hierarchy and read back every remote write.
- Do not call Kaneo MCP, the `/kaneo/api/mcp` URL, or another project's
  wrapper for task lifecycle. MCP is a separate host-registration path and is
  used only when user explicitly requests MCP itself.
- If wrapper or REST call fails, diagnose local wrapper, credentials, or REST
  payload separately. Do not switch to MCP to hide the failure.
- Read-only or no-change work creates no Kaneo task.
