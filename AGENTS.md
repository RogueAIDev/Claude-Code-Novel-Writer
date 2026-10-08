# Multi-Agent Novel Writer v4.1

## Purpose

This repository is a long-form fiction workspace for planning, drafting, revising, and maintaining a novel across Claude Code, OpenAI Codex, and Pi.

Preserve the user's creative intent, established voice, and story continuity. Use automation as support, not as proof of literary quality.

## Supported harnesses

- Claude Code uses `CLAUDE.md`, `.claude/agents/`, `.claude/skills/`, the project output style, and Claude lifecycle hooks.
- OpenAI Codex reads this `AGENTS.md`, discovers `.agents/skills/`, loads project agents from `.codex/agents/`, and can run `.codex/hooks.json`.
- Pi reads this `AGENTS.md`, discovers `.agents/skills/`, and exposes project prompt templates from `.pi/prompts/`.

The shared source of truth for roles and workflows lives under `.agents/`. Harness-specific directories are adapters.

## Ground-truth order

When sources disagree, use this order unless the user says otherwise:

1. Explicit instructions from the user
2. Existing prose in `manuscript/chapters/`
3. The author's canon documents, in their own stated order (see "Story sources")
4. Accepted outline and planning files
5. Character and world state
6. Derived metrics, flags, logs, and automation output

Manuscript files are authoritative for drafted prose and actual word counts. If tracking disagrees with manuscript files, run `./sync-state.sh`. Do not rewrite prose to match stale tracking.

## Story sources

This project is *Inheritance*, Book One of *Chronicles of the Shadow Vanguard*, by P. D. Fox II. The author's own documents are canon. They rank as follows, as the documents themselves state:

1. `planning/prequel_My_Final_Draft.md`: *Shadows of Loch Maree*, the published prequel novella, set in autumn 1845, several years before *Inheritance*. Never contradict it. Niall is effectively its lead. Alexander appears only near the end, as a young man. Use it for established history, for how characters already know each other, and as the living proof of the voice.
2. `planning/Series_Bible.md`: series canon. It governs every other planning document. Part Eleven holds the Drafting Guidelines.
3. `planning/Master_Vampire_Dossier.md`: every vampire rule. It expands Series Bible Part Six and governs vampire rules in the character bibles.
4. `characters/Main_Character_Bible.md` (twelve principals) and `characters/Supporting_Character_Bible.md` (everyone else): character profiles, voice, and arcs.
5. `worldbuilding/Location_Bible.md`: places, with the chapters each place appears in.
6. `planning/Inheritance_Detailed_Scene_Outline.md`: the working plan for Book One. It has 26 chapters and 153 scenes. Each chapter has an overview with its date span and a length guide. Each scene has a summary and a fifteen-field sheet. "3.2" means Chapter 3, Scene 2.
7. `planning/Inheritance_Scene_Packets.md`: the outline reproduced in full, plus per-scene drafting packets. These hold character notes, continuity in and out, rules in play, threads, flags, and decisions. Its DECIDED markers and Decisions Log are provisional choices that the author may veto. Nothing in it has entered the bibles.
8. `planning/Bible_Updates_Ch01-04.md` and `planning/Bible_Updates_Ch05-26.md`: the exact bible text proposed for the packets' decisions, awaiting the author's approval. Use them as the working answer where the bibles are silent. They never override a bible's existing text. The Ch05-26 file's Part Two lists gaps that are now settled in item 9.
9. `planning/Gap_Resolutions.md`: the author-directed resolutions of every open gap and "Ask Fox" flag in the packets and Bible Updates, with corrections to the packets' moon positions. Where it differs from a packet's DECIDED line, it wins. Its Part Four holds the author's own rulings, which outrank the bibles where they say so, and the questions still reserved for the author. Each open question has a Book One default to follow. Never decide those questions yourself.

Voice is governed by `planning/Author_Writing_Style_and_Voice_Guide.md`. It sits beneath the Series Bible's Drafting Guidelines and never overrules the bible.

Viewpoint and tense: tense is chosen separately for each work in the series, not fixed series-wide. The style guide leaves it open on purpose, because short stories and novellas may differ. For *Inheritance*, the scene outline does not state a tense, and the author has chosen past tense. Write in close third person, past tense. Alexander is the main character and the dominant viewpoint. Each scene uses the viewpoint listed in its "Perspective and goal" field in the scene outline. That includes the short interludes the outline assigns to other characters. Keep one viewpoint per scene.

Length: there is no hard word count for the novel, a chapter, or a scene. The outline's lengths are a general guide only. First drafts may run long and are trimmed in later drafts.

`planning/novel-outline.json` is a machine-readable index derived from the scene outline. It holds parts, chapter titles, viewpoints, spans, length guides, and per-scene location, date, and length guide. When the index and the markdown disagree, the markdown wins. Regenerate the index or fix it; never change the markdown to match it.

These files are large; the Scene Packets alone run to about 10,000 lines. Read by section, not whole files:

- For a chapter, grep the outline and the packets for the heading `Chapter N:` and read from there to the next chapter heading. Also read the packets' Decisions Log near the top of the file.
- For characters, places, or rules, grep the bibles for the names the scene sheet lists, then read the matching entries.
- For prequel history, grep the prequel for the relevant names or events. Its chapters open with `# **Chapter N**`, and its scenes are separated by `***`. Read the whole prequel only when calibrating voice.
- Read the style guide in full before the first drafting or revision session, and again whenever voice is in question.

When two of these documents disagree, do not resolve the conflict silently. Follow the higher-ranked source, and report the conflict to the author with exact file references.

## Core operating rules

1. Inspect existing files before creating or replacing substantial story content.
2. Preserve established canon unless the user explicitly authorizes a change.
3. Confirm the target chapter does not already contain substantial prose before drafting.
4. Keep character knowledge, chronology, physical state, and world rules consistent.
5. Do not claim that heuristic metrics prove literary or publication quality.
6. Do not invent completion, validation, recovery, or test results.
7. Keep JSON machine-readable where JSON is already used.
8. Prefer the smallest useful change during revision or continuity repair.
9. Do not delegate merely to create activity.
10. For repository maintenance, temporarily prioritize technically correct edits and validation over fiction generation.
11. Use normal harness permissions and project trust. Do not recommend bypassing safeguards as a default.
12. Before finishing repository changes, run the relevant validation commands.

## Canonical specialist roles

Role definitions live in `.agents/roles/`:

- `plot-architect`: premise, structure, turning points, chapter beats, setup, and payoff
- `chapter-writer`: complete chapter drafting and substantive prose revision
- `character-developer`: motivation, arcs, relationships, voice, and knowledge state
- `worldbuilder`: setting, institutions, history, geography, systems, and constraints
- `continuity-editor`: timeline, knowledge, physical state, names, rules, setups, and payoffs
- `smart-planner`: pacing, milestone analysis, and the next high-value action
- `error-recovery`: broken tracking, malformed JSON, scripts, and harness configuration

### Specialist execution protocol

If the current harness exposes a named specialist or custom subagent, use the exact role name above when specialization materially helps.

If named subagents are unavailable, disabled, or unnecessary, read the matching file in `.agents/roles/` and perform the role directly in the current session.

When delegating:

- provide a bounded task and exact file scope
- include the relevant chapter, outline, character, world, and continuity context
- require a concise handoff with changed files, story-state changes, and unresolved concerns
- keep creative decisions in the main workflow when they affect the user's intent

Pi compatibility does not require a third-party subagent extension. Pi can execute the canonical role directly.

## Shared project skills

Canonical skills live in `.agents/skills/`:

- `plan-novel`
- `write-chapter`
- `continuity-pass`
- `revise-chapter`
- `finalize-manuscript`

Harness invocation:

- Claude Code: use the matching slash command, such as `/write-chapter 7`
- Codex: mention the skill, such as `$write-chapter 7`, or select it through `/skills`
- Pi: use `/skill:write-chapter 7`, or the shorter project template `/write-chapter 7`

The Claude and Pi command layers are adapters. The canonical workflow remains the file under `.agents/skills/<name>/SKILL.md`.

## Planning workflow

Before planning:

1. Inspect `planning/`, `characters/`, `worldbuilding/`, and existing manuscript files.
2. Treat substantial manuscript prose as canon unless the user requests a retcon.
3. Identify premise, viewpoint, structural shape, central conflict, stakes, and character arcs.
4. Build causally connected chapter purposes rather than a list of unrelated events.
5. Record unresolved creative choices as explicit questions or provisional decisions.
6. Update `planning/novel-outline.json`.
7. Run `./sync-state.sh` when tracking needs initialization or reconciliation.

Use the `plan-novel` skill for the full procedure.

## Drafting workflow

Before drafting a chapter:

1. Run or inspect `./sync-state.sh`.
2. Read `planning/novel-outline.json` when present.
3. Read `planning/plot-progress.json` and `planning/chapter-status.json`.
4. Read the previous chapter and any directly relevant earlier chapters.
5. Read relevant character, world, and continuity state.
6. Confirm the target path does not already contain substantial prose.
7. Draft one coherent complete chapter unless the task calls for a bounded partial draft.

After writing:

1. Run `automation/quality-check.sh <chapter-path>` for mechanical signals.
2. Run `./sync-state.sh`.
3. Report the file, approximate word count, story-state changes, and continuity facts.
4. Note any downstream chapter or planning changes that may be needed.

Claude Code and Codex may perform some of this through trusted lifecycle hooks. Verify the resulting state rather than assuming the hook ran.

## Revision workflow

Before revising, distinguish among:

- prose and voice problems
- structural problems
- character motivation problems
- pacing problems
- continuity problems
- intentional ambiguity
- user-preferred stylistic choices

Preserve good existing material. Do not rewrite a whole chapter merely to normalize style. Recheck affected continuity after substantive changes.

## Continuity workflow

Audit before editing. Separate true contradictions from intentional ambiguity, unreliable narration, delayed revelation, or plausible off-page change.

Findings should include exact file references and be grouped by severity. Apply the smallest fix that restores consistency when the user asks for edits.

## Completion workflow

A manuscript is not complete merely because it reaches a word count. Before final polish, review:

- structural gaps
- unresolved promises and subplots
- character arc resolution
- continuity and chronology
- chapter order and pacing
- incomplete or unusually short chapter files
- revision priorities

Do not declare publication readiness solely because automated checks pass.

## Useful commands

```bash
./launch-novel.sh
./sync-state.sh
./verify-system.sh
automation/system-health-check.sh
automation/quality-check.sh manuscript/chapters/chapter-N.md
python3 automation/dashboard.py
```

## Repository validation

For configuration changes, validate all active adapters:

```bash
./verify-system.sh
python3 -m json.tool .claude/settings.json
python3 -m json.tool .codex/hooks.json
python3 -m py_compile automation/dashboard.py
```

Use Python `tomllib` to validate `.codex/config.toml` and `.codex/agents/*.toml` when Python 3.11 or newer is available.
