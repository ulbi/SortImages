---
type: operations-reference
title: Repository Guidance and Coding-Agent Configuration
description: Reference for the repository's coding-agent rules, LiteLLM provider settings, Optio setup helper, and validation expectations. It distinguishes agent tooling from the photo sorter's runtime configuration.
tags: [agent-configuration, repository-guidance, openwiki, litellm, codex, opencode, validation]
verified:
  - by: openwiki/0.9.0
    at: 2026-11-11T09:15:33.931Z
sources:
  - id: openwiki-source-ab585d88aca3958f2aa6a541
    resource: repo://.codex/config.toml
  - id: openwiki-source-837bd45ca24533212df316cc
    resource: repo://.optio/setup.sh
  - id: openwiki-source-8037e2358a2c4f9b2c722a11
    resource: repo://AGENTS.md
  - id: openwiki-source-8f91c5dcedd3f2e4b50c55de
    resource: repo://opencode.json
  - id: openwiki-source-edab51d2990d321ab74ffdac
    resource: repo://sortinfolder.py
generated: { by: "openwiki/0.9.0", at: "2026-11-11T09:15:33.931Z" }
---

# Repository Guidance and Coding-Agent Configuration

This page describes tooling that affects a coding agent working in this repository. It is **not** configuration for the photo-sorting application. [`AGENTS.md`](../../AGENTS.md), [`.codex/config.toml`](../../.codex/config.toml), [`opencode.json`](../../opencode.json), and [`.optio/setup.sh`](../../.optio/setup.sh) guide the agent and its model provider; the application itself reads no configuration file or environment variable and exposes only command-line flags. See [CLI, Configuration, and Operations](cli-and-configuration.md) for that runtime surface.

## Repository guidance in `AGENTS.md`

The repository-level `AGENTS.md` contains an OpenWiki guidance block. Its policy has four practical parts:

### Use the wiki only as just-in-time context

The generated `openwiki/` tree is optional context, not mandatory startup reading. An agent must not enumerate, preload, or search wikis when a task begins. It should retrieve context when the user asks for it, when unfamiliar architecture or dependency behavior materially affects the task, or when source inspection leaves an important uncertainty; retrieval should stop once the question is grounded.

When the OpenWiki retrieval tools are available, the documented sequence is:

1. Use `openwiki_search` for just-in-time context.
2. Use `openwiki_read` for the relevant complete sections.
3. If search returns `workspace_required`, ask which listed workspace to use and retry with its ID.
4. Use `openwiki_list_workspaces` or `openwiki_list_wikis` only when workspace membership itself needs to be discovered.

If those retrieval tools are unavailable, the fallback is to read [`openwiki/quickstart.md`](../../openwiki/quickstart.md) and follow its links to the relevant pages. The [Quickstart](../quickstart.md) is therefore also the task-routing map for the rest of this wiki.

### Treat source and tests as authoritative

`AGENTS.md` explicitly makes source code and tests authoritative. Unknowns and review items in a brief are verification gaps, not automatic requirements: they should be checked against the repository rather than converted into additional scope without evidence.

### Validate narrowly and retain failure output

Changes should use the **narrowest quiet validation** that proves the changed behavior, and the **complete failure output** should be preserved. For changes to the sorter, the behavioral checks and their invocation styles are documented in [Test Suite](../testing/test-suite.md). That page also explains the distinction between the full local pytest suite and the minimal CI import check.

### Let the maintenance process regenerate generated pages

After source changes, `AGENTS.md` directs agents to use the repository's documented maintenance process to refresh generated pages and to check its configuration and completed runs before relying on automatic updates. Generated OpenWiki pages must not be hand-edited unless that is explicitly requested; the preferred path is to update source code or documentation and let OpenWiki regenerate the page. `AGENTS.md` points to that documented process rather than embedding a refresh command, so this page does not prescribe one.

## LiteLLM provider configuration

Both coding-agent clients are routed through a provider named `litellm`.

### Codex: `.codex/config.toml`

The repository's Codex project configuration selects:

| Setting | Value |
| --- | --- |
| `model_provider` | `litellm` |
| `model` | `coding-router` |
| Provider `name` | `LiteLLM (Optio #1006)` |
| Provider `base_url` | `http://litellm-proxy.agents.svc:4000/v1` |
| Provider `env_key` | `OPENAI_API_KEY` |
| Provider `wire_api` | `responses` |

The file's comment states that Codex loads this project configuration from the repository worktree. The provider block therefore fixes the LiteLLM proxy endpoint, names the environment variable from which the API key is obtained, and selects the Responses wire API for the `coding-router` model.

### OpenCode: `opencode.json`

The OpenCode configuration declares the same provider name with a dynamic endpoint and model selection:

| Setting | Value |
| --- | --- |
| Provider | `litellm` |
| Provider package | `@ai-sdk/openai-compatible` |
| `options.baseURL` | `{env:OPENCODE_BASE_URL}` |
| `options.apiKey` | `{env:OPENAI_API_KEY}` |
| Model key | `{env:OPENCODE_MODEL}` |

Unlike the fixed `base_url` in the Codex configuration, OpenCode obtains both its base URL and model identifier through environment-variable substitutions. The file also grants agent permissions explicitly: `permission.external_directory` is `allow` and `permission.bash` is `allow`. These are broad coding-agent permissions and should be considered when planning operations that access paths outside the repository or execute shell commands.

## The Optio setup helper

[`.optio/setup.sh`](../../.optio/setup.sh) is a Bash helper with `set -euo pipefail`. It creates `${HOME}/.codex` if needed and then overwrites `${HOME}/.codex/config.toml` with this configuration:

```toml
model_provider = "litellm"
model = "coding-router"

[model_providers.litellm]
name = "LiteLLM (Optio)"
base_url = "http://litellm-proxy.agents.svc:4000/v1"
env_key = "OPENAI_API_KEY"
wire_api = "responses"
```

The helper writes a **home-directory configuration outside the repository**. Its core provider settings match the repository's `.codex/config.toml`; the display name differs (`LiteLLM (Optio)` rather than `LiteLLM (Optio #1006)`). The script finishes by printing `[optio] wrote ${HOME}/.codex/config.toml (AK4 LiteLLM provider)`.

This outside-repository write is separate from the tracked project configuration. Changes to the repository's `.codex/config.toml` do not by themselves rewrite the generated home-directory file, and changes to the home-directory file do not change the tracked repository file.

## Application boundary

The provider settings and agent instructions affect model access and working behavior only. The application in [`sortinfolder.py`](../../sortinfolder.py) has no runtime configuration surface beyond its `argparse` flags: two positional paths plus `--log`, `--threads`, and `--dry-run`. It does not load `AGENTS.md`, `.codex/config.toml`, `opencode.json`, or the Optio helper, and it does not consult environment variables.

For the application's architecture and workflow, see [Architecture Overview](../architecture/overview.md); for its complete operational behavior, see [CLI, Configuration, and Operations](cli-and-configuration.md).
