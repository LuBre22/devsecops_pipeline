#!/usr/bin/env bash
# Stage 9 - Publish the image and its SBOM. Reached only on a green gate,
# which is what "Secure in Deployment" means in practice.
STAGE=publish
source "$(dirname "$0")/_common.sh"
start=$(date +%s)

if [[ -z "${REGISTRY:-}" ]]; then
  log "REGISTRY not set, skipping publish (local demo mode)"
  record_time "$STAGE" 0
  exit 0
fi

REMOTE="${REGISTRY}/${IMAGE_NAME}:${IMAGE_VERSION}"
log "tagging and pushing ${REMOTE}"
"${RUNTIME}" tag "${IMAGE_TAG}" "${REMOTE}"
"${RUNTIME}" push "${REMOTE}"

if [[ -f "${RAW_DIR}/sbom.cdx.json" ]]; then
  log "storing the SBOM next to the image artefact"
  cp "${RAW_DIR}/sbom.cdx.json" "${RUN_DIR}/${IMAGE_NAME}-${IMAGE_VERSION}.sbom.json"
fi

record_time "$STAGE" "$(( $(date +%s) - start ))"
