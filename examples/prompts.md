# Example Prompts

## Full multi-agent architecture review

```text
Use agent-arena full_arena.
Task: review this architecture decision.
Participants: Codex and Claude Code by default.
Requirements:
- independent initial analysis,
- claim extraction,
- evidence checks where possible,
- cross-critique,
- final synthesis with dissent.
```

## Codex invoking Claude Code

```text
Use agent-arena. You are running inside Codex, so invoke Claude Code as the heterogeneous counterpart if available.
Review this PR for correctness, missing tests, security issues, and implementation risk.
If Claude Code is unavailable, disclose degraded mode.
```

## Claude Code invoking Codex

```text
Use agent-arena. You are running inside Claude Code, so invoke Codex as the heterogeneous counterpart if available.
Have Codex independently inspect source/test feasibility while Claude Code critiques the design and synthesizes.
```

## Deliberative analysis for non-obvious alternatives

```text
Use deliberative-analysis.
We are comparing A vs B vs A+B, but I worry we are stuck in the wrong framing.
Generate at least one genuinely different option C, one reframed option D, and the smallest reversible experiment.
Then decide whether to escalate to agent-arena.
```

## Evidence arena for RAG or research claims

```text
Use agent-arena evidence_arena.
Extract concrete claims from this answer, verify with web/docs/source evidence, and label each claim supported/refuted/uncertain.
Do not treat model consensus as evidence.
```

## Bug root cause arena

```text
Use agent-arena bug_root_cause_arena.
We have three plausible root causes. Have agents independently rank them, identify decisive tests, critique each other, and recommend the cheapest next check.
```

## Implementation plan review

```text
Use agent-arena implementation_plan_review.
Review this plan before implementation. Preserve dissent, identify missing tests, flag irreversible steps, and recommend a revised plan.
```
