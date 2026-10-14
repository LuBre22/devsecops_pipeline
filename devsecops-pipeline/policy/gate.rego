# Optional OPA/Conftest variant of the gate (architecture decision AD-5).
# Run with:  conftest test reports/<run>/findings.json --policy policy/
package devsecops.gate

blocking_severity := {
  "secrets": {"CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"},
  "sast":    {"CRITICAL", "HIGH"},
  "sca":     {"CRITICAL"},
  "image":   {"CRITICAL", "HIGH"},
  "dast":    set(),
}

deny[msg] {
  finding := input.findings[_]
  not finding.false_positive
  severities := blocking_severity[finding.test_class]
  severities[finding.severity]
  msg := sprintf("[%s] %s %s at %s", [finding.severity, finding.tool, finding.rule_id, finding.location])
}
