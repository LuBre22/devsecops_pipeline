#!/usr/bin/env bash
# Compatibility entry point. Windows can run pipeline.py directly.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
exec python3 "$ROOT/scripts/pipeline.py" "$@"
