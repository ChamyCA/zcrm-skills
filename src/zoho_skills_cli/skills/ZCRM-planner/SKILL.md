---
name: ZCRM-planner
description: Given a validated Zoho CRM design package (the handoff YAML produced by ZCRM-design), think step by step through the build order and produce a single, credential-free Markdown implementation plan that a later Claude Code session can execute via the Zoho CRM API, discovery-first and with explicit per-step write confirmation. Use when a pre-sales engineer has a validated design package for a prospect and wants a plan to actually build it in a real demo org.
---

# Customization Implementation Plan Generator

> **Asking questions**: by default, always ask the user questions as multiple choice (use the
> `AskUserQuestion` tool when available), with 2–4 concrete options, the recommended one first,
> plus the automatic "Other" for free text. Fall back to an open-ended question only when
> options can't be meaningfully enumerated (e.g., asking for a name or pasted material) or the
> user asks for it.

> **Default edition**: always assume **Zoho CRM Enterprise** (features, limits, availability)
> unless the user explicitly states another edition. Never ask for it; state the assumption
> in outputs, and verify edition-specific claims against Zoho Documentation.

## Safety rules (shared across all ZCRM skills)

1. **No writes without confirmation.** Never create, change, send, post or delete anything in a
   Zoho org or external system without showing the exact action and getting the engineer's
   explicit confirmation for that action. Writes to an org are made only through ZCRM-executor,
   which shows the exact preview and request hash and executes only after the engineer confirms
   that step in chat. (D2)
2. **No secrets.** Never ask for, accept, store or repeat a client secret, grant code, token or
   password. If one appears in chat, do not use or repeat it and tell the engineer to revoke it.
   Never write one into any output file.
3. **Connectors.** "(Corp)" connectors hold internal data; "US DC -" connectors are demo test
   accounts, used only to configure a customer demo and never presented as real data. Never copy
   Corp data into a demo org unless the engineer confirms it is cleared. If unclear which
   applies, ask.
4. **Regulated claims.** Do not state pricing, discounts, roadmap dates, SLAs, certifications,
   contract terms, or competitor features/pricing unless a cited Zoho source confirms them.
   Flag them `[HUMAN REVIEW]` (`human_review: true` in structured files).
5. **Grounding.** Zoho product facts come from the Zoho-Documentation connector with the page
   cited; company facts from zoho-canon. Otherwise label the claim `[UNVERIFIED]`.
6. **Source tags.** Every factual claim carries one tag from the shared vocabulary
   (`ORG`, `DOCS`, `CUSTOMER`, `WEB`, `INFERRED`, `UNVERIFIED`; discovery adds its answer tags
   and `PROSPECT-DOC`). (D5)
7. **Style.** US spelling and USD unless told otherwise. Default edition is Zoho CRM Enterprise;
   state the assumption, never ask for it.
8. **Higher-risk work** (legal, privacy, security, financial, personnel, production, deletion):
   state uncertainty, verify against authoritative sources, flag `[HUMAN REVIEW]`.

> **Process**: Implementation Planning — turn a validated design package into an executable,
> credential-free build sequence.
> **Outcome**: `output/<prospect-slug>/14-implementation-plan.md`, ready to hand to a separate
> Claude Code session with a live API token, for Demo Packaging (`ZCRM-demo`) afterward.

## What this skill does, and does not, do

This skill reads one input file and writes one output file. It never calls any Zoho CRM API
itself and never touches a live org (spec Assumptions). It is the bridge between a design
package (what to build) and a build (how a *separate* Claude Code session, run later, with its
own token, actually builds it).

- **Input**: `output/<prospect-slug>/12-handoff-spec.yaml`, produced by the upstream
  `ZCRM-design` skill, matching
  `specs/004-crm-data-model-customizer/contracts/handoff-spec.schema.md`.
- **Output**: `output/<prospect-slug>/14-implementation-plan.md`, matching
  `specs/006-customization-implementation-plan/contracts/implementation-plan.schema.md` and
  built from `templates/implementation-plan.md`.

If asked to call a CRM API, create/modify/delete anything in a real org, or skip straight to
"just build it," decline and explain this skill only produces the plan file — a separate
Claude Code execution session, given this plan and a live token, does the building.

---

## Step 0 — Input validation gate (spec FR-001, FR-002)

Before anything else:

1. Read `output/<prospect-slug>/12-handoff-spec.yaml`.
2. Confirm `validation.blocking_failure_count == 0`. If it is missing, non-zero, or the
   `validation` block is absent entirely: **refuse**. Report exactly which check is
   failing/missing and stop — do not generate a partial plan.
3. Confirm every one of these top-level arrays is present (each may be empty, but the key must
   exist): `modules`, `pipelines`, `blueprints`, `automation_rules`, `personas`. If any is
   missing: **refuse** and name the missing array(s).
4. Only once both checks pass, proceed to Step 1.

This mirrors the upstream skill's own gating discipline — never guess past a missing
precondition.

---

## Step 1 — Decompose into Build Steps (spec FR-003, FR-011, FR-012)

Walk the handoff spec and emit exactly one Build Step per design element, using this ID scheme
for `design_element_ref`. In the plan file this is written as the step field **Design package
reference** (`design_element_ref`) and as the `Step N:` heading text; the executor parser reads
that exact label. IDs are stable, derived directly from the handoff YAML, never invented (standard
modules and standard fields, `is_standard: true`, need no `module:` / `field:` row and no create
step; the executor gate checks this both ways, C-05):

| Element | `design_element_ref` format |
|---|---|
| Module | `module:<api_name>` |
| Field | `module:<module_api_name>.field:<field_api_name>` |
| Relationship | `module:<module_api_name>.relationship:<target_module>` |
| Pipeline stage | `pipeline:<pipeline_name>.stage:<stage_name>` |
| Blueprint transition | `blueprint:<module>.transition:<from>-><to>` |
| Automation rule | `automation:<rule_id>` |
| Persona dashboard | `persona:<persona_name>` |

Every Build Step has: `step_number`, `design_element_ref`, `build_method`, `operation`,
`required_scope`, `depends_on[]`, and (for mutating `api` steps) a `confirmation_instruction`
— per the Build Step entity in `specs/006-customization-implementation-plan/data-model.md` (if
present; the shipped implementation-plan contract above is authoritative).

**No element may be skipped and no step may reference an element absent from the handoff
spec** — this is checked explicitly in Step 5 (Traceability).

---

## Step 2 — Determine build method per element (spec FR-013; research.md §5)

Map each element type to a `build_method` based on the actual Zoho CRM tool surface available
in this environment (the Zoho CRM MCP tools). Do not assume an API exists where none is listed
here — an incorrect `api` tag is worse than an honest `manual` tag, because it sends the
executor toward a call that doesn't exist.

When the plan is run by ZCRM-executor, `api` steps are composed and run as guarded, confirmed
requests, and `manual` steps go to its manual-steps checklist and are recorded with an
attestation. After a run, the executor's `api-upgrade-proposals.md` lists the `manual` steps a
Zoho API could do (route, scope, doc page or `[UNVERIFIED]`); use it to correct this table.
Only routes with a cited Zoho documentation page may be moved from `manual` to `api`.

| Element type | `build_method` | Why |
|---|---|---|
| Module (new custom module) | `api` | The Create Custom Module API (`POST /settings/modules`, scope `ZohoCRM.settings.modules.CREATE`) exists. `[DOCS]` [Create Custom Module](https://www.zoho.com/crm/developer/docs/api/v8/create-custom-module-api.html). |
| Field (custom field on a module) | `api` | `createFields` creates custom fields on a module. `[DOCS]` [Create Custom Fields](https://www.zoho.com/crm/developer/docs/api/v8/create-custom-field.html). A field with `is_standard: true` gets NO `createFields` step (see below). |
| Relationship (lookup field) | `api` | A lookup relationship is created as a field via `createFields` with a lookup field type. If the same lookup is also declared as a field, there is ONE `createFields` step (see below). |
| Pipeline / stage | `manual` | No stage-definition tool is exposed; pipeline stages are configured via Setup, not the available API surface. |
| Blueprint / transition | `manual` | No Blueprint read/write tool is exposed in this environment's tool surface. |
| Automation rule | `manual` | No workflow/automation-rule read/write tool is exposed in this environment's tool surface. |
| Persona dashboard | `manual` | No dashboard/home-page tool is exposed in this environment's tool surface. |

**Standard fields and duplicate lookups (hard rules).**
- A field with `is_standard: true` (default `false`) already exists in Zoho CRM: emit NO
  `createFields` step for it. Emit at most a read-only verification step (`.READ` scope only, no
  STOP line) or none. Its Traceability row is optional (the executor gate allows but does not
  require it); omit the row unless you emit a verification step, in which case the row cites
  that step and is `yes`.
- A lookup declared both as a field (`type: lookup`) and as a relationship
  (`lookup_field_api_name`) is ONE lookup: emit ONE `createFields` step, on the field's
  `design_element_ref`. The relationship's Traceability row is still required (C-05) and cites
  that same step number (or a read-only verification of that lookup); never create it twice.
- `[DOCS]` module creation is listed `api` above only because the Zoho API docs name the
  endpoint; the module-create step still needs the narrowest scope and a STOP line (Step 8).

If a future environment exposes additional tools (e.g., a Blueprint API), update this table —
do not silently start tagging those elements `api` without a corresponding row here naming the
tool.

Every `manual` step still gets a full Build Step entry (Step 1) for traceability (spec
FR-012); it is additionally listed in the `Manual Steps Summary` (Step 6).

---

## Step 3 — Order steps by dependency (spec FR-004; contract invariant C-06)

Sequence steps so that:
1. All `module` steps come before any `field`/`relationship` step on that module.
2. All `field`/`relationship` steps come before any `pipeline`, `blueprint`, `automation`, or
   `persona` step that references that field by API name.
3. Within the fixed section order required by the template: Modules → Fields → Relationships →
   Pipelines → Blueprints → Automation Rules → Dashboards.

A step's `depends_on` list may only contain step numbers strictly less than its own
`step_number`. If a true circular dependency exists in the handoff spec itself (should be
impossible — the upstream skill's own validation forbids orphan/dangling references), refuse
and report it rather than emitting an invalid plan.

---

## Step 4 — Discovery and Reconciliation (spec FR-006, FR-007; research.md §3; contract C-02)

Generate `Phase 1: Discovery` and `Phase 2: Reconciliation` using only read-level Zoho CRM MCP
tools, before any Phase 3+ step, structurally fixed by the template:

| What to discover | Tool(s) |
|---|---|
| Existing modules | `getModules` |
| Existing fields per module | `getFields` |
| Existing layouts | `getLayouts`, `getLayoutById` |
| Existing related lists / relationships | `getRelatedLists` |

There is no read tool in this environment's surface for pipelines-as-stage-metadata,
blueprints, or automation rules directly; for those, instruct the executor to use `getFields`
on the relevant module to inspect the stage/status picklist values actually configured (this is
how pipeline stages and blueprint states surface in the CRM data model), and note in the
Reconciliation instructions that full blueprint/automation-rule state can only be confirmed
manually in the Zoho CRM Setup UI — call this out explicitly rather than silently treating it
as discovered.

For every discovered element, instruct the executor (per the template's Phase 2 text) to
compare it against the design package's assumption and STOP on any mismatch before touching
that element in Phase 3+.

---

## Step 5 — Traceability (spec FR-011, FR-012; contract C-04, C-05)

Build the `Traceability` table with exactly one row per element ID from the handoff spec
(`modules[].api_name` and nested `fields[]`/`relationships[]`, `pipelines[].stages[]`,
`blueprints[].transitions[]`, `automation_rules[].rule_id`, `personas[].persona`; rows for
`is_standard: true` modules and fields are optional), each row's
`Step Number(s)` pointing to the Build Step(s) from Step 1, and `Covered?` set to `yes` for
`api`-method steps or `manual` for `manual`-method steps. Never leave a row blank or `no`.

Cross-check in both directions before finalizing: every handoff-spec element has a row, and
every Build Step's `design_element_ref` resolves to a real row.

---

## Step 6 — Manual Steps Summary (spec FR-013; research.md §5)

If, and only if, at least one Build Step has `build_method: manual`, include the `Manual Steps
Summary` section (per the template's conditional block) listing each such step's number,
`design_element_ref`, and a one-line reason (reuse the "Why" column from Step 2's table).
Omit the section entirely if every step is `api`.

---

## Step 7 — Prerequisites and credential safety (spec FR-008, FR-009, FR-010, FR-010a)

Fill `Prerequisites`:
1. List the union of every `api`-method step's `required_scope`, deduplicated.
2. Include the literal sentence from the template: "This file contains no credentials. Before
   proceeding, request a live API token with the scopes above from the engineer running this
   plan."
3. Never write a token, secret, or any credential-shaped value anywhere in the generated file.
   Before finalizing output, scan your own draft for anything that looks like a credential
   (long hex/base64 strings, `token:`/`secret:` followed by a value) and remove it — this
   should never occur since no credential is ever an input to this skill, but it is checked as
   a hard gate anyway (contract invariant C-01).

For every `api`-method mutating Build Step, state its `required_scope` directly on the step
(Step 1), not only in the aggregate Prerequisites list.

**Least-privilege scopes (hard rule).** Name the narrowest scope that permits the operation, never a
broader one: creating a custom field needs `ZohoCRM.settings.fields.CREATE`, creating a custom module
`ZohoCRM.settings.modules.CREATE`, and read-back or verification checks only `ZohoCRM.settings.<resource>.READ`
(per the Zoho CRM API docs: each create API lists `.CREATE` as sufficient). Never emit `.ALL` or `.DELETE`
unless no narrower scope can do the job, and then say why on the step and mark it `[HUMAN REVIEW]`. The CRM
Build Executor refuses a plan whose build profile would need `.ALL` unless the engineer accepts it, so an
over-broad scope here makes the plan harder to execute and widens the token.

---

## Step 8 — Per-step write confirmation (spec FR-010a; constitution Principle IV; contract C-03)

Every Build Step whose `build_method` is `api` and whose operation mutates org state (i.e.,
every `api` step in Phase 3+ that writes — read-only discovery in Phase 1 is exempt, and so is
any step whose `required_scope` lists only `.READ` scopes, such as a read-back or verification
check) MUST end with the literal line. Do not add the line to read-only check steps: the executor
runs those without a per-step approval, and a STOP line on a read only creates needless prompts:

> STOP — ask the engineer for explicit confirmation before executing this step.

Keep that line exactly as written (the executor's intake gate compares it character for
character). When the plan is run by ZCRM-executor, the line means the executor shows the exact
preview and request hash for that step and runs it only after the engineer confirms that step in
chat; one confirmation per write, never a blanket "yes".

This appears **individually on every such step** — never as one blanket "approve this whole
plan" statement at the top of Phase 3+. A plan that gates all writes behind a single up-front
approval is non-compliant and must be corrected before being presented as finished (this repo's
constitution, Principle IV: Read-Only Safety — no batch or implicit write approval).

If, at execution time, the engineer's supplied token lacks a scope a step requires, instruct
the executor (via this same per-step text, reused at execution time) to stop and report the
missing scope rather than attempt a workaround or a different, unscoped call (spec FR-010,
Acceptance Scenario 3).

---

## Step 9 — Write the plan file

Render all of the above into `templates/implementation-plan.md`'s structure and save as
`output/<prospect-slug>/14-implementation-plan.md`. This MUST be the only file this skill
writes.

---

## Re-run behavior (spec FR-014; research.md §7)

Each invocation regenerates the plan fresh from the current `12-handoff-spec.yaml` and
overwrites any existing `14-implementation-plan.md` at the same path. There is no diff/merge
against a prior plan version — the handoff YAML, not the plan file, is the durable source of
truth. If the engineer has made manual notes directly in a previous plan file, warn them before
overwriting that re-running will discard those notes.

---

## Final summary

At the end of any run, report: total Build Step count, count by `build_method` (api vs.
manual), the required-scope list, and whether a Manual Steps Summary was included.

---

## Functional Requirements traceability (spec.md FR-001–FR-014, FR-010a)

| Requirement | Where addressed above |
|---|---|
| FR-001 | Step 0 |
| FR-002 | Step 0 |
| FR-003 | Step 1 |
| FR-004 | Step 3 |
| FR-005 (single Markdown file) | Step 9 — one output path, one file |
| FR-006 | Step 4 |
| FR-007 | Step 4 |
| FR-008 | Step 7 |
| FR-009 | Step 7 |
| FR-010 | Step 7, Step 8 |
| FR-010a | Step 8 |
| FR-011 | Step 1, Step 5 |
| FR-012 | Step 1, Step 5 |
| FR-013 | Step 2, Step 6 |
| FR-014 | Re-run behavior |

No gaps identified between this skill's instructions and spec.md's Functional Requirements.

## Capture lessons (close-out)

At close-out, draft 0-5 lessons for this skill in the entry format of `lessons/README.md`. Only
real ones: a step that failed or needed a guess, an ambiguity in this skill's text, a validator,
gate or executor refusal, a Zoho API or docs fact learned, or an engineer correction.
- Show the drafts to the engineer in the closing summary.
- Unless the engineer says to drop one, append them to `lessons/ZCRM-planner.md` (create it from the
  README header if missing). Use ids `L-planner-<NNN>`, status `new`.
- Never record prospect or customer names, contacts, emails, phone numbers, URLs of customer
  systems, amounts or record contents; never record secrets or tokens; no Corp data. Generalize;
  if unsure, leave it out.
- Never edit this skill's own files, contracts, validators or tests as part of capture. That happens
  only through review in ZCRM-alignment (`lessons` mode).
