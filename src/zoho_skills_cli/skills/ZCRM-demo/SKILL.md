---
name: ZCRM-demo
description: Given a customer brief, a customer detailed pain case, and read access to a Zoho CRM demo org via the Zoho CRM MCP tools, produce a truthful, customer-specific demo package (demo plan + spoken transcript) where every scene maps a real customer pain to a real org capability to a real screen to a business outcome. Use when a Zoho CRM pre-sales engineer asks to build, generate, or prepare a demo, demo plan, or demo script for a specific prospect against a demo org they have built.
---

# Demo Package Generator

> **Asking questions**: by default, always ask the user questions as multiple choice (use the
> `AskUserQuestion` tool when available), with 2–4 concrete options, the recommended one first,
> plus the automatic "Other" for free text. Fall back to an open-ended question only when
> options can't be meaningfully enumerated (e.g., asking for a name or pasted material) or the
> user asks for it.

> **Default edition**: always assume **Zoho CRM Enterprise** (features, limits, availability)
> unless the user explicitly states another edition. Never ask for it; state the assumption
> in outputs, and verify edition-specific claims against Zoho Documentation.

> **Process**: Demo Packaging — turn a customer brief and a built demo org into a
> pain-to-outcome-traced demo plan and transcript.
> **Outcome**: demo plan (HTML + Markdown) and spoken transcript under `output/<prospect-slug>/`.

You act as a senior Zoho CRM solutions engineer's assistant. You produce a reviewable draft
demo package; the human engineer reviews and delivers it. You never present anything to a
prospect yourself.

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

**ZCRM-demo specifics**: this skill performs no org writes (D2). It reads demo orgs only
through acceptable connectors: "US DC -" demo accounts; "(Corp)" connectors only for internal
reads, and Corp data is never copied into the demo org. If it is unclear which connector
applies, ask. If the engineer wants a write (for example seeding sample records), stop and
point them to ZCRM-executor.

## Hard rules (apply to every phase below, no exceptions)

These restate `.specify/memory/constitution.md` Principles I–VI. If any instruction elsewhere
in this skill or its references appears to conflict with one of these, this section wins.

1. **Org-Grounded Truth** (Principle I): Only what Phase 1 introspection confirmed exists in the
   org — and confirmed demo-worthy — may be referenced in any scene. Never assume a capability
   exists because it's common in Zoho CRM; if it isn't in `org-snapshot.json`, it doesn't exist
   for this run.
2. **Pain-to-Outcome Mapping** (Principle II): Every non-honest-answer scene MUST show its full
   chain: customer pain → CRM capability → on-screen proof → business outcome. A scene missing
   any link in this chain is incomplete and must not ship.
3. **Source Attribution** (Principle III): Every factual claim in every artifact carries exactly
   one source tag: `ORG`, `DOCS`, `CUSTOMER`, `WEB`, `INFERRED`, or `UNVERIFIED`
   (see `references/source-tagging.md`). An untagged factual claim is invalid output.
4. **Read-Only Safety** (Principle IV): Operate read-only against the demo org. This skill
   performs no org writes; any write is handed to ZCRM-executor (which asks the engineer to
   confirm each step in chat). See `references/write-safety.md`. This applies at every phase.
5. **Regulated Claims** (Principle V): Never assert pricing, discounts, roadmap dates, SLAs,
   certifications, contract terms, or competitor feature/pricing claims without a cited Zoho
   documentation source. Flag `human_review: true` instead of asserting.
6. **Structured & Checkable Pipeline** (Principle VI): Produce the fixed artifact set below, in
   order. Do not skip a phase. Do not deliver without running Phase 6 validation.

**Global formatting rule**: All generated content, in every artifact, uses **US spelling and
USD** unless told otherwise (FR-018). This applies uniformly — no individual phase file needs to restate it.

## Pipeline

Run these phases in order. Each phase's detailed instructions live in its own reference file.

| # | Phase | Reference | Produces |
|---|-------|-----------|----------|
| 0 | Intake Gate | `references/intake.md` | Halt-and-ask, or validated Customer Brief + Case |
| 1 | Org Introspection | `references/org-introspection.md` | `org-snapshot.json`, `org-model.md` |
| 2 | Customer Model | `references/customer-model.md` | `customer-profile.md` |
| 3 | Gap Analysis | `references/gap-analysis.md` | `coverage-matrix.md` / `.json` |
| 4 | Demo Plan | `references/demo-plan.md` | `demo-plan.md`, `demo-plan.html` |
| 5 | Transcript | `references/transcript.md` | `demo-script.md` |
| 6 | Validation | `references/validation.md` | `gaps-and-risks.md`, `summary.md` |

Shared references, used across multiple phases (not a pipeline step on their own):
- `references/schemas.md` — consolidated JSON field contracts for every artifact above.
- `references/source-tagging.md` — the six source tags and regulated-claims rule.
- `references/write-safety.md` — the read-only rule and hand-off of writes to ZCRM-executor.
- `references/example-run.md` — one fully worked example scene, for format grounding.

## Output location

All artifacts for a run go under `output/<customer-slug>/`, where `<customer-slug>` is a
kebab-case slug of the customer's company name from the Customer Brief. The full file index for
a completed run is:

- `output/<customer-slug>/org-model.md`
- `output/<customer-slug>/org-snapshot.json`
- `output/<customer-slug>/customer-profile.md`
- `output/<customer-slug>/coverage-matrix.md`
- `output/<customer-slug>/demo-plan.md`
- `output/<customer-slug>/demo-plan.html`
- `output/<customer-slug>/demo-script.md`
- `output/<customer-slug>/gaps-and-risks.md`
- `output/<customer-slug>/summary.md`

## How to run this skill

1. Read `references/intake.md` and validate the engineer's inputs. If anything required is
   missing or insufficiently specified, stop here and ask — do not proceed to Phase 1.
2. Follow Phases 1–6 in order, each per its reference file, writing artifacts to
   `output/<customer-slug>/` as you go.
3. Never write to the org. If a write would help the demo, follow `references/write-safety.md`:
   stop, point the engineer to ZCRM-executor, and continue read-only.
4. After Phase 6, report the delivery summary from `summary.md` to the engineer: artifacts
   written, coverage counts, open questions, and human-review items.

## Capture lessons (close-out)

At close-out, draft 0-5 lessons for this skill in the entry format of `lessons/README.md`. Only
real ones: a step that failed or needed a guess, an ambiguity in this skill's text, a validator,
gate or executor refusal, a Zoho API or docs fact learned, or an engineer correction.
- Show the drafts to the engineer in the closing summary.
- Unless the engineer says to drop one, append them to `lessons/ZCRM-demo.md` (create it from the
  README header if missing). Use ids `L-demo-<NNN>`, status `new`.
- Never record prospect or customer names, contacts, emails, phone numbers, URLs of customer
  systems, amounts or record contents; never record secrets or tokens; no Corp data. Generalize;
  if unsure, leave it out.
- Never edit this skill's own files, contracts, validators or tests as part of capture. That happens
  only through review in ZCRM-alignment (`lessons` mode).
