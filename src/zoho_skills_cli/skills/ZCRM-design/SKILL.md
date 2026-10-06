---
name: ZCRM-design
description: Given discovery material about a prospect (calls, notes, emails, documents, website, web research), produce a traceable, validated Zoho CRM design package (data model, pipelines, blueprints, automation, persona dashboards) for a pre-sales engineer, ready to hand off to a downstream demo-building agent. Use when a Zoho CRM pre-sales engineer asks to design, customize, or model a CRM solution for a specific prospect before any demo org is built.
---

# CRM Data Model Customizer

> **Asking questions**: by default, always ask the user questions as multiple choice (use the
> `AskUserQuestion` tool when available), with 2–4 concrete options, the recommended one first,
> plus the automatic "Other" for free text. Fall back to an open-ended question only when
> options can't be meaningfully enumerated (e.g., asking for a name or pasted material) or the
> user asks for it.

> **Default edition**: always assume **Zoho CRM Enterprise** (features, limits, availability)
> unless the user explicitly states another edition. Never ask for it; state the assumption
> in outputs, and verify edition-specific claims against Zoho Documentation.

> **Process**: CRM Design — turn discovery material into a traceable, validated Zoho CRM
> design package.
> **Outcome**: `output/<prospect-slug>/12-handoff-spec.yaml` plus the full design package,
> ready for Implementation Planning (`ZCRM-planner`).

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

## Read-only safety boundary (spec FR-018)

**This skill never writes to any live CRM organization.** Every phase below (0 through 9)
produces only Markdown/YAML documents under `output/<prospect-slug>/`. There is no "apply to
org" capability in this skill — that is explicitly out of scope for this version (see spec.md
Assumptions). If a user asks this skill to create/modify/delete anything in a real CRM org,
decline and explain that this skill only produces a design package.

## Overview

Pipeline: `Intake → Extraction → Synthesis/Gap-Interview → Data Model → Pipelines →
Blueprints → Automation → Personas → Validation → Handoff`.

Each phase writes one or more documents to `output/<prospect-slug>/`, using the templates in
`templates/`. Every later phase reads only the documents already written by earlier phases —
never invents facts the evidence doesn't support (spec FR-001–FR-003).

All documents share a header: prospect name, version, date, source-register version, status
(spec FR-023).

---

## Phase 0 — Intake & Source Register

**Input**: every file/transcript/email/document/website excerpt the engineer provides, plus
permission to crawl the prospect's public website and run public web research unless the
engineer restricts it (spec Assumptions).

**Steps**:
0. If `output/<prospect-slug>/customer-brief.md` exists (produced by `ZCRM-discovery`), include it
   as an input: register it as a `document` source and keep its origin tags (`[CUSTOMER]`,
   `[SUGGESTED-ACCEPTED]`, `[WEB]`, `[PROSPECT-DOC]`, `[INFERRED]`, etc.). Only the five coverage
   sections count as confirmed; "Unconfirmed Findings" and "Outstanding / Unresolved" entries
   are not requirements and go to `03-open-questions.md`. Source register row for the brief:
   `date` = the brief's `Date` header if present, otherwise today's date; `reliability` = `M`
   unless the brief itself marks a different level. Map the brief's origin tags to requirement
   tags: `[CUSTOMER]` stays `CUSTOMER`; `[SUGGESTED-ACCEPTED]` becomes `CUSTOMER` (the customer
   accepted the option); `[SUGGESTED-REJECTED]` and `[UNDECIDED-DELEGATED]` are not
   requirements (record as open questions); `[PROSPECT-DOC]` is an unconfirmed finding from a
   prospect-supplied document, not a requirement, until the customer confirms it (then
   `CUSTOMER`). Read the brief for the gate (step 3): industry = the `**Industry:**` bullet;
   top pains = the `**Pain:**` bullets; sales process = Business Process & Stages; user roles =
   Roles & People. If those are present with confirmed tags, that gate input counts as present;
   an Outstanding "Industry not provided" / "No pains reported" bullet means it is missing.
1. Inventory every input. For each, create a row in `00-source-register.md` (copy
   `templates/source-register.md`) with a stable `SRC-###` ID, `type`
   (call_transcript/email/document/website/web_research), `date`, `reliability` (H/M/L — your
   judgment of how authoritative this *kind* of source is, independent of recency), and
   `language`.
2. Confidentiality guard (spec FR-021): before issuing any web search/crawl call, strip the
   prospect's name, contact names, and any other identifying detail from the outbound query.
   Scope queries to public company/industry facts only (research.md §5).
3. Check the **blocking-inputs gate**: industry, top pains, sales process description, user
   roles (for a discovery brief, read them as described in step 0). (Target edition is not a blocking input: default to **Zoho CRM Enterprise** unless the
   engineer explicitly states another edition, and record the assumption in the source register.) If any of these cannot be determined from the inputs
   so far, do not guess — record each missing one as a `blocking` row in
   `03-open-questions.md` (Phase 2's template, created here if needed). **The whole pipeline
   halts before Phase 1** while any blocking row is unanswered; present the blocking questions
   to the engineer. Record every missing item in the same pass (do not stop at the first), and
   still record non-blocking items as open questions. Proceed only once the engineer answers
   the blocking rows. Phase 2 step 4 applies the same rule to blocking rows raised later.

**Output**: `00-source-register.md`.

---

## Phase 1 — Extraction

**Input**: `00-source-register.md`, raw inputs.

**Steps**:
1. For every requirement (explicit or clearly implied) found in the inputs, create a row in
   `01-requirements-register.md` (copy `templates/requirements-register.md`) with:
   - A stable, sequential `REQ-###` ID (never reused across a re-run — research.md §4).
   - `statement`, `type` (functional/process/data/report/integration/compliance).
   - `source_id` (→ `00-source-register.md`) and a **verbatim** `quote` — both required, no
     exceptions (spec FR-002; data-model.md > Requirement validation).
   - `tag` — exactly one of `CUSTOMER`, `DOCS`, `WEB`, `ORG`, `INFERRED` (spec FR-003). An
     untagged factual claim anywhere in any document you produce — not just here — is invalid
     output; carry this discipline into every later phase too.
   - `confidence` (H/M/L) and `priority` (high/medium/low).
   - **Rule**: a row tagged `INFERRED` must never also be `confidence = H` — inference is
     never high-confidence fact (data-model.md > Requirement validation).
2. Also extract and append to the same document: a glossary of customer terms, actors/roles,
   entities and their lifecycles, volumes, existing systems/integrations mentioned, and ranked
   pains/KPIs.

**Output**: `01-requirements-register.md` (spec FR-002).

---

## Phase 2 — Synthesis & Gap Interview

**Input**: `01-requirements-register.md`.

**Steps**:
1. Write `02-customer-understanding.md` (copy `templates/customer-understanding.md`):
   business model, as-is vs. to-be process, entity lifecycles, stakeholders, and a
   terminology map (customer term → Zoho object/field equivalent).
2. **Precedence rule for conflicts** (spec Assumptions; research.md §/spec Assumptions): when
   two sources disagree, the default order is: most recent direct customer statement
   (call/email) > customer-supplied documents > the prospect's own public website > third-party
   web research > the agent's own inference. Apply this to decide which statement is the
   current truth — **but every conflict you detect, including ones resolved by this rule, MUST
   be recorded as a row in `03-open-questions.md`** (copy `templates/open-questions.md`),
   never silently dropped (spec FR-004). Mark conflict rows as `NON-BLOCKING` with the
   resolution explained, unless the conflict itself blocks a later phase.
3. Marketing-copy guard: treat a prospect website's aspirational claims (e.g., "zero missed
   deadlines", "fully automated") as `WEB`-tagged marketing language, never as a confirmed
   as-is process, unless a call or document independently confirms the same claim.
4. **Blocking halt** (spec FR-005; data-model.md > OpenQuestion validation): same rule as
   Phase 0 step 3, the whole pipeline halts (not just the affected item). If any `BLOCKING`
   row in `03-open-questions.md` has no `resolution` yet, **stop here**. Present the engineer
   with the exact blocking question list from `03-open-questions.md` and wait. Do not proceed
   to Phase 3 until every blocking row is resolved.

**Output**: `02-customer-understanding.md`, `03-open-questions.md` (spec FR-004, FR-005).

---

## Phase 3 — Data Model

**Precondition**: zero unresolved `blocking` rows in `03-open-questions.md`.

**Input**: `01-requirements-register.md`, `02-customer-understanding.md`.

**Steps**:
1. Initialize this engagement's copy of `templates/handoff-spec.yaml` (the canonical model)
   with `prospect_slug`, `source_register_version`, `generated_at` filled in.
2. For every requirement needing a data element, decide the module/field placement:
   - **Prefer standard Zoho modules/fields.** Only introduce a custom module or field when no
     standard element can reasonably satisfy the same requirement(s) (spec FR-007;
     data-model.md > DesignModelElement validation: `is_standard = false` is only valid when no
     standard element satisfies the same `req_ids`).
   - Custom module only when the entity has its own lifecycle, ownership, or permissions
     distinct from existing modules, or represents a genuine many-to-many relationship that
     needs its own data (plan.md decision rules) — not just because a field doesn't fit neatly
     elsewhere.
   - Every module/field/relationship entry in the YAML **must** carry a non-empty `req_ids`
     list (spec FR-006, SC-002 — zero orphan elements). Never add an element "just in case."
   - Field type is one of the 19 tokens in `templates/handoff-spec.yaml`. Mark standard Zoho
     fields (e.g. `Deals.Stage`, `Deals.Owner`) with `is_standard: true` (default `false`);
     they must still be declared, including any standard field an automation rule reads or
     writes. Every state-driving picklist (a blueprint's state field, `Deals.Stage`) must carry
     a `values` list containing every state/stage. A lookup is declared as one field plus one
     relationship entry (the same lookup, not two).
3. **Capability verification** (spec FR-008): for any claim about what Zoho CRM can do, its
   limits, or edition availability, verify it against an authoritative Zoho Documentation
   source and cite it. If you cannot verify it, label it `[UNVERIFIED]` in the written
   document — never assert a capability, limit, or edition restriction from memory.
4. Write `04-data-model.md`: a field-level table per module (module, field, type, standard or
   custom, `req_ids`, notes/decision log), citing every capability claim per step 3.
5. Generate diagrams from the YAML, never by hand:
   - `python3 scripts/yaml_to_mermaid.py <engagement>.yaml 04a-erd-overview.mmd` (keys +
     relationships only, all modules).
   - For each domain with >~12 entities in the overview, generate a focused diagram:
     `python3 scripts/yaml_to_mermaid.py <engagement>.yaml 04b-erd-<domain>.mmd --domain
     <domain>`.
   - Embed both as fenced ` ```mermaid ` blocks inside `04-data-model.md` (spec FR-009 — the
     document and diagrams must never disagree, because the diagrams are generated from the
     same YAML the document describes, not hand-drawn).
6. Cardinality mapping when writing module relationships into the YAML (idea-doc Mermaid
   rules, carried through by the generator):
   - Lookup field on child → `many_to_one`.
   - Multi-select lookup → `many_to_many` (model a junction module if the relationship itself
     carries data).
   - Subform → `subform`, labeled `subform:<name>` (child has no independent lifecycle).
   - Self-reference (e.g., parent account) → relationship with `target_module` equal to its
     own module.

**Output**: `04-data-model.md`, `04a-erd-overview.mmd`, `04b-erd-<domain>.mmd` (spec FR-006,
FR-007, FR-008, FR-009).

---

## Phase 4 — Pipelines

**Input**: `04-data-model.md` + YAML.

**Steps**: For each pipeline the prospect needs (default: one, unless requirements call for
more — spec Assumptions), define stages in the YAML `pipelines` section and in
`05-pipelines.md`: `name`, `probability`, `forecast_category`, `entry_criteria`,
`exit_criteria`, `required_fields` (must already exist in the Phase 3 data model —
data-model.md > PipelineStage validation), and `req_ids` (non-empty).

**Output**: `05-pipelines.md` (spec FR-010).

---

## Phase 5 — Blueprints

**Input**: `04-data-model.md` + YAML.

**Steps**: Write one blueprint file per module that has a lifecycle a requirement needs
governed (Leads, Deals, or any other module, standard or custom). Do not create a Leads
blueprint file when no requirement calls for one. File names: `06-blueprint-leads.md`,
`07-blueprint-deals.md`, and `07a-blueprint-<module-slug>.md` (e.g.
`07a-blueprint-import-dossiers.md`) for any other module; one `blueprints` entry per file in
the YAML. For each state and transition: `mandatory_fields` (must resolve to existing data-model elements), `validations`,
`approvals`, `time_rules`, and `req_ids` (non-empty). Every state must map to an actual field
value in the data model (data-model.md > BlueprintState/Transition validation). Include a
Mermaid state diagram per blueprint, generated the same disciplined way as Phase 3's ER
diagrams (hand-drawn-but-reference-checked is acceptable here since state diagrams are not
produced by `yaml_to_mermaid.py`; cross-check every state/field name against the YAML before
finalizing).

**Output**: the blueprint files above (`06-`/`07-`/`07a-…`) (spec FR-011).

---

## Phase 6 — Automation

**Input**: `04-data-model.md`, `05-pipelines.md`, blueprints.

**Steps**: Write `08-automation.md` with workflow and assignment rules: `trigger`,
`condition`, `action`, `reads_fields`, `writes_fields`, `req_ids` (non-empty). After drafting
all rules, scan for conflicts: flag any two rules that both write the same field, and flag any
trigger→action chain that could re-trigger itself (a loop) (spec FR-012; data-model.md >
AutomationRule validation).

**Output**: `08-automation.md` (spec FR-012).

---

## Phase 7 — Personas & Home Pages

**Input**: `02-customer-understanding.md` (roles discovered), `04-data-model.md`.

**Steps**: Select personas from the roles actually discovered during discovery — not a fixed
universal list — and confirm the selection with the engineer (spec Assumptions). For each
persona, write goals, daily decisions, dashboard layout, reports, and KPIs into
`09-personas-homepages.md`. **Every KPI's `source_fields` must resolve to an existing
data-model element** (data-model.md > PersonaHomePage validation, spec FR-013). If a KPI the
prospect wants cannot be computed from the current data model, either add the missing field in
the Phase 3 model (and keep it REQ-ID-justified) or drop the KPI — never leave an unsupported
KPI in the document.

**Output**: `09-personas-homepages.md` (spec FR-013).

---

## Phase 8 — Validation (mandatory gate before handoff)

**Input**: all documents produced so far.

**Steps**: Run every check below and record pass/fail for each as a `ValidationRun` with a
`blocking_failure_count`:
1. No orphan design elements — every module/field/relationship/stage/state/rule/KPI has a
   non-empty `req_ids`.
2. Every field/module/stage/value referenced anywhere (blueprint, automation, dashboard)
   exists in `04-data-model.md` with a matching type.
3. Every stage/state/picklist value used anywhere matches its canonical definition.
4. Every requirement in `01-requirements-register.md` is either covered, partial, a gap (with
   rationale), or deferred — write this mapping into `10-traceability-matrix.md` (spec
   FR-016).
5. Every `[DOCS]`-tagged claim has a citation; every `[UNVERIFIED]` claim is listed.
6. **Every factual claim across *all* produced documents — not only the requirements register
   and data-model capability claims — carries one of `[CUSTOMER]`/`[DOCS]`/`[WEB]`/`[ORG]`/
   `[INFERRED]`** (spec FR-003). Scan `02-customer-understanding.md`,
   `09-personas-homepages.md`, and the automation/blueprint documents too, not just Phases 1
   and 3.
7. Naming conventions (labels, API names, terminology map) are consistent across all
   documents.
8. Every `.mmd` file renders without error (`npx -p @mermaid-js/mermaid-cli mmdc -i file.mmd -o
   out.svg`).
9. Every entity in the diagrams exists as a module in the YAML, and vice versa; every
   attribute in the diagrams matches the YAML with the same API name and type token; the
   overview diagram's entity set equals the union of the per-domain diagrams' entity sets.
10. No entity or attribute lacks a `req_ids` comment, except explicitly-listed system fields.

**Mechanical vs manual.** Run `python3 scripts/validate_package.py <engagement>.yaml` first.
- *Mechanical, blocking (script exits 1)*: check 1 for YAML elements; the five required
  top-level arrays exist (`modules`, `pipelines`, `blueprints`, `automation_rules`,
  `personas`); unique module api_names and unique field api_names per module; every field
  `type` is a token from `templates/handoff-spec.yaml` (part of check 2); `module.field`
  references in required/mandatory/reads/writes/source fields; relationship target modules;
  `many_to_one` `lookup_field_api_name` declared on the owning module and typed
  `lookup`/`ownerlookup`; `Module.Field` tokens in rule trigger/condition/action, KPI formulas
  and stage criteria (an undeclared module or an undeclared field both fail); blueprint
  transition `from`/`to` are in that blueprint's `states`; blueprint modules declare a
  stage/status picklist field, pipelines require `Deals.Stage` declared, and that state-driving
  field must declare `values` containing every blueprint state / pipeline stage (missing
  `values` fails); all 13 required top-level keys exist; field `is_standard` is a boolean and
  `values` a list of strings. A standard field (`is_standard: true`) must still be declared:
  rules naming an undeclared standard field (e.g. `Deals.Owner`) fail.
- *Mechanical, WARN only (review each)*: two rules writing the same field, a rule reading and
  writing the same field (loop risk), `erd_content_hash` mismatch (the key is required, the
  mismatch only warns), sibling `.md` files citing
  `Module.Field` that the YAML does not declare.
- *Manual (not checked by the script)*: check 2 (other than field type tokens and the
  references above), 3 (beyond the above), 4–10 (for check 9, `yaml_to_mermaid.py` now emits
  each field's real `type` token, plus `PK` on the module's name field and `FK` on relationship
  lookup fields; compare against the YAML on name and type), stale
  or resolved open questions in `03-open-questions.md`, and whether a field cited as "defined in"
  a doc is actually defined there.

**If any check fails**: fix the underlying document, don't suppress the failure, and re-run
validation. **Do not proceed to Phase 9 while `blocking_failure_count > 0`** (spec FR-014,
FR-015; data-model.md > ValidationRun).

**Output**: `10-traceability-matrix.md`, a `ValidationRun` record (spec FR-014, FR-015,
FR-016).

---

## Phase 9 — Handoff

**Precondition**: the latest `ValidationRun.blocking_failure_count == 0`.

**Steps**:
1. Write `11-assumptions-risks-review.md`: every assumption made, every `[INFERRED]` item,
   every `[HUMAN REVIEW]`-flagged item (see the regulated-claims guard below), and known risks.
2. Finalize the engagement's YAML as `12-handoff-spec.yaml`, matching
   `specs/004-crm-data-model-customizer/contracts/handoff-spec.schema.md` exactly: `modules`,
   `pipelines`, `blueprints`, `automation_rules`, `personas`, `traceability_summary`,
   `validation`, `erd_source` (path to the overview `.mmd`), and `erd_content_hash` (all required
   top-level keys, plus `package_version`, `prospect_slug`, `generated_at`,
   `source_register_version`; blueprint files are named `06-blueprint-leads.md`,
   `07-blueprint-deals.md`, `07a-blueprint-<module-slug>.md`; hash of
   the modules section: `"sha256:" + sha256(json.dumps({"modules": modules}, sort_keys=True,
   separators=(",", ":"), ensure_ascii=False))`, i.e. `compute_erd_hash` in
   `scripts/validate_package.py`; recompute after any module edit)
   (spec FR-017; data-model.md > HandoffPackage).
3. Print the final summary (see "Final summary" below).

**Output**: `11-assumptions-risks-review.md`, `12-handoff-spec.yaml` (spec FR-015, FR-017).

This is the single artifact a separate, downstream demo-building agent consumes. This skill
has no knowledge of and no dependency on that agent's internals — see the contract's
"Non-goals" section.

---

## Regulated-claims guard (applies across Phases 4–9)

Any pricing, discount, roadmap date, SLA, certification, contract term, or competitor claim
**must not** be asserted in any document unless backed by a cited authoritative source. If you
cannot cite one, flag it `[HUMAN REVIEW]` in the document (`human_review: true` in structured files) instead
of stating it as fact (spec FR-020). Competitor features/pricing are included.

## Incremental re-run behavior

When the engineer supplies new or corrected inputs after an initial run: diff the new inputs
against `00-source-register.md`, add new `SRC-###`/`REQ-###` entries rather than renumbering
existing ones, update only the documents actually affected by the change, and append a dated
changelog entry at the top of each updated document describing what changed and why. Never
discard prior, still-valid work and start over (spec FR-022, SC-007).

## Final summary

At the end of any run (full or incremental), report: files written, requirement counts by
status (covered/partial/gap/deferred), remaining blocking questions (should be zero at
handoff), and counts of `[UNVERIFIED]` and `[HUMAN REVIEW]` items.

## Capture lessons (close-out)

At close-out, draft 0-5 lessons for this skill in the entry format of `lessons/README.md`. Only
real ones: a step that failed or needed a guess, an ambiguity in this skill's text, a validator,
gate or executor refusal, a Zoho API or docs fact learned, or an engineer correction.
- Show the drafts to the engineer in the closing summary.
- Unless the engineer says to drop one, append them to `lessons/ZCRM-design.md` (create it from the
  README header if missing). Use ids `L-design-<NNN>`, status `new`.
- Never record prospect or customer names, contacts, emails, phone numbers, URLs of customer
  systems, amounts or record contents; never record secrets or tokens; no Corp data. Generalize;
  if unsure, leave it out.
- Never edit this skill's own files, contracts, validators or tests as part of capture. That happens
  only through review in ZCRM-alignment (`lessons` mode).
