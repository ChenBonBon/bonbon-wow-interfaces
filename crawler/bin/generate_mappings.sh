#!/bin/sh
set -eu

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
CRAWLER_DIR="$(dirname -- "$SCRIPT_DIR")"

cd "$CRAWLER_DIR"
python3 -m scripts.generate_mappings "$@"
