#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
export $(grep -v '^#' .env 2>/dev/null | xargs) 2>/dev/null || true
uvicorn app.main:app --reload --port "${PORT:-8000}"
