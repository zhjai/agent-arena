# Changelog

## v0.2.8

- **Add `supervised_execution` mode.** Arena plans and verifies; the primary agent executes one Arena-authorized step at a time and returns raw evidence; every step is checked, answer-only requests receive a final Arena review, and only `APPROVED: task complete` completes the run. Content, context, tool discovery, turns, step attempts, and elapsed time are unlimited unless the user sets a limit; privacy, redaction, least privilege, irreversible-action human approval, and liveness protections still apply.
- **Identify the execution mode and participants.** State the mode, its purpose, open/bounded scope, and participant models before launch and at close-out; disclose changes and distinguish planned or configured identities from verified execution.
- **Report every Arena outcome explicitly.** Always list successful, failed, and unfinished or unexecuted work, with evidence and observed failure causes. Preserve recovered failures, distinguish unknown causes from hypotheses, and report blocking findings separately from successful review execution.

## v0.2.7

- **Improve Arena invocation ergonomics and continuity.** Add short natural-language triggers, infer the review mode and target, and reserve a bare `继续` for an unfinished Arena checkpoint.
- **Add first-use participant-route setup.** Preflight the default heterogeneous harness, ask once which passing route to remember, persist the project route without credentials, revalidate model-family heterogeneity on each run, and never silently switch providers or model families.
- **Make Arena state explicit.** Persist per-round checkpoints with route metadata, commit-gate state, structured digests, dissent, blocker coverage, and retry accounting. Distinguish resumable mechanical failures from authentication, model-availability, and refusal failures that require user action.
- **Clarify privacy and commit safety.** Route preflight does not authorize project-content transfer; external repository access requires per-run scope approval. Pre-commit reviews must cover all pending changes, and `.arena/` artifacts are ignored by default.
- **Synchronize portable documentation.** Update the English and Chinese READMEs with route setup, continuation, raw-evidence, degraded-mode, and host-local artifact guidance.

## v0.2.6

- **Fix: v0.2.4's root/sudo rule hardcoded `--permission-mode default`, which is a legacy alias already removed from validation once.** Caught by a *candidate lesson* an agent had written on this machine's H100 project back on 2026-07-16 — which had never been promoted to project authority, so the knowledge sat unused in `state/` while this repo shipped the fragile rule anyway. Its claim: "Claude Code 2.1.211 removed the previously used `default` choice… inspect the installed CLI version and supported permission-mode choices; use an explicitly supported read-only mode." Verified on 2.1.222: `--permission-mode` **is** validated (`argument 'bogusmode' is invalid. Allowed choices are acceptEdits, auto, bypassPermissions, manual, dontAsk, plan`), and `default` **still functions but is absent from that list** — a hidden alias one upgrade away from breaking a pinned call site. The rule now says to **preflight `claude --help | grep -A3 -- --permission-mode` and pick an explicitly supported read-only mode (`plan` on current builds)** rather than naming one. The reason for the override is unchanged (a root account defaulting to `bypassPermissions` makes `claude -p` refuse to launch). Cross-reference in the `num_turns: 1–2` fingerprint updated.

## v0.2.5

- **Calibration: recalibrated the `error_max_turns` (Class B) turn budgets and added a retry-delta discriminator.** Arena-reviewed (Claude + Codex, two independent heterogeneous reviewers, one round) against the genuine Class-B failures in the 199-server session: only **17** genuine `error_max_turns` result-objects, all dying at `num_turns` 3 (×12) / 4 (×1) / 5 (×4), **none** at 12/19/20, while successful runs reached `num_turns` 10 and 19. Three evidence-backed changes:
  - **Open-review floor 12 → 20.** A *successful* open review used `num_turns: 19`, so a 12-turn cap would have killed it; 12 is now reserved for narrow "read these 1–3 named files" tasks, and open/self-discovery reviews start at 20 (25 for larger/ambiguous). Both reviewers agreed 12 is unsafe as an open-review floor; noted 20 is near the edge of observed demand, so a convergence contract is required, not optional.
  - **Turn-budget is a lever only with tools.** Made explicit that a no-tools (`--allowedTools ''`) call can never hit `error_max_turns` (it answers in one turn), so raising `--max-turns` on it does nothing — "just crank the number" is wrong for that case; the real decision is mode (which sets tools *and* turns together).
  - **Retry-delta discriminator (raising the budget is a diagnostic, not a ratchet).** Branch the single retry on what the failed call had: no-tools → mode/packet bug, re-issue with tools+20; tools at low cap → ordinary starvation, retry at 20; tools already at ~20 → structural (unbounded task / repo-mapping loop / no convergence contract), do not double — split/inline/final-25-30-with-hard-verdict, then stop and flag. Cap retries at 2; a death at a *higher* `num_turns` after raising is the structural signal; corroborate with per-turn `total_cost_usd` (flat = starved-productive, rising = looping). The mode-first fix itself (v0.2.0–v0.2.1) is unchanged — this only sizes the numbers correctly and adds the stop rule.

## v0.2.4

- **Fix: `claude -p` silently fails to launch under root when the account defaults to `bypassPermissions`.** Same 199-server investigation (`019ef905`): 13× `--dangerously-skip-permissions cannot be used with root/sudo privileges for security reasons`. Root cause: `/root/.claude/settings.json` had `permissions.defaultMode: bypassPermissions`, so `claude -p` resolved to an implicit `--dangerously-skip-permissions`, which the CLI refuses to run as root — a *startup* gate, independent of tools/turns, that masqueraded as review failure. The only invocation that empirically worked (used 146× in that transcript as an ad-hoc workaround) was passing `--permission-mode default` explicitly. Added a preflight rule to the Default Cross-Agent Rule: **under root/sudo, pass an explicit read-only `--permission-mode` at the call site** (correctly scoped to the one call), and never "fix" it with `--dangerously-skip-permissions` (a security regression the CLI is right to block) or by globally editing `defaultMode` on a shared account. Cross-linked from the `num_turns: 1–2` startup-failure fingerprint below. **Superseded in v0.2.6 — do not hardcode `default`; preflight the accepted choices.**
- **Fix: `error_max_turns` was being over-counted and misattributed when auditing how often it happens.** Investigating a real 199-server Codex session (`019ef905`, GEFCom2014 prompt redesign) that "kept hitting arena mechanical errors": the raw string `error_max_turns` appeared **147×**, but this was two measurement traps stacked, not 147 real failures. (1) **The skill's own guidance/frontmatter contains the string** — every arena call carrying the packet re-emits it into the transcript, so grepping the word over-counts; genuine result-object (`subtype":"error_max_turns"` inside a `type":"result"`) occurrences were ~59. (2) Some of those ~59 were **not real Class-B budget misses at all** — reading `num_turns` separates them: a genuine turn-exhaustion shows `num_turns` 3–5+ with discovery tools on (reviewer ran out mid-exploration — the mode-misclass case the doc already covers), whereas `num_turns` 1–2 means it died at *startup* (CLI refused to launch under root+`bypassPermissions`, or a proxy `ECONNRESET`/hang) and merely wears an `error_max_turns` label — fixing turns/tools does nothing for those. Added a **"First confirm it is a genuine `error_max_turns`, and don't over-count it"** block to the SKILL.md diagnosis section (subtype-not-string counting + the `num_turns` fingerprint). The *fix* for genuine Class B (mode-first, read/analyze split, retry-once-lossless) was already fully documented in v0.2.0–v0.2.3 and is unchanged; this release only adds the identify/measure step so the fix is applied to the right failures.

## v0.2.3

- **Fix: arena could blow up the orchestrator's own context and loop forever.** New failure mode, observed in a real 910b Codex session (Time-R1 reproduction, ~7h, 7.6 MB / 3343 records): each `claude -p` review packet was ~15 KB, and with multi-round critique the big prompt + the counterpart's long JSON output got narrated back into Codex's *own* context. That repeatedly tripped auto-compaction; compaction summarized away the arena's mid-flight state (round, verdict-so-far); Codex then re-launched arena from scratch, which re-inflated context, which compacted again — dozens of compactions each followed by a fresh arena call. Added an **"Orchestrator-side context budget"** rule (body + description), hardened over two Codex arena rounds:
  - **Stage the packet out-of-band** (via stdin/file) — inlining a 15 KB `'<packet>'` in the tool call pollutes the transcript even when the *output* is redirected.
  - **Redirect output to a file; read back only a small structured digest** (`recommendation`, `key_disagreements`, `uncertainties`, `what_would_change_mind`, `requested_evidence`) — never `cat` the raw JSON. A free-form "verdict" is too lossy and can drop the minority view this skill exists to preserve (principle #6); the raw file stays the source of truth.
  - **Checkpoint each round to disk** (`round`, `session_id`, raw path, digest) so compaction can't force a re-run — you re-read the checkpoint and resume the *same* arena.
  - Tools-off applies to **bounded** critique only; open design/self-discovery still requires broad read-only tools + ample turns (cross-refs the MODE rule, so this doesn't starve an open review).
  - Large verdicts / many rounds: per-round archive files + a small index; never reread the archive wholesale; start a fresh session carrying only the on-disk checkpoint if the current one is already huge.

## v0.2.2

- **Fix: `deliberative-analysis` triggered too rarely.** Its description was abstract failure-mode jargon only ("risk overconfidence, tunnel vision, premature convergence, shallow A/B framing") — which (a) required the agent to first self-diagnose overconfidence, the very thing an overconfident agent won't notice, and (b) contained zero phrases a user actually says, so intent-matching rarely fired. Rewrote the description around real user utterances ("比较一下 A 和 B", "还有别的方案吗", "方案的利弊/权衡", "compare A vs B vs A+B", "what are the tradeoffs", "is this the right approach") plus checkable self-trigger cues ("you only have A/B/A+B", "options are minor variants", "flip conditions unclear", "one hidden assumption is deciding the answer"). Guarded against over-firing (Codex arena round): positive gate requires non-trivial options / real tradeoffs / commitment risk, and excludes trivial naming/style choices, routine review, and fast-answer requests. 922/1024 chars, single-line, YAML-valid.


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
