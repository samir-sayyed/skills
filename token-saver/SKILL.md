---
name: token-saver
description: >-
  Cut token burn in a session — the 15 rules from Nate B. Jones' "Never Hit a Token
  Limit Again" (Jul 2026), turned into working behaviour. Use when the user says
  "token saver", "save tokens", "I keep hitting limits", "running out of tokens",
  "usage limit", "context is filling up", "this is burning tokens", "be token
  efficient", "/token-saver", or complains about cost, rate limits, or compaction.
  Also use unprompted at the start of any job that will obviously be heavy — reading
  many files, a large refactor, a long research thread — to pick a cheaper shape
  before the burn starts.
---

# Token Saver

The message you typed is the smallest part of the call. Every turn re-sends the whole
conversation, so the cost of turn 30 is mostly turns 1–29. Everything here shrinks
what gets re-sent.

## Do these without being asked

0. **Check the model before the technique.** The same task ran 3.8–5.1× cheaper on
   Haiku than on Sonnet, and **Haiku reading everything the dumb way beat Sonnet with
   every optimisation applied, 2×**. No technique below closes a model-tier gap. Use
   the dumbest model that still gets it right.
1. **Search before you open.** `grep`/`Glob` to find the lines, then `Read` with
   `offset`/`limit`. Never `Read` a file over ~400 lines whole to answer a narrow
   question. **Measured: 51–54% cheaper than reading the file**, on both models.
   The cheapest technique and the most reliable.
2. **Delegate to `scout` when you're on an expensive model, or above ~40k tokens of
   reading.** Two different mechanisms, and which one applies depends on the parent:
   - **Same model as the parent:** a subagent re-pays the ~39k-token envelope, so it
     only pays off on bulk. *Measured on Haiku: 34% cheaper on 157KB, a slight loss on
     18KB.*
   - **Parent on a pricier model:** `scout` runs on Haiku, so delegating is a
     model-downgrade for the read — it wins even on small jobs. *Measured with a
     Sonnet parent: 53% cheaper on 18KB, 61% on 157KB.*
3. **Run exact work as code.** Counting, diffing, date math, JSON reshaping — a
   `Bash` one-liner is cheaper and correct. Don't reason token-by-token over data a
   command can compute.
4. **Answer at the size asked.** No preamble, no recap of what you just did, no
   "here's what I'll do next" when you already did it. Output is billed again as
   input on every later turn — verbosity compounds.
5. **Carry the artifact, not the argument.** When a stage finishes (research, plan,
   draft), the next stage gets the result. Rejected options, superseded drafts and
   the reasoning that produced them stay behind.
6. **Don't re-derive what's stored.** Check `~/brain/wiki/` (via its index) and
   `/mem-search` before reconstructing something from sources.
7. **Stop pointless retries.** Two failed attempts at the same thing = say what's
   blocking and ask. A third identical retry pays full freight for the same answer.

## Tell the user when it applies

These need their decision — raise them in one line, don't lecture:

- **"Start a fresh session"** — when the topic changes. Biggest measured win in the
  source. Say it plainly: *"this is a different job — new session will be cheaper."*
- **"Edit that message instead"** — when their prompt was the problem. Editing
  rewrites history; a correcting reply pays for the mistake forever.
- **"Drop these MCP servers"** — tool definitions bill before the first token of the
  request. ~55k tokens for a handful of servers (Anthropic's figure). If the session
  has 8 connected servers and needs 1, say so.
- **"Paste the text, not the PDF"** — if the layout doesn't carry meaning, the layout
  is waste.
- **"A smaller model finishes this"** — mechanical edits, renames, boilerplate,
  bulk conversion. Use the dumbest model that still gets it right.

## Model routing, quick

| Job | Model |
|---|---|
| Mechanical edits, renames, format conversion, bulk file ops | Haiku |
| Normal feature work, debugging with a known cause | Sonnet |
| Architecture, ambiguous bugs, anything where a wrong answer costs a re-run | Opus |

Wrong-cheap costs more than right-expensive: a Haiku answer you have to redo on Opus
paid twice.

## What this skill cannot do — and what does it

It cannot shrink the call it is inside of. By the time this text is read, the
conversation, standing instructions and every tool definition are already in the
envelope. This only improves what happens *next*.

Below the wire, `scripts/ringer.py` can. It's a local proxy — stdlib only, one file:

```bash
python3 ~/.claude/skills/token-saver/scripts/ringer.py serve
```

Then in the shell that runs Claude Code:

```bash
export ANTHROPIC_BASE_URL=http://127.0.0.1:8787
```

It does the two things a proxy can and a prompt can't:

- **Counts what actually left**, per call — fresh input, cache reads, output — to
  `~/.ringer/log.jsonl`. `ringer.py report` totals it and prints reused input as a
  percentage. That number is the whole argument; measure yours before believing anyone's.
- **Blocks a request over `RINGER_MAX_TOKENS`** (default 200k) with a 400 the client
  surfaces. A runaway guard, not a budget.

Everything else passes through untouched, streaming included. It forwards your auth
header without reading it and binds to `127.0.0.1` — but the whole conversation crosses
it in plaintext, so don't move it off localhost.

Not implemented: answering from a store without a model call. Coding sessions never
repeat a request byte-for-byte, so the cache would never hit. Add it if the log ever
shows otherwise.

## Benchmark

Measured 2026-07-30 with `ringer.py` in front of headless `claude -p`, three turns per
arm, real quiet-hours source, answers verified equivalent before comparing cost. Priced
at standard rates (Haiku $1/$5, Sonnet $3/$15 per MTok; cache write 1.25×, read 0.1×).
One run per cell — directional, not significant.

| Task | Approach | Haiku 4.5 | Sonnet 5 |
|---|---|---|---|
| 1 file, 18KB | read it whole | $0.1407 | $0.5347 |
| | delegate to `scout` | $0.1297 (0.92×) | $0.2533 (0.47×) |
| | **grep + offset read** | **$0.0693 (0.49×)** | **$0.2449 (0.46×)** |
| 12 files, 157KB | read them all | $0.2141 | $1.0860 |
| | **delegate to `scout`** | **$0.1415 (0.66×)** | **$0.4225 (0.39×)** |

Four things this changes:

- **Model choice dominates every technique.** Haiku naive on the big task ($0.2141) beat
  Sonnet with delegation ($0.4225). Optimise the model before the prompt.
- **Token count is not cost.** `scout` on Haiku/18KB used 2.1× the tokens and came out
  cheaper — re-read context bills at 10% of fresh input. The number in a context bar is
  the wrong number to optimise.
- **A fresh session costs ~39k tokens before your first word** — system prompt plus tool
  definitions. Every subagent pays it again; that's the delegation threshold.
- **Delegation's value depends on the parent's price.** Same-model delegation is a
  context-isolation trade that needs bulk to pay off. Expensive-parent delegation is a
  model downgrade, and pays immediately.

Source: [Never Hit a Token Limit Again](https://www.youtube.com/watch?v=Y8vAQ1FgNbM),
Nate B. Jones, Jul 2026. Brief: `~/video-briefs/2026-07-30-token-limits-nate-jones.html`
