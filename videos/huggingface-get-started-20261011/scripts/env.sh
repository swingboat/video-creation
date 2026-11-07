#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p .cache/tmp .cache/npm .cache/remotion-browser
export TMPDIR="$PWD/.cache/tmp" TMP="$PWD/.cache/tmp" TEMP="$PWD/.cache/tmp"
export npm_config_cache="$PWD/.cache/npm"
export PLAYWRIGHT_BROWSERS_PATH="$PWD/.cache/playwright-browsers"
export REMOTION_BROWSER_EXECUTABLE="${REMOTION_BROWSER_EXECUTABLE:-}"
export PATH="$PWD/node_modules/.bin:$PATH"
exec "$@"
