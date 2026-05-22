---
name: agent-arena
description: Use when complex AI agent work needs heterogeneous multi-agent debate, red teaming, evidence checking, judging, or synthesis across Codex, Claude Code, Hermes, OpenClaw, and other coding agents.
version: 1.0.0
author: zhjai
license: MIT
metadata:
  tags:
    - ai-agents
    - multi-agent
    - agent-arena
    - codex
    - claude-code
    - hermes-agent
    - opencode
    - openclaw
    - rag
    - llm-as-judge
    - red-team
---

# Agent Arena

## Overview

Agent Arena is a reusable skill for AI coding agents and LLM agent harnesses. Use it when one agent is likely to be overconfident, trapped in a single framing, or missing evidence.

The core idea: **independent heterogeneous agents first, debate later, evidence before consensus, dissent preserved.**

Agent Arena is designed for Claude Code, OpenAI Codex, Hermes Agent, OpenClaw, OpenCode, Copilot CLI, and other autonomous coding agents or agentic workflows.

## When to Use

Use this skill when the task involves:

- Multi-agent debate or panel review
- Codex vs Claude Code comparison
- Architecture decisions or implementation plan reviews
- Complex bug root-cause analysis
- PR/code review with high consequence
- Research synthesis that needs source checking
- LLM-as-a-judge, agent judge, agent game theory, or debate workflows
- Red teaming a design, prompt, implementation, benchmark, or experiment plan
- Avoiding single-model-family blind spots

Do **not** use full Agent Arena for:

- Simple factual lookups
- Translation, formatting, or summarization
- One obvious local tool call
- Low-risk tasks where the user asked for speed
- Cases where deterministic tests or source code inspection alone answer the question

## Quick Decision Gate

Before starting, choose the lightest mode that can work:

- `solo_red_team`: one agent self-critiques when no external agents are available.
- `quick_panel`: two or more agents give short independent opinions; no heavy evidence ledger.
- `design_debate`: compare design alternatives with critique and synthesis.
- `deliberative_analysis`: prevent premature convergence and shallow A/B/A+B framing.
- `evidence_arena`: claims require web, docs, source, test, or benchmark evidence.
- `code_review_arena`: review code, diffs, pull requests, or implementation plans.
- `bug_root_cause_arena`: compare root-cause hypotheses and required checks.
- `decision_memo_arena`: high-stakes recommendation with dissent and uncertainty.
- `tree_search`: explore a large option space with branching strategies.
- `full_arena`: independent generation, evidence, critique, revision, blind judging, synthesis.

## Core Principles

1. **Independence before discussion** — agents must produce initial answers before seeing each other.
2. **Evidence beats consensus** — agreement between LLMs is not proof.
3. **Deterministic checks beat model judgment** — tests, source code, docs, logs, benchmarks, and calculators outrank opinions.
4. **Heterogeneity must be real** — different model families, harnesses, tools, prompts, or evidence paths are better than same-model roleplay.
5. **No forced consensus** — preserve strong minority views when uncertainty remains.
6. **Expose dissent** — final answers must include the best counterargument.
7. **Degrade honestly** — if an agent, tool, or search source is unavailable, state the degraded mode and confidence impact.
8. **Use the lightest arena** — avoid expensive orchestration for simple tasks.
9. **Human checkpoints for high-risk actions** — do not push, deploy, delete, spend money, or expose secrets without appropriate confirmation.

## Default Cross-Agent Rule

When this skill runs inside **Codex**, invoke **Claude Code** by default as the heterogeneous counterpart.

When this skill runs inside **Claude Code**, invoke **Codex** by default as the heterogeneous counterpart.

When this skill runs inside **Hermes Agent**, **OpenClaw**, or another parent orchestrator, include both Codex and Claude Code by default if available, unless the user specifies otherwise.

If the counterpart is unavailable:

- disclose the missing participant,
- use `solo_red_team` or `quick_panel` as a fallback,
- state that heterogeneity is reduced,
- do not pretend same-family agents are equivalent.

## Core Protocol

### 1. Frame the Task

Write a compact task packet:

- user question or decision,
- constraints and success criteria,
- known facts,
- allowed tools and side effects,
- required output format,
- risks and irreversible actions.

### 2. Select Participants

Prefer heterogeneous participants:

- Codex for implementation feasibility, tests, source inspection, tool execution, and code-grounded critique.
- Claude Code for long-context design critique, reframing, synthesis, and red-team analysis.
- Hermes Agent as orchestrator when available.
- OpenClaw/OpenCode/Copilot or domain-specific agents when useful.
- Humans for ambiguous preferences, ethics, irreversible actions, or high-stakes choices.

### 3. Independent Generation

Each agent answers privately before debate.

Require each participant to return:

- recommendation,
- reasoning summary,
- assumptions,
- evidence used,
- uncertainties,
- what would change its mind.

### 4. Claim and Assumption Extraction

Extract concrete claims:

- factual claims,
- code claims,
- benchmark/performance claims,
- user-preference claims,
- risk claims,
- hidden assumptions.

### 5. Evidence Checking

For every important claim, prefer direct checks:

- read source files,
- run tests or linters,
- inspect logs,
- fetch docs or papers,
- use web search for current facts,
- compute numbers with tools,
- cite exact URLs, file paths, commands, or quotes.

### 6. Cross-Critique

Agents critique each other after independent generation.

Critique should focus on:

- missing evidence,
- hidden assumptions,
- failure modes,
- misleading analogies,
- implementation risks,
- cost and complexity,
- user intent mismatch.

### 7. Revision

Allow agents to revise after critique and evidence. Do not erase original dissent.

### 8. Blind or Rubric-Based Judging

When practical, anonymize candidate answers before judging.

Judge against a rubric:

- correctness,
- evidence quality,
- feasibility,
- risk handling,
- novelty or option coverage,
- simplicity,
- alignment with user constraints.

### 9. Synthesis

The orchestrator produces one final answer with dissent and uncertainty visible.

## `deliberative_analysis` Mode

Use this mode when the main risk is **premature convergence, overconfidence, path dependence, or shallow A/B/A+B framing** during design analysis, experiment planning, architecture choice, product strategy, or research synthesis.

This is stricter than `design_debate`: it must expand the option space before judging.

Required additions:

- Generate at least three distinct option families before critique.
- Include a `frame_challenger` role that questions whether the problem is framed correctly.
- Include a `non_obvious_alternative_finder` role that searches outside A, B, and A+B.
- Compare A, B, A+B, neither A nor B, reframed problem, and smallest reversible experiment.
- Run premortem on top candidates.
- Identify assumptions that would flip the recommendation.
- Final synthesis must include discarded frames, strongest rejected alternative, unresolved uncertainty, and cheap validation tests.

Use the companion skill `deliberative-analysis` as a lightweight trigger or wrapper when the user asks to avoid tunnel vision or find non-obvious alternatives.

## Evidence Ledger Format

For research, factual, or technical claims, keep a compact ledger:

```markdown
- Claim:
  - Status: supported / refuted / uncertain
  - Evidence: URL, file path, command, quote, benchmark, or test
  - Checked by:
  - Reliability:
  - Notes:
```

## Final Output Template

```markdown
## Recommendation

## Why

## Alternatives Considered

## Evidence / Checks

## Dissenting Views

## Best Counterargument

## Remaining Uncertainty

## Suggested Next Step
```

If degraded:

```markdown
## Arena Limitations

- Failed agents:
- Missing checks:
- Degraded mode used:
- Confidence impact:
```

## Harness Adapters

### Codex

- Run the task as Codex.
- Invite Claude Code as default counterpart when available.
- Use Codex strengths for source inspection, tests, CLI checks, implementation feasibility, and structured diffs.
- If Claude Code is unavailable, disclose fallback and run `solo_red_team` or ask the orchestrator for another heterogeneous agent.

### Claude Code

- Run the task as Claude Code.
- Invite Codex as default counterpart when available.
- Use Claude Code strengths for design critique, long-context synthesis, reframing, and adversarial review.
- Avoid letting one Claude session be proposer, judge, and synthesizer without disclosure.

### Hermes Agent

- Act as parent orchestrator.
- Prepare the task packet.
- Dispatch Codex and Claude Code independently.
- Run evidence checks directly when possible.
- Synthesize and disclose limitations.

### OpenClaw / OpenCode / Generic Agents

- Use both Codex and Claude Code if callable.
- If only one external family is available, call the missing family when possible.
- If no external agent is available, use `solo_red_team` and disclose reduced heterogeneity.

## Common Mistakes

1. **Debating before independent answers** — this causes early anchoring.
2. **Treating agreement as proof** — multiple LLMs can share the same hallucination.
3. **Skipping evidence checks** — use docs, code, tests, logs, benchmarks, and web sources when claims matter.
4. **Using fake heterogeneity** — same model plus different roles is weaker than different harnesses and tools.
5. **Hiding dissent** — the final answer should show meaningful disagreement.
6. **Overusing full arena** — use quick modes for low-risk tasks.
7. **Forgetting degradation disclosure** — state which agents or checks failed.
8. **Letting the judge know authors unnecessarily** — blind judging reduces halo effects.

## Example Prompts

- “Use agent-arena to let Codex and Claude Code review this architecture decision.”
- “Run an evidence_arena on these RAG claims and cite sources.”
- “Use deliberative_analysis mode: do not just compare A vs B; find non-obvious alternatives.”
- “Have Codex and Claude Code independently analyze this bug root cause, then judge.”
- “Red-team this implementation plan before I build it.”

## Verification Checklist

- [ ] Initial answers were independent.
- [ ] Important claims were extracted.
- [ ] Evidence was checked where possible.
- [ ] Dissent and counterarguments are visible.
- [ ] Final answer states uncertainty and next checks.
- [ ] Any unavailable agents/tools are disclosed.
