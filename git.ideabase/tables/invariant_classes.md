# Invariant Classes

Invariant failures are typed before halt behavior is selected.

| Class | Example | Default Response |
|---|---|---|
| LEXICAL_INVARIANT | Exact label, placeholder, required phrase. | SOFT_HALT_OR_PATCH |
| NUMERIC_INVARIANT | Threshold, constant, version number, parameter. | ROLLBACK_HALT |
| LOGICAL_INVARIANT | Operator, condition, causal dependency, precondition. | QUARANTINE_HALT |
| ONTOLOGY_INVARIANT | Canonical term definition, approved mapping, forbidden equivalence. | HUMAN_ADJUDICATION_HALT |
| PROVENANCE_INVARIANT | Source hash, citation path, ledger reference, manifest linkage. | IRREVERSIBLE_CONTAMINATION_REVIEW |
