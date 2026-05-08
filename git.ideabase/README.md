# git.ideabase

Repopulated ideabase for **Constraint-Stable Recursive Synthesis (CSRS)**.

This bundle applies the v0.2.1 -> v0.2.3 patch series to the uploaded `Method Package Plan v0.2 Update.pdf` source package and converts the work into repo-ready method architecture files.

## Current package state

- Package: CSRS Method Package
- Applied version: v0.2.3
- Source: `Method Package Plan v0.2 Update.pdf`
- Status: `PATCHED_IDEABASE_CANDIDATE`
- Main posture: architecture and validation harness, not formal proof
- Blocked until case runs: manifesto drafting, production-readiness claims, mathematical proof claims, standardization claims

## Repo map

```text
.
├── README.md
├── ideabase.manifest.yaml
├── docs/
│   ├── CSRS_Method_Package_v0.2.3.md
│   ├── source_notes.md
│   └── next_actions.md
├── schemas/
│   ├── canon_manifest_template.yaml
│   ├── claim_posture.yaml
│   ├── determinism_tiers.yaml
│   ├── method_failure_event.schema.json
│   └── validation_run_record.schema.json
├── tables/
│   ├── claim_admission_labels.md
│   ├── halt_taxonomy.md
│   └── invariant_classes.md
├── patches/
│   └── CSRS_v0.2_to_v0.2.3.patch
├── runbooks/
│   └── validation_runbook.md
└── tests/
    └── fixtures/
        ├── method_failure_event.example.json
        └── validation_run_record.example.json
```

## What changed

The patch series does three things:

1. **v0.2.1 - Claim hygiene and failure taxonomy**
   - Downgrades proof-like language.
   - Adds FALSE_STABILITY, GRAPH_CONSTRUCTION_DRIFT, and ADVERSARIAL_METRIC_PRESSURE.
   - Splits verification from truth.

2. **v0.2.2 - Execution schema and replay tiers**
   - Adds STRICT_REPLAY, STRUCTURAL_REPLAY, SEMANTIC_REPLAY, and NON_REPLAYABLE_EXPLORATORY.
   - Adds Canon Manifest governance.
   - Adds claim admission labels and burden accounting.

3. **v0.2.3 - Validation harness and case refactor**
   - Splits Cognition Kiln into B1 recursive stress and B2 transfer stress.
   - Adds validation run records and method failure event schema.
   - Bounds Case C as optional decision-support unless tested against actual infrastructure.

## Recommended next command

```bash
python -m json.tool schemas/validation_run_record.schema.json >/dev/null
python -m json.tool schemas/method_failure_event.schema.json >/dev/null
```

Then run the first dry validation record against `tests/fixtures/validation_run_record.example.json`.
