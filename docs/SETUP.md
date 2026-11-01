# Setup and operation

## Platform and prerequisites

The original installation targets macOS on Apple Silicon (M2, 16 GB memory). Windows and Linux compatibility has not been established. Required components are Python, FFmpeg/FFprobe, the renderer packages in `requirements.txt`, and a separate local model installation. `Setup.command` prepares only the renderer environment; it does not install all models.

## Renderer

From the repository root, run `zsh Setup.command` or double-click the file. It creates `.venv` and installs the pinned requirements. Network access is needed for package installation. If Finder strips executable permission after a download, run `chmod +x *.command`.

## Model installation contract

The default model root is `~/AI_EXPLAINER_FACTORY`. `CARTOON_MODEL_ROOT` overrides it. The source uses the existing audio and vision environments, VoxCPM2 speech weights, FLUX artwork weights, and whisper.cpp with its English model. Inspect `studio/render.py` and `studio/voices.py` for exact executable/model paths in this snapshot. The root must contain working runtimes as well as weights; pointing at a directory of model files alone is insufficient.

Model names and original upstream references are preserved in [the original guide](../README-ORIGINAL.md). The repository deliberately does not auto-download large weights or choose model licenses on your behalf.

## Launch

```sh
zsh 'Start Cartoon Studio.command'
```

Open `http://127.0.0.1:8768` and keep the Terminal window open. Run heavy jobs sequentially. Import a bundled JSON example before authoring a larger script. The active script and scene queue are generated locally and ignored by Git.

## Output and recovery

Outputs go into `renders/<job>/`. Keep the episode JSON alongside the MP4 to reproduce acting and framing. Reuse voice caches for visual-only changes. Cancelled jobs can leave intermediate files; only completed exports should be used. Do not remove model environments while jobs run.

## Troubleshooting

| Symptom | Check |
|---|---|
| Launcher fails immediately | Python and `.venv`; rerun renderer setup |
| Speech or artwork worker fails | Model root, worker environment, weight files and job log |
| FFmpeg missing | Install FFmpeg and ensure the launcher can find Homebrew binaries |
| Dialogue check rejects a line | Shorten/rephrase the line, inspect pronunciation, request a new take |
| Portrait looks smaller than expected | Quality is output height, not short-edge width |
| Port already in use | Reuse the existing local studio or stop its server before restarting |

The original local setup is not a fully automated clean-machine installer. No claim of fresh end-to-end model generation is made for this publication.
