#!/bin/sh
set -eu

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
CRAWLER_DIR="$(dirname -- "$SCRIPT_DIR")"

cd "$CRAWLER_DIR"

PYTHON_BIN="${PYTHON_BIN:-python3}"
FETCH_FILTER_INIT_BIN="${FETCH_FILTER_INIT_BIN:-./bin/fetch_filter_init.sh}"
GENERATE_MAPPINGS_BIN="${GENERATE_MAPPINGS_BIN:-./bin/generate_mappings.sh}"

echo "Starting parallel Filter.init fetch for armor and weapons..."

"$FETCH_FILTER_INIT_BIN" "https://www.wowhead.com/items/armor" armor &
armor_pid=$!

"$FETCH_FILTER_INIT_BIN" "https://www.wowhead.com/items/weapons" weapons &
weapons_pid=$!

armor_status=0
weapons_status=0

wait "$armor_pid" || armor_status=$?
wait "$weapons_pid" || weapons_status=$?

if [ "$armor_status" -ne 0 ] || [ "$weapons_status" -ne 0 ]; then
  echo "Failed to refresh Filter.init data." >&2
  exit 1
fi

echo "Generating normalized mappings..."
"$PYTHON_BIN" -m scripts.generate_normalized_mappings

echo "Generating crawler mappings module..."
"$GENERATE_MAPPINGS_BIN"

echo "Mappings update completed successfully."
