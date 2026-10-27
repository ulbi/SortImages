#!/usr/bin/env bash
set -euo pipefail

mkdir -p "${HOME}/.codex"
cat > "${HOME}/.codex/config.toml" <<CODE_EOF
model_provider = "litellm"
model = "coding-router"

[model_providers.litellm]
name = "LiteLLM (Optio)"
base_url = "http://litellm-proxy.agents.svc:4000/v1"
env_key = "OPENAI_API_KEY"
wire_api = "responses"
CODE_EOF

echo "[optio] wrote ${HOME}/.codex/config.toml (AK4 LiteLLM provider)"
