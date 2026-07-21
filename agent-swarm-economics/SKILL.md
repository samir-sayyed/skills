---
name: agent-swarm-economics
description: >-
  Two modes. ADVISE — architecture and cost-optimization guidance for multi-agent / subagent systems, distilled from Cursor's agent-swarm model-economics research (July 2026); use whenever the user is designing, building, reviewing, or debugging any multi-agent setup, or asks which model to use for which agent role, how to cut multi-agent costs, why agents conflict or churn, or how to scale agent parallelism. EXECUTE — actually run the planner/worker split on the current task: plan with a strong model, delegate code-writing to cheaper worker subagents; use whenever the user asks to "swarm this", "plan with X and code with Y", "use cheap workers", "delegate to haiku", or hands over a large decomposable coding task and wants it done cost-efficiently. Also trigger on mentions of "swarm", "orchestrator", "subagent strategy", "agent economics", or "cheap model vs frontier model", even without the word "multi-agent". Users can pass planner=<model> and worker=<model> options.
---

# Agent Swarm Economics

Two modes — pick based on what the user wants:

- **ADVISE**: they're asking how to design/fix/cost a multi-agent system → use
  the principles below to answer.
- **EXECUTE**: they hand you a task and want it done with the planner/worker
  split → jump to "Executing the pattern" at the end and do it.

Harness-agnostic principles for architecting multi-agent systems. Works with any
orchestration framework (Claude Agent SDK, LangGraph, CrewAI, custom loops, CI
pipelines) and any model vendor — reason in **model tiers**, not model names:

- **Frontier tier**: the most capable model you can access (expensive per token)
- **Efficient tier**: a fast, cheap model that reliably follows explicit instructions

Source: Cursor, "Agent Swarms and Model Economics" (cursor.com/blog/agent-swarm-model-economics).
Benchmark: swarms implementing SQLite in Rust from docs alone, graded on sqllogictest.

## Core principle: split planning from execution

Work decomposes into a tree. Assign two roles:

- **Planners** (frontier tier): recursively decompose goals, make architectural
  decisions, collapse ambiguity into detailed explicit instructions. Own
  non-overlapping subtrees.
- **Workers** (efficient tier): execute one narrow, fully-specified task each.

Why: a solo long-running agent must either focus on the piece and lose the big
picture, or hold the big picture and do the piece badly. Role-splitting removes
the tradeoff — planners keep strategic context, workers keep task context. This
is a **context-efficiency** win, not a parallelism win, so it pays off on
moderately sized tasks too, not just huge ones.

## The economics (why hybrid wins)

Most large tasks contain only a few moments that need frontier intelligence:
the initial decomposition, architectural decisions, critical tradeoffs. Once a
frontier planner has turned ambiguity into an explicit instruction, a cheap
model just follows it.

Measured results from the SQLite benchmark:

| Configuration | Total cost | Outcome |
|---|---|---|
| Frontier model in both roles | $10,565 | 100% pass |
| Frontier planner + efficient workers | $1,339 | 100% pass, fewest lines (4,645) |

- Workers generate 69–90%+ of tokens but should be a minority of cost.
  Identical worker workload: $9,373 on a frontier model vs $411 on an
  efficient one — a **23× reduction** with no quality loss, because the
  planner had already removed the ambiguity.
- Warning: a *smarter but pricier* planner isn't automatically better. In the
  benchmark, the top-tier planner emitted vaguer decompositions whose workers
  burned several times more tokens, making the run more expensive overall.
  Judge a planner by **how many worker tokens its instructions save**, not by
  its own benchmark scores.

**Rule of thumb**: pay frontier prices only where ambiguity is being collapsed.
Everything downstream of an explicit spec goes to the efficient tier.

## Coordination failure modes (and the fixes that worked)

If agents share a workspace, expect these five failures. The old un-fixed swarm
produced 70,000+ merge conflicts and 68k churn-commits; the fixed one, under
1,000 of each, and reached 100% with 6–14× less code.

1. **Split-brain** — two planners implement the same concept differently.
   Fix: planners make architectural decisions themselves and own strictly
   non-overlapping subtrees.
2. **Planner contention** — planners fight over shared files. Fix: decisions
   are recorded in shared design documents; code references the decision doc
   (compile-checked if possible); an automatic reconciler merges contradicting
   docs.
3. **Merge conflicts** — workers resolve collisions badly (overwrite or give
   up). Fix: a neutral third-party agent arbitrates conflicts, like a human
   merge queue.
4. **Megafiles** — popular files bloat until they're expensive to diff and
   merge. Fix: workers flag bloated files; the system blocks new commits to
   them while a dedicated agent decomposes them into modules.
5. **Ossification** — agents refuse to touch core code (habits learned from
   human repos). Fix: explicitly license intentional breakage — justified core
   changes with an explanatory comment; let the compiler propagate breakage and
   dependent agents update.

## Review: stack decorrelated lenses

No single review method catches everything, but decorrelated lenses stack (the
way self-driving stacks imperfect sensors). Combine several of:

- transcript review (how the agent worked)
- output-only review (what it produced)
- codebase-only inspection (ignore the process)
- a reviewer running a *different model family* (decorrelated blind spots)

Review compute has outsized ROI: auditing costs far less than the work it
audits. Budget for it.

## Shared memory: the field guide (stigmergy)

Agents coordinate through the environment, not direct messages. Maintain one
shared, agent-curated document injected into every agent's context, capturing
surprising discoveries whose only purpose is to **shorten the next agent's
trajectory**. Enforce a hard line budget — scarcity forces curation, so only
high-value notes survive. This substitutes for learning, since weights are
frozen mid-run.

## Applying this in any harness

When designing or reviewing a multi-agent system, walk this checklist:

1. **Do you need a swarm at all?** One agent with a clear spec beats a swarm
   with a vague one. Swarms pay off when the task exceeds one context window.
2. **Where does ambiguity collapse?** Put the frontier model exactly there
   (planning/decomposition/arch decisions) and nowhere else.
3. **Are worker tasks fully specified?** If workers need judgment, the planner
   under-specified — fix the decomposition, don't upgrade the worker model.
4. **Are subtrees non-overlapping?** Every shared surface needs an owner or an
   arbiter (design docs, merge arbiter, file-size watchdog).
5. **Is there a shared field guide** with a line budget?
6. **Is review stacked** with at least two decorrelated lenses, ideally one on
   a different model family?
7. **Measure**: cost per role, worker-token multiplier per planner, conflict
   rate, churn (commits or edits that don't survive). Rising conflict/churn
   curves mean a coordination failure mode above, not a model-quality problem.

The end state to aim for: the scarce input is a good **spec**, not model
capability. The swarm is a probabilistic compiler from intent to artifact —
every mechanism above exists to close the gap between probabilistic steps and
a deterministic-feeling result.

## Executing the pattern (EXECUTE mode)

This is where the skill *does* the economics instead of describing them: the
strong model plans, cheap subagents write the code.

### Model selection — user choice first

The user may specify models anywhere in their request or as skill arguments,
e.g. `planner=opus worker=haiku`, or in prose: "plan with Opus, code with
Haiku". Honor whatever they name. Defaults when unspecified:

- **Planner**: the current session model (you) — no separate planner agent
  needed; you do the planning in-conversation where the user can see and
  correct it.
- **Worker**: the cheapest available model tier (in Claude Code: `haiku` via
  the Agent tool's `model` parameter).
- If the user names only one role, default the other as above. If the
  requested model isn't available in this harness, say so and use the nearest
  tier rather than silently substituting.

State the chosen pair in one line before starting ("Planning here, workers on
haiku") so the user can redirect cheaply.

### When to use it — and when not to

Use the split when the task decomposes into ≥2 worker tasks that are
independent and specifiable. **Fall back to doing it yourself** when the task
fits comfortably in one context and one sitting — a swarm on a small task is
pure overhead, and saying so is the correct output. Not every task deserves
workers; the checklist above (step 1) applies to you too.

### The workflow

1. **Plan at full strength.** Decompose the task into worker assignments with
   strictly non-overlapping file ownership. Make every architectural decision
   NOW — interfaces, naming, data shapes, error conventions, which files exist.
   Anything left undecided becomes a coin-flip inside a cheap model.
2. **Write real specs.** Each worker task must be executable without judgment:
   exact file paths it owns, the interfaces it implements or consumes (signatures
   spelled out), conventions to follow, edge cases to handle, and an acceptance
   check it can run (a command, a test, a compile). The spec test: could two
   different models produce interchangeable results from it? If not, it's vague.
3. **Spawn workers on the worker model** (in Claude Code: Agent tool with
   `model` set to the worker model; parallelize independent tasks in one batch).
   Include in each prompt: the spec, the shared conventions, and two standing
   rules, stated explicitly — cheap models follow stated rules well but don't
   infer unstated ones:
   - Ambiguity is returned as a question, never guessed at. (A returned
     question means your spec was under-specified; tighten it and re-dispatch,
     don't upgrade the worker.)
   - Touching ANY file outside the declared ownership list is a spec
     violation — including "helpful" stubs, scaffolding, or placeholder files
     for modules other workers own. If a missing file blocks the acceptance
     check, report the blockage instead of creating the file.
4. **Review at full strength.** After workers land, you (planner tier) review
   the integrated result — run the acceptance checks, then read the diff as a
   decorrelated lens (you have the whole-plan context workers lacked). Fix-ups
   discovered here are respawned as new specs, or done inline if trivial.
5. **Report the economics.** Tell the user what ran where — roughly how much
   work went to the cheap tier vs planning/review — so they can see the lever
   working and recalibrate the split next time.

Escalation valve: a worker task that fails its acceptance check twice on a
tightened spec is genuinely hard — pull it up to the planner tier as a flagged
exception instead of looping. That should be rare; if it's frequent, your
decompositions are too coarse.
