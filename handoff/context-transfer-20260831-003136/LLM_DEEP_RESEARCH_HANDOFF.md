---
report_type: llm-deep-research-handoff
schema_version: 4.0
created_at: "2026-08-31T00:31:36+03:00"
research_track: "synthesis"
depth: "deep"
status: "COMPLETE"
project: "Mind Journal"
workstream: "The Venus Project political-idea map and glossary"
consultant_repository_access: none_assumed
expected_return_directory: "venus-project-idea-map-deep-research-20260831"
optional_return_zip: "venus-project-idea-map-deep-research-20260831.zip"
expected_return_index: "venus-project-idea-map-deep-research-20260831/00-venus-project-idea-map-research-index.md"
---

# Deep Research Handoff: Verify and Reconstruct the Venus Project Idea Map

## 0. Contract

- Track: `synthesis`
- Depth: `deep` (three evidence cycles; target 5–7 serious technique families)
- Exact decision: determine which actors, projects, concepts, status labels, source links, glossary definitions, and two-axis placements should be retained, corrected, decomposed, added, or removed from Mind Journal’s public map.
- Expected return directory: `venus-project-idea-map-deep-research-20260831`
- Access limits: assume no repository, private chat, Kaneo, local build, private correspondence, or unpublished evidence. Use only embedded observations and independently accessible public sources.

## 1. Executive brief

[OBS] Mind Journal publishes a trilingual interactive map connecting The Venus Project, direct critics, adjacent political thinkers, civic organisations, and governance tools. At repository commit `01e06fa36aee7aa73626da7e548f82661523616c`, the map has 26 nodes, public source links, EN/RU/UK prose, and a 16-term political glossary in each language.

[DEC] The current horizontal axis runs from public/resource planning (`-100`) through hybrid coordination (`0`) to market/private autonomy (`+100`). The vertical axis runs from expert/technocratic control (`-100`) to participatory/direct democracy (`+100`). Coordinates are editorial judgements, not measured facts.

[UNK] The project has not yet completed an independent, source-by-source freshness audit of all current status labels, repositories, organisations, authors, or coordinates as of 2026-08-31. Some nodes deliberately say “historical,” “unmaintained,” or “activity unverified.” Bundled nodes may hide differences between a person, organisation, software project, and idea.

The consultant must reconstruct canonical political and governance terminology first, then audit the map against current primary sources, counterevidence, regional coverage, and consistent placement rules. The result should support an editorial correction decision, not endorse any ideology.

## 2. Objective, Definition of Done, and non-goals

### Objective

Produce a current, source-backed synthesis that lets an editor revise the map without treating personal ideology, institutional design, software capability, and movement rhetoric as interchangeable.

### Definition of Done

1. Every current node is classified `KEEP`, `CORRECT`, `DECOMPOSE`, `REMOVE`, or `VERIFY_FIRST`, with evidence and confidence.
2. Current activity/status claims are checked against sources dated or accessed in 2025–2026 where available; stale archives are clearly marked.
3. Each coordinate is assessed with an explicit rubric and uncertainty, or declared not meaningfully placeable.
4. The two axes are tested against canonical political-spectrum and governance literature; better axis formulations are compared if needed.
5. At least 5–7 canonical technique families are reconstructed before recommending additions.
6. Missing people, organisations, critiques, and implementations are proposed across Ukraine/Eastern Europe, Japan, China/Taiwan, the United States, Canada, Latin America, Europe, Africa, and other materially relevant regions. Do not add regions merely to satisfy a quota.
7. Glossary definitions and EN/RU/UK terminology are checked for conceptual equivalence and misleading translations.
8. Original sources, independent evidence, counterevidence, and material conflicts are separated.
9. The exact Markdown-only return archive defined by `CONSULTANT_RESPONSE_CONTRACT.md` is produced.

### Non-goals

- Do not edit or deploy the site.
- Do not rank people morally or infer a person’s complete politics from one project.
- Do not use private correspondence, leaked data, or unverifiable accounts.
- Do not claim that external literature proves Mind Journal’s coordinates or editorial framing.
- Do not turn Wikipedia into the sole authority; it is used mainly as a reader glossary and discovery aid.

## 3. Why broad research is required

A focused correction is insufficient because several domain layers are open at once:

- the canonical meaning and limits of “left,” “centre,” “right,” “technocracy,” “planning,” and democracy families;
- whether a two-axis model can represent heterogeneous units without category error;
- the current status and real practices of 26 actors/projects/tools;
- direct criticism of The Venus Project versus adjacent governance alternatives;
- global omissions and selection bias;
- disagreement between official claims, independent analysis, archives, and implementation evidence.

These questions require synthesis across political theory, democratic innovation, public administration, civic technology, AI governance, political economy, social ecology, and movement history. The task is not to discover one clever coordinate formula.

## 4. Frozen baseline and claim boundaries

### Frozen baseline

- [OBS] Public project: [Mind Journal](https://mmortall.github.io/blogs-Mind-Journal/).
- [OBS] English map: [Future design network map](https://mmortall.github.io/blogs-Mind-Journal/posts/en/future-design-network-map/).
- [OBS] Repository baseline: public commit [`01e06fa`](https://github.com/mmortall/blogs-Mind-Journal/commit/01e06fa36aee7aa73626da7e548f82661523616c).
- [OBS] Canonical data source at that commit: `data/future_network.yaml`.
- [OBS] Article sources: `content/posts/{en,ru,uk}/...future map...md`.
- [OBS] Rendering logic: `layouts/shortcodes/future-map.html`, `static/js/future-map.js`, `static/css/future-map.css`.
- [OBS] Current automated validator requires three localized map pages, 26 consistent node IDs, valid coordinates within `-100..100`, valid edges, source links, and local article anchors.
- [OBS] The release and draft Hugo builds passed before this handoff. This proves build integrity, not external factual freshness.
- [OBS] A separate critical article about The Venus Project exists in EN/RU/UK as a draft and was not publicly released at this baseline.
- [OBS] The glossary contains 16 terms per language; 46 unique Wikipedia URLs returned HTTP 200 when checked on 2026-08-31.
- [OBS] A 2026-08-31 reachability check covered 53 unique node-source URLs: 50 returned HTTP 200 to `HEAD`; the Fudan profile returned HTTP 200 to `GET` after rejecting `HEAD`; Medium rejected automated access with HTTP 403, which is inconclusive; and the RBE10K host failed DNS resolution. Reachability does not prove current activity or factual accuracy.
- [OBS] After that check, the RBE10K node gained a live, dated 2013 partner profile while retaining its unavailable original wiki as a visibly labelled provenance link. Its status remains historical and current activity remains unverified.

### Claim boundaries

- [FACT] means the consultant supports the statement with an external source.
- [OBS] means supplied project state, not external truth.
- [DEC] means an editorial/design choice.
- [HYP] means a placement, interpretation, or suggested relationship requiring testing.
- Current coordinates, roles, scopes, and summaries are `[DEC]` or `[HYP]` unless independently supported.
- A working URL does not prove current activity, effectiveness, institutional adoption, or ideological fit.
- An official site can establish self-description and product semantics but is not independent evidence of effectiveness.
- External evidence is limited to plausibility and public support (`L0`) until mapped and reviewed locally.

## 5. Self-contained project and decision model

Mind Journal is an independent trilingual editorial project about Sytrism, political systems, direct democracy, civic technology, AI governance, The Venus Project criticism, and future design. The map is a research index, not a ranking or endorsement.

Each node currently contains:

```text
id, kind, role, scope, themes, open_source
localized name, region, status, summary, proposal, caveat
editorial x/y position
public links
optional label offset
```

### Decision path

```text
public original or independent source at access time
  -> editorial extraction of actor, mechanism, status, proposal, and caveat
  -> normalization into one map node (sometimes a bundled node)
  -> role/scope/theme/open-source classification
  -> editorial placement on economic-coordination and political-agency axes
  -> Hugo/JavaScript rendering, filters, and detail panel
  -> reader selects a point
  -> first link returns to Mind Journal context; later links open source material
  -> reader forms comparison or editor revises the map
```

The consultant changes the evidence and decision layer: recommended node boundaries, terminology, source set, status, caveat, coordinates, and uncertainty. The consultant does not change runtime code.

## 6. Prompt-anchor classification

| Anchor | Class | Reason and research obligation |
|---|---|---|
| Political spectrum; left, centre, right | `CANONICAL` | Established but multidimensional and context-dependent. Reconstruct competing canonical models before judging this map. |
| Technocracy, meritocracy, direct democracy, participatory democracy, deliberative democracy, liquid democracy, e-democracy | `CANONICAL` | Established terms with contested boundaries. Define authority, procedure, and failure modes. |
| Economic planning, markets, post-scarcity, social ecology, libertarian municipalism | `CANONICAL` | Established or recognisable families, but not interchangeable with a single left/right scale. |
| “Resource-based economy” as used by The Venus Project | `PROJECT_LOCAL` | Movement-specific programme drawing on broader planning/post-scarcity ideas; do not assume settled academic status. |
| Current two-axis formulation | `PROJECT_LOCAL` | Useful editorial model, not a validated canonical compass. Compare with alternatives. |
| Numeric coordinates for 26 nodes | `SPECULATIVE` | Editorial judgements with no published scoring rubric or inter-rater evidence. |
| Treating a bundled person/project/tool as one point | `SPECULATIVE` | May be defensible for navigation but can create category errors. Test decomposition. |
| “All current information is up to date” | `UNKNOWN` | Explicitly unresolved; verify source-by-source and date every conclusion. |
| A person’s coordinate equals their complete ideology | `CONTRADICTED` | The project explicitly intends coordinates to represent the mechanism shown, not the whole person. Preserve this correction. |

## 7. Canonical domain baseline

The consultant must verify and improve this preliminary baseline:

1. Political positions normally require more than one dimension; left/right meanings vary by country, period, and issue.
2. Economic allocation (planning/markets/commons) and political authority (experts/representatives/direct participation) are analytically separable.
3. Expertise and participation can be composed: experts may advise, model, administer, or hold decision power under different accountability rules.
4. “Technology-enabled” is not itself democratic, technocratic, or effective. Ownership, agenda control, authentication, transparency, appeal, and institutional response determine political meaning.
5. Direct, participatory, deliberative, representative, liquid, and sortition-based democracy solve different problems and can coexist.
6. Open source establishes inspectability under licence and available code; it does not prove maintenance, adoption, security, inclusion, or public authority.
7. A plan can be centralised, decentralised, participatory, indicative, algorithmic, or nested. A market can coexist with extensive public provision and regulation.
8. The strongest conventional editorial solution is likely a typed, evidence-dated catalogue with explicit mechanism-level placement and uncertainty, not a claim that one diagram captures complete ideologies. Test this rather than assuming it.

## 8. Ownership, hierarchy, scale, and composition audit

### Ownership

| Object | Owns | Must not silently inherit |
|---|---|---|
| Person | authored positions and public actions | every property of organisations/tools associated with them |
| Organisation/movement | programme, governance, current status | founder’s entire worldview or every supporter’s views |
| Software/tool | capabilities, licence, maintenance, deployment evidence | legitimacy or authority of an institution using it |
| Idea/mechanism | abstract decision/allocation rule | empirical effectiveness in every scale/context |
| Source/document | claims at publication time | present-day status or independent confirmation |
| Map node | editorial synthesis of a defined unit | universal ideological identity |
| Coordinate | relative placement under this map’s rubric | absolute political truth across countries and periods |

### Hierarchy and scale

One level up: an ideology or governance regime may combine several nodes and mechanisms; a local point cannot define the whole regime.

One level down: a single platform may contain proposal intake, deliberation, agenda setting, voting, execution, audit, and appeal with different authority structures. One coordinate can hide those internal differences.

Scale test: a mechanism suitable for a voluntary local group may fail under municipal, national, or global coercive authority. Record scale assumptions.

Time test: historical proposals, active organisations, maintained repositories, and deployed public institutions need distinct temporal states and access dates.

### Composition

Accepted observations compose into a likely correction:

```text
heterogeneous node types
+ editorial numeric coordinates
+ bundled entities
+ changing project status
+ source links with unequal authority
-> each node needs typed evidence, access date, placement rationale, uncertainty,
   and possible decomposition before coordinates can be presented as comparable
```

This implication is semantically strong. Whether to retain the visual coordinates, replace them with bands, or add uncertainty is an empirical/editorial decision.

## 9. Current evidence and validated observations

### Current node inventory

| ID | Name | Role | Scope | X | Y | Current project status label | Current public sources |
|---|---|---|---|---:|---:|---|---|
| `jacque-fresco` | Jacque Fresco | `origin` | `direct` | -82 | -72 | historical source | [Official history](https://www.thevenusproject.com/about/history/) |
| `venus-project` | The Venus Project | `origin` | `direct` | -88 | -80 | active organisation | [Official programme](https://www.thevenusproject.com/the-venus-project/); [history](https://www.thevenusproject.com/about/history/) |
| `sliuzko-dtf` | Yevhen Sliuzko / Designing the Future | `critic` | `direct` | -28 | 18 | active public authors and NGO | [Sliuzko](https://sluzko.com/); [author page](https://designing-the-future.org/author/yevhen_sliuzko/); [Designing the Future](https://designing-the-future.org/ua/); [Telegram](https://t.me/sluzko); [Medium](https://medium.com/@DesigningTheFuture) |
| `critical-document` | Critical source document | `source` | `direct` | -12 | 8 | public advocacy document | [Google Docs original](https://docs.google.com/document/d/1EI_Le4-MgLDhm1c2tpYdjjVwwpbiAk_XRsD-dKx1qH8) |
| `renovation-earth` | Dmitriy Molodozhonov / Renovation Earth | `proposal` | `direct` | -38 | 34 | volunteer media initiative | [Author page](https://designing-the-future.org/author/dmitriymolodozhonov/); [Telegram](https://t.me/earthrenovate) |
| `zeitgeist-integral` | Peter Joseph / TZM / Integral Collective | `proposal` | `direct` | -68 | -32 | active movement; early cooperative prototype | [TZM model](https://www.thezeitgeistmovement.com/model); [Peter Joseph](https://www.peterjoseph.info/); [Integral Collective](https://integralcollective.io/) |
| `municipalist-critique` | Libertarian-municipalist critique | `critic` | `direct` | -54 | 76 | historical rough draft | [Original essay](https://postscarcityeconomics.wordpress.com/2015/07/26/critique-of-a-resource-based-economy-the-venus-project-and-the-zeitgeist-movement-from-a-the-perspective-of-a-libertarian-municipalist-who-is-for-post-scarcity-economics-by-hagbard-celine33/) |
| `rbe10k` | RBE10K | `proposal` | `direct` | -76 | -46 | historical; activity unverified; own host failed DNS on 2026-08-31 | [dated partner profile (2013)](https://onecommunityglobal.org/people-changing-the-world/); [original RBE wiki, unavailable at handoff](https://en.rbem.org/wiki/The_RBE10K_Project) |
| `morozov-mcquillan` | Evgeny Morozov / Dan McQuillan | `critic` | `adjacent` | -22 | 48 | active authors | [Morozov](https://newleftreview.org/issues/ii116/articles/evgeny-morozov-digital-socialism.pdf); [McQuillan](https://www.danmcquillan.org/pages/about.html) |
| `landemore` | Hélène Landemore | `proposal` | `adjacent` | -18 | 86 | active political theorist | [Open Democracy](https://politicalscience.yale.edu/publications/open-democracy-reinventing-popular-rule-twenty-first-century) |
| `tongdong-bai` | Tongdong Bai | `proposal` | `adjacent` | 12 | -58 | active political philosopher | [Fudan profile](https://philosophy.fudan.edu.cn/philoenglish/10/d6/c48705a725206/page.htm); [book](https://www.jstor.org/stable/j.ctvhrd162) |
| `hidalgo` | César Hidalgo / Augmented Democracy | `research` | `adjacent` | 4 | -26 | experimental proposal | [Proposal](https://cesarhidalgo.com/augmented-democracy) |
| `radicalxchange` | Glen Weyl / RadicalxChange | `proposal` | `adjacent` | 42 | 42 | active research network | [Quadratic voting](https://www.radicalxchange.org/wiki/quadratic-voting/) |
| `anno-dd2030` | Takahiro Anno / Digital Democracy 2030 | `political` | `tool` | 8 | 72 | active civic and political programme | [DD2030](https://dd2030.org/about/); [Team Mirai](https://team-mir.ai/); [Kouchou-AI](https://github.com/digitaldemocracy2030/kouchou-ai); [Idobata](https://github.com/digitaldemocracy2030/idobata) |
| `vtaiwan-polis` | Audrey Tang / vTaiwan / Polis | `implementation` | `tool` | -4 | 94 | deployed process and active software | [vTaiwan](https://info.vtaiwan.tw/); [Polis](https://github.com/compdemocracy/polis) |
| `democracyos` | Pia Mancini / DemocracyOS | `implementation` | `tool` | 4 | 84 | historical; unmaintained | [Repository](https://github.com/DemocracyOS/democracyos) |
| `your-priorities` | Róbert Bjarnason / Your Priorities | `implementation` | `tool` | 18 | 70 | active deployed platform | [Official site](https://citizens.is/); [repository](https://github.com/CitizensFoundation/your-priorities-app) |
| `decidim-consul` | Decidim / Consul Democracy | `implementation` | `tool` | -34 | 92 | active deployed platforms | [Decidim](https://github.com/decidim/decidim); [Consul](https://github.com/consuldemocracy/consuldemocracy) |
| `liquidfeedback` | LiquidFeedback | `proposal` | `tool` | 26 | 82 | established open-source system | [Open-source information](https://liquidfeedback.com/en/open-source.html) |
| `openfisca` | OpenFisca | `implementation` | `tool` | -16 | -16 | active digital public good | [Official site](https://openfisca.org/en/); [GitHub](https://github.com/openfisca) |
| `verifiable-voting` | ElectionGuard / Helios / Belenios | `implementation` | `tool` | 28 | 30 | active research and deployment tools | [ElectionGuard](https://github.com/Election-Tech-Initiative/electionguard-python); [Helios](https://github.com/benadida/helios-server); [Belenios](https://www.belenios.org/) |
| `talk-to-city` | Talk to the City | `implementation` | `tool` | 2 | 56 | active open-source tool | [About](https://www.talktothe.city/about); [repository](https://github.com/AIObjectives/tttc-light-js) |
| `cip-habermas` | CIP / Habermas Machine | `research` | `adjacent` | -8 | 38 | active research and prototypes | [CIP roadmap](https://www.cip.org/research/ai-roadmap); [DeepMind](https://deepmind.google/research/publications/65220/); [critical analysis](https://ojs.aaai.org/index.php/AIES/article/view/36687) |
| `forward-voting` | Forward Party / voting reform | `political` | `adjacent` | 66 | 32 | active political party and reform field | [Forward](https://www.forwardparty.com/faq/); [RCV](https://fairvote.org/our-reforms/ranked-choice-voting/); [Approval](https://electionscience.org/education/approval-voting/); [STAR](https://www.starvoting.org/star) |
| `open-north-flux` | Open North / Flux Australia | `political` | `adjacent` | 36 | 64 | active civic infrastructure / historical experiment | [Open North](https://opennorth.ca/); [GitHub](https://github.com/opennorth); [Flux archive](https://voteflux.org/) |
| `mind-journal` | Mind Journal | `source` | `reference` | 0 | 0 | independent editorial project | [Site](https://mmortall.github.io/blogs-Mind-Journal/); [repository](https://github.com/mmortall/blogs-Mind-Journal) |

### Current glossary inventory

Political spectrum; left-wing politics; centrism; right-wing politics; technocracy; meritocracy; participatory democracy; direct democracy; deliberative democracy; liquid democracy; e-democracy; economic planning; post-scarcity; resource-based economy; libertarian municipalism; social ecology.

Wikipedia links are reader aids. The consultant must replace or supplement them with foundational, review, official, and primary empirical sources for load-bearing conclusions.

### Operational continuity

- `KAN-1`: Kaneo task `xovvrdnx58ds6h86jneziwuc`, “Prepare deep research handoff for Venus Project political map freshness audit,” status `in-progress` when the bundle was created. The consultant has no Kaneo access and must not mutate it.
- No Cerebro query was used. Repository content and public sources were sufficient to define the unresolved question.

## 10. Failed approaches and negative knowledge

| Attempt or prior assumption | Why plausible | Observed result | Decision / retry condition |
|---|---|---|---|
| Simple network/grid layout | Good for relations and catalogue coverage | Did not communicate left/centre/right-like ideological placement | Replaced by two-axis view; retain network edges only as secondary context |
| Treating Google document as multi-author | Related archive work had two authors | Accompanying publication attributes the main document to Yevhen Sliuzko; archive article is separate co-authorship | Do not merge authorship without primary evidence |
| Marking Integral Collective open source | Project language suggested openness | No verified code repository supported that flag | Keep `open_source: false` unless current source proves otherwise |
| Assuming build success proves map correctness | Hugo rendered without fatal errors | Earlier data/JSON defects still existed | Require content/schema/browser checks separately |
| YAML key `y` without quoting | Looked like ordinary coordinate syntax | YAML 1.1 parsed `y` as boolean `true` | Preserve quoted `"y"` in project data; research should not infer coordinate validity from parsing success |
| Background SVG zones with pointer events | Visual bands were harmless in appearance | Bands intercepted map clicks | Fixed by disabling pointer events; irrelevant to political evidence |
| Treating a working link as current activity | Fast freshness proxy | Archives and dormant repositories can still return HTTP 200 | Require dated activity/adoption evidence and archive status |
| Treating a failed automated request as a dead source | `403`, timeout, and DNS failure all prevent immediate retrieval | Fudan accepted `GET` after rejecting `HEAD`; Medium remained automation-blocked; RBE10K failed DNS | Record protocol and failure class; only DNS failure is currently strong evidence that the original host is unavailable |
| Treating person + project + tool as one ideological unit | Compact map navigation | Risks category error and false coordinate precision | Explicitly test decomposition and unit ownership |

## 11. Track-specific initial map

The consultant must reconstruct and compare these seven preliminary families. Merge or split them only with evidence.

### `FAM-1` Resource planning, post-scarcity, and RBE

- Problem: allocate production and access beyond price-mediated scarcity.
- Preconditions: measurable resources/capacity, planning institutions, transition rules, accountability.
- Boundary: abundance in some goods does not remove all scarcity, conflict, or political choice.
- Project implication: Jacque Fresco, The Venus Project, TZM/Integral, RBE10K.

### `FAM-2` Expert, technocratic, and meritocratic governance

- Problem: use specialised knowledge in complex decisions.
- Preconditions: competence selection, transparent mandate, accountability, correction and appeal.
- Boundary: expertise does not settle values or authorise coercive power by itself.
- Project implication: Fresco/TVP’s technical design, Tongdong Bai, Augmented Democracy, parts of OpenFisca.

### `FAM-3` Direct, participatory, liquid, and open democracy

- Problem: give affected people real decision power beyond periodic representation.
- Preconditions: inclusion, agenda rules, identity/authentication where needed, decision scope, implementation commitments.
- Boundary: participation can be unequal; delegation can concentrate power.
- Project implication: Landemore, DemocracyOS, LiquidFeedback, Decidim/Consul, parts of DD2030.

### `FAM-4` Deliberation, collective intelligence, and AI mediation

- Problem: aggregate diverse knowledge and find actionable disagreement/common ground.
- Preconditions: plural input, transparent framing, traceable synthesis, human contestability, privacy.
- Boundary: consensus text is not public authorisation; model control can suppress minority views.
- Project implication: vTaiwan/Polis, Your Priorities, Talk to the City, CIP/Habermas Machine, DD2030.

### `FAM-5` Libertarian municipalism, social ecology, and polycentric governance

- Problem: combine local democratic autonomy with confederal coordination and ecological responsibility.
- Preconditions: functioning assemblies, delegated/recallable coordination, inter-municipal rules, resource sharing.
- Boundary: localism can reproduce exclusion and may not scale to global externalities.
- Project implication: municipalist critique, possible missing Bookchin/Ostrom/commons institutions.

### `FAM-6` Market-oriented and electoral institutional reform

- Problem: change incentives and representation without replacing the whole political economy.
- Preconditions: enforceable rules, broad access, administrative capacity, campaign/media safeguards.
- Boundary: voting rules do not solve every power or information problem.
- Project implication: RadicalxChange, Forward/RCV/Approval/STAR, Flux.

### `FAM-7` Digital public infrastructure, rules-as-code, and verifiable governance

- Problem: make public rules, data, participation, and counting inspectable and reusable.
- Preconditions: maintained code, public ownership or enforceable governance, security, accessibility, institutional integration.
- Boundary: software capability is not constitutional legitimacy or empirical adoption.
- Project implication: OpenFisca, ElectionGuard/Helios/Belenios, Open North, repositories across other nodes.

Direct criticism and accountability are cross-cutting lenses rather than one positive governance family. Compare transition feasibility, organisational accountability, fundraising/reporting, democratic legitimacy, and independent audit across all families.

## 12. Source strategy

Use source types according to claim:

1. Canonical terminology: foundational books, peer-reviewed reviews, major reference works, standards, and mature comparative literature.
2. A movement’s stated programme: official current pages and archived versions, clearly labelled as self-description.
3. Current project status: official announcements plus repository releases/commits, public institutional deployments, independent reporting, or archive evidence. Record access date.
4. Effectiveness/adoption: primary empirical studies, evaluations, replication, public procurement/deployment records, and negative results.
5. Criticism/conflict: original critique, reply/right-of-reply where available, independent records, and the strongest counterargument.
6. Regional discovery: search relevant local languages only when they plausibly expose unique actors or evidence; translate cautiously.
7. Wikipedia: glossary cross-check and source discovery only, not sole support for contentious claims.

For each load-bearing source record title, author/publisher, date, URL, access date, exact supported/weakened claim, related IDs, applicability, limitations, and counterevidence.

## 13. Research cycles and stopping conditions

### Cycle 1 — Canonical reconstruction and freshness triage

- Reconstruct axis concepts and seven families.
- Verify every URL, entity identity, node type, and current status.
- Flag archives, dormant repositories, changed organisations, renamed programmes, and inaccessible sources.

### Cycle 2 — Evidence, counterevidence, and global coverage

- Build dossiers for all current nodes.
- Seek strongest independent support and strongest criticism.
- Discover missing direct TVP critics, successors, adjacent governance schools, and real implementations.
- Check regional/language blind spots and selection bias.

### Cycle 3 — Comparative placement and editorial decision

- Apply one common placement rubric.
- Run decomposition tests for bundled nodes.
- Compare current axes with better alternatives or uncertainty bands.
- Produce KEEP/CORRECT/DECOMPOSE/REMOVE/VERIFY_FIRST decisions and ranked project-side experiments.

### Stop when

- each retained node has a dated primary source and at least one appropriate independent or counterevidence lane where available;
- new sources no longer change node classification, family model, coordinate band, or missing-actor list;
- every unresolved conflict has an explicit `HUM-*` evidence request or `VERIFY_FIRST` status;
- no conclusion depends only on an undated official claim, Wikipedia summary, or model inference.

If responsible breadth cannot reach 5–7 families, return `BREADTH_BLOCKED` with the reason instead of adding filler.

## 14. Required experiments and local evidence

### `EXP-1` Node freshness audit

- Baseline: current 26-node inventory.
- Comparison: current official source, repository/activity signal, independent evidence, archive status.
- Prediction: several nodes need status correction or decomposition.
- Falsifier: all current status labels are supported by dated evidence.
- Output: dated node ledger and exact replacement text.

### `EXP-2` Independent coordinate coding

- Baseline: current numeric coordinates.
- Intervention: at least two independent coders apply an explicit rubric to mechanism-level evidence without seeing current coordinates.
- Controls: same evidence packets; record disagreement; separate person, programme, tool, and implementation.
- Prediction: bundled/ambiguous nodes show high disagreement.
- Falsifier: independent placements converge within predeclared bands.
- Decision: retain point, widen uncertainty, decompose, or remove coordinate.

### `EXP-3` Bundled-node decomposition

- Test at least `morozov-mcquillan`, `zeitgeist-integral`, `decidim-consul`, `verifiable-voting`, and `open-north-flux`.
- Compare whether components have materially different status, authority, source types, or placement.
- Kill condition: decomposition adds no decision-relevant distinction and only clutters navigation.

### `EXP-4` Glossary equivalence audit

- Compare EN/RU/UK term scope using authoritative references and native-language usage.
- Flag false friends, missing local articles, overly broad translations, and movement-specific terms presented as canonical.
- Output exact corrected definitions and links.

### `EXP-5` Coverage-gap audit

- Compare the seven-family model with current geographic and institutional coverage.
- Add candidates only when they change a family, evidence lane, regional blind spot, or implementation maturity.
- Null branch: current map may already be sufficient for its editorial purpose; do not reward list growth itself.

### Human evidence requests

- `HUM-1`: confirm whether the editor wants people, organisations, tools, documents, and ideas on one visual layer or accepts typed/decomposed layers.
- `HUM-2`: confirm tolerance for coordinate uncertainty bands versus exact points.
- `HUM-3`: provide any private correspondence only as a disclosure that such evidence exists; do not transfer it into the public map or consultant archive without explicit publication authority.
- `HUM-4`: identify which proposed additions feel “close in spirit” to the editor; treat affinity as editorial relevance, not factual validation.

## 15. Consultant response contract

Return exactly:

```text
venus-project-idea-map-deep-research-20260831/
├── 00-venus-project-idea-map-research-index.md
├── 01-venus-project-idea-map-decision-brief.md
├── 02-venus-project-idea-map-canonical-model-and-decision-map.md
├── 03-venus-project-idea-map-hypotheses-or-technique-families.md
├── 04-venus-project-idea-map-evidence-and-counterevidence.md
├── 05-venus-project-idea-map-candidate-or-family-dossiers.md
├── 06-venus-project-idea-map-ranked-experiments.md
└── 07-venus-project-idea-map-next-loop-and-required-evidence.md
```

All files must be Markdown. Follow `CONSULTANT_RESPONSE_CONTRACT.md` in this bundle. Use visible `[REQ]`, `[FACT]`, `[OBS]`, `[DEC]`, `[INF]`, `[HYP]`, `[UNK]`, and `[CONFLICT]` labels and High/Medium/Low confidence with reasons.

## 16. Return-to-implementer protocol

The implementing agent must first verify the consultant’s terminology, node ownership, scale assumptions, source dates, and decomposition against the real repository. External findings do not automatically authorise edits.

Classify every recommendation:

```text
APPLICABLE | VERIFY_FIRST | CONFLICTS | ALREADY_TRIED | HIGH_RISK | OUT_OF_SCOPE
```

Logical corrections (wrong author, dead link, type mismatch, unsupported status) may be applied directly after source verification. New axes, scores, node splits, or political interpretations should move through a focused-solution handoff or a small reversible editorial change with validation.

Read `RETURN_TO_IMPLEMENTER_PROMPT.md` before implementation.

## 17. Limitations and review status

- [UNK] This handoff does not independently re-research all 26 entities; it freezes project state and defines the required synthesis.
- [UNK] Current official activity can change after 2026-08-31. Consultant outputs must include access dates.
- [UNK] RBE10K's original wiki host did not resolve on 2026-08-31. A dated third-party partner profile preserves historical evidence, but present activity and an authoritative archive snapshot still require research.
- [UNK] Medium returned HTTP 403 to automated retrieval. This is an access limitation, not evidence that the account is inactive.
- [OBS] Several committed wiki status pages lag behind the current trilingual map. They are not used as factual baseline here; current content/data at commit `01e06fa` is authoritative.
- [OBS] Uncommitted work from another active project task existed under `docs/wiki/` when this bundle was prepared and was intentionally excluded.
- [FACT boundary] Build and browser validation support runtime integrity only. They do not validate political accuracy.
- Self-review: task requires broad synthesis; no implicit audit/discovery workload was introduced; canonical anchors are classified; hierarchy, ownership, scale, and composition are explicit; counterevidence and null branches are required; filenames and return contract are exact.
