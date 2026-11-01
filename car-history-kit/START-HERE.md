# From Steam to Software — production guide

## Use this script

1. Open Cartoon Studio and choose **Upload full script**.
2. Select **SCRIPT.md** from this folder.
3. Review the 33 imported scenes, then add them to the queue.
4. Select the new scenes you want and use **Render selected**. They render one at a time as separate MP4s.
5. Join the clips in your editor. Add your title, chapter transitions and source credits there.

The script has 3,925 spoken words and 208 dialogue turns. At 150 words per minute plus the marked pauses, estimated dialogue runtime is 27 minutes 32 seconds. Allow approximately 28–30 minutes with chapter/title/source cards and your preferred edit. This is an estimate; no new speech or full video was rendered while writing the kit.

This is intentionally longer than the earlier eight-minute videos: compressing both the history and the mechanical explanations into eight minutes would remove much of the detail requested. It is one documentary with chapters, not a set of unrelated shorts.

## What is included

- SCRIPT.md: full importable script, with cast, layouts, explicit Dialogue sections, acting and visual cues.
- READING-COPY.md: comfortable dialogue-only reading copy. Not the full-script upload file.
- RESEARCH.md: 48 source entries with links and qualifications, covering history, engineering and calculated charts.
- CHAPTERS.md: scene list and approximate start times. Replace these with measured times for a final YouTube description.
- dialogue/01.txt through dialogue/33.txt: individual dialogue reference files.
- VISUAL-PREVIEW.png: selected previews from the actual visual renderer.
- VALIDATION.json: importer and scene validation result.

## Visual design

The 28 explainer scenes contain 26 animated step/highlight diagrams and two bar charts. The remaining five scenes use conversational framing. Existing `explainer-stage.png` and `garage.png` backgrounds are reused. No new backgrounds, historical photos, image models, voices or avatar designs need downloading. Local speech generation is still required when you render.

The charts show a sourced historical assembly-time comparison and a calculated kinetic-energy comparison. The diagrams are intentionally simplified conceptual visuals, not physically animated engine simulations. They do not require features beyond the current backend. Characters remain at the sides of the centre board. Individual @visual cues start reveals with the corresponding dialogue line.

Long speeches stay below the app's 400-character limit. Custom directions use only installed expressions and gestures. Each scene has no more than two installed characters.

## Chapter groups

- Scenes 1–4: steam, the combustion breakthrough and Bertha Benz.
- Scenes 5–12: the engine, electrics, cooling, gears, steering and diesel.
- Scenes 13–18: early propulsion rivals, production, automatic transmissions, tyres and braking.
- Scenes 19–24: safety, electronics, emissions, turbocharging and wider adoption.
- Scenes 25–29: hybrids, regeneration, modern EVs and battery chemistry.
- Scenes 30–33: charging, efficiency, software and the closing recap.

The narrative returns briefly to earlier dates when a mechanical topic spans decades. Those are explicit parallel-history explanations, not claims that one technology disappeared when another arrived.

## Voice and edit notes

- Cugnot: approximately “koo-NYOH”.
- Pforzheim: approximately “PFORTS-hyme”.
- Nicolaus Otto: “NIK-oh-lows OT-oh”.
- Bertha Benz: use a natural English pronunciation; no exaggerated accent.
- Read abbreviations as letters where natural: ABS, ESC, CVT, AC, DC. The script expands technical terms in the explanation.
- Use brief pauses after jokes. Keep core explanations clear rather than performing every line as a punchline.
- Retain source captions and qualifications, especially on the charts. The kinetic-energy graph is not a braking-distance test.
- Dates in speech are written out for local voice generation. Numeric dates in scene titles are editorial labels, not dialogue.

Project and queue state were not changed. This folder contains the new script kit only; rendering and final joining remain under your control.
