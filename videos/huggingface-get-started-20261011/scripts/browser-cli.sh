#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
export TMPDIR="$PWD/.cache/tmp" TMP="$PWD/.cache/tmp" TEMP="$PWD/.cache/tmp"
export npm_config_cache="$PWD/.cache/npm"
export PLAYWRIGHT_DAEMON_SESSION_DIR="$PWD/.cache/playwright-sessions"
# macOS Unix socket paths must be short. This transport-only exception is cleaned after capture.
export PLAYWRIGHT_DAEMON_SOCKETS_DIR="/tmp/hf-getstarted-8653"
exec playwright-cli -s=hfintro "$@"
