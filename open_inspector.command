#!/bin/zsh
set -euo pipefail

cd "$(dirname "$0")"
exec npx @modelcontextprotocol/inspector --config inspector.json
