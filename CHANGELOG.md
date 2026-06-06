# Changelog

## v0.2.1

- **Fix: the v0.2.0 error_max_turns rule lived only in the SKILL.md body, so Codex never applied it.** Codex loads only a skill's one-line `description` into context, not the body — so the new "lossless retry / STOP-and-ask before lossy moves" rule was invisible to it. Real recurrence: Codex hit error_max_turns, then auto-retried by telling the reviewer to **stop using tools and answer directly** — exactly the LOSSY move v0.2.0 said requires user approval (disabling the reviewer's tools damages heterogeneous independence), done without asking. Now the hard rule is embedded in the `description` itself: on error_max_turns → mode-check first, auto-retry ONCE with lossless moves only, and disabling tools / feeding excerpts / narrowing scope are LOSSY → never automatic, STOP and ask the user. (Same fix pattern as agent-completion-gate v0.4.3.) Single-quoted, 1009/1024 chars, single-line, YAML-valid.


## v0.2.0

- **Fix: `error_max_turns` handling — mode-first diagnosis + lossless/lossy escalation rule.** Root cause traced from a real session (castmind eval ops, 2026-06-05): an open design/architecture question was mis-boxed as bounded verification, producing `stop_reason: tool_use` + no answer at `--max-turns 2` then `4`. Old rule ("retry with higher cap, narrower scope, or no-tools summary") was backwards — narrowing or disabling tools damages independent judgment, the core thing arena protects. New rule, arena-reviewed (two Codex heterogeneous rounds):
  - **Mode-first** (`FIRST decide the review MODE`): open design/architecture tasks REQUIRE broad read-only access (`Read,Glob,Grep,Bash`-readonly) + ample turns; narrowing is both contamination (orchestrator picks evidence) and starvation (reviewer can't form independent judgment). Bounded verification is the only mode where the read/analyze split and narrow tools are correct.
  - **Auto-retry with lossless moves only**: resume session, raise `--max-turns`, inject turn-budget contract into prompt ("you have N turns; judge disputes only; avoid exploration"), or add soft prompt hints about likely files (keeps `Read,Glob,Grep` broad — this is lossless). Dropping `Glob,Grep` is only safe when the evidence set is provably closed.
  - **Human gate for lossy moves**: disabling `Read`, hard CLI scope narrowing (`--add-dir`/`--allowedTools` create hard walls the reviewer cannot expand), fixed excerpts the reviewer cannot go beyond, or accepting a no-critique degraded result — these are the user's tradeoff, not the orchestrator's to make silently.
  - Updated line 428 (Codex quick-ref) to match. Fixed old line 145 which listed "narrower scope" as a default retry option.

## v0.1.9

- Add Common Mistake #10 — **reviewing from a summary instead of the raw file**. Format / structure / spec-compliance problems (frontmatter, schema, config, exact YAML) live in the precise text, so a summary-fed reviewer is blind to them; give the reviewer the actual file for those checks. Captures the lesson from v0.1.8: the skill's own frontmatter stayed off-spec through many summary-fed Codex reviews until one file-reading review caught it.

## v0.1.8

- **Spec-compliant frontmatter.** Move `version` and `author` under `metadata` (`version` as a quoted string), convert `metadata.tags`/`related_skills` from YAML arrays to comma-separated strings, and drop the nested `metadata.hermes` block. The [agentskills spec](https://agentskills.io/specification) defines `metadata` as a string→string map with no top-level `version`/`author` field, so the previous frontmatter was off-spec (parsers tolerated it). Caught by a cross-environment Codex review that read the actual file against the spec — earlier summary-fed reviews never saw the frontmatter and missed it. (Note: this is unrelated to the withdrawn 0.1.8/0.1.9 timeout experiments, which were reverted; the version number is reused.)

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
