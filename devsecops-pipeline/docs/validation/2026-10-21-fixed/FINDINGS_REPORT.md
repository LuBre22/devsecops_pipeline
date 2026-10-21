# Findings Report - DevSecOps Pipeline

## 1. Run overview

| Run | Workload | Branch | Commit | Tools | Findings | Blocking | Suppressed | Gate |
|---|---|---|---|---|---|---|---|---|
| 20261021-093042-01-flask-api-fixed-a81b6c | 01-flask-api-fixed | validation/pipeline-pruefung | 826e1bd5 | 10 | 17 | 0 | 1 | PASS |
| 20261021-093306-01-flask-api-vulnerable-890797 | 01-flask-api-vulnerable | validation/pipeline-pruefung | 826e1bd5 | 6 | 30 | 8 | 0 | FAIL |
| 20261021-093408-02-cli-deps-fixed-a92d15 | 02-cli-deps-fixed | validation/pipeline-pruefung | 826e1bd5 | 9 | 11 | 0 | 1 | PASS |
| 20261021-093612-02-cli-deps-vulnerable-a3861a | 02-cli-deps-vulnerable | validation/pipeline-pruefung | 826e1bd5 | 7 | 31 | 4 | 0 | FAIL |
| 20261021-093726-03-container-service-fixed-ad56b9 | 03-container-service-fixed | validation/pipeline-pruefung | 826e1bd5 | 10 | 10 | 0 | 1 | PASS |
| 20261021-093956-03-container-service-vulnerable-8c8860 | 03-container-service-vulnerable | validation/pipeline-pruefung | 826e1bd5 | 6 | 16 | 10 | 0 | FAIL |
| 20261021-094047-01-flask-api-fixed-ffd215 | 01-flask-api-fixed | validation/pipeline-pruefung | 826e1bd5 | 10 | 17 | 0 | 1 | PASS |
| 20261021-094239-01-flask-api-vulnerable-39dd26 | 01-flask-api-vulnerable | validation/pipeline-pruefung | 826e1bd5 | 6 | 30 | 8 | 0 | FAIL |
| 20261021-094326-02-cli-deps-fixed-1c5456 | 02-cli-deps-fixed | validation/pipeline-pruefung | 826e1bd5 | 9 | 11 | 0 | 1 | PASS |
| 20261021-094444-02-cli-deps-vulnerable-a201e5 | 02-cli-deps-vulnerable | validation/pipeline-pruefung | 826e1bd5 | 7 | 31 | 4 | 0 | FAIL |
| 20261021-094540-03-container-service-fixed-51a564 | 03-container-service-fixed | validation/pipeline-pruefung | 826e1bd5 | 10 | 10 | 0 | 1 | PASS |
| 20261021-094744-03-container-service-vulnerable-d6b5a1 | 03-container-service-vulnerable | validation/pipeline-pruefung | 826e1bd5 | 6 | 16 | 10 | 0 | FAIL |

## Execution status

### 20261021-093042-01-flask-api-fixed-a81b6c

| Check | Status | Reason / error |
|---|---|---|
| runtime | ok |  |
| gitleaks | ok |  |
| history | ok |  |
| semgrep | ok |  |
| bandit | ok |  |
| trivy-fs | ok |  |
| syft | ok |  |
| hadolint | ok |  |
| build | ok |  |
| image-export | ok |  |
| trivy-image | ok |  |
| dockle | ok |  |
| package-cache-empty | ok |  |
| test-network | ok |  |
| deploy | ok |  |
| health | ok |  |
| api-smoke | ok |  |
| zap | ok |  |
| publish | skipped | No REGISTRY configured |

- Reviewed exception `dockle:DKL-DI-0004`: Reviewed official Python Alpine build layer: initial apk add uses --no-cache. The later apk add --no-network resolves local shared-library dependencies. Dockle 0.4.14 mistakes this for a cached network installation. Only accepted with the exact base digest, exact inherited command and successful empty-package-cache inspection. Re-review on scanner/base updates or expiry. Owner: DevSecOps project group; expires 2026-11-20.

### 20261021-093306-01-flask-api-vulnerable-890797

| Check | Status | Reason / error |
|---|---|---|
| runtime | ok |  |
| gitleaks | ok |  |
| history | ok |  |
| semgrep | ok |  |
| bandit | ok |  |
| trivy-fs | ok |  |
| syft | ok |  |

### 20261021-093408-02-cli-deps-fixed-a92d15

| Check | Status | Reason / error |
|---|---|---|
| runtime | ok |  |
| gitleaks | ok |  |
| history | ok |  |
| semgrep | ok |  |
| bandit | ok |  |
| trivy-fs | ok |  |
| syft | ok |  |
| hadolint | ok |  |
| build | ok |  |
| cli-smoke | ok |  |
| image-export | ok |  |
| trivy-image | ok |  |
| dockle | ok |  |
| package-cache-empty | ok |  |
| zap | skipped | CLI has no HTTP interface |
| publish | skipped | No REGISTRY configured |

- Reviewed exception `dockle:DKL-DI-0004`: Reviewed official Python Alpine build layer: initial apk add uses --no-cache. The later apk add --no-network resolves local shared-library dependencies. Dockle 0.4.14 mistakes this for a cached network installation. Only accepted with the exact base digest, exact inherited command and successful empty-package-cache inspection. Re-review on scanner/base updates or expiry. Owner: DevSecOps project group; expires 2026-11-20.

### 20261021-093612-02-cli-deps-vulnerable-a3861a

| Check | Status | Reason / error |
|---|---|---|
| runtime | ok |  |
| gitleaks | ok |  |
| history | ok |  |
| semgrep | ok |  |
| bandit | ok |  |
| trivy-fs | ok |  |
| syft | ok |  |
| hadolint | ok |  |
| build | ok |  |
| cli-smoke | ok |  |

### 20261021-093726-03-container-service-fixed-ad56b9

| Check | Status | Reason / error |
|---|---|---|
| runtime | ok |  |
| gitleaks | ok |  |
| history | ok |  |
| semgrep | ok |  |
| bandit | ok |  |
| trivy-fs | ok |  |
| syft | ok |  |
| hadolint | ok |  |
| build | ok |  |
| image-export | ok |  |
| trivy-image | ok |  |
| dockle | ok |  |
| package-cache-empty | ok |  |
| test-network | ok |  |
| deploy | ok |  |
| health | ok |  |
| api-smoke | ok |  |
| zap | ok |  |
| publish | skipped | No REGISTRY configured |

- Reviewed exception `dockle:DKL-DI-0004`: Reviewed official Python Alpine build layer: initial apk add uses --no-cache. The later apk add --no-network resolves local shared-library dependencies. Dockle 0.4.14 mistakes this for a cached network installation. Only accepted with the exact base digest, exact inherited command and successful empty-package-cache inspection. Re-review on scanner/base updates or expiry. Owner: DevSecOps project group; expires 2026-11-20.

### 20261021-093956-03-container-service-vulnerable-8c8860

| Check | Status | Reason / error |
|---|---|---|
| runtime | ok |  |
| gitleaks | ok |  |
| history | ok |  |
| semgrep | ok |  |
| bandit | ok |  |
| trivy-fs | ok |  |
| syft | ok |  |

### 20261021-094047-01-flask-api-fixed-ffd215

| Check | Status | Reason / error |
|---|---|---|
| runtime | ok |  |
| gitleaks | ok |  |
| history | ok |  |
| semgrep | ok |  |
| bandit | ok |  |
| trivy-fs | ok |  |
| syft | ok |  |
| hadolint | ok |  |
| build | ok |  |
| image-export | ok |  |
| trivy-image | ok |  |
| dockle | ok |  |
| package-cache-empty | ok |  |
| test-network | ok |  |
| deploy | ok |  |
| health | ok |  |
| api-smoke | ok |  |
| zap | ok |  |
| publish | skipped | No REGISTRY configured |

- Reviewed exception `dockle:DKL-DI-0004`: Reviewed official Python Alpine build layer: initial apk add uses --no-cache. The later apk add --no-network resolves local shared-library dependencies. Dockle 0.4.14 mistakes this for a cached network installation. Only accepted with the exact base digest, exact inherited command and successful empty-package-cache inspection. Re-review on scanner/base updates or expiry. Owner: DevSecOps project group; expires 2026-11-20.

### 20261021-094239-01-flask-api-vulnerable-39dd26

| Check | Status | Reason / error |
|---|---|---|
| runtime | ok |  |
| gitleaks | ok |  |
| history | ok |  |
| semgrep | ok |  |
| bandit | ok |  |
| trivy-fs | ok |  |
| syft | ok |  |

### 20261021-094326-02-cli-deps-fixed-1c5456

| Check | Status | Reason / error |
|---|---|---|
| runtime | ok |  |
| gitleaks | ok |  |
| history | ok |  |
| semgrep | ok |  |
| bandit | ok |  |
| trivy-fs | ok |  |
| syft | ok |  |
| hadolint | ok |  |
| build | ok |  |
| cli-smoke | ok |  |
| image-export | ok |  |
| trivy-image | ok |  |
| dockle | ok |  |
| package-cache-empty | ok |  |
| zap | skipped | CLI has no HTTP interface |
| publish | skipped | No REGISTRY configured |

- Reviewed exception `dockle:DKL-DI-0004`: Reviewed official Python Alpine build layer: initial apk add uses --no-cache. The later apk add --no-network resolves local shared-library dependencies. Dockle 0.4.14 mistakes this for a cached network installation. Only accepted with the exact base digest, exact inherited command and successful empty-package-cache inspection. Re-review on scanner/base updates or expiry. Owner: DevSecOps project group; expires 2026-11-20.

### 20261021-094444-02-cli-deps-vulnerable-a201e5

| Check | Status | Reason / error |
|---|---|---|
| runtime | ok |  |
| gitleaks | ok |  |
| history | ok |  |
| semgrep | ok |  |
| bandit | ok |  |
| trivy-fs | ok |  |
| syft | ok |  |
| hadolint | ok |  |
| build | ok |  |
| cli-smoke | ok |  |

### 20261021-094540-03-container-service-fixed-51a564

| Check | Status | Reason / error |
|---|---|---|
| runtime | ok |  |
| gitleaks | ok |  |
| history | ok |  |
| semgrep | ok |  |
| bandit | ok |  |
| trivy-fs | ok |  |
| syft | ok |  |
| hadolint | ok |  |
| build | ok |  |
| image-export | ok |  |
| trivy-image | ok |  |
| dockle | ok |  |
| package-cache-empty | ok |  |
| test-network | ok |  |
| deploy | ok |  |
| health | ok |  |
| api-smoke | ok |  |
| zap | ok |  |
| publish | skipped | No REGISTRY configured |

- Reviewed exception `dockle:DKL-DI-0004`: Reviewed official Python Alpine build layer: initial apk add uses --no-cache. The later apk add --no-network resolves local shared-library dependencies. Dockle 0.4.14 mistakes this for a cached network installation. Only accepted with the exact base digest, exact inherited command and successful empty-package-cache inspection. Re-review on scanner/base updates or expiry. Owner: DevSecOps project group; expires 2026-11-20.

### 20261021-094744-03-container-service-vulnerable-d6b5a1

| Check | Status | Reason / error |
|---|---|---|
| runtime | ok |  |
| gitleaks | ok |  |
| history | ok |  |
| semgrep | ok |  |
| bandit | ok |  |
| trivy-fs | ok |  |
| syft | ok |  |

## 2. Findings per severity and test class

### 20261021-093042-01-flask-api-fixed-a81b6c - 01-flask-api-fixed

| Test class | CRITICAL | HIGH | MEDIUM | LOW | INFO |
|---|---|---|---|---|---|
| dast | 0 | 0 | 1 | 2 | 0 |
| image | 1 | 0 | 6 | 1 | 1 |
| sast | 0 | 0 | 2 | 3 | 0 |
| **total** | 1 | 0 | 9 | 6 | 1 |

### 20261021-093306-01-flask-api-vulnerable-890797 - 01-flask-api-vulnerable

| Test class | CRITICAL | HIGH | MEDIUM | LOW | INFO |
|---|---|---|---|---|---|
| sast | 0 | 8 | 3 | 0 | 0 |
| sca | 0 | 4 | 12 | 3 | 0 |
| **total** | 0 | 12 | 15 | 3 | 0 |

### 20261021-093408-02-cli-deps-fixed-a92d15 - 02-cli-deps-fixed

| Test class | CRITICAL | HIGH | MEDIUM | LOW | INFO |
|---|---|---|---|---|---|
| image | 1 | 0 | 6 | 1 | 2 |
| sca | 0 | 0 | 0 | 1 | 0 |
| **total** | 1 | 0 | 6 | 2 | 2 |

### 20261021-093612-02-cli-deps-vulnerable-a3861a - 02-cli-deps-vulnerable

| Test class | CRITICAL | HIGH | MEDIUM | LOW | INFO |
|---|---|---|---|---|---|
| sast | 0 | 3 | 2 | 0 | 0 |
| sca | 1 | 7 | 17 | 1 | 0 |
| **total** | 1 | 10 | 19 | 1 | 0 |

### 20261021-093726-03-container-service-fixed-ad56b9 - 03-container-service-fixed

| Test class | CRITICAL | HIGH | MEDIUM | LOW | INFO |
|---|---|---|---|---|---|
| image | 1 | 0 | 6 | 1 | 1 |
| sast | 0 | 0 | 1 | 0 | 0 |
| **total** | 1 | 0 | 7 | 1 | 1 |

### 20261021-093956-03-container-service-vulnerable-8c8860 - 03-container-service-vulnerable

| Test class | CRITICAL | HIGH | MEDIUM | LOW | INFO |
|---|---|---|---|---|---|
| sast | 0 | 1 | 1 | 3 | 0 |
| sca | 0 | 1 | 0 | 1 | 0 |
| secrets | 9 | 0 | 0 | 0 | 0 |
| **total** | 9 | 2 | 1 | 4 | 0 |

### 20261021-094047-01-flask-api-fixed-ffd215 - 01-flask-api-fixed

| Test class | CRITICAL | HIGH | MEDIUM | LOW | INFO |
|---|---|---|---|---|---|
| dast | 0 | 0 | 1 | 2 | 0 |
| image | 1 | 0 | 6 | 1 | 1 |
| sast | 0 | 0 | 2 | 3 | 0 |
| **total** | 1 | 0 | 9 | 6 | 1 |

### 20261021-094239-01-flask-api-vulnerable-39dd26 - 01-flask-api-vulnerable

| Test class | CRITICAL | HIGH | MEDIUM | LOW | INFO |
|---|---|---|---|---|---|
| sast | 0 | 8 | 3 | 0 | 0 |
| sca | 0 | 4 | 12 | 3 | 0 |
| **total** | 0 | 12 | 15 | 3 | 0 |

### 20261021-094326-02-cli-deps-fixed-1c5456 - 02-cli-deps-fixed

| Test class | CRITICAL | HIGH | MEDIUM | LOW | INFO |
|---|---|---|---|---|---|
| image | 1 | 0 | 6 | 1 | 2 |
| sca | 0 | 0 | 0 | 1 | 0 |
| **total** | 1 | 0 | 6 | 2 | 2 |

### 20261021-094444-02-cli-deps-vulnerable-a201e5 - 02-cli-deps-vulnerable

| Test class | CRITICAL | HIGH | MEDIUM | LOW | INFO |
|---|---|---|---|---|---|
| sast | 0 | 3 | 2 | 0 | 0 |
| sca | 1 | 7 | 17 | 1 | 0 |
| **total** | 1 | 10 | 19 | 1 | 0 |

### 20261021-094540-03-container-service-fixed-51a564 - 03-container-service-fixed

| Test class | CRITICAL | HIGH | MEDIUM | LOW | INFO |
|---|---|---|---|---|---|
| image | 1 | 0 | 6 | 1 | 1 |
| sast | 0 | 0 | 1 | 0 | 0 |
| **total** | 1 | 0 | 7 | 1 | 1 |

### 20261021-094744-03-container-service-vulnerable-d6b5a1 - 03-container-service-vulnerable

| Test class | CRITICAL | HIGH | MEDIUM | LOW | INFO |
|---|---|---|---|---|---|
| sast | 0 | 1 | 1 | 3 | 0 |
| sca | 0 | 1 | 0 | 1 | 0 |
| secrets | 9 | 0 | 0 | 0 | 0 |
| **total** | 9 | 2 | 1 | 4 | 0 |

## 3. HIGH/CRITICAL findings (including reviewed exceptions)

### 20261021-093042-01-flask-api-fixed-a81b6c

| Severity | Tool | Rule / CVE | Location | Title | Remediation | Gate action |
|---|---|---|---|---|---|---|
| CRITICAL | dockle | DKL-DI-0004 | image | Use "apk add" with --no-cache | Use --no-cache option if use 'apk add': RUN /bin/sh -c set - | suppressed |

### 20261021-093306-01-flask-api-vulnerable-890797

| Severity | Tool | Rule / CVE | Location | Title | Remediation | Gate action |
|---|---|---|---|---|---|---|
| HIGH | Bandit | B201 | file:///src/app.py:71 | A Flask app appears to be run with debug=True, which exposes the Werkzeug debugg | See rule documentation | block |
| HIGH | Bandit | B324 | file:///src/app.py:65 | Use of weak MD5 hash for security. Consider usedforsecurity=False | See rule documentation | block |
| HIGH | Bandit | B605 | file:///src/app.py:57 | Starting a process with a shell, possible injection detected, security issue. | See rule documentation | block |
| HIGH | Semgrep OSS | rules.flask-debug | /src/app.py:71 | Disable the debugger outside local development. | See rule documentation | block |
| HIGH | Semgrep OSS | rules.flask-reflected-xss | /src/app.py:50 | Escape request data before returning an HTML f-string. | See rule documentation | block |
| HIGH | Semgrep OSS | rules.md5-security-hash | /src/app.py:65 | Use a modern hash for security-sensitive data. | See rule documentation | block |
| HIGH | Semgrep OSS | rules.request-to-sql | /src/app.py:41 | Request input reaches SQL. Use bound parameters. | See rule documentation | block |
| HIGH | Semgrep OSS | rules.shell-command | /src/app.py:57 | Avoid shell execution of application data. | See rule documentation | block |
| HIGH | trivy-fs | CVE-2023-25577 | requirements.txt -> Werkzeug | Werkzeug 2.0.1: python-werkzeug: high resource usage when parsing multipart form | Upgrade to 2.2.3 | warn |
| HIGH | trivy-fs | CVE-2023-30861 | requirements.txt -> Flask | Flask 2.0.1: flask: Possible disclosure of permanent session cookie due to missi | Upgrade to 2.3.2, 2.2.5 | warn |
| HIGH | trivy-fs | CVE-2024-34069 | requirements.txt -> Werkzeug | Werkzeug 2.0.1: python-werkzeug: user may execute code on a developer's machine | Upgrade to 3.0.3 | warn |
| HIGH | trivy-fs | DS002 | Dockerfile | Image user should not be 'root' | Add 'USER <non root user name>' line to the Dockerfile | warn |

### 20261021-093408-02-cli-deps-fixed-a92d15

| Severity | Tool | Rule / CVE | Location | Title | Remediation | Gate action |
|---|---|---|---|---|---|---|
| CRITICAL | dockle | DKL-DI-0004 | image | Use "apk add" with --no-cache | Use --no-cache option if use 'apk add': RUN /bin/sh -c set - | suppressed |

### 20261021-093612-02-cli-deps-vulnerable-a3861a

| Severity | Tool | Rule / CVE | Location | Title | Remediation | Gate action |
|---|---|---|---|---|---|---|
| CRITICAL | trivy-fs | GHSA-6q48-6c7w-9gw2 | requirements.txt -> certifi | certifi 2024.8.30: certifi bundles emSign root CAs with compromised intermediate | Upgrade to 2026.10.19 | block |
| HIGH | Bandit | B501 | file:///src/main.py:25 | Call to requests with verify=False disabling SSL certificate checks, security is | See rule documentation | block |
| HIGH | Semgrep OSS | rules.disabled-tls-validation | /src/main.py:25 | Certificate validation must be enabled. | See rule documentation | block |
| HIGH | Semgrep OSS | rules.unsafe-yaml | /src/main.py:20 | Use yaml.safe_load for configuration. | See rule documentation | block |
| HIGH | trivy-fs | CVE-2018-18074 | requirements.txt -> requests | requests 2.19.1: python-requests: Redirect from HTTPS to HTTP does not remove Au | Upgrade to 2.20.0 | warn |
| HIGH | trivy-fs | CVE-2019-11324 | requirements.txt -> urllib3 | urllib3 1.23: python-urllib3: Certification mishandle when error should be throw | Upgrade to 1.24.2 | warn |
| HIGH | trivy-fs | CVE-2023-43804 | requirements.txt -> urllib3 | urllib3 1.23: python-urllib3: Cookie request header isn't stripped during cross- | Upgrade to 2.0.6, 1.26.17 | warn |
| HIGH | trivy-fs | CVE-2025-66471 | requirements.txt -> urllib3 | urllib3 1.23: urllib3: urllib3 Streaming API improperly handles highly compresse | Upgrade to 2.6.0 | warn |
| HIGH | trivy-fs | CVE-2026-21441 | requirements.txt -> urllib3 | urllib3 1.23: urllib3: urllib3 vulnerable to decompression-bomb safeguard bypass | Upgrade to 2.6.3 | warn |
| HIGH | trivy-fs | CVE-2026-44431 | requirements.txt -> urllib3 | urllib3 1.23: urllib3: urllib3: Information disclosure via cross-origin redirect | Upgrade to 2.7.0 | warn |
| HIGH | trivy-fs | CVE-2026-97689 | requirements.txt -> urllib3 | urllib3 1.23: urllib3: urllib3: Denial of Service via unbounded memory allocatio | Upgrade to 2.8.0 | warn |

### 20261021-093726-03-container-service-fixed-ad56b9

| Severity | Tool | Rule / CVE | Location | Title | Remediation | Gate action |
|---|---|---|---|---|---|---|
| CRITICAL | dockle | DKL-DI-0004 | image | Use "apk add" with --no-cache | Use --no-cache option if use 'apk add': RUN /bin/sh -c set - | suppressed |

### 20261021-093956-03-container-service-vulnerable-8c8860

| Severity | Tool | Rule / CVE | Location | Title | Remediation | Gate action |
|---|---|---|---|---|---|---|
| CRITICAL | gitleaks | aws-access-token | /src/app.py:16 | Identified a pattern that may indicate AWS credentials, risking unauthorized clo | Rotate the credential and move it into Vault or a CI variabl | block |
| CRITICAL | gitleaks | generic-api-key | /src/Dockerfile:10 | Detected a Generic API Key, potentially exposing access to various services and  | Rotate the credential and move it into Vault or a CI variabl | block |
| CRITICAL | gitleaks | generic-api-key | /src/app.py:14 | Detected a Generic API Key, potentially exposing access to various services and  | Rotate the credential and move it into Vault or a CI variabl | block |
| CRITICAL | gitleaks | github-pat | /src/Dockerfile:10 | Uncovered a GitHub Personal Access Token, potentially leading to unauthorized re | Rotate the credential and move it into Vault or a CI variabl | block |
| CRITICAL | gitleaks | github-pat | /src/app.py:14 | Uncovered a GitHub Personal Access Token, potentially leading to unauthorized re | Rotate the credential and move it into Vault or a CI variabl | block |
| CRITICAL | gitleaks | stripe-access-token | /src/.env:4 | Found a Stripe Access Token, posing a risk to payment processing services and se | Rotate the credential and move it into Vault or a CI variabl | block |
| CRITICAL | trivy-fs | github-pat | Dockerfile:10 | GitHub Personal Access Token | Remove the secret from the image and rotate it | block |
| CRITICAL | trivy-fs | github-pat | app.py:14 | GitHub Personal Access Token | Remove the secret from the image and rotate it | block |
| CRITICAL | trivy-fs | stripe-secret-token | .env:4 | Stripe Secret Key | Remove the secret from the image and rotate it | block |
| HIGH | Semgrep OSS | rules.http-path-to-file | /src/app.py:31 | HTTP request paths must be confined before opening a file. | See rule documentation | block |
| HIGH | trivy-fs | DS002 | Dockerfile | Image user should not be 'root' | Add 'USER <non root user name>' line to the Dockerfile | warn |

### 20261021-094047-01-flask-api-fixed-ffd215

| Severity | Tool | Rule / CVE | Location | Title | Remediation | Gate action |
|---|---|---|---|---|---|---|
| CRITICAL | dockle | DKL-DI-0004 | image | Use "apk add" with --no-cache | Use --no-cache option if use 'apk add': RUN /bin/sh -c set - | suppressed |

### 20261021-094239-01-flask-api-vulnerable-39dd26

| Severity | Tool | Rule / CVE | Location | Title | Remediation | Gate action |
|---|---|---|---|---|---|---|
| HIGH | Bandit | B201 | file:///src/app.py:71 | A Flask app appears to be run with debug=True, which exposes the Werkzeug debugg | See rule documentation | block |
| HIGH | Bandit | B324 | file:///src/app.py:65 | Use of weak MD5 hash for security. Consider usedforsecurity=False | See rule documentation | block |
| HIGH | Bandit | B605 | file:///src/app.py:57 | Starting a process with a shell, possible injection detected, security issue. | See rule documentation | block |
| HIGH | Semgrep OSS | rules.flask-debug | /src/app.py:71 | Disable the debugger outside local development. | See rule documentation | block |
| HIGH | Semgrep OSS | rules.flask-reflected-xss | /src/app.py:50 | Escape request data before returning an HTML f-string. | See rule documentation | block |
| HIGH | Semgrep OSS | rules.md5-security-hash | /src/app.py:65 | Use a modern hash for security-sensitive data. | See rule documentation | block |
| HIGH | Semgrep OSS | rules.request-to-sql | /src/app.py:41 | Request input reaches SQL. Use bound parameters. | See rule documentation | block |
| HIGH | Semgrep OSS | rules.shell-command | /src/app.py:57 | Avoid shell execution of application data. | See rule documentation | block |
| HIGH | trivy-fs | CVE-2023-25577 | requirements.txt -> Werkzeug | Werkzeug 2.0.1: python-werkzeug: high resource usage when parsing multipart form | Upgrade to 2.2.3 | warn |
| HIGH | trivy-fs | CVE-2023-30861 | requirements.txt -> Flask | Flask 2.0.1: flask: Possible disclosure of permanent session cookie due to missi | Upgrade to 2.3.2, 2.2.5 | warn |
| HIGH | trivy-fs | CVE-2024-34069 | requirements.txt -> Werkzeug | Werkzeug 2.0.1: python-werkzeug: user may execute code on a developer's machine | Upgrade to 3.0.3 | warn |
| HIGH | trivy-fs | DS002 | Dockerfile | Image user should not be 'root' | Add 'USER <non root user name>' line to the Dockerfile | warn |

### 20261021-094326-02-cli-deps-fixed-1c5456

| Severity | Tool | Rule / CVE | Location | Title | Remediation | Gate action |
|---|---|---|---|---|---|---|
| CRITICAL | dockle | DKL-DI-0004 | image | Use "apk add" with --no-cache | Use --no-cache option if use 'apk add': RUN /bin/sh -c set - | suppressed |

### 20261021-094444-02-cli-deps-vulnerable-a201e5

| Severity | Tool | Rule / CVE | Location | Title | Remediation | Gate action |
|---|---|---|---|---|---|---|
| CRITICAL | trivy-fs | GHSA-6q48-6c7w-9gw2 | requirements.txt -> certifi | certifi 2024.8.30: certifi bundles emSign root CAs with compromised intermediate | Upgrade to 2026.10.19 | block |
| HIGH | Bandit | B501 | file:///src/main.py:25 | Call to requests with verify=False disabling SSL certificate checks, security is | See rule documentation | block |
| HIGH | Semgrep OSS | rules.disabled-tls-validation | /src/main.py:25 | Certificate validation must be enabled. | See rule documentation | block |
| HIGH | Semgrep OSS | rules.unsafe-yaml | /src/main.py:20 | Use yaml.safe_load for configuration. | See rule documentation | block |
| HIGH | trivy-fs | CVE-2018-18074 | requirements.txt -> requests | requests 2.19.1: python-requests: Redirect from HTTPS to HTTP does not remove Au | Upgrade to 2.20.0 | warn |
| HIGH | trivy-fs | CVE-2019-11324 | requirements.txt -> urllib3 | urllib3 1.23: python-urllib3: Certification mishandle when error should be throw | Upgrade to 1.24.2 | warn |
| HIGH | trivy-fs | CVE-2023-43804 | requirements.txt -> urllib3 | urllib3 1.23: python-urllib3: Cookie request header isn't stripped during cross- | Upgrade to 2.0.6, 1.26.17 | warn |
| HIGH | trivy-fs | CVE-2025-66471 | requirements.txt -> urllib3 | urllib3 1.23: urllib3: urllib3 Streaming API improperly handles highly compresse | Upgrade to 2.6.0 | warn |
| HIGH | trivy-fs | CVE-2026-21441 | requirements.txt -> urllib3 | urllib3 1.23: urllib3: urllib3 vulnerable to decompression-bomb safeguard bypass | Upgrade to 2.6.3 | warn |
| HIGH | trivy-fs | CVE-2026-44431 | requirements.txt -> urllib3 | urllib3 1.23: urllib3: urllib3: Information disclosure via cross-origin redirect | Upgrade to 2.7.0 | warn |
| HIGH | trivy-fs | CVE-2026-97689 | requirements.txt -> urllib3 | urllib3 1.23: urllib3: urllib3: Denial of Service via unbounded memory allocatio | Upgrade to 2.8.0 | warn |

### 20261021-094540-03-container-service-fixed-51a564

| Severity | Tool | Rule / CVE | Location | Title | Remediation | Gate action |
|---|---|---|---|---|---|---|
| CRITICAL | dockle | DKL-DI-0004 | image | Use "apk add" with --no-cache | Use --no-cache option if use 'apk add': RUN /bin/sh -c set - | suppressed |

### 20261021-094744-03-container-service-vulnerable-d6b5a1

| Severity | Tool | Rule / CVE | Location | Title | Remediation | Gate action |
|---|---|---|---|---|---|---|
| CRITICAL | gitleaks | aws-access-token | /src/app.py:16 | Identified a pattern that may indicate AWS credentials, risking unauthorized clo | Rotate the credential and move it into Vault or a CI variabl | block |
| CRITICAL | gitleaks | generic-api-key | /src/Dockerfile:10 | Detected a Generic API Key, potentially exposing access to various services and  | Rotate the credential and move it into Vault or a CI variabl | block |
| CRITICAL | gitleaks | generic-api-key | /src/app.py:14 | Detected a Generic API Key, potentially exposing access to various services and  | Rotate the credential and move it into Vault or a CI variabl | block |
| CRITICAL | gitleaks | github-pat | /src/Dockerfile:10 | Uncovered a GitHub Personal Access Token, potentially leading to unauthorized re | Rotate the credential and move it into Vault or a CI variabl | block |
| CRITICAL | gitleaks | github-pat | /src/app.py:14 | Uncovered a GitHub Personal Access Token, potentially leading to unauthorized re | Rotate the credential and move it into Vault or a CI variabl | block |
| CRITICAL | gitleaks | stripe-access-token | /src/.env:4 | Found a Stripe Access Token, posing a risk to payment processing services and se | Rotate the credential and move it into Vault or a CI variabl | block |
| CRITICAL | trivy-fs | github-pat | Dockerfile:10 | GitHub Personal Access Token | Remove the secret from the image and rotate it | block |
| CRITICAL | trivy-fs | github-pat | app.py:14 | GitHub Personal Access Token | Remove the secret from the image and rotate it | block |
| CRITICAL | trivy-fs | stripe-secret-token | .env:4 | Stripe Secret Key | Remove the secret from the image and rotate it | block |
| HIGH | Semgrep OSS | rules.http-path-to-file | /src/app.py:31 | HTTP request paths must be confined before opening a file. | See rule documentation | block |
| HIGH | trivy-fs | DS002 | Dockerfile | Image user should not be 'root' | Add 'USER <non root user name>' line to the Dockerfile | warn |

## 4. Stage duration (fail-fast evidence)

### 20261021-093042-01-flask-api-fixed-a81b6c

| Stage | Duration (s) |
|---|---|
| runtime | 5.73 |
| gitleaks | 2.62 |
| history | 14.09 |
| semgrep | 4.33 |
| bandit | 4.12 |
| trivy-fs | 8.2 |
| syft | 3.83 |
| hadolint | 1.48 |
| build | 4.02 |
| image-export | 1.69 |
| trivy-image | 11.19 |
| dockle | 14.81 |
| package-cache-empty | 1.02 |
| test-network | 0.3 |
| deploy | 1.11 |
| health | 0.52 |
| api-smoke | 0.61 |
| zap | 41.36 |

### 20261021-093306-01-flask-api-vulnerable-890797

| Stage | Duration (s) |
|---|---|
| runtime | 5.84 |
| gitleaks | 2.12 |
| history | 21.75 |
| semgrep | 8.2 |
| bandit | 2.38 |
| trivy-fs | 4.25 |
| syft | 1.61 |

### 20261021-093408-02-cli-deps-fixed-a92d15

| Stage | Duration (s) |
|---|---|
| runtime | 6.2 |
| gitleaks | 3.89 |
| history | 33.03 |
| semgrep | 7.31 |
| bandit | 3.03 |
| trivy-fs | 6.06 |
| syft | 1.95 |
| hadolint | 1.3 |
| build | 4.3 |
| cli-smoke | 1.94 |
| image-export | 3.61 |
| trivy-image | 6.56 |
| dockle | 11.53 |
| package-cache-empty | 1.75 |

### 20261021-093612-02-cli-deps-vulnerable-a3861a

| Stage | Duration (s) |
|---|---|
| runtime | 6.41 |
| gitleaks | 1.19 |
| history | 20.73 |
| semgrep | 6.53 |
| bandit | 3.81 |
| trivy-fs | 6.14 |
| syft | 7.08 |
| hadolint | 2.17 |
| build | 5.44 |
| cli-smoke | 2.22 |

### 20261021-093726-03-container-service-fixed-ad56b9

| Stage | Duration (s) |
|---|---|
| runtime | 6.22 |
| gitleaks | 1.94 |
| history | 11.86 |
| semgrep | 9.83 |
| bandit | 2.38 |
| trivy-fs | 4.91 |
| syft | 1.77 |
| hadolint | 1.7 |
| build | 5.7 |
| image-export | 3.67 |
| trivy-image | 9.05 |
| dockle | 17.81 |
| package-cache-empty | 1.39 |
| test-network | 0.67 |
| deploy | 1.48 |
| health | 1.12 |
| api-smoke | 0.98 |
| zap | 33.89 |

### 20261021-093956-03-container-service-vulnerable-8c8860

| Stage | Duration (s) |
|---|---|
| runtime | 5.59 |
| gitleaks | 1.31 |
| history | 8.86 |
| semgrep | 4.72 |
| bandit | 2.89 |
| trivy-fs | 4.89 |
| syft | 3.56 |

### 20261021-094047-01-flask-api-fixed-ffd215

| Stage | Duration (s) |
|---|---|
| runtime | 5.62 |
| gitleaks | 1.31 |
| history | 8.86 |
| semgrep | 5.0 |
| bandit | 4.42 |
| trivy-fs | 3.81 |
| syft | 3.31 |
| hadolint | 2.27 |
| build | 0.25 |
| image-export | 3.0 |
| trivy-image | 6.89 |
| dockle | 14.09 |
| package-cache-empty | 1.0 |
| test-network | 0.36 |
| deploy | 1.23 |
| health | 0.86 |
| api-smoke | 0.8 |
| zap | 31.88 |

### 20261021-094239-01-flask-api-vulnerable-39dd26

| Stage | Duration (s) |
|---|---|
| runtime | 5.58 |
| gitleaks | 1.22 |
| history | 12.5 |
| semgrep | 6.55 |
| bandit | 3.34 |
| trivy-fs | 3.89 |
| syft | 2.52 |

### 20261021-094326-02-cli-deps-fixed-1c5456

| Stage | Duration (s) |
|---|---|
| runtime | 5.81 |
| gitleaks | 1.7 |
| history | 7.03 |
| semgrep | 6.19 |
| bandit | 2.38 |
| trivy-fs | 4.64 |
| syft | 1.97 |
| hadolint | 1.56 |
| build | 0.38 |
| cli-smoke | 1.7 |
| image-export | 3.53 |
| trivy-image | 5.34 |
| dockle | 11.62 |
| package-cache-empty | 1.33 |

### 20261021-094444-02-cli-deps-vulnerable-a201e5

| Stage | Duration (s) |
|---|---|
| runtime | 1.02 |
| gitleaks | 6.39 |
| history | 7.17 |
| semgrep | 8.23 |
| bandit | 7.25 |
| trivy-fs | 3.77 |
| syft | 3.19 |
| hadolint | 1.5 |
| build | 0.53 |
| cli-smoke | 1.83 |

### 20261021-094540-03-container-service-fixed-51a564

| Stage | Duration (s) |
|---|---|
| runtime | 6.03 |
| gitleaks | 1.48 |
| history | 16.42 |
| semgrep | 6.42 |
| bandit | 3.45 |
| trivy-fs | 3.81 |
| syft | 3.95 |
| hadolint | 3.25 |
| build | 0.5 |
| image-export | 2.42 |
| trivy-image | 6.91 |
| dockle | 7.61 |
| package-cache-empty | 1.33 |
| test-network | 0.53 |
| deploy | 0.91 |
| health | 1.33 |
| api-smoke | 1.03 |
| zap | 29.7 |

### 20261021-094744-03-container-service-vulnerable-d6b5a1

| Stage | Duration (s) |
|---|---|
| runtime | 5.72 |
| gitleaks | 1.03 |
| history | 4264.91 |
| semgrep | 9.08 |
| bandit | 1.62 |
| trivy-fs | 2.59 |
| syft | 3.47 |

## 5. False positive assessment

Fill in during triage. A finding counts as a false positive only after
manual verification; the rate per tool is a core insight for the presentation.

| Tool | Findings | Verified true | False positive | FP rate |
|---|---|---|---|---|
| trivy-fs | 102 |  |  |  |
| trivy-image | 42 |  |  |  |
| Bandit | 36 |  |  |  |
| Semgrep OSS | 18 |  |  |  |
| dockle | 14 |  |  |  |
| gitleaks | 12 |  |  |  |
| owasp-zap | 6 |  |  |  |

## 6. Lessons learned

- Which tool produced the most actionable findings?
- Where did the gate block, and was the threshold appropriate?
- Which findings only the dynamic scan could reveal?
- What is still uncovered (container runtime security, IAST, pen testing)?
