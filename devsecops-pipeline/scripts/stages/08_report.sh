#!/usr/bin/env bash
# Stage 8 - Normalise, aggregate, evaluate the gate, render the report.
# Runs always (even after a failed stage) so that findings are never lost.
STAGE=report
source "$(dirname "$0")/_common.sh"
start=$(date +%s)

log "normalising raw reports into the common finding model"
python3 "${ROOT}/scripts/collect.py" --run-dir "${RUN_DIR}" --workload "${WORKLOAD:-unknown}"

log "evaluating the security gate"
set +e
python3 "${ROOT}/scripts/gate.py" \
  --findings "${RUN_DIR}/findings.json" \
  --policy "${ROOT}/policy/thresholds.yaml" \
  --suppressions "${ROOT}/policy/suppressions.json" \
  --out "${RUN_DIR}/gate.json"
GATE_EXIT=$?
set -e

log "rendering findings report and metrics"
python3 "${ROOT}/scripts/report.py" \
  --reports-dir "${ROOT}/reports" \
  --out "${ROOT}/reports/FINDINGS_REPORT.md" \
  --metrics "${ROOT}/reports/metrics.csv"

# Optional: push findings into DefectDojo for central defect management.
if [[ -n "${DEFECTDOJO_URL:-}" && -n "${DEFECTDOJO_TOKEN:-}" ]]; then
  log "importing findings into DefectDojo"
  python3 "${ROOT}/scripts/defectdojo_import.py" --run-dir "${RUN_DIR}" || warn "DefectDojo import failed"
fi

record_time "$STAGE" "$(( $(date +%s) - start ))"
exit "${GATE_EXIT}"
