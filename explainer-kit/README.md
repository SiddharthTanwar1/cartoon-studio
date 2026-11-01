# Explanatory visual feature

The backend update is active; refresh the existing Cartoon Studio tab to obtain its new session token. The editor layout is unchanged.

- `demo-sleep/video.mp4`: full sleep scene with a clean central diagram, actual existing voices, captions and animated side characters. Audio was reused from the completed render; no voice generation was requested.
- `EXAMPLE.md`: importable bar-chart demonstration with explicitly illustrative data.
- `bar-example.json`, `line-example.json`, `diagram-example.json`, `picture-example.json`: importable queue examples.
- `preview-bar/video.mp4`, `preview-line/video.mp4`, `preview-diagram/video.mp4`, `preview-picture/video.mp4`: silent three-second renderer checks, not finished narrated scenes.
- `PREVIEWS.png`: a sheet showing all four supported visual types.
- `../human-manual-kit/SCRIPT.md`: updated full script with six diagram scenes. Previously queued copies keep their original version; reimport to render the updated script.
- `../EXPLAINER-SCENES.md`: complete script labels, timing cues, supported inputs and limitations.

Verification: 20 automated checks passed, all three existing full scripts parse, all four visual types encoded to separate MP4s, and the running HTTP importer and preview endpoint accepted the updated script. The generated-picture command and cache were checked using a test runner; no new FLUX illustration was generated during this change. Existing local FLUX installation is reused by that route.
