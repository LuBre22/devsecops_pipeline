#!/usr/bin/env bash
# Stage 7 - Dynamic Application Security Testing with OWASP ZAP.
# Warn-only by policy: baseline scans produce many false positives
# (lecture slide 39), so they inform the triage instead of breaking the build.
STAGE=dast
source "$(dirname "$0")/_common.sh"
start=$(date +%s)

if ! "${RUNTIME}" ps --format '{{.Names}}' | grep -qx "${APP_CONTAINER}"; then
  log "no running test instance, skipping DAST"
  record_time "$STAGE" 0
  exit 0
fi

TARGET="http://${APP_CONTAINER}:8080"
log "ZAP baseline scan against ${TARGET}"

# ZAP writes into /zap/wrk; the raw report directory is mounted there.
"${RUNTIME}" run --rm \
  --network "${TEST_NETWORK}" \
  -v "${RAW_DIR}:/zap/wrk:rw" \
  --user root \
  "${IMG_ZAP}" zap-baseline.py \
    -t "${TARGET}" \
    -J zap.json \
    -r zap.html \
    -m 2 \
    -I \
  || warn "zap-baseline exited non-zero (expected when alerts are found)"

record_time "$STAGE" "$(( $(date +%s) - start ))"
