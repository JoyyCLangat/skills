---
name: writing-great-skills
description: Reference for creating, writing, editing, and pruning agent skills in this repo so they stay lean and predictable. Use when creating a new skill, editing a SKILL.md, or reviewing a skill for quality.
---

# Writing Great Skills

Adapted from Matt Pocock's MIT-licensed [writing-great-skills](https://github.com/mattpocock/skills) and `creating-skills` in [tobilafinhangit/skill-master](https://github.com/tobilafinhangit/skill-master).

A skill exists to make a non-deterministic agent take the **same process** every run. Predictability is the root virtue.

## Anatomy

```
skills/<skill-name>/
  SKILL.md          # required
  references/*.md   # optional: detail only some runs need
  templates/*       # optional: files the skill fills in
  scripts/*         # optional: deterministic helpers
```

Frontmatter:

```yaml
---
name: <skill-name>            # kebab-case, must match the folder name
description: <what it does>. Use when <concrete triggers the user would say or situations>.
---
```

- The **description** is what the agent reads to decide whether to fire the skill. Put the triggers in it ("Use when the user mentions plugin trace logs, …"). Keep it to what makes it fire — no body restatement.
- Add `disable-model-invocation: true` only for skills that should run when a person types the name and never on their own.

## Body

1. **Steps, each ending in a completion criterion** — a checkable condition ("every dependent component listed with its solution layer"), not a vibe ("check dependencies").
2. **Reference material** below the steps, consulted on demand.
3. **Progressive disclosure** — if only some runs need a section, move it to `references/<topic>.md` and point to it with a sentence saying *when* to read it.

## Prune hard

- **No-ops:** delete any sentence that doesn't change behaviour compared to what the model already does ("be careful", "be thorough").
- **Duplication:** each rule lives in one skill; others link to it.
- **Sediment:** remove incident stories once a guard or rule exists.
- **Sprawl:** over ~300 lines? Split by branch or push reference out.

## Checklist before committing a skill

- [ ] `name` matches the folder; description says what + when.
- [ ] Every step has a completion criterion.
- [ ] No client names, secrets, tenant URLs, or customer data — use `{PLACEHOLDERS}`.
- [ ] Added to the table in the repo `README.md`.
- [ ] `scripts/validate-skills.sh` passes.
