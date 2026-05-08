# Claim Admission Labels

Only `SOURCE_BOUND` and validated `DERIVED` claims may enter reseeded canonical context without adjudication.

| Label | Definition | Canonical Entry | Default Handling |
|---|---|---:|---|
| SOURCE_BOUND | Directly supported by admitted source span. | Allowed | Preserve with source span ID. |
| DERIVED | Logically transformed from SOURCE_BOUND material. | Allowed after validation | Require derivation note and validator. |
| HEURISTIC | Operationally useful but not validated. | Blocked unless explicitly approved | Quarantine or mark noncanonical. |
| SPECULATIVE | Conceptual extension beyond available evidence. | Blocked | Quarantine. |
| UNVERIFIED_TRANSFER | Cross-domain mapping not yet validated. | Blocked | Send to transfer adjudication. |
| ONTOLOGY_EXTRAPOLATION | New or stretched term outside manifest authority. | Blocked | Manifest governance review. |
| CONTAMINATED_CHAIN | Claim lineage includes unsupported, ambiguous, or failed node. | Blocked and logged | Ledger event required. |
