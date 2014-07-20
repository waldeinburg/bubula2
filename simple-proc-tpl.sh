#!/bin/bash

if [[ $# -lt 2 || $# -gt 3 ]]; then
    cat <<EOF >&2
Simple Template Processor
Usage: $0 <template> <context> [output]

All arguments are filenames.
Template field are marked as %FIELD%
Context file should contain lines of the form
FIELD=value
Field names must consist of uppercase letters and underscores only.
Make a directive in the data file by beginning a line with %:
%include <file>
Comments can be made by starting a line with #.
EOF
    exit 1
fi

TPL="$1"
MAIN_CTX_FILE="$2"
CTX_DIR=$(dirname "$MAIN_DATA_FILE")
OUTPUT=${3:-'/dev/stdout'}

process_data_file() {
    CTX_FILE=$1
    cat "$CTX_FILE" | while read LINE; do
        if echo "$LINE" | grep -q '^%'; then
            DIRECTIVE=$(echo "$LINE" | cut -d' ' -f1 | cut -c 2-)
            case $DIRECTIVE in
            'include')
                INC_FILE=$(echo "$LINE" | cut -d' ' -f2)
                process_data_file "$CTX_DIR/$INC_FILE"
                if [ $? -ne 0 ]; then
                    echo "Error reading include file!" >&2
                    exit 1
                fi
                ;;
            *) echo "Invalid directive '$DIRECTIVE'!" >&2
               exit 1
               ;;
            esac
        elif ! echo "$LINE" | grep -q '^#'; then
            echo "$LINE"
        fi
    done
}

CTX=$(process_data_file "$MAIN_DATA_FILE")

cat "$TPL" | sed "$(echo "$CTX" | sed -r 's/[\/&]/\\\0/g; s/([A-Z_]+)=(.*)/s\/%\1%\/\2\/g/')" > "$OUTPUT"
