#!/usr/bin/env bash
# Stage 2 - Static Application Security Testing (test class: sast).
# Semgrep is the gate-relevant scanner; Bandit adds Python-specific depth.
STAGE=sast
source "$(dirname "$0")/_common.sh"
start=$(date +%s)

log "running semgrep (owasp-top-ten, security-audit, secrets rule packs)"
# The registry packs are resolved over the network, hence the bridge network.
# Explicit packs instead of --config=auto keep the run deterministic.
TOOL_NETWORK=bridge run_tool "${IMG_SEMGREP}" semgrep scan \
  --config "p/owasp-top-ten" \
  --config "p/security-audit" \
  --config "p/secrets" \
  --sarif --output /out/semgrep.sarif \
  --metrics off \
  --quiet \
  /src || warn "semgrep reported findings or an error"

if compgen -G "${WORKLOAD_DIR}/*.py" >/dev/null; then
  log "running bandit on python sources"
  "${RUNTIME}" run --rm --network bridge \
    -v "${WORKLOAD_DIR}:/src:ro" -v "${RAW_DIR}:/out:rw" \
    "${IMG_PYTHON}" sh -c \
      'pip install --quiet "bandit[sarif]==1.7.9" >/dev/null 2>&1 && bandit -r /src -f sarif -o /out/bandit.sarif --exit-zero' \
    || warn "bandit run failed, continuing without python-specific findings"
fi

record_time "$STAGE" "$(( $(date +%s) - start ))"
