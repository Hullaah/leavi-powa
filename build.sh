#!/usr/bin/env bash
set -o errexit
uv sync --no-dev --locked
uv run manage.py tailwind build
uv run manage.py collectstatic --no-input
