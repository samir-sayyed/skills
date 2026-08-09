---
name: code-as-prompt
description: >-
  Diagnose why an agent keeps failing on a particular file or module by reading the code as
  context rather than rewriting the prompt again. Finds the four mechanical causes — apologetic
  comments, commented-out code, long declare-to-use distance, and mutate-and-return functions —
  and fixes them in passing. Use when the user says "the agent keeps messing this up", "why does
  Claude/Cursor do so badly in this file", "same prompt worked yesterday", "it went down a rabbit
  hole", "make this codebase agent-friendly", "why is my agent hallucinating here", or invokes
  /code-as-prompt. Also use before handing an unfamiliar or legacy file to an agent for a
  non-trivial change.
---

# Code as Prompt

When an agent works one day and flails the next on the same prompt and the same config, the
codebase is the variable nobody checks. The file **is** context. This skill reads it as such.

Mechanism, from Danny Preussler's *Clean Code Revisited in the Age of AI* (droidcon USA 2026):
distance between related tokens sits in the **exponent** of attention decay, so scatter doesn't
degrade comprehension gradually — it falls off a cliff. Models also have no quality prior; the
code already in the file sets the expected distribution for what gets written next.

Treat these as a plausible frame, not measured law. Act on them anyway — every fix below is an
edit you make while already in the file.

## Run the scan first

```bash
~/.claude/skills/code-as-prompt/scan.sh <path>
```

Greps the four mechanical smells. Fast, no dependencies, no false sense of completeness — it
finds what a regex can find and nothing else. Read its output, then do the judgement passes
below on whatever it flagged plus the file the agent is actually failing in.

## The four checks, in fix-first order

**1. Apologetic comments — delete or reword.** `// hacky`, `// temporary`, `// fix this later`.
These are keywords for expected code quality, sitting at maximum attention weight next to the
code they describe. The model correctly infers the house standard and keeps writing to it. Either
fix the code or describe it neutrally: *what* it does, not how you feel about it.

**2. Commented-out code — delete it.** There is no skip flag; dead code gets attention weight
comparable to live code, and it is usually an *older* pattern, which is why it was commented out.
Git has it. This is the single cheapest win on the list.

**3. Declare-to-use distance — shorten it.** Move a declaration next to its use. Prefer one
slightly longer single-responsibility function over a chain of one-liners — every hop compounds
decay, which is why "functions should be small" is the one classic rule that now points the wrong
way. Flatten `a.b().c().d()` train wrecks; they load four classes to produce one value.

**4. Mutate-and-return — split it.** Query words (`get`, `fetch`, `calculate`, `view`) and command
words (`save`, `update`, `process`) live in different regions of embedding space. A function that
mutates *and* returns lands in both at once. `seek(pos): Position` reads fine and is the same
defect as `getAndRemoveTrack()`. **This is the check to run first when an agent flails on one
specific function while doing fine everywhere else** — it's a concrete, checkable hypothesis.

## Two more, when reorganising rather than patching

**Newspaper order.** High-level at the top, detail descending. Long-context attention is U-shaped —
live at the start and end, near-dead in the middle — so this puts *what this is* and *how it ends*
in the two live zones. Corollary: stop burying hacky code at the bottom of the file. That is a
high-attention position, not a hiding place.

**Single Context Principle.** A file should hold everything needed to execute the prompt — DTO,
interface, implementation, when they share a boundary, lifecycle and vocabulary. One class per
file is Java-era dead weight. Past ~300 lines compliance drops, so when a file outgrows that,
split into a **directory** of sibling files that stay adjacent, not across the tree. Same rule
applies to `CLAUDE.md` and skill files.

Local names carry what the traversal used to: `deliveryZipCode`, not `zipCode`.

## Rules of engagement

- **Diagnose before rewriting the prompt.** If the user is on their third prompt revision, stop
  and read the code instead.
- **Fix in passing.** These are edits inside work already happening, not a refactoring project.
  Never open a "make the repo agent-friendly" PR unless asked.
- **Don't touch behaviour.** Deleting a comment is free. Splitting a mutate-and-return function is
  a behaviour-adjacent change — propose it, and check the callers.
- **Report what you didn't do.** A file with 40 train wrecks gets the top three and an honest note,
  not a 900-line diff.

## What this does not cover

Nothing here is about correctness, security, or whether the code is *good*. It is only about
whether an agent can read it. A file can pass every check and still be wrong — use `/code-review`
for that.
