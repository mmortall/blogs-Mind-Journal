# Signal-dependence map for AI checks

> source: public data of `nikhgarg/llm_correlated_errors_public` (resume `final.csv`, HELM and HF MMLU pair tables) and `allenai/reward-bench(-results)` (2,985 same items, 117 checkers); full map, code and tables live in task #82 artifacts (`signal-dependence-map.md`, `scripts/`).

Question: do several AI checks add information, or repeat shared data and model assumptions?

- Average error correlation between checkers is positive in all four lines, but not for every pair. Resume (450 human-labeled rows): cross-lab phi 0.32 (FP) / 0.33 (FN); five labs give n_eff about 1.4; majority vote did not beat the best single judge. HELM (71 models) phi 0.42; HF (349) minimum 0.205.
- Same-item test (RewardBench, 66 competent checkers, 2,145 pairs): mean phi 0.25; shared lineage 0.31, different mechanism and lineage 0.21. Pairs of strong checkers (both accuracy >= 0.85) stay at phi >= 0.12.
- Low-correlation pairs exist (140 pairs, pooled phi about 0; some significantly negative, i.e. complementary failure) and persist on held-out items, but come from a weaker checker failing in a different place (Qwen1.5-Chat DPO-implicit). Low correlation is not demonstrated independence.
- Non-neural executor (public docstring examples, 164 code items): mean error phi 0.05 with 66 neural checkers (0.15 neural vs neural), none significant, but power is low (20 executor errors); full-test execution reproduces the reference by construction, so it validates it but is not an independent comparison.
- Disagreement flags catch 62% of a checker's errors vs 84% if errors were independent.
- Redundancy is cosmetic when checks share item text, scale and difficulty and no member fails in a different place; independence from near-chance members is uselessness.
- Unknown: reference-label error, training overlap and benchmark contamination of checkers. Not done: source-level independence; non-neural checker beyond 164 code items; controlled B1/B2 arms (need paid live calls).
