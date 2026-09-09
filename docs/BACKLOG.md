# Candidate future functions

These ideas come from recurring workflows in the contractor's prior use of the library.
Obsolete analysis folders and historical outputs are not part of the reusable API.

| Priority | Capability | Why it would help | Boundary for a future implementation |
|---|---|---|---|
| Delivered | Batch scenario comparisons and Excel summaries | Repeated site/group and before/after analyses | Reuse identical demand and retain settings/coverage |
| Delivered | Shipment-to-profile preparation | Repeated SKU mapping and order aggregation | Explicit keys, quantity rules and missing-mapping reports |
| Next | Replacement-shipper ranking | Find alternatives when a supplier's shipper is unavailable | Rank only a supplied candidate catalog; distinguish geometric capacity from validated availability |
| Next | Dimension sensitivity | Check whether small dimension changes alter capacities or usage | Vary named dimensions and show thresholds without modifying references |
| Next | Explain unused shippers | Understand zero usage after adding an option | Separate no-fit, dominated modeled cost, objective effects and equivalent solutions; do not invent causal explanations |
| Later | Shipper alias and container-group mapping | Reconcile regional, historical and production IDs | Company-maintained explicit mappings, with ambiguity reports |
| Later | Actual-versus-expected packing audit | Compare warehouse packed-shipper records to intended rules | Requires confirmed order/oLPN keys, quantity meaning, deduplication and routing rules |
| Later | Additional cost models | Evaluate real destination/weight/cost behavior | Requires company rate data and explicit outer dimensions/weight; do not treat the legacy Zone 4 curve as live rates |

The delivered workflows also cover ordinary dimension overrides and reference
inspection; the deferred items are dedicated ranking, sweep or auditing functions.
