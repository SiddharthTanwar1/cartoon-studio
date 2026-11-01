#!/bin/zsh
cd "${0:A:h}"
export PATH="/opt/homebrew/bin:/usr/local/bin:$PATH"
if [[ ! -x .venv/bin/python ]]; then
  echo 'The local environment needs restoring. Run Setup.command once.'
  read '?Press Return to close.'
  exit 1
fi
if /usr/bin/curl -fsS http://127.0.0.1:8768/api/library >/dev/null 2>&1; then
  open http://127.0.0.1:8768
  exit 0
fi
exec .venv/bin/python studio/server.py --open
