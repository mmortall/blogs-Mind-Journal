---
translationKey: governance-ai-layer-ru
title: "Can AI Become a Layer of Governance?"
description: "How to distinguish decision support from authority, responsibility and the ability to correct mistakes."
date: 2026-11-16T00:00:00Z
lastmod: 2026-11-16T00:00:00Z
tags:
  - artificial intelligence
  - governance
  - accountability
author: Sergii Taraban
draft: true
---

Imagine an organization receives thousands of requests. An AI system helps sort them, find similar cases and suggest an answer to an employee. This can change people's work even if a human formally makes the final decision: it matters what information the system shows, which cases it sends for review and how much time remains for an independent assessment.

Let us call a **governance layer** the set of rules and tools that guide decisions, allocate authority and allow errors to be corrected. This is a working definition for discussion, not a validated classification. The question is not only whether a model can suggest an answer, but also who sets the goals, checks the grounds for a decision and is accountable to the person affected.

## A person alongside the model

Human confirmation alone does not show that review was independent or effective. An employee needs access to the material, an opportunity to challenge the suggestion and time to check it. How a particular interface influences a decision should be measured in the relevant task, not assumed from the name of the procedure.

An example from another field shows why interaction design matters. In a study with 259 clinicians, participants reviewed descriptions of patients with acute respiratory failure. After cases without AI, they were randomly assigned to a condition showing all predictions or one that withheld potentially harmful inaccurate predictions and informed the participant of this. In version 2 of the preprint, the authors report that selective withholding partly reduced the negative effect of inaccurate suggestions on overall treatment accuracy, but the false-negative rate remained elevated. [Jabbour and colleagues, arXiv v2, 2026](https://arxiv.org/html/2508.07617v2).

This was a study of clinical vignettes, not public administration or actual treatment of patients during the experiment. Withholding relied on an experimental definition of potentially harmful predictions; the study does not establish that a deployed system can always identify such errors in advance. The result cannot be transferred to every AI-assisted decision or taken as proof that deferring a decision to a person is safe.

## Several models and one error

Several answers may help reveal disagreements, but agreement does not guarantee an independent check. Kim and colleagues studied errors from more than 350 language models across benchmark datasets and a résumé-screening task and reported correlated errors. This result concerns the models and tasks studied, not a universal measure of risk or proof of consequences in actual hiring. The methods and limitations sections of the [2025 PMLR paper](https://proceedings.mlr.press/v267/kim25e.html) distinguish agreement on multiple-choice answers when both models are wrong from residual correlation against subjective human ratings of résumé–job pairs. Its hiring market analysis is a simulation, not a measurement of real hiring outcomes.

For a particular system, it is useful to check not only model agreement but also data provenance, test conditions and cases where answers agree and are wrong. This is a proposal for evaluation, not proof that any model diversity removes shared error.

## From correcting an answer to accountability

Suppose a person challenges a refusal prepared with AI assistance. Correcting one decision may help that person; it does not by itself show that the organization changed a rule or found other similar cases. Checking this requires separate information about how appeals are handled, recurring causes of error and actual process changes. A low number of complaints likewise does not prove that submitting them is easy or safe.

Designers can ask several questions that can be checked:

- Who approves the system's purpose and limits, and who can stop it?
- What data and grounds are available to the reviewer and to the person affected by the decision?
- How can the result be challenged, who will consider the appeal, and can that person change the decision?
- Which errors are measured separately, who checks omissions, and how do review results lead to process changes?

These questions are a working framework, not an established standard of sufficiency or a guarantee of a fair outcome. The answers depend on authority, resources and the specific procedure. Automation can take part in governance, but the presence of a model alone does not determine who is responsible or how affected people's rights are protected.

> Editorial limitation: the clinical study is a preprint using experimental vignettes; the findings on correlated errors concern offline benchmarks and résumé ratings, with hiring outcomes simulated. Unreproduced internal metrics and unsupported historical or normative generalizations in the original material are not used here. No author or language review has been performed.
