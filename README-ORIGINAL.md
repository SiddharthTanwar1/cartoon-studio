# Cartoon Studio

A working, local pipeline for short, two-character cartoon dialogue scenes. Built and tested on your M2 MacBook Air with 16 GB memory. No paid model APIs or cloud rendering are used. The original explainer installation is reused for its models and environments, without changing its code.

## Start here

1. Double-click **Start Cartoon Studio.command** in this folder.
2. The editor opens at **http://127.0.0.1:8768**. Keep its Terminal window open.
3. Play the included sample. Replace the dialogue, or open **Paste a script** and enter one `Milo: …` or `Nova: …` turn per line.
4. Set each line’s expression, gesture, camera and pause. Click **Render episode**.
5. Play or download the MP4. **Export episode** saves the reusable script and settings.

The bundled sample is `renders/demo/video.mp4`. Each new render gets a separate folder under `renders/`, containing the MP4, authored episode, subtitle file, soundtrack, shot stills, and quality report. The most recently saved script opens next time.

A second completed example is in `renders/coffee-demo/video.mp4`, with its reusable script in `examples/coffee-machine.json`. Open **Paste a script → Import episode JSON** to switch between the bundled examples. Toggle **Robot prop** to show or hide the sample’s robot.

## What is ready

- Two original, consistent character rigs, with editable clothing, hair and skin colors.
- Seven expressions, eight gestures, blinks, head movement, and animated gesture settling.
- Five mouth states driven by speech energy and approximate word shapes. This is approximate lip sync, not phoneme-perfect lip sync.
- Speaker close-ups, reaction cuts, two-shots and wide reveals. Framing adapts to square, portrait and landscape exports.
- Your local VoxCPM2 generates distinct voices. A saved reference anchors each character’s voice across turns.
- Your local Whisper checks the spoken wording and estimates caption timing. The renderer tries up to two additional takes when a line misses the tighter wording target, selecting the best. Major mismatches stop the export rather than silently accepting garbled dialogue.
- Captions follow short phrases and highlight the current word.
- Your local FLUX generates new sets from the **Cast & set** panel. You can also import background images.
- A reusable robot-vacuum prop and an original synthesized sound effect in the example.
- Cached voices and artwork. Changing acting, captions, or output size does not regenerate unchanged dialogue.
- A **New take** button for a single line. Changing a voice description creates a new voice identity and corresponding cache.
- Local H.264/AAC MP4 export, 24/30 fps through episode JSON, and 480/720/1080-pixel height options.

## Scope and quality

The reference uses hand-authored poses, changing mouth shapes, expressive gestures, shot/reverse-shot editing and an action reveal. This studio reproduces that production structure with reusable original puppets. It does not reproduce the reference’s exact artwork or its custom transforming-car sequence.

The supported repeatable format is one or two standing characters talking on a set. The cast is currently two body designs; changing colors does not create a new body design. Walk cycles, turns into profile, fights, elaborate transformations, new props, and entirely new character designs need additional rig/artwork work. A downloaded video model would not automatically supply those controls or guarantee consistent acting on this 16 GB machine.

The default dialogue checker uses the installed **English** Whisper model. Other-language voices are not a validated workflow here. Write English scripts for the verified path. You author the script; there is no paid or hidden LLM script-generation call.

“No paid APIs” excludes electricity and the cost of the computer you already own. No extra model weights were needed for this setup. New set generation used the existing FLUX weights; speech used the existing VoxCPM2 weights.

## Editing tips

- Aim for 1–2 sentences per turn. A question paired with a reaction pause usually reads better than constant movement.
- Use **speaker** for close dialogue, **reaction** to watch the listener, **two** for a shared beat, and **wide** for a reveal.
- Keep sets at eye level with clear foreground space. Very different perspectives will not match the standing rigs.
- Keep model jobs sequential on this Mac. The editor enforces one job at a time.
- A background takes more compute than rerendering existing actors. Reuse it across episodes.
- The **Height** setting means output height: for example, square 720 is 720×720; portrait 720 is approximately 406×720. Choose 1080 height for a larger portrait export.

## Advanced episode fields

The example JSON is the complete editable format. `characters` supports one or two named actors with `rig` (`mechanic` or `customer`), hex `shirt`, `hair`, and `skin` colors, and a `voice` description. Rename the keys and the matching `speaker` values to rename actors. `prop` may be `robot` or omitted. `captions` can be false.

Each dialogue line supports `speaker`, `text`, `emotion`, `pose`, `shot`, `pause`, and an optional integer `take`. To use your own recording, add `audio` with an absolute local WAV/MP3 path to that line; the recording is checked and timed by the same pipeline. The checker currently expects English.

From this folder:

```sh
.venv/bin/python studio/render.py examples/robot-vacuum.json --out renders/my-episode
```

To rerender only visuals after changing acting, framing or colors in an existing episode (dialogue and pauses must match):

```sh
.venv/bin/python studio/render.py renders/my-episode/episode.json --out renders/my-episode --render-only
```

## Files and recovery

- `studio/`: editor, renderer, original character artwork code, and voice worker.
- `assets/`: garage set, preview poster, and persistent generated voice cache.
- `examples/robot-vacuum.json`: original sample episode.
- `renders/demo/`: completed sample and verification evidence.
- `requirements.txt`: pinned renderer packages.
- `.venv/`: installed isolated renderer environment.
- `Setup.command`: rebuilds the renderer environment if needed; this requires Internet access for free package downloads.

The local model root defaults to `~/AI_EXPLAINER_FACTORY`. Set `CARTOON_MODEL_ROOT` before launching if you deliberately move that installation. Do not move or delete its `envs`, `models`, or Whisper executable while using this studio. The launcher sets the Homebrew path so FFmpeg is found when opening it from Finder.

If you close the editor’s Terminal window, reopen the launcher. If you cancel a job, cached voices and artwork remain available. Rerender the same episode to reuse them. Partial video files are never presented as completed videos.

## Validation

The sample was generated with local models, rendered as an MP4, inspected as shot stills, and checked with FFprobe for video/audio streams, dimensions and duration. All seven final sample dialogue lines matched the authored words in Whisper’s check. This is a speech consistency check, not a guarantee of artistic quality.

Regression tests cover all shot/aspect combinations staying within the set, every expression/gesture rendering, invalid episode rejection, numeric dialogue normalization, silence closing the mouth, and demo timeline/voice consistency:

```sh
.venv/bin/python -m unittest discover -s studio -p 'test_*.py' -v
```

See `VERIFICATION.md` for the final measured exports and editor checks.

## Model sources

- [FLUX.2 Klein 4B MLX](https://huggingface.co/mlx-community/flux2-klein-4b-4bit): existing local image weights.
- [VoxCPM2 4-bit MLX](https://huggingface.co/mlx-community/VoxCPM2-4bit): existing local speech weights.
- [whisper.cpp](https://github.com/ggml-org/whisper.cpp): existing local speech recognition runtime.
- [resvg-py](https://pypi.org/project/resvg-py/): installed SVG rendering package.

Character rig artwork, script, and the generated garage set were created for this studio. No frames, voices, or music from your reference clip are included in the sample.


## Scene queue and full-script import

Use **+ Add scene to queue** to collect scenes, then **Render selected** to process them sequentially. Or use **Upload full script** to import the updated [Ötzi script](otzi-kit/SCRIPT.md). The importer fills cast, sets, props, dialogue and acting; missing sets are generated during rendering and reused when their prompts match. Each scene produces its own MP4. There is no joining stage.

The queue survives restarts. Completed outputs remain saved; failed scenes can be retried independently. Use **Edit → Update queued scene** to change a queued item. Direction controls now include custom arm angles, facial adjustments and head tilt with a still preview. See [SCRIPT-FORMAT.md](SCRIPT-FORMAT.md) for the import format and supported acting controls, or [the updated Ötzi guide](otzi-kit/START-HERE.md).
