#!/usr/bin/env node
// PreToolUse hook (matcher: Bash). Blocks commands that could reach the executor's secrets or
// run the human-only auth commands (credential entry). Exit code 2 blocks the call; the stderr text is shown to Claude.
// Fails closed: if the input cannot be parsed, the call is blocked.
// Limits: text matching cannot catch deliberately obfuscated commands (e.g. a path built from
// string pieces); the sandbox filesystem deny is the layer that covers those.

import { readFileSync } from "node:fs";

// A command word: start of text, or right after a separator, quote, subshell opener, or a "/".
// Optional leading VAR=value assignments are skipped, and the word must end at whitespace, a quote,
// a separator, or end of text.
const B = String.raw`(?:^|[;&|(\x60"'\n]|\$\(|/)\s*(?:\w+=\S*\s+)*`;
const END = String.raw`(?=[\s"'\x60;&|)]|$)`;

const RULES = [
  [/zcrm-exec\s+auth\b/, "human-only zcrm-exec command"],
  [/cli\/index\.js\s+auth\b/, "human-only zcrm-exec command"],
  [/\bcli\.mjs\s+auth\b/, "human-only zcrm-exec command"],
  [/\.config\/zcrm-exec|zcrm-exec[/\\]\S*\.secret/, "executor secret location"],
  [new RegExp(B + String.raw`security\s+[a-z-]`), "macOS keychain tool"],
  [new RegExp(B + String.raw`(?:env|printenv)` + END), "environment dump"],
  [/\bprocess\.env\b|\bos\.environ\b|\/proc\/self\/environ/, "environment access"],
];

export function check(command) {
  for (const [re, why] of RULES) if (re.test(command)) return why;
  return null;
}

function main() {
  let command;
  try {
    const input = JSON.parse(readFileSync(0, "utf8"));
    command = input?.tool_input?.command;
    if (typeof command !== "string") throw new Error("no tool_input.command");
  } catch (e) {
    process.stderr.write(`guard-secrets: cannot parse hook input (${e.message}); blocking.\n`);
    process.exit(2);
  }
  const why = check(command);
  if (why) {
    process.stderr.write(
      `Blocked by guard-secrets (${why}). Human-only commands and the executor's secrets must be ` +
        `used from your own terminal, not through the assistant.\n`,
    );
    process.exit(2);
  }
}

if (import.meta.url === `file://${process.argv[1]}`) main();
