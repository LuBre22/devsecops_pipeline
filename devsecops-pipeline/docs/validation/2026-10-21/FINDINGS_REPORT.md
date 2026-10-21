# Findings Report - DevSecOps Pipeline

## 1. Run overview

| Run | Workload | Branch | Commit | Tools | Findings | Gate |
|---|---|---|---|---|---|---|
| 20261021-080607-01-flask-api-vulnerable | 01-flask-api-vulnerable | unknown | unknown | 4 | 35 | FAIL |
| 20261021-080826-01-flask-api-fixed | 01-flask-api-fixed | unknown | unknown | 7 | 309 | FAIL |
| 20261021-081124-02-cli-deps-vulnerable | 02-cli-deps-vulnerable | unknown | unknown | 4 | 41 | FAIL |
| 20261021-081233-02-cli-deps-fixed | 02-cli-deps-fixed | unknown | unknown | 4 | 19 | FAIL |
| 20261021-081442-03-container-service-vulnerable | 03-container-service-vulnerable | unknown | unknown | 4 | 15 | FAIL |
| 20261021-081626-03-container-service-fixed | 03-container-service-fixed | unknown | unknown | 8 | 6 | PASS |

## 2. Findings per severity and test class

### 20261021-080607-01-flask-api-vulnerable - 01-flask-api-vulnerable

| Test class | CRITICAL | HIGH | MEDIUM | LOW | INFO |
|---|---|---|---|---|---|
| sast | 0 | 7 | 9 | 0 | 0 |
| sca | 0 | 4 | 12 | 3 | 0 |
| **total** | 0 | 11 | 21 | 3 | 0 |

### 20261021-080826-01-flask-api-fixed - 01-flask-api-fixed

| Test class | CRITICAL | HIGH | MEDIUM | LOW | INFO |
|---|---|---|---|---|---|
| image | 1 | 48 | 94 | 147 | 3 |
| sast | 0 | 0 | 3 | 3 | 0 |
| sca | 0 | 0 | 9 | 1 | 0 |
| **total** | 1 | 48 | 106 | 151 | 3 |

### 20261021-081124-02-cli-deps-vulnerable - 02-cli-deps-vulnerable

| Test class | CRITICAL | HIGH | MEDIUM | LOW | INFO |
|---|---|---|---|---|---|
| sast | 0 | 2 | 2 | 0 | 0 |
| sca | 3 | 14 | 17 | 3 | 0 |
| **total** | 3 | 16 | 19 | 3 | 0 |

### 20261021-081233-02-cli-deps-fixed - 02-cli-deps-fixed

| Test class | CRITICAL | HIGH | MEDIUM | LOW | INFO |
|---|---|---|---|---|---|
| sca | 1 | 9 | 7 | 2 | 0 |
| **total** | 1 | 9 | 7 | 2 | 0 |

### 20261021-081442-03-container-service-vulnerable - 03-container-service-vulnerable

| Test class | CRITICAL | HIGH | MEDIUM | LOW | INFO |
|---|---|---|---|---|---|
| sast | 0 | 0 | 1 | 3 | 0 |
| sca | 0 | 1 | 0 | 1 | 0 |
| secrets | 9 | 0 | 0 | 0 | 0 |
| **total** | 9 | 1 | 1 | 4 | 0 |

### 20261021-081626-03-container-service-fixed - 03-container-service-fixed

| Test class | CRITICAL | HIGH | MEDIUM | LOW | INFO |
|---|---|---|---|---|---|
| dast | 0 | 0 | 1 | 1 | 1 |
| image | 0 | 0 | 1 | 0 | 1 |
| sast | 0 | 0 | 1 | 0 | 0 |
| **total** | 0 | 0 | 3 | 1 | 2 |

## 3. Findings detail (blocking and high severity)

### 20261021-080607-01-flask-api-vulnerable

| Severity | Tool | Rule / CVE | Location | Title | Remediation |
|---|---|---|---|---|---|
| HIGH | Bandit | B201 | file:///src/app.py:71 | A Flask app appears to be run with debug=True, which exposes the Werkzeug debugg | See rule documentation |
| HIGH | Bandit | B324 | file:///src/app.py:65 | Use of weak MD5 hash for security. Consider usedforsecurity=False | See rule documentation |
| HIGH | Bandit | B605 | file:///src/app.py:57 | Starting a process with a shell, possible injection detected, security issue. | See rule documentation |
| HIGH | Semgrep OSS | python.django.security.injection.command.command-injection-os-system.command-injection-os-system | /src/app.py:56 | Request data detected in os.system. This could be vulnerable to a command inject | See rule documentation |
| HIGH | Semgrep OSS | python.flask.security.injection.os-system-injection.os-system-injection | /src/app.py:57 | User data detected in os.system. This could be vulnerable to a command injection | See rule documentation |
| HIGH | Semgrep OSS | python.flask.security.injection.tainted-sql-string.tainted-sql-string | /src/app.py:40 | Detected user input used to manually construct a SQL string. This is usually bad | See rule documentation |
| HIGH | Semgrep OSS | python.lang.security.dangerous-system-call.dangerous-system-call | /src/app.py:57 | Found user-controlled data used in a system call. This could allow a malicious a | See rule documentation |
| HIGH | trivy-fs | CVE-2023-25577 | requirements.txt -> Werkzeug | Werkzeug 2.0.1: python-werkzeug: high resource usage when parsing multipart form | Upgrade to 2.2.3 |
| HIGH | trivy-fs | CVE-2023-30861 | requirements.txt -> Flask | Flask 2.0.1: flask: Possible disclosure of permanent session cookie due to missi | Upgrade to 2.3.2, 2.2.5 |
| HIGH | trivy-fs | CVE-2024-34069 | requirements.txt -> Werkzeug | Werkzeug 2.0.1: python-werkzeug: user may execute code on a developer's machine | Upgrade to 3.0.3 |
| HIGH | trivy-fs | DS002 | Dockerfile | Image user should not be 'root' | Add 'USER <non root user name>' line to the Dockerfile |

### 20261021-080826-01-flask-api-fixed

| Severity | Tool | Rule / CVE | Location | Title | Remediation |
|---|---|---|---|---|---|
| CRITICAL | dockle | DKL-DI-0005 | image | Clear apt-get caches | Use 'rm -rf /var/lib/apt/lists' after 'apt-get install\|updat |
| HIGH | trivy-image | CVE-2025-69720 | devsecops-demo-01-flask-api-fixed:local (debian 13.7) -> lib | libncursesw6 6.5+20250216-2: ncurses: ncurses: Buffer overflow vulnerability may | No fix available yet |
| HIGH | trivy-image | CVE-2025-69720 | devsecops-demo-01-flask-api-fixed:local (debian 13.7) -> lib | libtinfo6 6.5+20250216-2: ncurses: ncurses: Buffer overflow vulnerability may le | No fix available yet |
| HIGH | trivy-image | CVE-2025-69720 | devsecops-demo-01-flask-api-fixed:local (debian 13.7) -> ncu | ncurses-base 6.5+20250216-2: ncurses: ncurses: Buffer overflow vulnerability may | No fix available yet |
| HIGH | trivy-image | CVE-2025-69720 | devsecops-demo-01-flask-api-fixed:local (debian 13.7) -> ncu | ncurses-bin 6.5+20250216-2: ncurses: ncurses: Buffer overflow vulnerability may  | No fix available yet |
| HIGH | trivy-image | CVE-2026-12064 | devsecops-demo-01-flask-api-fixed:local (debian 13.7) -> cur | curl 8.14.1-2+deb13u7: curl: curl: SSH host verification bypass when using schem | No fix available yet |
| HIGH | trivy-image | CVE-2026-12064 | devsecops-demo-01-flask-api-fixed:local (debian 13.7) -> lib | libcurl4t64 8.14.1-2+deb13u7: curl: curl: SSH host verification bypass when usin | No fix available yet |
| HIGH | trivy-image | CVE-2026-16742 | devsecops-demo-01-flask-api-fixed:local (debian 13.7) -> lib | libsystemd0 257.13-1~deb13u1: systemd: systemd-homed: Local privilege escalation | No fix available yet |
| HIGH | trivy-image | CVE-2026-16742 | devsecops-demo-01-flask-api-fixed:local (debian 13.7) -> lib | libudev1 257.13-1~deb13u1: systemd: systemd-homed: Local privilege escalation vi | No fix available yet |
| HIGH | trivy-image | CVE-2026-54369 | devsecops-demo-01-flask-api-fixed:local (debian 13.7) -> lib | libacl1 2.3.2-2+b1: acl: Symlink traversal privilege escalation via libacl funct | No fix available yet |
| HIGH | trivy-image | CVE-2026-76642 | devsecops-demo-01-flask-api-fixed:local (debian 13.7) -> bsd | bsdutils 1:2.41.5-0+deb13u1: util-linux: util-linux: failed external mount helpe | No fix available yet |
| HIGH | trivy-image | CVE-2026-76642 | devsecops-demo-01-flask-api-fixed:local (debian 13.7) -> lib | libblkid1 2.41.5-0+deb13u1: util-linux: util-linux: failed external mount helper | No fix available yet |
| HIGH | trivy-image | CVE-2026-76642 | devsecops-demo-01-flask-api-fixed:local (debian 13.7) -> lib | liblastlog2-2 2.41.5-0+deb13u1: util-linux: util-linux: failed external mount he | No fix available yet |
| HIGH | trivy-image | CVE-2026-76642 | devsecops-demo-01-flask-api-fixed:local (debian 13.7) -> lib | libmount1 2.41.5-0+deb13u1: util-linux: util-linux: failed external mount helper | No fix available yet |
| HIGH | trivy-image | CVE-2026-76642 | devsecops-demo-01-flask-api-fixed:local (debian 13.7) -> lib | libsmartcols1 2.41.5-0+deb13u1: util-linux: util-linux: failed external mount he | No fix available yet |
| HIGH | trivy-image | CVE-2026-76642 | devsecops-demo-01-flask-api-fixed:local (debian 13.7) -> lib | libuuid1 2.41.5-0+deb13u1: util-linux: util-linux: failed external mount helper  | No fix available yet |
| HIGH | trivy-image | CVE-2026-76642 | devsecops-demo-01-flask-api-fixed:local (debian 13.7) -> log | login 1:4.16.0-2+really2.41.5-0+deb13u1: util-linux: util-linux: failed external | No fix available yet |
| HIGH | trivy-image | CVE-2026-76642 | devsecops-demo-01-flask-api-fixed:local (debian 13.7) -> mou | mount 2.41.5-0+deb13u1: util-linux: util-linux: failed external mount helper sti | No fix available yet |
| HIGH | trivy-image | CVE-2026-76642 | devsecops-demo-01-flask-api-fixed:local (debian 13.7) -> uti | util-linux 2.41.5-0+deb13u1: util-linux: util-linux: failed external mount helpe | No fix available yet |
| HIGH | trivy-image | CVE-2026-78408 | devsecops-demo-01-flask-api-fixed:local (debian 13.7) -> bsd | bsdutils 1:2.41.5-0+deb13u1: util-linux: util-linux: nsenter --join-cgroup leaks | No fix available yet |
| HIGH | trivy-image | CVE-2026-78408 | devsecops-demo-01-flask-api-fixed:local (debian 13.7) -> lib | libblkid1 2.41.5-0+deb13u1: util-linux: util-linux: nsenter --join-cgroup leaks  | No fix available yet |
| HIGH | trivy-image | CVE-2026-78408 | devsecops-demo-01-flask-api-fixed:local (debian 13.7) -> lib | liblastlog2-2 2.41.5-0+deb13u1: util-linux: util-linux: nsenter --join-cgroup le | No fix available yet |
| HIGH | trivy-image | CVE-2026-78408 | devsecops-demo-01-flask-api-fixed:local (debian 13.7) -> lib | libmount1 2.41.5-0+deb13u1: util-linux: util-linux: nsenter --join-cgroup leaks  | No fix available yet |
| HIGH | trivy-image | CVE-2026-78408 | devsecops-demo-01-flask-api-fixed:local (debian 13.7) -> lib | libsmartcols1 2.41.5-0+deb13u1: util-linux: util-linux: nsenter --join-cgroup le | No fix available yet |
| HIGH | trivy-image | CVE-2026-78408 | devsecops-demo-01-flask-api-fixed:local (debian 13.7) -> lib | libuuid1 2.41.5-0+deb13u1: util-linux: util-linux: nsenter --join-cgroup leaks r | No fix available yet |
| HIGH | trivy-image | CVE-2026-78408 | devsecops-demo-01-flask-api-fixed:local (debian 13.7) -> log | login 1:4.16.0-2+really2.41.5-0+deb13u1: util-linux: util-linux: nsenter --join- | No fix available yet |
| HIGH | trivy-image | CVE-2026-78408 | devsecops-demo-01-flask-api-fixed:local (debian 13.7) -> mou | mount 2.41.5-0+deb13u1: util-linux: util-linux: nsenter --join-cgroup leaks root | No fix available yet |
| HIGH | trivy-image | CVE-2026-78408 | devsecops-demo-01-flask-api-fixed:local (debian 13.7) -> uti | util-linux 2.41.5-0+deb13u1: util-linux: util-linux: nsenter --join-cgroup leaks | No fix available yet |
| HIGH | trivy-image | CVE-2026-78409 | devsecops-demo-01-flask-api-fixed:local (debian 13.7) -> bsd | bsdutils 1:2.41.5-0+deb13u1: util-linux: util-linux: X-mount.subdir detached-tre | No fix available yet |
| HIGH | trivy-image | CVE-2026-78409 | devsecops-demo-01-flask-api-fixed:local (debian 13.7) -> lib | libblkid1 2.41.5-0+deb13u1: util-linux: util-linux: X-mount.subdir detached-tree | No fix available yet |
| HIGH | trivy-image | CVE-2026-78409 | devsecops-demo-01-flask-api-fixed:local (debian 13.7) -> lib | liblastlog2-2 2.41.5-0+deb13u1: util-linux: util-linux: X-mount.subdir detached- | No fix available yet |
| HIGH | trivy-image | CVE-2026-78409 | devsecops-demo-01-flask-api-fixed:local (debian 13.7) -> lib | libmount1 2.41.5-0+deb13u1: util-linux: util-linux: X-mount.subdir detached-tree | No fix available yet |
| HIGH | trivy-image | CVE-2026-78409 | devsecops-demo-01-flask-api-fixed:local (debian 13.7) -> lib | libsmartcols1 2.41.5-0+deb13u1: util-linux: util-linux: X-mount.subdir detached- | No fix available yet |
| HIGH | trivy-image | CVE-2026-78409 | devsecops-demo-01-flask-api-fixed:local (debian 13.7) -> lib | libuuid1 2.41.5-0+deb13u1: util-linux: util-linux: X-mount.subdir detached-tree  | No fix available yet |
| HIGH | trivy-image | CVE-2026-78409 | devsecops-demo-01-flask-api-fixed:local (debian 13.7) -> log | login 1:4.16.0-2+really2.41.5-0+deb13u1: util-linux: util-linux: X-mount.subdir  | No fix available yet |
| HIGH | trivy-image | CVE-2026-78409 | devsecops-demo-01-flask-api-fixed:local (debian 13.7) -> mou | mount 2.41.5-0+deb13u1: util-linux: util-linux: X-mount.subdir detached-tree res | No fix available yet |
| HIGH | trivy-image | CVE-2026-78409 | devsecops-demo-01-flask-api-fixed:local (debian 13.7) -> uti | util-linux 2.41.5-0+deb13u1: util-linux: util-linux: X-mount.subdir detached-tre | No fix available yet |
| HIGH | trivy-image | CVE-2026-78410 | devsecops-demo-01-flask-api-fixed:local (debian 13.7) -> bsd | bsdutils 1:2.41.5-0+deb13u1: util-linux: util-linux: restricted bind mounts do n | No fix available yet |
| HIGH | trivy-image | CVE-2026-78410 | devsecops-demo-01-flask-api-fixed:local (debian 13.7) -> lib | libblkid1 2.41.5-0+deb13u1: util-linux: util-linux: restricted bind mounts do no | No fix available yet |
| HIGH | trivy-image | CVE-2026-78410 | devsecops-demo-01-flask-api-fixed:local (debian 13.7) -> lib | liblastlog2-2 2.41.5-0+deb13u1: util-linux: util-linux: restricted bind mounts d | No fix available yet |

### 20261021-081124-02-cli-deps-vulnerable

| Severity | Tool | Rule / CVE | Location | Title | Remediation |
|---|---|---|---|---|---|
| CRITICAL | trivy-fs | CVE-2019-20477 | requirements.txt -> PyYAML | PyYAML 5.1: PyYAML: command execution through python/object/apply constructor in | Upgrade to 5.2 |
| CRITICAL | trivy-fs | CVE-2020-14343 | requirements.txt -> PyYAML | PyYAML 5.1: PyYAML: incomplete fix for CVE-2020-1747 | Upgrade to 5.4 |
| CRITICAL | trivy-fs | CVE-2020-1747 | requirements.txt -> PyYAML | PyYAML 5.1: PyYAML: arbitrary command execution through python/object/new when F | Upgrade to 5.3.1 |
| HIGH | Bandit | B501 | file:///src/main.py:25 | Call to requests with verify=False disabling SSL certificate checks, security is | See rule documentation |
| HIGH | Semgrep OSS | python.requests.security.disabled-cert-validation.disabled-cert-validation | /src/main.py:25 | Certificate verification has been explicitly disabled. This permits insecure con | See rule documentation |
| HIGH | trivy-fs | CVE-2018-18074 | requirements.txt -> requests | requests 2.19.1: python-requests: Redirect from HTTPS to HTTP does not remove Au | Upgrade to 2.20.0 |
| HIGH | trivy-fs | CVE-2019-10906 | requirements.txt -> Jinja2 | Jinja2 2.10: python-jinja2: str.format_map allows sandbox escape | Upgrade to 2.10.1 |
| HIGH | trivy-fs | CVE-2019-11324 | requirements.txt -> urllib3 | urllib3 1.24.1: python-urllib3: Certification mishandle when error should be thr | Upgrade to 1.24.2 |
| HIGH | trivy-fs | CVE-2020-25659 | requirements.txt -> cryptography | cryptography 2.3: python-cryptography: Bleichenbacher timing oracle attack again | Upgrade to 3.2 |
| HIGH | trivy-fs | CVE-2023-0286 | requirements.txt -> cryptography | cryptography 2.3: openssl: X.400 address type confusion in X.509 GeneralName | Upgrade to 39.0.1 |
| HIGH | trivy-fs | CVE-2023-43804 | requirements.txt -> urllib3 | urllib3 1.24.1: python-urllib3: Cookie request header isn't stripped during cros | Upgrade to 2.0.6, 1.26.17 |
| HIGH | trivy-fs | CVE-2023-50782 | requirements.txt -> cryptography | cryptography 2.3: python-cryptography: Bleichenbacher timing oracle attack again | Upgrade to 42.0.0 |
| HIGH | trivy-fs | CVE-2025-66418 | requirements.txt -> urllib3 | urllib3 1.24.1: urllib3: urllib3: Unbounded decompression chain leads to resourc | Upgrade to 2.6.0 |
| HIGH | trivy-fs | CVE-2025-66471 | requirements.txt -> urllib3 | urllib3 1.24.1: urllib3: urllib3 Streaming API improperly handles highly compres | Upgrade to 2.6.0 |
| HIGH | trivy-fs | CVE-2026-21441 | requirements.txt -> urllib3 | urllib3 1.24.1: urllib3: urllib3 vulnerable to decompression-bomb safeguard bypa | Upgrade to 2.6.3 |
| HIGH | trivy-fs | CVE-2026-26007 | requirements.txt -> cryptography | cryptography 2.3: cryptography: cryptography Subgroup Attack Due to Missing Subg | Upgrade to 46.0.5 |
| HIGH | trivy-fs | CVE-2026-44431 | requirements.txt -> urllib3 | urllib3 1.24.1: urllib3: urllib3: Information disclosure via cross-origin redire | Upgrade to 2.7.0 |
| HIGH | trivy-fs | CVE-2026-97689 | requirements.txt -> urllib3 | urllib3 1.24.1: urllib3: urllib3: Denial of Service via unbounded memory allocat | Upgrade to 2.8.0 |
| HIGH | trivy-fs | GHSA-537c-gmf6-5ccf | requirements.txt -> cryptography | cryptography 2.3: Vulnerable OpenSSL included in cryptography wheels | Upgrade to 48.0.1 |

### 20261021-081233-02-cli-deps-fixed

| Severity | Tool | Rule / CVE | Location | Title | Remediation |
|---|---|---|---|---|---|
| CRITICAL | trivy-fs | GHSA-6q48-6c7w-9gw2 | requirements.txt -> certifi | certifi 2024.8.30: certifi bundles emSign root CAs with compromised intermediate | Upgrade to 2026.10.19 |
| HIGH | trivy-fs | CVE-2025-66418 | requirements.txt -> urllib3 | urllib3 2.2.3: urllib3: urllib3: Unbounded decompression chain leads to resource | Upgrade to 2.6.0 |
| HIGH | trivy-fs | CVE-2025-66471 | requirements.txt -> urllib3 | urllib3 2.2.3: urllib3: urllib3 Streaming API improperly handles highly compress | Upgrade to 2.6.0 |
| HIGH | trivy-fs | CVE-2026-21441 | requirements.txt -> urllib3 | urllib3 2.2.3: urllib3: urllib3 vulnerable to decompression-bomb safeguard bypas | Upgrade to 2.6.3 |
| HIGH | trivy-fs | CVE-2026-26007 | requirements.txt -> cryptography | cryptography 43.0.1: cryptography: cryptography Subgroup Attack Due to Missing S | Upgrade to 46.0.5 |
| HIGH | trivy-fs | CVE-2026-44431 | requirements.txt -> urllib3 | urllib3 2.2.3: urllib3: urllib3: Information disclosure via cross-origin redirec | Upgrade to 2.7.0 |
| HIGH | trivy-fs | CVE-2026-69249 | requirements.txt -> cryptography | cryptography 43.0.1: python-cryptography: python-cryptography: Duplicate self-si | Upgrade to 49.0.0 |
| HIGH | trivy-fs | CVE-2026-97687 | requirements.txt -> urllib3 | urllib3 2.2.3: urllib3: urllib3: Traffic interception via HTTPS proxy TLS config | Upgrade to 2.8.0 |
| HIGH | trivy-fs | CVE-2026-97689 | requirements.txt -> urllib3 | urllib3 2.2.3: urllib3: urllib3: Denial of Service via unbounded memory allocati | Upgrade to 2.8.0 |
| HIGH | trivy-fs | GHSA-537c-gmf6-5ccf | requirements.txt -> cryptography | cryptography 43.0.1: Vulnerable OpenSSL included in cryptography wheels | Upgrade to 48.0.1 |

### 20261021-081442-03-container-service-vulnerable

| Severity | Tool | Rule / CVE | Location | Title | Remediation |
|---|---|---|---|---|---|
| CRITICAL | gitleaks | aws-access-token | /src/app.py:16 | Identified a pattern that may indicate AWS credentials, risking unauthorized clo | Rotate the credential and move it into Vault or a CI variabl |
| CRITICAL | gitleaks | generic-api-key | /src/Dockerfile:12 | Detected a Generic API Key, potentially exposing access to various services and  | Rotate the credential and move it into Vault or a CI variabl |
| CRITICAL | gitleaks | generic-api-key | /src/app.py:14 | Detected a Generic API Key, potentially exposing access to various services and  | Rotate the credential and move it into Vault or a CI variabl |
| CRITICAL | gitleaks | github-pat | /src/Dockerfile:12 | Uncovered a GitHub Personal Access Token, potentially leading to unauthorized re | Rotate the credential and move it into Vault or a CI variabl |
| CRITICAL | gitleaks | github-pat | /src/app.py:14 | Uncovered a GitHub Personal Access Token, potentially leading to unauthorized re | Rotate the credential and move it into Vault or a CI variabl |
| CRITICAL | gitleaks | stripe-access-token | /src/.env:4 | Found a Stripe Access Token, posing a risk to payment processing services and se | Rotate the credential and move it into Vault or a CI variabl |
| CRITICAL | trivy-fs | github-pat | Dockerfile:12 | GitHub Personal Access Token | Remove the secret from the image and rotate it |
| CRITICAL | trivy-fs | github-pat | app.py:14 | GitHub Personal Access Token | Remove the secret from the image and rotate it |
| CRITICAL | trivy-fs | stripe-secret-token | .env:4 | Stripe Secret Key | Remove the secret from the image and rotate it |
| HIGH | trivy-fs | DS002 | Dockerfile | Image user should not be 'root' | Add 'USER <non root user name>' line to the Dockerfile |

### 20261021-081626-03-container-service-fixed

_No critical or high findings._

## 4. Stage duration (fail-fast evidence)

### 20261021-080607-01-flask-api-vulnerable

| Stage | Duration (s) |
|---|---|
| secrets | 9 |
| sast | 57 |
| sca | 69 |

### 20261021-080826-01-flask-api-fixed

| Stage | Duration (s) |
|---|---|
| secrets | 1 |
| sast | 19 |
| sca | 70 |
| build | 24 |
| image-scan | 61 |

### 20261021-081124-02-cli-deps-vulnerable

| Stage | Duration (s) |
|---|---|
| secrets | 1 |
| sast | 19 |
| sca | 46 |

### 20261021-081233-02-cli-deps-fixed

| Stage | Duration (s) |
|---|---|
| secrets | 0 |
| sast | 23 |
| sca | 94 |

### 20261021-081442-03-container-service-vulnerable

| Stage | Duration (s) |
|---|---|
| secrets | 2 |
| sast | 25 |
| sca | 69 |

### 20261021-081626-03-container-service-fixed

| Stage | Duration (s) |
|---|---|
| secrets | 2 |
| sast | 32 |
| sca | 80 |
| build | 8 |
| image-scan | 65 |
| deploy-test | 5 |
| dast | 355 |

## 5. False positive assessment

Fill in during triage. A finding counts as a false positive only after
manual verification; the rate per tool is a core insight for the presentation.

| Tool | Findings | Verified true | False positive | FP rate |
|---|---|---|---|---|
| trivy-image | 290 |  |  |  |
| trivy-fs | 90 |  |  |  |
| Bandit | 19 |  |  |  |
| Semgrep OSS | 12 |  |  |  |
| gitleaks | 6 |  |  |  |
| dockle | 4 |  |  |  |
| owasp-zap | 3 |  |  |  |
| Hadolint | 1 |  |  |  |

## 6. Lessons learned

- Which tool produced the most actionable findings?
- Where did the gate block, and was the threshold appropriate?
- Which findings only the dynamic scan could reveal?
- What is still uncovered (container runtime security, IAST, pen testing)?
