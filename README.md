# skills

Personal Claude Code skills. One directory per skill; each contains a `SKILL.md` (plus optional `scripts/`, `references/`, `assets/`).

## Index

| Skill | What it does |
|---|---|
| [agent-swarm-economics](agent-swarm-economics/) | Multi-agent architecture & cost optimization, from Cursor's agent-swarm model-economics research. Two modes: ADVISE (design/debug/cost guidance for any multi-agent setup) and EXECUTE (actually runs the planner/worker split — plan with a strong model, delegate code-writing to cheap worker subagents; `planner=` / `worker=` overridable). |
| [explain-diff-html](explain-diff-html/) | Rich, self-contained interactive HTML explanation of a code change (diff/branch/PR) — background, intuition, code walkthrough, and a quiz with bias fixes. Based on [Explain Diff](https://gist.github.com/geoffreylitt/a29df1b5f9865506e8952488eac3d524) by [Geoffrey Litt](https://github.com/geoffreylitt). |

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
