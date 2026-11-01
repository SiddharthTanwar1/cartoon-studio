# Architecture and source map

The application runs locally: a browser editor sends requests to a Python server; job orchestration calls isolated model workers and assembles media with FFmpeg.

## Source modules

- [`server.py`](../studio/server.py) — HTTP routes, local access checks and request handling.
- [`render.py`](../studio/render.py) — speech/render orchestration and media export.
- [`directions.py`](../studio/directions.py) — Supporting implementation; inspect the module for its public functions and dependencies.
- [`script_import.py`](../studio/script_import.py) — authored script parsing.
- [`voices.py`](../studio/voices.py) — local speech-generation worker.
- [`jobs.py`](../studio/jobs.py) — persistent scene queue and job execution.
- [`ensemble.py`](../studio/ensemble.py) — Supporting implementation; inspect the module for its public functions and dependencies.
- [`art.py`](../studio/art.py) — original scene and character artwork.
- [`visuals.py`](../studio/visuals.py) — explanatory visual rendering.
- [`avatars.py`](../studio/avatars.py) — Supporting implementation; inspect the module for its public functions and dependencies.

## State and reproducibility

Source and curated examples are versioned. Model weights, caches, job state and production outputs remain local. Record script/project JSON, model versions and output verification alongside each release-worthy film. Historical examples may contain installation-specific absolute paths; replace these with your own local assets when importing.

## Extending the studio

Read the script format before adding new cues. Keep planning separate from execution, preserve cancellation handling, and update corresponding regression tests when changing parsing, timing, validation or rendering. Review third-party licenses before adding assets. Never commit credentials or runtime environments.
