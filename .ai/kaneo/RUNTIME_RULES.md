# Integrated Kaneo Runtime Rules

For material work, run `manage.ps1 health`, then
`manage.ps1 start --outcome "..." --area "..." --apply` before edits. Finish
only after canonical output and validation exist:
`manage.ps1 finish --task-id "<leaf_id>" --changed "<path>" --validation "<check> — <result>" --apply`.

Reuse named work and stable managed markers. Do not invent IDs, create sibling
relations, or mirror Kaneo hierarchy into research knowledge. Kaneo owns task
state; this repository owns articles, Hugo files, and maintained Wiki pages.
