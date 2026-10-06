# Contract: MCP tools exposed to the LLM

No tool returns a token, secret, or grant code. All outputs pass redaction. Inputs validated with zod.

| Tool | Writes to org? | Input | Output |
|---|---|---|---|
| `validate_plan` | no | plan path, handoff path | intake-gate result: pass or named failures |
| `check_target` | no (read) | profile | match/mismatch per attribute |
| `discover` | no (read) | none | reconciliation report |
| `list_steps` | no | none | steps with state |
| `confirm_reconciliation` | no (records an unsigned local record) | `report_hash` | refused unless it equals the current non-halted reconciliation report's hash; unlocks the build-profile `auth init` |
| `read_request` | no (GET only) | `request{method:GET,path,query?}`, `required_scope` | redacted JSON; guarded; no confirmation needed |
| `preview_step` | no | `step_id`, `request{method,path,query?,body?}`, `required_scope`, `exists_check?`, `verify?` | method, path, query, required scope, the body exactly as sent (only token-shaped values and loaded secrets are scrubbed; credential-named keys are refused by the guard), the `exists_check` and `verify` requests in full, and `request_hash`; the executor stores it as the latest preview for the step (an edited re-preview invalidates the older hash). Writes only (POST/PUT/PATCH) |
| `execute_step` | **yes** | `step_id`, `request_hash` | applies **only if** `request_hash` equals the hash the preview computed for the current request (recomputed at execution); else refused with reason. The engineer's chat "yes" precedes the call |
| `verify_step` | no (read) | `step_id` | re-runs the previewed `verify` GET; executor evaluates it |
| `skip_step` | no (records SKIPPED) | `step_id`, `reason` | marks SKIPPED(user); dependents become blocked |
| `record_manual_step` | no (records MANUAL-DONE in the local ledger) | `step_id`, `attestation` | refused for api steps, an empty attestation, a step that already has a final state, or a dependency that is FAILED, SKIPPED, or has no final state; attestation is redacted |
| `propose_upgrades` | no | none | writes `api-upgrade-proposals.md` to the run dir (step, route, scope, doc page or `[UNVERIFIED]`, risk, status) plus planner `build_method` corrections; executes nothing |
| `record_upgrade_decision` | no (records a decision file beside the ledger) | `step_id`, `decision` (`proposed`/`accepted`/`rejected`) | rewrites the proposals file; executes nothing; an accepted step is still built via `preview_step`, chat confirmation, `execute_step` |
| `generate_reports` | no (local files; read-only org re-read) | `plan_path`, `handoff_path`, `out_dir` (inside the project) | writes `run-ledger.jsonl`, `execution-report.md`, `manual-steps-checklist.md`, `api-upgrade-proposals.md`, `rollback-checklist.md`; the final fidelity diff re-reads the org through the read-only discover profile; returns counts, and an error if counts do not sum to the plan's step count |

`exists_check` = `{request:{method:GET,path,query?}, required_scope, match:{json_pointer, equals|exists}}`: if it matches, the step is marked DONE with no write. `verify` = `{request, required_scope, expect:[{json_pointer, equals|exists}]}`; a mismatch records FAILED(validation). Both are included in the request hash and evaluated by the executor, not the model. A `*` JSON-pointer segment matches any array element. Without `verify` the result is recorded DONE-UNVERIFIED.

Rules: no tool takes a URL, header, or token (host is the build profile's api_domain); only plan-named or approved discovery operations are callable
(endpoint allowlist). `execute_step` is never pre-allowlisted in the agent runtime (always ask).
There is no delete tool and no tool or command that approves a step; the confirmation is given in chat. Confirmation is given in chat and is prompt-level; accepted for internal demo/sandbox orgs only.
