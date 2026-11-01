# Make your 7–8 minute Ötzi documentary

Everything here is a preparation pack. Your saved episode has not been replaced, and no documentary project or movie has been created.

## New: upload the whole film and render a batch

1. Refresh Cartoon Studio. Under **Scene queue**, click **Upload full script** and choose **SCRIPT.md** from this folder.
2. The importer prepares **14 scenes** with their cast, outfits, props, dialogue, set prompts and per-line acting. Review the list, then click **Add imported scenes to queue**. Uploading does not generate anything yet.
3. Since you already rendered scene 1, **uncheck scene 1**. Check scenes 2–14 (or whichever scenes you want now), then click **Render selected**.
4. The app generates a missing background just before it is needed, then renders the scene. The six distinct set prompts are cached and reused across this script and later retries. If you prefer an existing background, click a scene’s **Edit**, choose the image under Cast & set, uncheck **Generate this set during render**, then **Update queued scene**.
5. Each completed scene has **Play** and **Download MP4**. Download them separately. The app performs **no joining, stitching or final-film encoding**.

You can also build scenes manually: configure a scene → **+ Add scene to queue** → configure the next one → add it → **Render selected**. Queued scenes are saved on disk and survive browser refreshes and editor restarts. Stopping preserves completed scenes and caches; select unfinished scenes to continue. A failed scene records its error and the batch continues with the next one. You can retry the failed scene afterward.

To revise a queued scene, **Edit** loads a copy. Finish by clicking **Update queued scene** before starting the batch. Editing a completed scene makes it ready for another render; its previous MP4 remains in its render folder. **Export queue** saves a portable JSON copy that **Upload full script** can also import.

**Direction & custom acting** now appears under every dialogue line. It supports the usual expression, gesture, shot and pause controls plus arm angles, brow tilt, eye openness, resting mouth curve and head tilt. **Preview acting** makes a still preview without voice or video generation. Plain-language cues map to supported presets; complex physical actions, titles and source cards remain editorial work. Keep character voice descriptions unchanged to preserve their cached voice identities.

The original step-by-step instructions below remain useful for manual scene creation. Full-script import replaces the repeated cast/set/paste work. See [the reusable script format](../SCRIPT-FORMAT.md) for future films.

## What is ready

- [Complete script, timing, acting and source notes](SCRIPT.md): 1,082 spoken words, 14 takes, planning runtime about 7:50 at 155 words/minute with the marked pauses.
- [Research and linked primary sources](RESEARCH.md), including the 2023 appearance findings and the 2025 forensic qualification.
- [Cast sheet](CAST.png). Milo and Nova remain your original characters. New presets: Ötzi without cap; the same Ötzi with fur cap and axe; Mira; Officer; and a silent Unknown silhouette. A frozen-body prop completes the opening.
- [Paste-ready dialogue files](dialogue/): numbered 01 through 14. These contain only speaker names and spoken words.
- [Avatar files](../assets/avatars/otzi/): transparent PNGs, editable SVGs, and four acting sheets. The speaking rigs support the app’s expressions, gestures, blinking, and mouth animation. These are reusable vector rigs, not model-generated look-alikes.

## 1. Open the app and preserve what you already have

Open **Start Cartoon Studio.command** as usual. Refresh the browser if the app was already open. Under **Cast & set**, each cast slot now has an avatar dropdown and thumbnail. Near Render, **Prop** offers None, Robot, and Ötzi in ice.

If the editor contains a scene you want to retain, click **Export episode** before replacing dialogue. You will assemble this film by rendering separate takes. The app currently supports up to two cast members per take; it does not provide a long-form timeline or automatic multi-scene assembly.

Use **Landscape · 16:9**, **720 · standard**, captions on. Make a 480-height test first if you want to check delivery cheaply; final clips should all share one format, resolution, and frame rate. Preserve the original episode’s seed and the preset voice descriptions between takes. This helps reuse the same cached character voices. Switching Ötzi’s wardrobe preserves his name and voice description.

## 2. Prepare six reusable backgrounds

Use **Cast & set → Or describe a new cartoon set → Generate set locally**, or import your own images. The installed local model supplies the set; cast members are placed over it separately. Do not request characters in the background. Select the result before rendering each take. These are prompts for you to use, not pre-generated sets.

**A — Alpine discovery** (takes 01 and 14)

> Original flat 2D cartoon alpine mountain pass, blue-grey rock, patches of pale snow and ice, distant jagged peaks, crisp dark outlines, muted teal and warm cream palette, bright overcast daylight. Broad flat empty foreground across the lower third for two standing cartoon actors and a small ice patch. No people, no body, no objects in foreground, no text, landscape composition.

**B — Museum** (02, 04, 05, 09, 12)

> Original flat 2D cartoon archaeology museum interior, warm cream walls, restrained teal display cases in the distant background, soft museum lighting, simple clean shapes, crisp dark outlines. Broad empty floor and uncluttered central wall for two foreground actors. No people, no skeletons, no mummy, no writing or logos, landscape composition.

**C — Mountain refuge, 1991** (03)

> Original flat 2D cartoon alpine refuge reception in 1991, simple wood panelling, small desk in the distant background with a corded landline telephone, paper noticeboard without readable writing, warm amber lighting, crisp dark outlines. Empty foreground for two actors. No people, no computers, no smartphones, no text, landscape composition.

**D — Copper Age mountain slope / rest stop** (06, 08, 13)

> Original flat 2D cartoon alpine foothill clearing, muted green grass, pale rocks, distant mountains and sparse trees, natural daylight, crisp dark outlines, warm earthy palette. Broad flat empty foreground for two actors. No people, no buildings, no modern objects, no lettering, landscape composition.

**E — Equipment display** (07)

> Original flat 2D cartoon archaeology exhibit wall, distant simple silhouettes of a long wooden bow and small stone tools in a recessed display, warm neutral lighting, teal and cream palette, crisp outlines. Clear empty floor and central space for two actors. No people, no labels, no modern camping equipment, landscape composition.

**F — Evidence room** (10 and 11)

> Original flat 2D cartoon research room with a dark teal evidence board in the distant background, several blank cream paper rectangles connected by fine muted lines, soft light, restrained serious atmosphere, crisp outlines. Clear uncluttered foreground for two actors. No people, no weapons, no readable text, no photographs, landscape composition.

Inspect generated backgrounds: discard accidental people, anachronistic equipment, malformed tools, or fake writing. A simple plain set is preferable to inaccurate detail. Reuse D for the lunch scene; narration conveys the food without needing eating animation.

## 3. Build each take

For each numbered take in SCRIPT.md:

1. Set its two cast members with the dropdowns. Choose the correct Ötzi wardrobe. Selection updates the cast names and existing line speaker assignments. Do this **before** pasting dialogue.
2. Choose its background. Set **Prop → Ötzi in ice** only for 01 and 14; set None for the others.
3. Open the matching numbered `.txt` file. Copy its entire contents into **Paste a script** and click **Use this dialogue**. Names must match exactly: `Milo`, `Nova`, `Mira`, `Officer`, `Otzi`, `Unknown`. Unknown never speaks.
4. Set the episode title to `Otzi 01`, `Otzi 02`, etc. Follow the take’s direction notes for Expression, Gesture, Camera, and Pause. Start with 0.25-second pauses. Increase a punchline’s pause to about 0.6–1.0 seconds where useful.
5. Click **Render episode**, listen, and inspect. **New take** retries a bad delivery on that line; it does not require rewriting the dialogue. Avoid repeating this unnecessarily because local generation costs time.
6. Download the MP4 as `01.mp4`, `02.mp4`, etc. Also **Export episode** and name it `01.json`, etc., so you can restore and revise that take. Save downloads into a folder you choose.

If a dropdown refuses a duplicate name, change the other slot first. You cannot put two Otzi presets in the same take because both represent the same person.

For take 11, choose **Mira + Unknown** and paste only Mira’s lines. The second slot is a silent evidence symbol, not an extra speaker. For the discovery, use a **wide** shot to keep the ice prop visible; a close-up may crop it naturally.

## 4. Direct the comedy

Deliver the factual lines clearly. Let Nova be dry, Milo earnest, Ötzi mildly offended, and Mira quietly amused. Avoid exaggerated laughter after every joke. The voice model follows text and the character voice description; expression and gesture controls animate the rig, not a guaranteed vocal emotion.

Use `speaker` for narration and punchlines, `two` for exchanges, and `wide` for setting or clothing reveals. A `reaction` shot shows the listener while the current line is still heard; use it deliberately. The rigs do not walk, pick up bodies, eat, fight, or fire arrows. Stage those ideas through dialogue, cuts, and simple illustrations.

The existing hikers have contemporary cartoon clothes. Treat them as comedic stand-ins, not exact 1991 reconstructions. The generic Officer uniform is also illustrative. Keep an onscreen “Fictional reenactment” note in the final edit. Titles, labels, music, sound effects, and end cards are added in your finishing editor; Cartoon Studio’s current UI does not add them automatically.

If the speech model mispronounces Ötzi, first audition the line with `Uht-see` in the spoken text. Captions use authored text, so restore conventional spelling in the finishing edit. Do not alter the `Otzi:` speaker prefix.

## 5. Assemble and hit 7–8 minutes

Place clips 01–14 in order in your preferred video editor. Add a 4-second opening card and about 11 seconds of closing/source cards. SCRIPT.md gives the card text. Keep visual transitions short; a hard cut often lands a joke better than a long dissolve.

The updated estimate is **1,082 words ÷ 155 words/minute + 35.65 seconds of marked pauses + 15 seconds of cards ≈ 7:50**. At 150 words/minute it is about 8:03; shorten the closing card or pauses slightly if needed. These are estimates, not measured render durations. Check the actual timeline after you generate the clips.

- If under 7 minutes: add useful visual holds and readable source cards, up to the target; do not fill the gap with random silence.
- If over 8 minutes: shorten pauses and trim an optional joke, such as the barber reply or the LinkedIn comparison. Preserve the discovery attribution, appearance qualification, and uncertain death mechanism.
- Keep dialogue louder than any music. No music is necessary for this format. Use only audio you have permission to publish.

For a simple straight join of matching MP4s, the app’s existing FFmpeg installation can also join them. This adds no cards or music. Put `01.mp4` through `14.mp4` in one folder, open Terminal in that folder, and run:

```sh
python3 - <<'PY'
from pathlib import Path
names = [f'{i:02}.mp4' for i in range(1, 15)]
missing = [n for n in names if not Path(n).is_file()]
if missing:
    raise SystemExit('Missing clips: ' + ', '.join(missing))
Path('clips.txt').write_text(''.join("file '" + n + "'\n" for n in names))
PY
ffmpeg -f concat -safe 0 -i clips.txt -c copy -movflags +faststart otzi-joined.mp4
```

If FFmpeg reports incompatible streams, re-export the mismatched take with the same settings before joining. Preview the joined result for audio continuity and captions. The command does not overwrite an existing output without prompting.

## 6. Publish accurately

Use a description such as: “A comedy documentary about Ötzi. Conversations and character performances are fictional; archaeological claims are based on museum material and published research. Appearance reflects 2023 genome research; the discussion of death includes a 2025 forensic reassessment.” Paste the source links from RESEARCH.md below it.

No paid service was used to create this cast pack. Rendering and local background generation use your installed models and computer; there are no per-clip API charges in this workflow. Runtime, electricity, and available storage still matter. The pack does not promise photorealistic movement or perfect voice delivery.
