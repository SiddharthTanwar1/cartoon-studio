# Publication validation · 1 November 2026

Validation ran on isolated publication copies using the original installed Python environments. The active studios and production queues were not modified.

## Python regression suite

Command: `python -m unittest discover -s studio -p 'test_*.py' -v` using the installed Cartoon Studio environment.

**18 passed; 2 failed due to unavailable historical demo media.** `test_demo_has_real_audio_and_matching_timeline` requires `renders/demo/soundtrack.wav`, which is absent in the original installation. `test_voice_manifest_matches_script` requires voice-cache WAV files at historical absolute paths, also absent. The parsing, direction, geometry, queue and visual tests passed. These two checks were not removed, weakened or marked as passing.

The retained demo reports are historical evidence, not complete rerenderable media bundles. Regenerate the sample and its voice cache before rerunning those media-dependent checks. No new full model-generation run was performed.
