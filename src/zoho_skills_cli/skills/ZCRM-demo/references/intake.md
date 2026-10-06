# Phase 0: Intake Gate

Run this before any other phase. Do not proceed to Phase 1 until every check below passes.

## Required: Customer Brief

All of the following fields are required. If any is missing, halt and list exactly which ones:

- `company`
- `industry`
- `size`
- `pain_points` (summary list)
- `current_tools_process`
- `audience_roles` (list)
- `demo_duration`
- `success_criteria`

## Required: Customer Detailed Case

One entry per pain. Each entry requires:

- `pain_id`, `rank`
- `customer_words` (verbatim quote)
- `quantified_impact`
- `process_location` — one of: `lead capture`, `qualification`, `pipeline`, `quoting`,
  `handoff`, `renewal`, `reporting`
- `affected_role`
- `failure_example`
- `root_cause`
- `evaluation_trigger`
- `prior_attempts`
- `priority_flag` — `must-solve` or `nice-to-solve`

If any pain entry is missing a required field, halt and list exactly which pain and which
field(s) are missing.

## Must-solve validation rule

A pain flagged `priority_flag: must-solve` MUST have non-empty `quantified_impact` AND
non-empty `failure_example`. If either is empty for a must-solve pain, flag that pain as
insufficiently specified and halt — do not silently downgrade it or proceed without it. Name
the specific pain and the specific missing field(s) when you ask.

## Deriving inputs from upstream artifacts (decision D1)

If the engineer has no ready Customer Brief / Detailed Case, derive them from the discovery
`customer-brief.md` plus the design package under `output/<slug>/` (`02-customer-understanding.md`,
`01-requirements-register.md`, `12-handoff-spec.yaml`). Read those files; do not guess. Each
derived value keeps its origin tag (`CUSTOMER`, `INFERRED`, etc.) from the source line, and
shows the file it came from. Anything with no source is asked of the engineer in one batched
multiple-choice or free-text message, never filled in.

| Demo field | Derive from | Ask engineer if |
|---|---|---|
| `company` | brief title / prospect slug; requirements register title | name ambiguous |
| `industry` | `02-customer-understanding.md` "Business model" only if stated | not stated (always verify) |
| `size` | requirements register "Volumes, systems, pains, KPIs" only if stated | not stated |
| `pain_points` | register pains (REQ IDs) and customer-understanding as-is process | none found |
| `current_tools_process` | brief "Business Process & Stages"; as-is process; register systems | tools not named |
| `audience_roles` | brief "Roles & People"; "Stakeholders"; register Actors / Roles | none found |
| `demo_duration` | not in any upstream file | always ask |
| `success_criteria` | brief "Success Metrics"; register KPIs | none found |
| `pain_id`, `rank` | register REQ ID; rank from brief priorities, else ask | no priority stated |
| `customer_words` | verbatim quote in register/brief tagged `CUSTOMER` only | no verbatim quote (never paraphrase) |
| `quantified_impact` | register KPIs/volumes only if a number is stated for this pain | usually ask |
| `process_location` | map from as-is/to-be process stage to the allowed values | no clear match |
| `affected_role` | register Actors / Roles for the pain | unclear |
| `failure_example` | brief "Concrete instance cited" if present | usually ask |
| `root_cause` | customer-understanding as-is process, tagged `INFERRED` if reasoned | unsupported |
| `evaluation_trigger` | brief "Outstanding / Unresolved" or constraints if stated | not stated |
| `prior_attempts` | brief/register mentions of workarounds or past tools | not stated |
| `priority_flag` | brief "Explicit Constraints / Must-Haves" => `must-solve` | not stated |

The required fields and the must-solve rule above still apply unchanged to derived values:
a must-solve pain with empty `quantified_impact` or `failure_example` halts. Present derived
values to the engineer for confirmation before Phase 1.

## Halting behavior

When any of the above checks fail:

1. Do not generate any demo content.
2. List every missing or insufficient field/pain in one message (not one round-trip per field).
3. Wait for the engineer to supply the missing information before re-attempting Phase 0.

When all checks pass, proceed to Phase 1 (`references/org-introspection.md`) using the
validated Customer Brief and Customer Detailed Case as input to Phase 2
(`references/customer-model.md`) and Phase 3 (`references/gap-analysis.md`).
