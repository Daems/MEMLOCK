# Halt Taxonomy

| Halt Type | Use When | Default Next Action |
|---|---|---|
| SOFT_HALT | Repairable formatting error, missing metadata, low-severity schema gap. | Patch locally, rerun gate. |
| QUARANTINE_HALT | Speculative, unsupported, or contaminated claim enters candidate state. | Remove from reseed, create ledger event. |
| ROLLBACK_HALT | Prior stable state exists and failure is localized. | Revert to prior stable node, append rollback reference. |
| HUMAN_ADJUDICATION_HALT | Ambiguity cannot be resolved mechanically. | Escalate with source spans and failed claims. |
| IRREVERSIBLE_CONTAMINATION_HALT | Corrupted state has propagated beyond local repair. | Freeze chain, mark contaminated, require new run. |
