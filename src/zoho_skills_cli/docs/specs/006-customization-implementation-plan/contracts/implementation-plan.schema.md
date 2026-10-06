# Contract: Implementation Plan File

This is the external contract this skill produces, consumed by a later Claude Code execution
session. Since the deliverable is a Markdown document for an LLM executor (not a machine-parsed
API), the contract is expressed as a required document structure and a set of invariants an
executor — or an automated check — can verify against the rendered Markdown.

## Required sections (in order)

1. `# Implementation Plan: <Prospect Name>`
2. `## Prerequisites`
   - `### Required API Scopes` — bullet list, one scope per line, union of every step below
   - A literal statement: "This file contains no credentials. Before proceeding, request a live
     API token with the scopes above from the engineer running this plan."
3. `## Manual Steps Summary` (omit only if zero `manual`-method steps exist)
   - Bullet list of design elements with no direct API equivalent, referencing their step number
4. `## Phase 1: Discovery (read-only)`
   - Numbered steps, each: API call description, what it discovers, no `required_scope` beyond
     read-level access, no confirmation instruction required
5. `## Phase 2: Reconciliation`
   - Instruction block: compare each discovery finding to the Design Package's assumption for
     that element; on any mismatch, STOP and report to the engineer before Phase 3 begins
6. `## Phase 3+: Build Steps`
   - Numbered steps, grouped by element type in dependency order (modules → fields →
     relationships → pipelines → blueprints → automation rules → dashboards)
   - Each step: Design package reference (`design_element_ref`; rendered as the step field
     "Design package reference"), `build_method`, `operation`, `required_scope` (if any),
     `depends_on`, and — for every write operation — the literal confirmation instruction
7. `## Traceability` — table: Design Element ID | Step Number(s) | Covered? (yes/no/manual)

## Invariants (machine-checkable against the rendered Markdown)

| ID | Invariant |
|---|---|
| C-01 | Zero matches for a credential-shaped token pattern anywhere in the file |
| C-02 | Phase 1 (Discovery) section appears before any Phase 3+ step |
| C-03 | Every Phase 3+ write step's text contains the literal confirmation instruction |
| C-04 | Every row in the Traceability table has `Covered? = yes` or `manual` — no blanks, no `no` |
| C-05 | Every Design Package element ID appears at least once in the Traceability table, and every Traceability row is a Design Package element (checked both ways by the executor gate; IDs derived per ZCRM-planner Step 1; standard modules and standard fields, `is_standard: true`, need no `module:` / `field:` row and no create step, but a row for them is allowed; a lookup declared as both a field and a relationship has ONE `createFields` step, and both rows cite it) |
| C-06 | Every `depends_on` reference in a build step points to a step number that appears earlier in the document |
| C-07 | Every write step lists at least one `required_scope` |

## Non-contract (explicitly out of scope)

- This skill does not call any Zoho CRM API itself — there is no request/response contract
  between this skill and the CRM.
- This document is not a JSON/OpenAPI schema because the consumer is an LLM-driven executor
  reading Markdown instructions, not a program parsing structured data; invariants above are
  phrased so they can still be checked mechanically (e.g., in the golden test, research.md).
