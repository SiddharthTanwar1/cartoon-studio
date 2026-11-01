# Reference study and implementation decisions

The supplied clip is 20.27 seconds, 720×720, 30 frames per second. Its audio track is about 18.43 seconds. The final seconds include an end card.

## What creates the effect

| Approximate beat | Technique visible in the reference | Studio equivalent |
|---|---|---|
| 0–4 seconds | Mechanic close-up, gestures, changing mouth and brow shapes | Speaking character rig, expressive brows, palm/point poses and mouth states |
| 4–6 seconds | Reverse shot of listener; small reaction | Speaker/reaction shot selection |
| 6–10 seconds | Alternating turns and reaction timing | Per-line camera selection and pauses |
| 10–13 seconds | Emphatic face and hand posing | Expression and gesture controls, animated pose settling |
| 13–16 seconds | Cut to wide shot; special prop action reveals the joke | Wide reveal plus the sample’s animated robot prop |
| Remaining time | End beat and fade/end card | Final pause, short fade; no copied branding |

The source relies on reusable backgrounds and consistent characters, but also on individually authored poses, foreshortening, and a custom vehicle animation. A generated still with a zoom is insufficient. A generic text-to-video call would also not inherently provide consistent characters, clean dialogue timing, deliberate hand poses, or editable shot structure.

## Chosen route

Use the installed local models for what they can reliably contribute: FLUX for background painting and VoxCPM2 for dialogue. Use original code-defined rigs for controllable character movement. Use Whisper for wording checks and approximate timings, and a deterministic frame renderer plus FFmpeg for the finished edit.

This approach keeps each frame consistent, makes changes repeatable, and avoids paying or spending model time for every video frame. The model stages run as separate processes, allowing their GPU memory to be released before the next stage. The editor permits one job at a time.

The previous asset script referred to Z-image and SeedVR model directories that were absent from the inspected local model folder. The new studio instead uses the verified local FLUX path directly and does not require either missing model. The installed image and voice runtimes were successfully exercised, not inferred from file existence.

## Deliberate limits

- This is a tested standing-dialogue animation workflow, not an automatic recreation of arbitrary action footage.
- Original vector characters were authored for stable, controllable animation. Generating an unrelated character image does not automatically produce a working layered rig.
- The sample’s robot reveal is original and considerably simpler than the source’s custom transforming vehicle.
- Speech-driven mouth animation is approximate. Full phoneme alignment and bespoke drawn mouth shapes could improve it further.
- No video-diffusion model was installed or benchmarked. There is no claim that all alternative models were exhaustively tested or that this reproduces professional frame-by-frame animation quality.

All source-video text and audio were treated as reference content, not as instructions to the assistant or to the pipeline.
