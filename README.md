# Agent Arena

[![Skill](https://img.shields.io/badge/skill-AI%20agents-blue)](#installation)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-skill-6b46c1)](#claude-code)
[![OpenAI Codex](https://img.shields.io/badge/OpenAI%20Codex-skill-111827)](#openai-codex)
[![Hermes Agent](https://img.shields.io/badge/Hermes%20Agent-skill-059669)](#hermes-agent)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**Agent Arena is a multi-agent debate, red-team, evidence-checking, and judge skill for Claude Code, OpenAI Codex, Hermes Agent, OpenClaw, OpenCode, and other AI coding agents.**

It helps agents avoid overconfidence, tunnel vision, shallow A/B comparisons, and single-model-family blind spots by using heterogeneous agents such as **Codex + Claude Code** to independently analyze, critique, verify evidence, judge, and synthesize.

## Why this exists

LLM agents often become too confident too early. They can converge on one framing, reinforce each other's hallucinations, or treat consensus as proof.

Agent Arena adds a reusable protocol:

```text
independent generation -> claim extraction -> evidence checking -> critique -> revision -> blind judging -> synthesis
```

Core principle:

> Independent heterogeneous agents first. Debate later. Evidence before consensus. Dissent preserved.

## Included skills

- [`agent-arena`](skills/agent-arena/SKILL.md) — the main multi-agent orchestration protocol.
- [`deliberative-analysis`](skills/deliberative-analysis/SKILL.md) — a lightweight companion for anti-overconfidence, anti-tunnel-vision, non-obvious alternatives, and escalation into Agent Arena.

## Use cases

- Multi-agent debate for AI coding agents
- Codex vs Claude Code review
- Claude Code + OpenAI Codex architecture analysis
- LLM-as-a-judge workflows
- Agent judge / agent game theory / agent arena workflows
- Red team review of implementation plans
- Evidence-checked RAG and research synthesis
- Bug root-cause analysis with competing hypotheses
- Pull request and code review with dissent preservation
- Experiment planning and design-space exploration
- Avoiding shallow A vs B vs A+B reasoning

## Installation

This repository uses the portable `skills/<skill-name>/SKILL.md` layout so it can be copied into different agent skill directories.

### Claude Code

Copy one or both skills into your Claude Code skills directory:

```bash
git clone https://github.com/zhjai/agent-arena.git
mkdir -p ~/.claude/skills
cp -R agent-arena/skills/agent-arena ~/.claude/skills/
cp -R agent-arena/skills/deliberative-analysis ~/.claude/skills/
```

Then ask Claude Code:

```text
Use agent-arena to have Claude Code and Codex independently review this architecture decision.
```

### OpenAI Codex

Copy the skills into your Codex/agent skills directory, commonly `~/.agents/skills/`:

```bash
git clone https://github.com/zhjai/agent-arena.git
mkdir -p ~/.agents/skills
cp -R agent-arena/skills/agent-arena ~/.agents/skills/
cp -R agent-arena/skills/deliberative-analysis ~/.agents/skills/
```

Then ask Codex:

```text
Use agent-arena. You are Codex; invite Claude Code as the heterogeneous counterpart if available.
```

### Hermes Agent

Clone or copy the skills into your Hermes skills directory:

```bash
git clone https://github.com/zhjai/agent-arena.git
mkdir -p ~/.hermes/skills
cp -R agent-arena/skills/agent-arena ~/.hermes/skills/
cp -R agent-arena/skills/deliberative-analysis ~/.hermes/skills/
```

Raw skill URLs:

- Agent Arena: https://raw.githubusercontent.com/zhjai/agent-arena/main/skills/agent-arena/SKILL.md
- Deliberative Analysis: https://raw.githubusercontent.com/zhjai/agent-arena/main/skills/deliberative-analysis/SKILL.md

### OpenClaw, OpenCode, Copilot CLI, and other agents

Use the same portable layout:

```text
skills/agent-arena/SKILL.md
skills/deliberative-analysis/SKILL.md
```

If your agent supports a custom skills directory, copy the skill folders there. Otherwise, paste the relevant `SKILL.md` as an instruction guide.

## Default cross-agent rule

- When running inside **Codex**, invite **Claude Code** by default.
- When running inside **Claude Code**, invite **Codex** by default.
- When running inside **Hermes Agent**, **OpenClaw**, or another orchestrator, include both Codex and Claude Code by default if available.
- If a counterpart is unavailable, disclose the degraded mode instead of pretending same-model roleplay is equivalent.

## Example prompts

```text
Use agent-arena to let Codex and Claude Code independently analyze this implementation plan, critique each other, and synthesize a final recommendation.
```

```text
Run an evidence_arena on these RAG claims. Extract claims, verify with docs/web/source evidence, then judge.
```

```text
Use deliberative-analysis. Do not only compare A vs B or A+B; find a genuinely non-obvious alternative and say what evidence would flip the recommendation.
```

```text
Have Codex and Claude Code independently analyze this bug root cause. Preserve dissent and tell me the cheapest next test.
```

```text
Red-team this architecture decision with Agent Arena. Include the best counterargument and remaining uncertainty.
```

More examples are in [`examples/prompts.md`](examples/prompts.md).

## Modes

Agent Arena supports these modes:

- `solo_red_team`
- `quick_panel`
- `design_debate`
- `deliberative_analysis`
- `evidence_arena`
- `red_team`
- `code_review_arena`
- `bug_root_cause_arena`
- `implementation_plan_review`
- `decision_memo_arena`
- `tree_search`
- `full_arena`

## SEO / discovery keywords

This repository is intentionally described with common search phrases used by AI agent builders:

- AI agent skill
- Claude Code skill
- OpenAI Codex skill
- Hermes Agent skill
- OpenClaw skill
- multi-agent debate
- multi-agent coding agents
- agent arena
- agent judge
- LLM-as-a-judge
- agent game theory
- AI red team
- evidence checking
- RAG evaluation
- deliberative analysis
- anti-overconfidence prompting
- tunnel vision prevention
- Codex Claude Code workflow

## License

MIT. See [`LICENSE`](LICENSE).
