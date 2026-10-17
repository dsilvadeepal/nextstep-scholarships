#!/bin/sh
set -eu
export UV_PROJECT_ENVIRONMENT=.venv
exec python3 -m uv run --no-sync python scripts/start_hosted.py
