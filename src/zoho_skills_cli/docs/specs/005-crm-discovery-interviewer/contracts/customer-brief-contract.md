# Contract: `customer-brief.md`

This is the one external interface this feature exposes: the handoff artifact consumed by the
CRM Design skill (ZCRM-design). There is no API/CLI/UI contract beyond this document,
since the feature is a single conversational skill with a filesystem output.

## Required structure

```markdown
# Customer Discovery Brief: <prospect-slug>

**Sessions**: <list of session dates>
**Coverage status**: <complete | partial — see Outstanding section>

## Business Process & Stages
- **Industry:** <statement> [ORIGIN-TAG] (source: <exchange ref or ingested-source ref>)
- <statement> [ORIGIN-TAG] (source: <exchange ref or ingested-source ref>)
  - Concrete instance cited: <reference to the real case the customer walked through>

## Roles & People
- <statement> [ORIGIN-TAG] (source: ...)

## Key Entities / Objects Tracked
- <statement> [ORIGIN-TAG] (source: ...)

## Success Metrics
- <statement> [ORIGIN-TAG] (source: ...)

## Explicit Constraints / Must-Haves
- <statement> [ORIGIN-TAG] (source: ...)
- **Pain:** <statement> [ORIGIN-TAG] (source: ...)

## Outstanding / Unresolved
- <item> — [UNDECIDED-DELEGATED] | unanswered dependency-blocked question
- <item> — [HUMAN REVIEW]: <regulated topic the customer asked about>

## Unconfirmed Findings (not yet promoted to fact)
- <finding> [WEB]/[PROSPECT-DOC] — awaiting customer confirmation
```

## Contract rules (consumer-facing guarantees)

1. **Every bullet under the five coverage sections carries exactly one origin tag** from
   `[CUSTOMER]`, `[SUGGESTED-ACCEPTED]`, `[SUGGESTED-REJECTED]`, `[INFERRED]`. An item that is
   still `[WEB]`/`[PROSPECT-DOC]`-only (unconfirmed) MUST live in "Unconfirmed Findings", never in a
   coverage section (FR-008, SC-002, SC-003).
2. **Every bullet is traceable** to a source reference (an exchange ID or ingested-source ID),
   satisfying FR-015 — a consumer must be able to ask "where did this come from?" and get an
   answer without replaying the full transcript.
3. **"Coverage status: complete"** is asserted only when every one of the five sections has at
   least one `[CUSTOMER]`/`[SUGGESTED-ACCEPTED]` item or an explicit `[UNDECIDED-DELEGATED]`
   acknowledgment recorded in Outstanding (FR-013), AND both `required_for_stop` questions
   (`business-industry`, `constraints-pain-points`) are `answered`. If either is deferred, skipped
   or absent, the status is `partial`. A consumer reading "complete" can rely on
   this without re-deriving it from the raw session state.
4. **Industry and pains for the ZCRM-design gate.** The industry answer is the FIRST bullet under
   "Business Process & Stages", prefixed `**Industry:**`. Each reported pain is its own bullet under
   "Explicit Constraints / Must-Haves", prefixed `**Pain:**`. Both keep their origin tag and source
   reference. If absent, "Outstanding / Unresolved" carries a bullet "Industry not provided" /
   "No pains reported", tagged `[HUMAN REVIEW]` with a short reason (e.g. "engineer to obtain before design"). ZCRM-design reads industry from the `**Industry:**`
   bullet and top pains from the `**Pain:**` bullets (its Phase 0 blocking-inputs gate also uses
   Business Process & Stages for sales process and Roles & People for user roles).
5. **No regulated claim** (pricing, SLA, roadmap, contract terms, competitor claims) appears
   anywhere in the document outside the `[HUMAN REVIEW]` tag in Outstanding (FR-011).
6. **No unverified Zoho capability claim** appears as if confirmed; any such claim surfaced
   during the interview is either cited (with its Zoho Documentation source) or labeled
   `[UNVERIFIED]` and kept out of the coverage sections (FR-010).

## Stability note

This provisional structure (the five coverage sections) mirrors the FR-013 provisional minimum
coverage set and is expected to be reconciled once the downstream CRM Customization Architect's
own Phase 0 gate is specified (see spec.md Assumptions and research.md). Any such reconciliation
is a breaking change to this contract and must be versioned accordingly when it happens.
