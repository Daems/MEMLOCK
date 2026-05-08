# CSRS Validation Runbook

## Purpose

This runbook gives a minimal execution path for validating CSRS artifacts without upgrading exploratory language into canonical state.

## Preflight

Confirm these artifacts exist:

- `ideabase.manifest.yaml`
- `schemas/validation_run_record.schema.json`
- `schemas/method_failure_event.schema.json`
- `schemas/determinism_tiers.yaml`
- `tables/claim_admission_labels.md`
- `tables/halt_taxonomy.md`

## Run record sequence

1. Assign `run_id`.
2. Select `case_id`.
3. Declare replay tier.
4. Hash source corpus, prompt, evaluator config, and initial state.
5. Execute baseline.
6. Execute CSRS variant.
7. Extract claims.
8. Apply claim admission labels.
9. Record failed checks.
10. Append method failure events if needed.
11. Decide PASS, PASS_WITH_LIMITATIONS, FAIL_REPAIRABLE, FAIL_CONTAMINATED, or INCONCLUSIVE.

## Case A: Long-Context Audit

Required baselines:

- raw long-context prompt
- naive summary prompt
- standard RAG prompt
- CSRS reseed plus rehydration prompt

Required metrics:

- single fact retrieval accuracy
- multi fact synthesis accuracy
- source span support ratio
- unsupported claim ratio
- middle context recovery rate
- rehydration burden cost
- verification latency

## Case B1: Cognition Kiln-R

Pressure: repeated reseed/diff loops and recursive contamination risk.

Required outputs:

- step count
- reseed count
- failed gate count
- invariant loss events
- rollback events
- final supported claim ratio

## Case B2: Cognition Kiln-T

Pressure: cross-domain migration of logic under constrained vocabulary.

Required outputs:

- source domain
- target domain
- approved transfer map
- rejected transfer map
- ontology extrapolation events
- unresolved ambiguity count
- final transfer validity score

## Case C: Carbon-Aware Orchestration

Use only as optional transfer-pressure study unless connected to controlled infrastructure testing.

## Closeout

Every run ends with:

- validation run record
- method failure events, if any
- residual risk statement
- next action
