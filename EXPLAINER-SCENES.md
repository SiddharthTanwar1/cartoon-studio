# Explanatory scenes — same editor, new script labels

Upload Markdown as before, add imported scenes to the queue, select and render. No new front-end controls. Existing dialogue scenes remain compatible. The existing **Preview acting** button also previews explanatory compositions; it does not run an image generator.

An explainer keeps a board in the middle 60% of the landscape frame and one character on each side. Captions remain below it. The camera stays on this layout even if dialogue directions request close-ups. Gestures, expressions and speech animation still work. One-character explainers keep the character at the left. Use **Prop: none** and **Format: landscape**.

## Animated chart example

```markdown
## Scene 1: Read the comparison
**Cast:** Mira + Milo
**Background:** explainer-stage.png
**Scene type:** explainer
**Visual:** bar
**Visual title:** Example values — not a study
**Visual unit:** units
**Visual source:** Illustrative data, not research findings
**Visual caption:** Replace with verified values before citing a study.
**Visual data:** {"labels":["Example A","Example B"],"values":[2,5]}
**Visual animation:** reveal
**Prop:** none
**Format:** landscape
**Resolution:** 720
**Acting:** expression=neutral; gesture=present; camera=wide; pause=0.3

### Dialogue
Mira: First, look at example A.
@direction: expression=neutral; gesture=point
@visual: 1
Milo: Now we can compare it with example B.
@visual: 2
### Notes
These values demonstrate the renderer. They are not study results.
```

## Fields

- **Scene type:** `explainer` is the explicit routing label. Omit it for ordinary dialogue.
- **Visual:** `bar`, `line`, `diagram` or `picture`.
- **Visual title:** up to 75 characters.
- **Visual caption:** optional explanatory text, up to 130 characters.
- **Visual source:** short visible attribution, up to 150 characters. Required for graphs. Put full links, limitations and bibliographic detail in research notes. Mark invented demonstration values as illustrative.
- **Visual animation:** `reveal` (default) or `none`.
- **Visual data:** a single-line JSON object. Never executable code.
- **Visual unit:** required for charts, for example `hours` or `percent`.

Bar charts: `{"labels":["A","B"],"values":[2,5]}`. One to six categories, matching finite nonnegative values. Zero baseline; exact final value labels. One series.

Line charts: the same fields, two to twelve points; negative values allowed. Categories are evenly spaced, so use this only for equal intervals or ordered categories. Axes show the range including zero. One series. No error bars, confidence bands, multiple series or irregular numeric x coordinates yet. Do not force a study into an unsuitable graph.

Diagrams: `{"nodes":["Input","Process","Result"]}`. Two to six steps, at most 60 characters each. Steps are numbered in reading order, with arrows between neighbours in each row. New steps highlight as they are explained; neutral outlines keep context visible. This is a sequence diagram, not an arbitrary anatomical drawing or freeform node graph.

Pictures: either **Visual image:** `visuals/my-picture.png` (relative to the project's `assets` folder; PNG/JPG/WebP), or **Visual prompt:** a 10–2000-character description. The existing background upload can import a picture; use the resulting `set-....png` filename as Visual image and keep Background as your stage. Local files outside assets and remote image URLs are not accepted. No automatic downloads.

A Visual prompt routes to the existing local FLUX model, caches the result, and contains it within the board without cropping. An explicit Visual image takes precedence. Generated illustrations are not evidence or precise medical diagrams: label them as illustrations and review them. Use supplied vetted images for anatomy and originals for study figures; do not ask image models to invent labels or research values. Text is drawn separately by the renderer.

## Synchronise with dialogue

`@visual: 1` reveals the first bar/point or highlights the first diagram step when that dialogue begins. `@visual: 2` reveals through the second, and so on. Transitions last 0.8 seconds; the state persists through lines without cues. Zero resets to the initial state. For pictures, use 0 or 1 for fade out/in. `none` shows the finished visual immediately and ignores reveal cues.

Without cues, reveal runs once over the opening 2.5 seconds. Cues use generated dialogue timing, not guessed timestamps. All cues and metadata remain outside speech. Edits, saved episodes and queue exports retain them. Editing dialogue text in the existing editor retains a line's cue; replacing all dialogue via the plain-dialogue paste box replaces the lines and therefore their cues. Reimport the full script to restore authored visual cues.

## Rendering routes and cost

- Bar/line: local data drawing and frame animation, no model calls.
- Diagram: local vector-style drawing and highlights, no model calls.
- Picture file: local image compositing, no model calls.
- Picture prompt: the installed local FLUX generator, once per cached prompt.
- Voices and character animation: the existing pipeline.

No paid API is added. Every scene stays an independent MP4. No joining step. This does not change the installed models or UI.
