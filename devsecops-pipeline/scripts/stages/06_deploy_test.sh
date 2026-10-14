#!/usr/bin/env bash
# Stage 6 - Deploy an ephemeral test instance (zone 3 of the architecture).
# The instance lives on an isolated bridge network, is never exposed to the
# internet and is torn down by the trap in run-pipeline.sh.
STAGE=deploy-test
source "$(dirname "$0")/_common.sh"
start=$(date +%s)

if ! "${RUNTIME}" image inspect "${IMAGE_TAG}" >/dev/null 2>&1; then
  log "no image to deploy, skipping"
  record_time "$STAGE" 0
  exit 0
fi

log "creating isolated network ${TEST_NETWORK}"
"${RUNTIME}" network create "${TEST_NETWORK}" >/dev/null 2>&1 || true

log "starting ${APP_CONTAINER} from ${IMAGE_TAG}"
"${RUNTIME}" run -d --rm \
  --name "${APP_CONTAINER}" \
  --network "${TEST_NETWORK}" \
  --read-only --tmpfs /tmp \
  --cap-drop ALL \
  --security-opt no-new-privileges \
  -e APP_ENV=test \
  -e API_TOKEN="${TEST_API_TOKEN:-injected-at-runtime-not-committed}" \
  "${IMAGE_TAG}" >/dev/null

log "waiting for the health endpoint"
ready=0
for i in $(seq 1 30); do
  if "${RUNTIME}" run --rm --network "${TEST_NETWORK}" \
       "${IMG_PYTHON}" python -c \
       "import urllib.request,sys;urllib.request.urlopen('http://${APP_CONTAINER}:8080/health',timeout=2);sys.exit(0)" \
       >/dev/null 2>&1; then
    ready=1; break
  fi
  sleep 1
done

if [[ "${ready}" -ne 1 ]]; then
  warn "health check failed - dumping container logs"
  "${RUNTIME}" logs "${APP_CONTAINER}" 2>&1 | tail -n 30 || true
  record_time "$STAGE" "$(( $(date +%s) - start ))"
  exit 1
fi

log "test instance is healthy at http://${APP_CONTAINER}:8080"
record_time "$STAGE" "$(( $(date +%s) - start ))"
