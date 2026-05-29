# Changelog

## v0.1.4

- Add explicit support for alternative model backends (GLM, DeepSeek, Qwen, Kimi, Doubao, etc.) accessible via proxy or Anthropic-protocol-compatible endpoint with Claude Code, or directly via OpenAI-compatible API with Codex.
- Add `## Alternative Model Backends` section with supported configurations, connection method table, task packet declaration format, and degradation rule.
- Clarify protocol distinction throughout: Claude Code uses the Anthropic API protocol; Codex uses the OpenAI API protocol. Alternative models connect to Claude Code via proxy (One API, LiteLLM, etc.) and to Codex natively.
- Update skill description, tags, Overview, When to Use, Core Principle #4, Select Participants, and Claude Code harness adapter to reflect alternative backend support.
- Add two example prompts for alternative backend arena sessions.

## v0.1.3

- Rewrite `agent-arena` skill description to use user-intent trigger phrases ("second opinion", "independent review", "red-team", "Codex-vs-Claude debate") instead of implementation terminology, improving LLM-based skill auto-triggering.
- Add "What it produces" section to README with a concrete Codex-vs-Claude example output showing independent analysis, cross-critique, synthesis, and preserved dissent.
- Improve README opening to lead with the result ("get a real second opinion") rather than the mechanism.
- Add natural-language trigger guidance to the Claude Code install section.
- Add unhyphenated and conversational trigger variants to description: "red team", "sanity check", "review my plan", "challenge this design".
- Fix README demo example: remove unsupported `~10k req/s` threshold, add DynamoDB global table consistency caveat, label output as condensed illustration.

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
