# Contract: Handoff Package (`12-handoff-spec.yaml`)

This is the one external interface this feature exposes: a machine-readable artifact that a
separate, downstream demo-building agent (in its own repository) consumes as input. This agent
is only responsible for producing a package that satisfies this contract — it has no knowledge
of, and no dependency on, how the downstream agent is implemented.

## Format

YAML, UTF-8, single file per engagement: `output/<prospect-slug>/12-handoff-spec.yaml`.

## Top-level shape

```yaml
package_version: "1.0.0"          # semver of this contract shape, not the engagement
prospect_slug: "acme-logistics"
generated_at: "2026-10-01T00:00:00Z"
source_register_version: "3"       # ties this package to the inputs it was built from

modules:                           # list of DesignModelElement grouped by module
  - api_name: "Import_Dossiers"
    is_standard: false
    req_ids: ["REQ-003", "REQ-011"]
    fields:
      - api_name: "Domiciliation_Date"
        type: "date"
        req_ids: ["REQ-011"]
      - api_name: "PPI_Limit"
        type: "currency"
        req_ids: ["REQ-012"]
      - api_name: "Stage"              # state-driving picklist: `values` is mandatory
        type: "picklist"
        values: ["Domiciliation", "Customs_Clearance"]
        req_ids: ["REQ-011"]
      - api_name: "Owner"              # standard field: is_standard true (default false)
        is_standard: true
        type: "ownerlookup"
        req_ids: ["REQ-015"]
    relationships:
      - target_module: "Accounts"
        lookup_field_api_name: "Account_Name"
        cardinality: "many_to_one"
        req_ids: ["REQ-004"]

pipelines:
  - name: "Import Operations"
    stages:
      - name: "Domiciliation"
        probability: 10
        forecast_category: "pipeline"
        entry_criteria: "..."
        exit_criteria: "..."
        required_fields: ["Import_Dossiers.Domiciliation_Date"]
        req_ids: ["REQ-011"]

blueprints:
  - module: "Deals"
    states: ["New", "Qualified", "..."]
    transitions:
      - from: "New"
        to: "Qualified"
        mandatory_fields: ["Deals.Industry"]
        validations: []
        approvals: []
        req_ids: ["REQ-009"]

automation_rules:
  - rule_id: "WF-001"
    type: "workflow"
    trigger: "..."
    condition: "..."
    action: "..."
    reads_fields: ["Deals.Stage"]
    writes_fields: ["Deals.Owner"]
    req_ids: ["REQ-015"]

personas:
  - persona: "Sales Manager"
    goals: "..."
    kpis:
      - name: "Pipeline Coverage"
        formula: "sum(Deals.Amount where Stage != Closed) / Quota"
        source_fields: ["Deals.Amount", "Deals.Stage"]
        req_ids: ["REQ-020"]

traceability_summary:
  total_requirements: 42
  covered: 38
  partial: 2
  gap: 2
  deferred: 0

validation:
  run_id: "VAL-004"
  blocking_failure_count: 0
  checks:
    - name: "no_orphan_elements"
      pass: true

erd_source: "04a-erd-overview.mmd"
erd_content_hash: "sha256:..."
```

## Field rules

- **`type`** is exactly one of these 19 tokens (the list in `templates/handoff-spec.yaml`, equal to
  `yaml_to_mermaid.TYPE_TOKENS`; `validate_package.py` imports that same set): `string`, `text`,
  `int`, `decimal`, `currency`, `boolean`, `date`, `datetime`, `picklist`, `multipicklist`,
  `email`, `phone`, `url`, `lookup`, `ownerlookup`, `formula`, `autonumber`, `file`, `subform`.
- **`values`** (list of strings) is allowed on `picklist` and `multipicklist` fields. It is
  mandatory on a state-driving picklist: the field behind a blueprint's states and `Deals.Stage`
  behind pipeline stages. Every blueprint state / pipeline stage must appear in it.
- **`is_standard`** (`true|false`, default `false`) marks a field as a standard Zoho field
  (e.g. `Deals.Stage`, `Deals.Owner`) as opposed to a custom one. It is not an exemption from
  declaration: a standard field must still be declared in its module's `fields`.
- **`writes_fields` / `reads_fields`** in `automation_rules` may name standard fields (e.g.
  `Deals.Owner`), but each such field must be declared in the module's `fields` with
  `is_standard: true`, so writer-conflict and loop checks can see it. Undeclared names fail.
- A lookup is declared both as a field (typed `lookup`/`ownerlookup`) and as a relationship
  (`lookup_field_api_name`); these describe one lookup, not two.

## Required top-level keys

`package_version`, `prospect_slug`, `generated_at`, `source_register_version`, `modules`,
`pipelines`, `blueprints`, `automation_rules`, `personas`, `traceability_summary`, `validation`,
`erd_source`, `erd_content_hash`. Arrays may be empty but must exist. `erd_content_hash` is a
required key, but a mismatch with the recomputed value is a warning, not a failure.

## Blueprint documents

One Markdown file per `blueprints` entry: `06-blueprint-leads.md`, `07-blueprint-deals.md`, and
`07a-blueprint-<module-slug>.md` for any other module, where module-slug is the lower-case
`api_name` with underscores replaced by hyphens (e.g. `07a-blueprint-import-dossiers.md`).

## Contract guarantees (what the downstream agent may rely on)

1. `validation.blocking_failure_count` is always `0` in a delivered package — a package is
   never emitted while blocking validation failures remain (spec FR-015).
2. Every `req_ids` list, on every element at every level, is non-empty (spec FR-006; zero
   orphan elements).
3. Every `api_name`, `target_module`, `required_fields`, `mandatory_fields`,
   `reads_fields`/`writes_fields`, and `source_fields` reference resolves to something defined
   elsewhere in the same file — no dangling references.
4. `erd_content_hash` changes whenever the modules/fields/relationships section changes,
   letting the downstream agent detect a stale diagram (idea-doc §6, Phase 10).
5. Fields not yet verified against Zoho documentation are never silently omitted from this
   contract — they appear in `data-model` output with an `[UNVERIFIED]` tag surfaced in the
   human-readable sibling document; this machine file only includes elements that passed
   validation.

## Non-goals of this contract

- This file does not include pricing, SLAs, or competitor claims (constitution Principle V) —
  those never appear in any deliverable without a citation, and the schema has no field for
  them.
- This file does not instruct the downstream agent on *how* to build a demo; it only describes
  *what exists* in the design. Demo narrative, scene sequencing, and talk tracks are entirely
  the downstream agent's responsibility.
- This agent does not call or depend on the downstream agent's API/interface in any way; the
  relationship is one-directional (produce a file matching this contract) and asynchronous.
