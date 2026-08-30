# Return to Implementer after Deep Research

Read the full handoff and all eight consultant files before editing Mind Journal.

## 1. Verify the canonical model first

Check:

- terminology and EN/RU/UK equivalence;
- separation of person, organisation, idea, source, tool, and implementation;
- ownership and time semantics of status labels;
- relative versus absolute meaning of coordinates;
- one-level-up and one-level-down scale tests;
- whether accepted facts were composed correctly;
- whether official self-description was mistaken for independent effectiveness evidence.

Quarantine recommendations with inconsistent ownership, missing dates, or no public source.

## 2. Map findings to the real project

For every recommendation classify:

```text
APPLICABLE | VERIFY_FIRST | CONFLICTS | ALREADY_TRIED | HIGH_RISK | OUT_OF_SCOPE
```

Compare against current `data/future_network.yaml`, trilingual map articles, runtime filters, validator, and public build. Check whether another task changed the baseline after commit `01e06fa`.

## 3. Separate correction from hypothesis

- Wrong author, dead link, false current-status claim, unsupported `open_source`, or type mismatch: correct after source verification.
- New node, coordinate, axis, split/merge, family, ranking, or effectiveness claim: treat as an editorial hypothesis requiring a reversible change and validation.

## 4. Choose next workflow

- Mechanism/editorial model remains open: run the first ranked experiment.
- Branch is selected but exact schema/UI is open: create a focused-solution handoff.
- Exact source-backed correction is specified: implement smallest coherent change, preserve EN/RU/UK parity, validate, commit, and deploy.

Do not implement the research archive wholesale. Preserve public-repository privacy and unrelated concurrent work.
