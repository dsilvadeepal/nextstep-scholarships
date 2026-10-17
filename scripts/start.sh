#!/bin/sh
set -eu
exec uv run --no-sync uvicorn nextstep.app:app --host 0.0.0.0 --port "${PORT:-8000}" --no-access-log
