# Changelog

## v0.1.2

- Clarify Claude Code print-mode `--max-turns` counts tool interaction turns, so Read/Glob/Grep exploration can exhaust low caps before a final answer.
- Add retry guidance for `error_max_turns`: raise the cap, narrow the approved scope, or pass a no-tools local summary instead of treating it as a substantive arena answer.

## v0.1.1

- Clarify Codex should discover Claude Code through the external `claude` CLI before falling back to same-model subagents.
- Add context-minimization-without-blindness guidance: external agents may read relevant source/docs/tests within the approved repo scope.
- Add multi-round cross-critique requirements for non-trivial arenas instead of one-shot heterogeneous review.
- Add `collaborative_design` mode so Codex and Claude Code can co-design architectures, interfaces, experiments, and implementation plans instead of only acting as reviewer/checker.
- Document sensitive-scope exclusions for secrets, datasets, generated results, private logs, and unrelated directories.

## v0.1.0

- Initial preview release of `agent-arena` and `deliberative-analysis`.
- Added portable skill folders for Claude Code, Codex, Hermes Agent, OpenClaw/OpenCode-compatible agents, and custom instruction workflows.
- Added safety/privacy boundaries, degraded-mode guidance, mode list consistency, portable license files, and Codex/OpenAI skill metadata.
