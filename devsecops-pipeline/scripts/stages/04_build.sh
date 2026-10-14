#!/usr/bin/env bash
# Stage 4 - Dockerfile lint and container image build (test class: image).
STAGE=build
source "$(dirname "$0")/_common.sh"
start=$(date +%s)

DOCKERFILE="${WORKLOAD_DIR}/Dockerfile"
if [[ ! -f "${DOCKERFILE}" ]]; then
  log "no Dockerfile in workload, skipping build stage"
  record_time "$STAGE" 0
  exit 0
fi

log "linting Dockerfile with hadolint"
"${RUNTIME}" run --rm --network none -i \
  "${IMG_HADOLINT}" hadolint --format sarif - < "${DOCKERFILE}" \
  > "${RAW_DIR}/hadolint.sarif" || warn "hadolint reported findings"

log "building image ${IMAGE_TAG}"
"${RUNTIME}" build --pull -t "${IMAGE_TAG}" "${WORKLOAD_DIR}"

record_time "$STAGE" "$(( $(date +%s) - start ))"
