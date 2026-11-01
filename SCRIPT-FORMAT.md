# Full-script import and scene queue

Choose **Upload full script** in Cartoon Studio’s Scene queue. Import accepts Markdown, plain text using this same layout, or an exported queue JSON. This is a local parser: it does not spend model credits or treat notes as executable instructions.

Use one numbered level-two heading per scene and an explicit **Dialogue** heading. One or two installed characters are supported per scene. All scene lines must fit the app’s 400-character-per-turn limit; break long speeches into successive turns by the same speaker. You can queue many separate scenes; there is no small scene-count limit. Upload size is limited to 2 MB.

```markdown
# My film

## Scene 1: A discovery

**Cast:** Milo + Nova
**Set:** Alpine pass
**Set prompt:** Flat 2D cartoon alpine pass, snow and rock, clear empty foreground, no people, no text.
**Prop:** otzi_ice
**Direction:** A surprised opening with a dry reply. Editorial notes are not spoken.
**Acting:** expression=neutral; gesture=present; camera=speaker; pause=0.25

### Dialogue

Nova: Is that somebody lying in the ice?
@direction: expression=surprised; gesture=question; camera=wide; pause=0.4

Milo: I think our walk just became a documentary.
@direction: expression=deadpan; gesture=shrug; camera=speaker; pause=0.7; head_tilt=4

### Notes

This is a fictional reenactment.

## Scene 2: At the museum

**Cast:** Mira + Otzi
**Avatars:** Otzi=otzi_travel
**Background:** garage.png
**Prop:** none
**Acting:** expression=neutral; gesture=present; camera=two; pause=0.25

### Dialogue

Mira: This placeholder set can be changed before rendering.
Otzi: Please select somewhere with heating.
@direction: expression=deadpan; gesture=present; head_tilt=-5; brow_tilt=4
```

Use **Set prompt** to generate and cache a set during the batch. Use **Background** with an existing filename to reuse an imported set. If both are present, the prompt takes priority. A bare **Set** name can produce a basic prompt, but the importer warns you to review it. Identical prompts share one generated image. Deliberately changing a prompt produces a separate set.

Available cast: **Milo, Nova, Otzi, Mira, Officer, Unknown**. “Ötzi” is accepted as a cast name and normalised to Otzi. Unknown is a silent silhouette. Avatar overrides: `milo`, `nova`, `otzi`, `otzi_travel`, `mira`, `officer`, `unknown`. Use the two Ötzi variants for the same identity in different scenes.

Props: `none`, `robot`, `otzi_ice`. Optional scene fields: **Format:** landscape / square / portrait; **Resolution:** 480 / 720 / 1080. Imports default to landscape, 720, captions on, and a stable voice seed.

`@direction` follows the dialogue line it controls. It never becomes speech. **Acting** supplies defaults for that scene. **Direction** preserves readable notes; without an Acting field, recognisable cues are mapped to presets and uncertain cues are flagged. Exact controls override prose interpretation.

| Control | Values |
|---|---|
| expression / emotion | neutral, happy, proud, skeptical, worried, surprised, deadpan |
| gesture / pose | rest, present, question, point, shrug, hips, wave, fold |
| camera / shot | speaker, reaction, two, wide |
| pause | 0–5 seconds |
| left_shoulder, right_shoulder | −150 to 150 degrees |
| left_elbow, right_elbow | −160 to 160 degrees |
| brow_tilt | −15 to 15 |
| eye_open | 0.25 to 1.5 |
| mouth_curve | −18 to 18; resting mouth only |
| head_tilt | −20 to 20 degrees |

Custom numeric values modify the real rig and can be mixed with presets. Changing a gesture or expression preset in the editor clears corresponding custom overrides. The axe outfit keeps its left arm in its holding pose. The Unknown silhouette has no facial or limb acting. Voice delivery still comes from the voice description and dialogue; these controls animate the artwork.

Upload parses and previews scenes; **Add imported scenes to queue** saves them. **Render selected** is the only batch-start action. One local generation/render process runs at a time. Completed scenes are not automatically rendered again. To render a revised completed scene, edit and update it first.

The queue is saved in `scene-queue.json`. Outputs remain in separate `renders/scene-…/` folders, each with its own MP4, episode file and log. Stop cancels the current job and leaves subsequent scenes pending. Restarted interrupted scenes are available to retry. Failures do not discard completed work or prevent later scenes from running. This workflow does not create a combined movie.

## Explanatory visuals

See [EXPLAINER-SCENES.md](EXPLAINER-SCENES.md) for **Scene type: explainer**, central diagrams, sourced charts, explanatory pictures, and dialogue-timed `@visual` cues. Existing script imports, queues, previews and renders support these fields without new UI controls. The cast catalog also includes Ellie, Jun, Anaya, Malik and Rowan.
