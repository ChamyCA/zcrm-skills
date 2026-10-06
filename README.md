# ZCRM Skills and Executor

Zoho CRM pre-sales skills for Claude Code (/ZCRM-intake, /ZCRM-discovery, /ZCRM-design, /ZCRM-planner,
/ZCRM-executor, /ZCRM-demo) plus a local executor that builds a validated plan in a demo or sandbox org,
one separately confirmed step at a time. The executor is BETA and has only been tested against a mock server.

## Install (one command, run in your project folder)

    uvx --from <install-source> zoho-skills init --here

`<install-source>` is the private repo URL (git+ssh://...) or the wheel file you were given.
The install also drops `ZCRM-guide.html` in your project: open it in a browser for the step-by-step guide.
Add `--dry-run` first to see exactly what will change. It never deletes your existing settings; it merges.

## Prerequisites

- uv (https://docs.astral.sh/uv/) and Node 20 or newer
- A sandbox or demo Zoho org you are allowed to build in
- Claude Code

## Connect to your org (tokens stay in your terminal)

1. `./zcrm-exec doctor` checks the executor and its protections.
2. Create a Zoho Self Client in the API Console, then run `./zcrm-exec scopes --profile discover` for the scopes to grant.
3. In your OWN terminal (not in Claude) run `./zcrm-exec auth init --profile discover --dc <DC>` and answer the hidden prompts.
4. Start Claude Code in the project and run /ZCRM-executor.

Tokens are never typed into the chat.

## Safety model

- Every write is previewed and needs your confirmation in chat, step by step.
- Credentials live only in your terminal and a protected folder the assistant cannot read.
- The executor has no delete operations.
- Internal demo or sandbox orgs only; never a customer or production org.

## Problems

Report issues to `<owner>`.
