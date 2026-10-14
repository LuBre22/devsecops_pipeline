#!/usr/bin/env bash
# Stage 3 - Software Composition Analysis and SBOM (test class: sca).
STAGE=sca
source "$(dirname "$0")/_common.sh"
start=$(date +%s)

log "trivy filesystem scan (dependencies, misconfigurations, secrets)"
TOOL_NETWORK=bridge run_tool "${IMG_TRIVY}" filesystem /src \
  --scanners vuln,misconfig,secret \
  --format json --output /out/trivy-fs.json \
  --severity UNKNOWN,LOW,MEDIUM,HIGH,CRITICAL \
  --exit-code 0 \
  --cache-dir /tmp/trivy \
  || warn "trivy fs scan failed"

log "generating CycloneDX SBOM with syft"
TOOL_NETWORK=bridge run_tool "${IMG_SYFT}" scan dir:/src \
  -o "cyclonedx-json=/out/sbom.cdx.json" -q \
  || warn "syft run failed, SBOM unavailable"

record_time "$STAGE" "$(( $(date +%s) - start ))"
