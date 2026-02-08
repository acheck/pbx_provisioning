#!/usr/bin/env bash
# Refresh unique-output-patterns.txt from this project's provisioning/ vendor model files.
# Extracts all output= values from *.txt files, deduplicates and sorts.

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROVISIONING_DIR="${PROVISIONING_DIR:-$SCRIPT_DIR/provisioning}"
OUTPUT_FILE="${OUTPUT_FILE:-$SCRIPT_DIR/unique-output-patterns.txt}"

if [[ ! -d "$PROVISIONING_DIR" ]]; then
  echo "Error: provisioning directory not found: $PROVISIONING_DIR" >&2
  exit 1
fi

header='# Unique '"'"'output'"'"' fields from '"$PROVISIONING_DIR"' vendor model files
# Source: *model*.txt, *.txt in tl-*-templates and models.d/
# Generated: sorted list, one pattern per line
'

patterns=$(grep -h -r --include='*.txt' -E '^output=' "$PROVISIONING_DIR" 2>/dev/null \
  | sed 's/^output=//' \
  | sort -u)

{
  echo "$header"
  echo "$patterns"
} > "$OUTPUT_FILE"

count=$(grep -v -e '^#' -e '^$' "$OUTPUT_FILE" | wc -l)
echo "Wrote $count unique output patterns to $OUTPUT_FILE"
