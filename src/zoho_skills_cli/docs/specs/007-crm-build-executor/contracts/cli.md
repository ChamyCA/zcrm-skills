# Contract: `zcrm-exec` CLI (run by the engineer in their own terminal)

Never invoked by the LLM. All secret input is hidden-prompt only; no secret via argv, env, or chat. Amended 2026-10-05 (constitution v1.2.0): there is no step-approval command; write confirmation is given in chat (see mcp-tools.md). Confirmation is given in chat and is prompt-level; accepted for internal demo/sandbox orgs only.

| Command | Purpose | Output (never secrets) |
|---|---|---|
| `zcrm-exec doctor` | Check Node, keychain availability, target file, deny-rule hints | pass/fail list |
| `zcrm-exec scopes --profile <discover\|build> --plan <file>` | Print exact scope string to paste into the Self Client | scope string |
| `zcrm-exec auth init --profile <p> --dc <dc>` | Hidden prompts for client id, client secret, grant code; exchange; store refresh token | profile, DC, org id/name, granted scopes |
| `zcrm-exec auth revoke --profile <p>` | Revoke and delete stored credentials | confirmation |
| `zcrm-exec status` | Show ledger summary and step states | counts |

`auth init` and `auth revoke` (the only TTY-enforced commands, because hidden prompts need a TTY) MUST read input from the controlling terminal (`/dev/tty`) and refuse with exit code 2 if none exists. Their input is never accepted via argv, env, or stdin redirection. SUPERSEDED by constitution v1.2.0: the step-approval command and the reconciliation-approval command (and their TTY requirement); reconciliation is confirmed in chat via MCP tool `confirm_reconciliation`.

Exit codes: 0 ok; 1 user declined/validation; 2 guard failure (target, scope); 3 internal.
Rules: `auth init` for `build` is refused until the reconciliation confirmation has been recorded for the run against the current report hash (recorded by the MCP tool `confirm_reconciliation`, not a terminal command).
