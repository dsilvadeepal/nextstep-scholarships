#!/bin/sh
set -eu
uv sync --locked --no-dev
npm --prefix frontend ci
npm --prefix frontend run build
