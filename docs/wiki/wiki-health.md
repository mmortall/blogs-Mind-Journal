# Wiki health

> source: `docs/wiki/index.md`, repository inventory and validation on 2026-08-31

## Current findings

- Core Wiki pages and all 20 governance article drafts are linked from
  `index.md`, `source-map.md`, or the relevant research map; no known orphan
  research page remains.
- Research inventory contains 43 Markdown files under `docs/wiki`, 20
  plain-language article drafts, 345 sequential bibliography records, and the
  current external URL counts recorded below. New succession, everyday-outcome,
  and closed-group sources cover leader change, conflict, persistence, service
  delivery, extraction, bargaining windows, commune durability, post-exit
  recovery, and mass control through services, information, co-optation and
  repression, participation, accountability and legitimacy; access and transfer
  limits remain explicit.
- All 20 article drafts contain a `Заметки по доказательствам` section and an
  explicit `Контрпример` section. The article series, evidence matrix,
  publication audit, and publication kit all cover the same 20-text set.
- Structural validation passed: 0 H1 issues, 0 unmatched fenced-code blocks, and
  0 missing local Markdown links. `git diff --check` passed. Hugo production
  build passed with EN 26, RU 25, UK 25.
- Hugo still emits the pre-existing `warning-goldmark-raw-html` warning for `/`.
  This is separate from Wiki structure and has not been silently suppressed.
- External URL inventory currently contains 373 unique Markdown link targets;
  unique raw URI-like-target inventory contains 374 strings because one
  public-site address also appears as inline code. A bounded parallel `curl -I`
  snapshot of the earlier 239-route inventory on 2026-08-31 (24 workers,
  8-second timeout) returned 78 `200`, 9 `203`,
  3 `301`, 68 `302`, 6 `303`, 32 `403`, and 2 network errors; no `404` was
  observed. Redirects are normal DOI or publisher resolution paths. `403`
  indicates publisher, paywall, or bot-protection access response and does not
  prove source invalidity. The two network errors were the OHCHR PDF and a
  Cambridge book URL; the OHCHR document loaded through an alternate PDF
  reader. A previous PowerShell `HttpClient` snapshot gave a different access
  profile, so client-specific status is not treated as source validity. The
  current algorithmic-management re-audit added eight unique routes: OECD,
  PMC, Frontiers and arXiv returned `200`; MDPI, SAGE and Wiley returned
  `403` to local `curl` but opened through browser or metadata routes; the DOI
  route for the attrition study returned `200` while publisher full text remains
  restricted. The correlated-error re-audit added eleven unique routes; arXiv,
  PMLR, ACL Anthology, GitHub, PMC, Nature, JMLR and AAAI all returned `200`.
  The culture-and-religion pass added six unique routes covering cultural-group
  selection, ritual synchrony, Tiwanaku archaeology, denominational authority,
  dyadic social control, and religious coercive-control safeguards; access and
  evidence limits are recorded per source in the research dossiers.
  The management-durability pass added one unique route for a preregistered
  participatory-meeting field experiment; its local context and post-intervention
  transfer limits are recorded in the management dossier and firm article. The
  comparative-state-formation pass added six routes covering early accounting
  technologies, non-written bookkeeping, fiscal legibility in colonial Mexico,
  divergent European fiscal equilibria, executive constraints, and the political
  settlement problem in early Pakistan; origin versus consolidation limits are
  recorded in the state-formation article and historical dossier.
- The state-capacity-and-everyday-outcomes pass added six comparative sources on
  public goods, local service delivery, intermediary incentives, municipal
  finance and long-run local cooperation in China, Russia, India, Nepal, Portugal
  and Vietnam. `EverydayOutcomeCase` now separates service access, quality,
  distribution, extraction burden, local knowledge, voice/appeal and persistence.
- The closed-group pass added six unique DOI routes covering commune survival,
  charismatic leadership and branch structures, exit and identity transition,
  post-exit experience, social-media support and multi-dimensional recovery
  problems. Their sample and causal limits are recorded in the NRM dossiers.
- The state-formation-case-coding pass added a standalone matched-case protocol
  with explicit `D/I/U/N` evidence statuses and a coverage ledger. It records
  that public task, resource and information-carrier fields are better covered
  than legitimacy, representation, succession, exit and everyday peripheral
  outcomes.
- The succession-and-persistence pass added `SuccessionPersistenceCase` to the
  state-formation, historical-case, and leadership materials. It separates
  succession rule, uncertainty, elite bargaining, bureaucratic memory, capacity
  after change, and voice after change; the evidence set covers European
  monarchies, Eurasian dynasties, and medieval cities with explicit limits on
  historical selection and working-paper transfer.
- The closed-group and new-religious-movement pass added `NRMExitCase` to the
  culture dossier, NRM article, evidence matrix and practical backlog. It
  separates group durability, leader centralization, resource and relationship
  dependence, exit mode, actual loss, external support and identity recovery.
  The follow-up pass adds `NRMExitTrajectory` and four sources on a small
  three-year individual panel, post-founder succession, changing spiritual
  communities and a general-religion cohort comparator. The direct NRM panel is
  useful but small; material loss, retaliation, appeal and long-term recovery
  remain mostly unmeasured.
- The cross-domain comparison pass added three sources on governance structures
  in ten international advocacy NGOs, matched SOE/POE firms in 40 countries, and
  movement–corporate co-optation. `CrossDomainCase` now separates domain,
  public task, information carrier, resource dependence, intermediary, authority,
  implementation, voice, appeal, exit, persistence, capture and scope condition.
- The mass-governance pass added four sources on state capacity, digital
  surveillance, informational autocracy, and post-conflict control modes. It
  added `MassControlCase`, separating capacity from compliance and measuring
  services, information quality, voice, appeal, exit and repression together;
  local, regime-specific and mixed-evidence limits remain explicit.
- The participation-and-accountability pass added eight sources on democratic
  rule choice, elected leadership, informal accountability, electoral and voice
  accountability, community-driven development and long-term durability. It
  added `ParticipationCooperationCase`, separating rule origin, participant scope,
  voice, sanction, mobilization, elite capture, cooperation, service outcome and
  persistence; task-specific and context-specific limits remain explicit.
- The legitimacy-compliance pass added seven sources on fair enforcement,
  authority trust, sanction severity, procedural justice, organizational justice,
  taxation legitimacy and noisy enforcement. It added
  `LegitimacyComplianceCase`, separating intrinsic from extrinsic compliance and
  linking fairness to voice, correction, appeal and exit; perception-based,
  laboratory and context-specific limits remain explicit.
- The metric-governance pass added six sources on performance-management
  dysfunctions, multitask incentives, hospital targets, team incentives and the
  politics of measurement. It added `MetricGovernanceCase`, separating true goal,
  proxy, task bundle, gaming, information quality, quality, equity, safety,
  correction and persistence; sector-specific and context-specific limits remain
  explicit.
- The institutional-learning pass added fifteen sources on policy feedback,
  policy experimentation, adaptive governance, organizational routines and
  memory, knowledge transfer, intentional forgetting, succession and
  routinization of charismatic authority. It added `InstitutionalLearningCase`,
  separating signal independence, trial, comparator, decision gate, memory,
  transfer, leader turnover, voice, appeal, rollback, forgetting, capture and
  short/long outcomes; selection, temporary over-effort, interpretation error,
  inertia and attention trade-offs remain explicit.
- The matched-longitudinal pass added ten sources and a `MatchedInstitutionalTrajectory`
  protocol. It compares baseline, comparator, intervention, implementation lag,
  voice, appeal, exit, leader turnover, process/quality/distribution/resource
  outcomes, persistence, rollback and alternative explanations across welfare
  payments, firms, historical commons, community forestry, irrigation and
  enforcement; causal strength remains mixed by design.
- The institutional-decay pass added eleven sources on corruption audits, elite
  capture, delegated public services, organizational decline, retrenchment,
  commons degradation, civil-service reform and reform reversal. It added
  `InstitutionalDecayCase`, separating decay, capture, failure and recovery;
  baseline, stressor, information loss, accountability, leadership change,
  independent process/quality/distribution/resource outcomes, voice, appeal,
  exit, rollback and persistence are now explicit. Evidence shows that audits,
  autonomy and protected delegation can improve delivery, while elite expertise,
  bureaucratic memory, centralization and short-run downsizing can preserve or
  deepen capture and decline. Single-context, observational and qualitative limits
  remain explicit.
- The safe-reform pass added three sources on employee voice and silence, policy
  repeal, and policy reversal, and added `SafeReformCase` to the field guide and
  voice/appeal/exit article. The protocol separates protected signal, independent
  review, stop authority, correction, compensation, exit, rollback, postmortem and
  persistence after personnel change. Robodebt remains a documented negative case;
  the evidence does not yet show that this protocol lowers correction latency in a
  live organization without creating veto overload or extra exit cost.
- The follow-up matched-case pass added four sources on heterogeneous well-being
  after exit, outside or family support, comparative disengagement across three
  NRMs, and young people raised inside closed groups. `NRMExitCase` now records
  age at entry, external ties and available support; retrospective, qualitative
  and non-causal limits remain explicit.
- All governance drafts remain `draft` research material. They are not yet
  transferred to `content/posts/`; translation, final fact-check, and publication
  decisions remain open. All 20 articles have completed reader-facing editing.
- Kaneo project is healthy and tracks the research queue. High-priority empirical
  tasks #77–#82 remain open because real pilot data and comparative audit data do
  not yet exist. Managed research leaf #262 records the institutional-learning
  pass under the institutional-learning-and-change sub-epic; #264 records the
  matched-longitudinal pass; #260 records the completed metric-governance pass.

## Recommended next checks

1. Continue re-auditing access-restricted sources through browser, metadata, or
   alternative full-text routes and replace or annotate only confirmed dead
   sources.
2. Run final fact-check and publication triage across all 20 reader-facing drafts.
3. Keep empirical tasks #77–#82 open until low-stakes reversible pilot data,
   comparison arms, and independent outcomes are collected.
4. Run `.ai/kaneo/manage.ps1 health` before each material research or publication
   change and finish each managed leaf with exact paths and validation evidence.
