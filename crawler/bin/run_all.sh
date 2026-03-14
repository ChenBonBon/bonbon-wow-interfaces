#!/bin/sh
set -eu

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
CRAWLER_DIR="$(dirname -- "$SCRIPT_DIR")"

cd "$CRAWLER_DIR"

if [ "$#" -eq 0 ]; then
  set -- "tasks/wowhead_items.json"
fi

python3 -m scripts.run_all "$@"
