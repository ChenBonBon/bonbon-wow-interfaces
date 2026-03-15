#!/bin/sh
set -eu

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
CRAWLER_DIR="$(dirname -- "$SCRIPT_DIR")"

cd "$CRAWLER_DIR"

if [ "$#" -lt 1 ] || [ "$#" -gt 2 ]; then
  echo "Usage: ./bin/fetch_filter_init.sh <url> [name]" >&2
  exit 1
fi

OUTPUT_NAME="${2:-filter-page}"
HTML_OUTPUT_PATH="outputs/filter_pages/${OUTPUT_NAME}.html"

python3 -m scripts.fetch_filter_page "$1" "$HTML_OUTPUT_PATH"
python3 -m scripts.extract_filter_init "$HTML_OUTPUT_PATH"
