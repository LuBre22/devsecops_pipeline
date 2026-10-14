#!/usr/bin/env bash
# Stage 1 - Secret scanning with Gitleaks (test class: secrets).
# Fail-fast: cheapest scan first, and any hit blocks unconditionally.
STAGE=secrets
source "$(dirname "$0")/_common.sh"
start=$(date +%s)

log "scanning ${WORKLOAD_DIR} for hardcoded secrets"
# Gitleaks exits 1 when leaks are found. The gate decides pass/fail, not the
# tool, so --exit-code 0 keeps the pipeline in control of the verdict.
run_tool "${IMG_GITLEAKS}" detect \
  --source /src \
  --no-git \
  --report-format json \
  --report-path /out/gitleaks.json \
  --redact \
  --exit-code 0 \
  || warn "gitleaks returned a non-zero exit code"

# Scan the git history too: a rotated secret still leaks from old commits.
if [[ -d "${ROOT}/.git" ]]; then
  log "scanning git history"
  "${RUNTIME}" run --rm --network none \
    -v "${ROOT}:/repo:ro" -v "${RAW_DIR}:/out:rw" \
    "${IMG_GITLEAKS}" detect --source /repo --config /repo/.gitleaks.toml \
      --report-format json --report-path /out/gitleaks-history.json \
      --redact --exit-code 0 || warn "history scan failed, continuing"
fi

count=$(python3 -c "import json;d=json.load(open('${RAW_DIR}/gitleaks.json'));print(len(d) if isinstance(d,list) else 0)" 2>/dev/null || echo 0)
log "found ${count} secret finding(s)"
record_time "$STAGE" "$(( $(date +%s) - start ))"
