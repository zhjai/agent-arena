# Changelog

## v0.1.8

- Add an **endpoint-vs-task probe** to the timeout guidance: on repeated timeouts, first run a trivial call (`codex exec 'reply OK'` / `claude -p 'reply OK'`). Returns in seconds → endpoint is fine, the task is just heavy (shrink / feed excerpts / raise timeout). The trivial call also hangs or shows connection errors (websocket 404, repeated reconnects, base-url errors) → the failure is the endpoint/proxy config, not the task or the timeout; restarting processes won't fix a config-level endpoint fault. Derived from real use where a proxy's websocket `/responses` endpoint returned 404 and masqueraded as task timeouts.

## v0.1.7

- Add `model-unavailable` to the failure taxonomy (Preflight runbook + Arena Limitations template). Reported from real use: a rejected model override (e.g. requesting `gpt-5.2-codex` on an account without access) is distinct from `auth` (authentication is fine) and `refusal` (the model declined to answer).
- Add guidance: do not pin a specific model version unless the account is confirmed to support it; prefer the default model. The standard retry for `model-unavailable` is to drop the override and re-run with the default model.

## v0.1.6

- Add interop hook to the companion skill [`groundcheck`](https://github.com/zhjai/groundcheck): a single-agent, evidence-grounded fact-gate. After independent generation, run groundcheck per answer; `refuted` claims are sent back to their `source_agent` (with evidence, not conclusions) before cross-critique, catching factual errors before debate can reinforce a shared hallucination. Adds groundcheck to `related_skills`. Frames the pair as "two depths of one verification stack": agent-arena (multi-agent debate, overconfidence) + groundcheck (single-agent verification, hallucination).

## v0.1.5

- **Right-size the arena (fix mode under-triage):** principle #8 changed from "use the lightest arena" to "right-size the arena"; Quick Decision Gate gains bidirectional triage with explicit escalation triggers (persistent/irreversible side effects, structure/contract/policy redesign, interdependent decisions, repeating a past mistake, output-becomes-contract) plus a coupling-vs-implementation-detail example. Common Mistake #6 reworded to cover both over- and under-triage. Root cause: the skill previously had three one-directional biases all pushing "go light" and no warning against under-triage.
- **Read/analyze separation as default (reduce error_max_turns):** for bounded critique, Codex supplies raw excerpts and Claude analyzes with no tools; `Read,Glob,Grep` + turn budget is reserved for genuine self-discovery. Added a context-budget protocol — feed raw evidence (paths, line numbers, omission notes), never Codex's conclusions, to protect Claude's independence.
- **Stop over-redacting evidence:** task-relevant artifacts (experiment runs, media, predictions, metrics, generated outputs) are evidence, not noise; excluding them forces inference from code instead of verifying real output.
- **Timing, timeouts, observability:** cross-agent calls take minutes in both directions (measured: single-turn no-tools ~6s, multi-turn repo review 2–5 min); a silent `--output-format json` run is not a hang. Set timeouts to match `--max-turns` (5–10 min, not 1 min), prefer `stream-json` to watch progress, and record `duration_ms`/`num_turns`. Added a preflight runbook and failure classification.
- **Failure handling for users:** Arena Limitations template gains `Failure type` and `Retry recommendation` fields; cross-agent failures must end the user-facing output with whether to retry and the one variable to change, never silently swallowed.

## v0.1.4

- Add explicit support for alternative model backends (GLM, DeepSeek, Qwen, Kimi, Doubao, etc.) accessible via proxy or Anthropic-protocol-compatible endpoint with Claude Code, or directly via OpenAI-compatible API with Codex.
- Add `## Alternative Model Backends` section with supported configurations, connection method table, task packet declaration format, and degradation rule.
- Clarify protocol distinction throughout: Claude Code uses the Anthropic API protocol; Codex uses the OpenAI API protocol. Alternative models connect to Claude Code via proxy (One API, LiteLLM, etc.) and to Codex natively.
- Update skill description, tags, Overview, When to Use, Core Principle #4, Select Participants, and Claude Code harness adapter to reflect alternative backend support.
- Add two example prompts for alternative backend arena sessions.
- Add one-line `npx skills add zhjai/agent-arena` install via the vercel-labs `skills` CLI as the recommended install method; verified the CLI detects both skills from the repo's portable layout. Demote manual per-agent copy instructions to a "Manual install" subsection.
- Replace the SVG banner with a richer infographic-style PNG banner (protocol flow, debate-arena visual, agent ecosystem). Compressed from 1.7 MB to ~250 KB via 256-color quantization at full resolution.

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
