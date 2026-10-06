# Customer Discovery Brief: <prospect-slug>

**Sessions**: <list of session dates>
**Coverage status**: <complete | partial — see Outstanding section>

<!--
  Coverage status is `partial` whenever any required_for_stop question (business-industry,
  constraints-pain-points) is not `answered`; `complete` needs the five categories AND both answered.
  Structure and rules for this document are the contract in
  specs/005-crm-discovery-interviewer/contracts/customer-brief-contract.md.
  Every bullet below MUST carry exactly one origin tag from
  .claude/skills/ZCRM-discovery/references/origin-tags.md and a source pointer.
  Do not place a [WEB]/[PROSPECT-DOC]-only (unconfirmed) finding in any of the five sections below —
  it belongs in "Unconfirmed Findings" until a customer confirms or corrects it (FR-008).
-->

## Business Process & Stages
- **Industry:** <what the business does and who its customers are> [ORIGIN-TAG] (source: <exchange ref or ingested-source ref>)
- <statement> [ORIGIN-TAG] (source: <exchange ref or ingested-source ref>)
  - Concrete instance cited: <reference to the real case the customer walked through>

## Roles & People
- <statement> [ORIGIN-TAG] (source: <exchange ref or ingested-source ref>)

## Key Entities / Objects Tracked
- <statement> [ORIGIN-TAG] (source: <exchange ref or ingested-source ref>)

## Success Metrics
- <statement> [ORIGIN-TAG] (source: <exchange ref or ingested-source ref>)

## Explicit Constraints / Must-Haves
- <statement> [ORIGIN-TAG] (source: <exchange ref or ingested-source ref>)
- **Pain:** <reported pain, one bullet each> [ORIGIN-TAG] (source: <exchange ref or ingested-source ref>)

## Outstanding / Unresolved
- Industry not provided — [HUMAN REVIEW]: engineer to obtain before design (only if absent)
- No pains reported — [HUMAN REVIEW]: engineer to obtain before design (only if absent)
- <item> — [UNDECIDED-DELEGATED] | unanswered dependency-blocked question
- <item> — [HUMAN REVIEW]: <regulated topic the customer asked about>

## Unconfirmed Findings (not yet promoted to fact)
- <finding> [WEB]/[PROSPECT-DOC] — awaiting customer confirmation
