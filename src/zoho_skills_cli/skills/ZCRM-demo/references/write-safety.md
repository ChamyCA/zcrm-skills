# Write Safety (cross-cutting, all phases)

This applies at every phase of the pipeline, not just Phase 1 introspection.

## Rule: the demo skill performs no org writes

Only read operations against the Zoho CRM demo org are permitted (`getModules`, `getFields`,
`getRecords`, `searchRecords`, `executeCOQLQuery`, etc.). No create, update, or delete operation
is run by this skill, ever. A chat "yes" given to this skill does not authorize a write.

## If a write would help the demo

(e.g., seeding a missing sample record so a scene has demo-worthy data, or tagging a record for
the walkthrough)

1. **Stop.** Do not perform the write.
2. **Tell the engineer** that writes are not done by this skill and point them to
   ZCRM-executor, which performs org writes only after the engineer confirms each step in chat
   against the exact preview and request hash.
3. **Continue read-only.** Do not reference the missing data in any scene.
4. **Record the skipped opportunity** in `gaps-and-risks.md` (Phase 6), describing the exact
   record/field/module and values that would be needed, so the engineer can take it to
   ZCRM-executor.

## Connectors

Use "US DC -" demo-account connectors for the demo org. "(Corp)" connectors are for internal
reads only; never copy Corp data into the demo org. If it is unclear which connector applies,
ask the engineer.

## Why this exists

The demo org is a shared asset used across multiple prospects and engagements. A single
unapproved write can silently break a future demo relied on for another active deal. Writes are
therefore centralized in ZCRM-executor, where a request-hash gate, a target-org guard, a scope
guard and a no-delete rule are enforced in code. The engineer's confirmation itself is given in
chat and is prompt-level; it is accepted only for internal demo and sandbox orgs.
