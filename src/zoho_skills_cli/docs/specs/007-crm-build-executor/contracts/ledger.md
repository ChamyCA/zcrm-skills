# Contract: `run-ledger.jsonl`

One JSON object per line, append-only, secret-free.

```json
{"step":12,"element":"FLD-004","hash":"sha256:…","state":"DONE-VERIFIED","created_ids":["…"],"ts":"2026-10-05T14:03:11Z","confirmed_hash":"sha256:…"}
```
Invariants: `state` is one of DONE-VERIFIED | DONE-UNVERIFIED (write applied, no read-back supplied) | MANUAL-DONE | SKIPPED | FAILED; FAILED has
`failure_class`; no value matches a token shape or loaded secret; a step's final state appears once.
Report counts (done + manual + skipped + failed) MUST equal the plan's step count.
