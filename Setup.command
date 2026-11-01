#!/bin/zsh
set -e
cd "${0:A:h}"
base="${CARTOON_MODEL_ROOT:-$HOME/AI_EXPLAINER_FACTORY}"
"$base/envs/core/bin/python" -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
chmod +x "Start Cartoon Studio.command"
echo 'Cartoon Studio is ready. Open Start Cartoon Studio.command.'
