#!/usr/bin/env bash
# Shared helpers for all stage scripts. Sourced, never executed directly.
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
: "${RUN_DIR:?RUN_DIR must be set by run-pipeline.sh}"
: "${WORKLOAD_DIR:?WORKLOAD_DIR must be set by run-pipeline.sh}"
RAW_DIR="${RUN_DIR}/raw"
mkdir -p "${RAW_DIR}"

# Container runtime: docker or podman, whichever is present.
RUNTIME="${CONTAINER_RUNTIME:-}"
if [[ -z "${RUNTIME}" ]]; then
  if command -v docker >/dev/null 2>&1; then RUNTIME=docker
  elif command -v podman >/dev/null 2>&1; then RUNTIME=podman
  else echo "ERROR: neither docker nor podman found" >&2; exit 2; fi
fi

# Pinned tool images - reproducibility (NF-01). Never use :latest.
IMG_GITLEAKS="${IMG_GITLEAKS:-zricethezav/gitleaks:v8.18.4}"
IMG_SEMGREP="${IMG_SEMGREP:-returntocorp/semgrep:1.86.0}"
IMG_PYTHON="${IMG_PYTHON:-python:3.12-slim}"
IMG_TRIVY="${IMG_TRIVY:-aquasec/trivy:0.55.2}"
IMG_SYFT="${IMG_SYFT:-anchore/syft:v1.14.0}"
IMG_DOCKLE="${IMG_DOCKLE:-goodwithtech/dockle:v0.4.14}"
IMG_HADOLINT="${IMG_HADOLINT:-hadolint/hadolint:2.12.0-alpine}"
IMG_ZAP="${IMG_ZAP:-ghcr.io/zaproxy/zaproxy:2.15.0}"

log()  { printf '\033[1;34m[%s]\033[0m %s\n' "${STAGE:-stage}" "$*"; }
warn() { printf '\033[1;33m[%s] WARN\033[0m %s\n' "${STAGE:-stage}" "$*"; }

# Run a tool container with the workload mounted at /src and reports at /out.
# Default network is "none"; stages that need rule feeds override TOOL_NETWORK.
run_tool() {
  local image="$1"; shift
  "${RUNTIME}" run --rm \
    --network "${TOOL_NETWORK:-none}" \
    -v "${WORKLOAD_DIR}:/src:rw" \
    -v "${RAW_DIR}:/out:rw" \
    -w /src \
    "${image}" "$@"
}

# Record the duration of a stage into timings.json (metric F-09).
record_time() {
  local stage="$1" seconds="$2"
  python3 - "$RUN_DIR/timings.json" "$stage" "$seconds" <<'PY'
import json, pathlib, sys
p = pathlib.Path(sys.argv[1])
data = json.loads(p.read_text()) if p.exists() else {}
data[sys.argv[2]] = int(float(sys.argv[3]))
p.write_text(json.dumps(data, indent=2))
PY
}
