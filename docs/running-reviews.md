# Running Cross-Model Reviews

A practical guide to running heterogeneous agent reviews with agent-arena — based on real experience running Codex × Claude reviews on skills, hooks, and implementations.

## Quick Reference

**When a review times out or stalls:**
1. Use **stdin** instead of long argv: pipe or redirection, not inline code substitution
2. **Break into blocks**: 3–5 focused questions per packet (2–5 KB each), not one 20 KB monolith
3. **Redirect output to a file**: capture to disk, read back a digest

**When the reviewer is anchored:**
1. Strip the implementer's self-assessment from the packet
2. Give only: artifact + acceptance criteria + adversarial framing
3. Never send: "I think this is solid" / "already addressed X" / test results with commentary

## The Core Problem: Anchoring

Research (ribrewguy 2024) shows that when a reviewer sees the implementer's framing, finding counts drop dramatically:
- Claude: 12.5 findings (clean) → 6.0 (with implementer framing)
- Codex: 9.4 → 2.4–4.0

The fix: **redacted handoff packets** — the reviewer gets only the raw artifact + acceptance criteria, never the implementer's self-assessment.

## Packet Construction: De-anchored

### Bad: Anchored
```bash
codex exec "I implemented the hook. I think it handles all edge cases. 
Here is the code: <paste code>. The tests pass. Any issues?"
```

Problems:
- "I think it handles all edge cases" anchors the reviewer to agree
- Long inline code can time out
- No structured acceptance criteria

### Good: De-anchored
```bash
cat > /tmp/packet.txt <<'EOF'
=== ARTIFACT ===
<paste hook.py content>

=== ACCEPTANCE ===
1. A failing tool call must increment the stall counter
2. Same error fingerprint 2x triggers STALL_RESCUE
3. A passing check resets counters
4. Bad env input must not crash the hook

=== MODE ===
adversarial_review: assume the implementer was careful but missed something.
Find real bugs only, 3 bullets, then ship/fix-then-ship.
EOF

codex exec - < /tmp/packet.txt > /tmp/review.txt 2>/tmp/review.err
```

Benefits:
- No anchoring framing
- stdin avoids argv length issues
- Output redirected (doesn't inflate your context)
- Explicit acceptance criteria

## Avoiding Timeouts

### Problem: Long argv stalls

**Symptom:** A small ping works in seconds, but a real review times out even on a working endpoint.

**Root cause:** The超长 argv (shell argument). When you inline multi-KB code into the command-line argument, some endpoints stall before the request even starts.

**Fix:** Use **stdin** instead:
```bash
# Bad - will stall on packets over a few KB:
codex exec "long text here..."

# Good - works reliably:
codex exec - < /tmp/packet.txt

# Or with a pipe:
cat /tmp/packet.txt | codex exec -
```

### Break into blocks when needed

If even stdin times out, split the review:

**Block 1: Core logic**
```bash
cat > /tmp/b1.txt <<'EOF'
Review the failure detection helpers (50 lines).
Real bugs in regex conflicts or false resets?
EOF
codex exec - < /tmp/b1.txt > /tmp/review_b1.txt
```

**Block 2: Counting/security**
```bash
cat > /tmp/b2.txt <<'EOF'
Review the counter + dedup logic.
Can 'fired' wrongly suppress a later real trigger?
EOF
codex exec - < /tmp/b2.txt > /tmp/review_b2.txt
```

**Block 3: Design**
```bash
cat > /tmp/b3.txt <<'EOF'
Review the SKILL.md design.
Token economy: can the budget be bypassed? Scope boundary clear?
EOF
codex exec - < /tmp/b3.txt > /tmp/review_b3.txt
```

Each block: 2–5 KB, focused questions, separate output. Synthesize findings after reading all.

## Output Management

### Redirect to disk, read back a digest

**Problem:** Long review output inflates your context. After 2–3 reviews, you hit compaction and lose state.

**Fix:** Redirect output, read back only what you need:

```bash
codex exec - < packet.txt > /tmp/review.txt 2>/tmp/review.err
echo "exit $? | bytes $(wc -c < /tmp/review.txt)"

# Read back a structured digest
grep -E "^(1\.|2\.|3\.|\*\*|FAIL|ship|fix)" /tmp/review.txt | head -30
```

Or checkpoint a compact summary:
```bash
cat > /tmp/review_summary.md <<'SUMMARY'
## Block 1: failure detection
- Bug: FAIL regex missed FAILURE / non-zero status
- Bug: mixed output falsely reset counters
- Verdict: fix-then-ship
SUMMARY
```

agent-arena SKILL.md says: "stage packet via stdin, redirect output to a file; read back only a structured digest preserving dissent; checkpoint each round to disk."

## When to Escalate Modes

- **quick_panel:** 2–3 agents, short independent opinions, no heavy evidence. Use for sanity checks or bounded questions.
- **full_arena:** independent generation → evidence → critique → revision → judge → synthesis. Use when:
  - Claims need web/docs/source/test evidence
  - The decision is high-stakes or hard-to-reverse
  - Two strong options remain after quick_panel
  - External critique would materially improve the decision

Default to quick_panel; escalate to full_arena only when needed.

## Example: 3-block review of know-your-limits v0.1.1

Real session that found 7 bugs:

**Block 1 (failure/fingerprint/reset):**
- Sent: helpers + "Bugs in regex conflicts or false resets?"
- Found: FAILED regex matched FAILE not FAIL; mixed output falsely reset; exit-0 edit counted as validation pass

**Block 2 (counting/security):**
- Sent: ledger path + counting logic + "Can fired suppress triggers? Path escape?"
- Found: fired not cleared on reset; reads counted as edits; bad env crashed at import; ledger dotdot escape

**Block 3 (SKILL.md design):**
- Sent: full SKILL.md + "Budget enforceable? Scope boundary clear?"
- Found: scope-boundary ambiguity; worker can classify narrowly or burn budget on every subtask; needs normative once-per-goal rule

All 7 bugs fixed, 20 tests added.

## Common Mistakes

1. **Sending the implementer's test results + commentary** — strip those
2. **One 20 KB monolithic packet** — break into 3–5 focused blocks
3. **Using long argv instead of stdin** — use input redirection
4. **Reading the full review into your context** — redirect to file, read digest
5. **Asking "any issues?" without acceptance criteria** — give concrete checks

## Further Reading

- ribrewguy (2024): "What I Found When Claude Reviewed Codex's Work" — quantifies anchoring
- agent-arena SKILL.md — full protocol
- know-your-limits dev case study — real 3-block review
