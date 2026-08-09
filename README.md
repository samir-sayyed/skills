# skills

Personal Claude Code skills. One directory per skill; each contains a `SKILL.md` (plus optional `scripts/`, `references/`, `assets/`).

## Index

| Skill | What it does |
|---|---|
| [agent-swarm-economics](agent-swarm-economics/) | Multi-agent architecture & cost optimization, from Cursor's agent-swarm model-economics research. Two modes: ADVISE (design/debug/cost guidance for any multi-agent setup) and EXECUTE (actually runs the planner/worker split — plan with a strong model, delegate code-writing to cheap worker subagents; `planner=` / `worker=` overridable). |
| [explain-diff-html](explain-diff-html/) | Rich, self-contained interactive HTML explanation of a code change (diff/branch/PR) — background, intuition, code walkthrough, and a quiz with bias fixes. Based on [Explain Diff](https://gist.github.com/geoffreylitt/a29df1b5f9865506e8952488eac3d524) by [Geoffrey Litt](https://github.com/geoffreylitt). |
| [code-as-prompt](code-as-prompt/) | Diagnoses *why* an agent keeps failing on a particular file, by reading the code as context instead of rewriting the prompt a fourth time. Four checks in fix-first order — apologetic comments (`// hacky, fix later` primes the model to keep writing badly), commented-out code (there's no skip flag; it reads as your house standard), declare-to-use distance (it sits in the **exponent** of attention decay, so scatter degrades comprehension off a cliff), and mutate-and-return functions (query and command words live in different embedding regions — a `seek(pos): Position` lands in both at once). **Benefit:** turns "the agent is being weird here" into a checkable hypothesis, and every fix is an in-passing edit rather than a refactoring project. Ships `scan.sh` (stdlib grep, no deps, `--selftest`) for the three regex-findable smells plus over-long files. From Danny Preussler's *Clean Code Revisited in the Age of AI*, droidcon USA 2026. |
| [onboard-agent](onboard-agent/) | Builds a `<project>-product` briefing skill for any repo (Android, iOS, frontend, backend, CLI) — analyses the code, then grills you one question at a time about the tacit knowledge it cannot read: load-bearing flows, invariants and the bugs that proved them, entitlement exceptions, and a runbook for driving the app. Wires the result into `CLAUDE.md` so agents actually load it. Re-run with an argument to deepen one section. |

## Installing a skill

Copy the skill's directory into your personal skills folder:

```bash
cp -r <skill-name> ~/.claude/skills/
```

Or for a single project: `cp -r <skill-name> <project>/.claude/skills/`

The skill is picked up on the next Claude Code session and triggers automatically based on its `description`, or explicitly via `/<skill-name>`.

## Adding a new skill

1. Create `<skill-name>/SKILL.md` with YAML frontmatter (`name`, `description` — the description drives triggering, so make it specific about *when* to use it).
2. Keep `SKILL.md` under ~500 lines; put bulky material in `references/` and executable helpers in `scripts/`.
3. Add a row to the index above.
