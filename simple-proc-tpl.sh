#!/bin/bash

if [[ $# -lt 2 || $# -gt 3 ]]; then
    cat <<EOF >&2
Simple Template Processor
Usage: $0 <template> <data> [output]

All arguments are filenames.
Template field are marked as %FIELD%
Data file should contain lines of the form
FIELD=value
Field names must consist of uppercase letters and underscores only.
EOF
    exit 1
fi

TPL="$1"
DATA="$2"
OUTPUT=${3:-'/dev/stdout'}

cat "$TPL" | sed "$(cat "$DATA" | sed -r 's/[\/&]/\\\0/g; s/([A-Z_]+)=(.*)/s\/%\1%\/\2\//')" > "$OUTPUT"
