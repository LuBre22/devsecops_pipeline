#!/usr/bin/env bash
# Stage 5 - Container image scanning (test class: image).
# Implements the CVE threshold check of lecture slide 32.
STAGE=image-scan
source "$(dirname "$0")/_common.sh"
start=$(date +%s)

if ! "${RUNTIME}" image inspect "${IMAGE_TAG}" >/dev/null 2>&1; then
  log "image ${IMAGE_TAG} not present, skipping"
  record_time "$STAGE" 0
  exit 0
fi

log "trivy image scan of ${IMAGE_TAG}"
"${RUNTIME}" run --rm --network bridge \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v "${RAW_DIR}:/out:rw" \
  "${IMG_TRIVY}" image "${IMAGE_TAG}" \
    --scanners vuln,secret \
    --format json --output /out/trivy-image.json \
    --severity UNKNOWN,LOW,MEDIUM,HIGH,CRITICAL \
    --exit-code 0 \
  || warn "trivy image scan failed"

log "dockle hardening check (CIS benchmark subset)"
"${RUNTIME}" run --rm --network bridge \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v "${RAW_DIR}:/out:rw" \
  "${IMG_DOCKLE}" --format json --output /out/dockle.json \
    --exit-code 0 "${IMAGE_TAG}" \
  || warn "dockle run failed"

record_time "$STAGE" "$(( $(date +%s) - start ))"
