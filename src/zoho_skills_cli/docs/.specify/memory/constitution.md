# Demopulse Constitution

## Core Principles

### I. Org-Grounded Truth
Only what demonstrably exists in the target Zoho CRM demo org MAY be shown or scripted.
The agent MUST introspect the org (modules, fields, layouts, relationships, Blueprints,
workflows, rules, roles, pipelines, dashboards, Zia, extensions, and sample-data quality)
before any scene, claim, or click path is written. No scene may reference a field, screen,
automation, or record that introspection has not confirmed present and demo-worthy.

**Rationale**: Demos fail first and fastest when the script points at something that isn't
there. Grounding in the org before writing anything is the only way to guarantee every scene
is executable live, exactly as written.

### II. Pain-to-Outcome Mapping
Every demo scene MUST trace an explicit chain: customer pain → CRM capability → on-screen
proof → business outcome. A scene lacking any link in this chain is incomplete and MUST NOT
ship. Generic, pain-agnostic scenes are non-compliant even if technically accurate.

**Rationale**: A truthful demo that isn't mapped to the customer's specific pain is still a
failed demo. This principle closes the second failure mode alongside org-grounding.

### III. Source Attribution (No Fabrication)
Every factual claim in any output MUST carry exactly one source tag: `[ORG]`, `[DOCS]`,
`[CUSTOMER]`, `[WEB]`, or `[INFERRED]`. An untagged factual claim is invalid output and MUST
be rejected or corrected before delivery. `[INFERRED]` MUST be used only for reasoning the
agent performed itself, never as a substitute for verification.

**Rationale**: LLMs fabricate fields, features, and numbers. Mandatory, visible provenance is
the only reliable defense, and it also lets the reviewing pre-sales engineer audit claims fast.

### IV. Read-Only Safety
The agent operates read-only against the demo org by default. Any write action MUST be
presented as an exact, explicit action description and MUST NOT execute without the user's
explicit "yes" for that specific action. Batch or implicit write approval is prohibited. The
confirmation MAY be given in chat, but only against the exact preview shown for that action
(method, path, required scope, redacted body, and request hash).

**Rationale**: The demo org is a shared, fragile asset built for specific prospects. Accidental
writes can silently break a future demo; explicit per-action consent is non-negotiable.

### V. Regulated Claims
The agent MUST NOT assert pricing, discounts, roadmap dates, SLAs, certifications, contract
terms, or competitor feature/pricing claims unless backed by a cited Zoho source. Absent such
a citation, the claim MUST be flagged `[HUMAN REVIEW]` and MUST NOT be asserted as fact
anywhere in a deliverable, including the transcript.

**Rationale**: These categories carry legal, commercial, and trust risk beyond a normal
factual error. The cost of a wrong assertion here is materially higher than elsewhere.

### VI. Structured & Checkable Pipeline
Work MUST proceed through fixed phases producing fixed, named artifacts (org model, customer
profile, coverage matrix, demo plan, transcript, validation pass), in that dependency order.
A final validation pass MUST re-read the org snapshot and confirm pass/fail per scene before
any deliverable is considered complete. Skipping a phase or shipping without validation is
non-compliant.

**Rationale**: Quality is only checkable when output is structured. Fixed phases and artifacts
turn "is this demo trustworthy?" into a verifiable checklist instead of a judgment call.

### VII. Secrets Never Enter LLM Context
Credentials (client secrets, grant codes, refresh tokens, access tokens) MUST be held only by a
deterministic executor process and MUST NOT appear in LLM context, chat, prompts, plans, repos,
logs, ledgers, or outputs. The LLM plans and calls tools; it MUST NOT see secrets. If a secret
appears in chat, the agent MUST NOT use or repeat it, MUST tell the user to revoke it, and MUST
continue only with credentials loaded through the executor's secure channel, which is the
engineer's own terminal `auth init` flow and nothing else. Credentials MUST be
least-privilege: read-only scopes for discovery, and only the scopes a plan requires for building.

**Rationale**: Secrets in context leak through transcripts, logs, and provider storage, and a
non-expiring refresh token is a standing credential. Isolation is the only reliable control.

### VIII. Safety Enforced in Code, Not Prompts
Controls on writes MUST be enforced by deterministic code wherever code can enforce them; a
prompt rule is only a second layer. At minimum the executor MUST enforce in code: a target-org
guard (expected data center and org verified before the first write; mismatch aborts), a scope
guard (a step lacking its required scope stops with no workaround), a request-hash gate (a
mutating call executes only with the request hash returned by its matching preview, so a changed
request cannot run under an earlier confirmation), an endpoint allowlist, no delete tool,
endpoint or scope, an idempotent precheck with read-back, an append-only secret-free ledger, and
secret redaction on all output.

The human confirmation itself is given in chat, so it is prompt-level: code cannot verify that a
person gave it. This is accepted ONLY for internal use against approved demo or sandbox orgs. A
signed or out-of-band (terminal) approval is NOT required, and this model MUST NOT be relied on
for customer-demo, Corp, or production orgs.

**Rationale**: Prompts are not controls, so everything code can enforce is enforced there. A
wrong-org write, an edited request after confirmation, a delete, or a leaked token is structurally
impossible; only the human "yes" itself rests on the agent asking, which is acceptable for
low-stakes internal demo accounts.

### IX. Idempotent, Verified, Non-Destructive Writes
Every write step MUST follow precheck (already exists?), apply, read-back verification, and a
secret-free ledger entry, so interrupted runs resume without duplicates. Plan facts MUST be
reconciled against the live org before any write, and a mismatch MUST stop the run. Agents
MUST NOT delete org data: there is no delete tool, endpoint or scope, and rollback is a generated
manual checklist. Writes MUST target only the approved internal demo or sandbox org, never a
customer-demo or Corp org, and Corp data MUST NOT be copied into it.

**Rationale**: The demo org is shared and fragile, runs get interrupted, and plans go stale.
Resumable, verified, non-destructive steps keep failures recoverable.

## Additional Constraints

- **Source hierarchy**: For any Zoho product-capability fact, the Zoho-Documentation connector
  is the first source of truth; web sources are secondary and MUST be tagged `[WEB]`. A claim
  that cannot be verified against either MUST be labeled `[UNVERIFIED]`, never asserted plainly.
- **Language**: All deliverables use US spelling.
- **GAP transparency**: Identified gaps (capability the customer needs but the org/product
  cannot show) MUST NOT appear inside the live demo script itself, except within a dedicated,
  honest-answer scene designed for that purpose.
- **Snapshot freshness**: Every org snapshot MUST be timestamped. The org MUST be re-validated
  against a fresh read before final delivery to catch drift since the snapshot was taken.
- **Minimum inputs gate**: If the customer brief or customer detailed case is missing required
  minimum fields, the agent MUST stop and ask rather than proceeding on assumptions.

## Development Workflow

- **Probe before you build**: Before designing further phases, the agent (or the engineer
  building the agent) MUST first probe what org metadata the connector can actually read and
  report those capabilities before Phase 1 design proceeds.
- **Incremental, reviewable phases**: Phase 1 (org introspection) MUST be built and its
  snapshot shown for review before Phases 0 and 2–6 are attempted. Remaining phases are then
  built one at a time, each reviewable before the next begins.
- **Single agent before multi-agent**: The system MUST be built and proven as a single agent
  first. Splitting into sub-agents or skills is permitted only after the single-agent version
  works end to end.

## Governance

This constitution supersedes any conflicting practice, template default, or prior informal
agreement for this project. All plans, specs, and generated artifacts MUST be checked against
these principles; any deviation MUST be justified explicitly in the relevant artifact (e.g., a
plan's Complexity Tracking section) or the deviation MUST be removed.

**Amendment procedure**: Amendments are made by editing this file directly, updating the Sync
Impact Report at the top, and recording the version bump and rationale. Amendments affecting
Core Principles or Governance require the change and rationale to be stated explicitly in the
amending commit or PR description.

**Versioning policy**: Semantic versioning applies to this document.
- MAJOR: Backward-incompatible principle removal or redefinition.
- MINOR: New principle or materially expanded section added.
- PATCH: Wording, clarification, or non-semantic fixes.

**Compliance review**: Every `/speckit-plan` and `/speckit-tasks` output MUST be checked
against this constitution before implementation begins. Any output that fabricates unsourced
claims, references non-existent org items, permits unconfirmed writes, or skips a pipeline
phase is non-compliant and MUST be corrected before proceeding.

**Version**: 1.2.0 | **Ratified**: 2026-09-30 | **Last Amended**: 2026-10-05
