#!/usr/bin/env bash
# Local pipeline orchestrator.
#
# Runs the same nine stages that GitLab CI runs, so the pipeline can be
# demonstrated without any CI server (NF-04: local demo capability after tool images are available).
#
# Usage:
#   scripts/run-pipeline.sh <workload-path> [--skip-dast] [--keep]
# Example:
#   scripts/run-pipeline.sh workloads/01-flask-api/vulnerable
#
# Exit code 0 = gate passed, 1 = gate failed, 2 = usage or setup error.
set -Eeuo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "${ROOT}"

usage() { sed -n '2,13p' "$0" | sed 's/^# \{0,1\}//'; exit 2; }

[[ $# -lt 1 ]] && usage
WORKLOAD_PATH="$1"; shift
SKIP_DAST=0
KEEP=0
while [[ $# -gt 0 ]]; do
  case "$1" in
    --skip-dast) SKIP_DAST=1 ;;
    --keep)      KEEP=1 ;;
    -h|--help)   usage ;;
    *) echo "unknown option: $1" >&2; usage ;;
  esac
  shift
done

[[ -d "${WORKLOAD_PATH}" ]] || { echo "ERROR: workload not found: ${WORKLOAD_PATH}" >&2; exit 2; }

export WORKLOAD_DIR="$(cd "${WORKLOAD_PATH}" && pwd)"
export WORKLOAD="$(echo "${WORKLOAD_PATH}" | sed 's#^workloads/##; s#/#-#g')"
RUN_ID="$(date +%Y%m%d-%H%M%S)-${WORKLOAD}"
export RUN_DIR="${ROOT}/reports/${RUN_ID}"
export IMAGE_NAME="devsecops-demo-${WORKLOAD}"
export IMAGE_VERSION="$(git rev-parse --short HEAD 2>/dev/null || echo local)"
export IMAGE_TAG="${IMAGE_NAME}:${IMAGE_VERSION}"
export TEST_NETWORK="dso-test-$$"
export APP_CONTAINER="dso-app-$$"

mkdir -p "${RUN_DIR}/raw"

RUNTIME="${CONTAINER_RUNTIME:-}"
if [[ -z "${RUNTIME}" ]]; then
  if command -v docker >/dev/null 2>&1; then RUNTIME=docker
  elif command -v podman >/dev/null 2>&1; then RUNTIME=podman
  else RUNTIME=docker; fi
fi
export CONTAINER_RUNTIME="${RUNTIME}"

cleanup() {
  local code=$?
  if [[ "${KEEP}" -eq 0 ]]; then
    "${RUNTIME}" rm -f "${APP_CONTAINER}" >/dev/null 2>&1 || true
    "${RUNTIME}" network rm "${TEST_NETWORK}" >/dev/null 2>&1 || true
  fi
  return "${code}"
}
trap cleanup EXIT

banner() {
  printf '\n\033[1;36m%s\033[0m\n' "=============================================================="
  printf '\033[1;36m %s\033[0m\n' "$1"
  printf '\033[1;36m%s\033[0m\n' "=============================================================="
}

banner "DevSecOps pipeline | workload=${WORKLOAD} | run=${RUN_ID}"
PIPELINE_START=$(date +%s)

# Stages 1-3 are hard gates on their own: a leaked secret or a blocking SAST
# finding makes every later stage a waste of time (fail fast, fail cheap).
run_stage() {
  local script="$1" required="${2:-required}"
  if ! bash "scripts/stages/${script}"; then
    if [[ "${required}" == "required" ]]; then
      echo "stage ${script} failed" >&2
      bash scripts/stages/08_report.sh || true
      exit 1
    fi
    echo "stage ${script} failed (non-blocking), continuing" >&2
  fi
}

run_stage 01_secrets.sh
run_stage 02_sast.sh
run_stage 03_sca.sh

# Early gate: stop before the expensive build if the cheap scans already block.
python3 scripts/collect.py --run-dir "${RUN_DIR}" --workload "${WORKLOAD}" >/dev/null
if ! python3 scripts/gate.py --findings "${RUN_DIR}/findings.json" \
       --policy policy/thresholds.yaml --suppressions policy/suppressions.json \
       --out "${RUN_DIR}/gate.json"; then
  banner "EARLY GATE FAILED - skipping build, deploy and DAST"
  python3 scripts/report.py >/dev/null
  echo "Report: reports/FINDINGS_REPORT.md"
  exit 1
fi

run_stage 04_build.sh
run_stage 05_image_scan.sh
# Image findings must block before the application is started (secure deploy).
python3 scripts/collect.py --run-dir "${RUN_DIR}" --workload "${WORKLOAD}" >/dev/null
if ! python3 scripts/gate.py --findings "${RUN_DIR}/findings.json" \
       --policy policy/thresholds.yaml --suppressions policy/suppressions.json \
       --out "${RUN_DIR}/gate.json"; then
  banner "IMAGE GATE FAILED - skipping deployment and DAST"
  python3 scripts/report.py >/dev/null
  echo "Report: reports/FINDINGS_REPORT.md"
  exit 1
fi
run_stage 06_deploy_test.sh optional
[[ "${SKIP_DAST}" -eq 0 ]] && run_stage 07_dast.sh optional

set +e
bash scripts/stages/08_report.sh
GATE_EXIT=$?
set -e

[[ "${GATE_EXIT}" -eq 0 ]] && run_stage 09_publish.sh optional

TOTAL=$(( $(date +%s) - PIPELINE_START ))
banner "Pipeline finished in ${TOTAL}s | gate=$([[ ${GATE_EXIT} -eq 0 ]] && echo PASSED || echo FAILED)"
echo "Run artefacts : reports/${RUN_ID}/"
echo "Findings report: reports/FINDINGS_REPORT.md"
echo "Metrics        : reports/metrics.csv"
exit "${GATE_EXIT}"
