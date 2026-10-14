#!/usr/bin/env bash
# Seed the Vault dev instance with the secrets the pipeline needs and print the
# export lines for the CI runner. Never commit the output of this script.
set -Eeuo pipefail

VAULT_ADDR="${VAULT_ADDR:-http://127.0.0.1:8200}"
VAULT_TOKEN="${VAULT_TOKEN:-dev-only-root-token}"
export VAULT_ADDR VAULT_TOKEN

echo "enabling the kv-v2 engine at secret/"
vault secrets enable -path=secret kv-v2 2>/dev/null || true

echo "writing the demo secrets"
vault kv put secret/devsecops/demo \
  api_token="$(openssl rand -hex 24)" \
  db_password="$(openssl rand -base64 24)"

echo "creating a least-privilege read policy for the runner"
vault policy write ci-runner - <<'POLICY'
path "secret/data/devsecops/demo" {
  capabilities = ["read"]
}
POLICY

RUNNER_TOKEN="$(vault token create -policy=ci-runner -ttl=1h -field=token)"
cat <<INFO

Runner token created (TTL 1h). Export it in the shell that runs the pipeline:

  export TEST_API_TOKEN="\$(VAULT_TOKEN=${RUNNER_TOKEN} vault kv get -field=api_token secret/devsecops/demo)"

INFO
