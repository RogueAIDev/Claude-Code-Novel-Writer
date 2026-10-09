---
name: write-chapter
description: Draft the next chapter or a specified chapter from the accepted outline while preserving manuscript continuity, character knowledge, and established voice.
---

# Write Chapter

Use any chapter number or constraints supplied with the invocation.

1. Resolve the repository root and run `./sync-state.sh --quiet`.
2. Determine the target chapter from the invocation, outline, and tracking state.
3. Refuse to overwrite substantial existing prose unless the request clearly asks for revision.
4. Read the target chapter's overview and every scene sheet in `planning/Inheritance_Detailed_Scene_Outline.md`. Read its scene packets in `planning/Inheritance_Scene_Packets.md`, along with the Decisions Log, and any entries for the chapter's scenes in `planning/Gap_Resolutions.md`, which override packet decisions. Read the previous chapter and directly relevant earlier chapters. Then read the bible entries for every character, place, and rule the scene sheets name. See "Story sources" in `AGENTS.md`. Draft scene by scene in outline order, honoring each scene's viewpoint, date and light, carried-forward details, setups, and rules.
5. Read `.agents/roles/chapter-writer.md`.
6. If the harness exposes a named `chapter-writer` specialist, delegate the complete bounded draft to it. Otherwise perform that role directly.
7. Write the chapter to `manuscript/chapters/chapter-N_draft-D.md`, where D is the draft number (1 for a first draft), preserving repository formatting conventions. For a new draft of an existing chapter, move the previous file to `manuscript/drafts/` first.
8. Run `automation/quality-check.sh` on the new chapter file for mechanical signals unless a lifecycle hook already did so.
9. Run `./sync-state.sh`.
10. Report the file, approximate word count, story-state changes, continuity facts, and any downstream concern.

Prefer one coherent chapter over many disconnected scene fragments unless there is a concrete reason to split the work.
