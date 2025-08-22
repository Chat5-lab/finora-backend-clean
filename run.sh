#!/usr/bin/env bash
set -euo pipefail

# If venv exists, use it straight away
if [ -x ./.venv/bin/python ]; then
  export PIP_CONFIG_FILE=/dev/null PYTHONNOUSERSITE=1
  ./.venv/bin/python -m pip install --upgrade pip
  ./.venv/bin/pip install -r requirements.txt
  # Build metadata for /health
  export BUILD_TIME="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  export GIT_COMMIT="$(git rev-parse HEAD 2>/dev/null || echo unknown)"
  exec ./.venv/bin/python -m uvicorn main:app --host 0.0.0.0 --port "${PORT:-8000}" --reload
fi

# Otherwise create venv with whichever python is available
if command -v python3 >/dev/null 2>&1; then
  python3 -m venv .venv
else
  python -m venv .venv
fi

export PIP_CONFIG_FILE=/dev/null PYTHONNOUSERSITE=1
./.venv/bin/python -m pip install --upgrade pip
./.venv/bin/pip install -r requirements.txt
# Build metadata for /health
export BUILD_TIME="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
export GIT_COMMIT="$(git rev-parse HEAD 2>/dev/null || echo unknown)"
exec ./.venv/bin/python -m uvicorn main:app --host 0.0.0.0 --port "${PORT:-8000}" --reload
