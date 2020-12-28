#!/usr/bin/env bash
# Replacement for "rsync -avuz --delete <folder> <host>:<folder>" when rsync does not exist on server.
# Currently all files are copied with no attempt to leave out unchanged files.
# Deleted files are detected and deleted.

if [[ $# -lt 3 ]]; then
    echo "Usage: $0 <src-folder> <host> <dest-folder>"
    exit 1
fi

SRC=$1
REMOTE_HOST=$2
DEST=$3
deleted_dirs=

function find_type_in_src() {
    cd "$SRC" && find -type "$1" | sort
}

function find_type_in_dest() {
    ssh "$REMOTE_HOST" "cd '$DEST' && find -type '$1' | sort"
}

function diff_find() {
    diff <(echo "$1") <(echo "$2") | sed -rn '/^> / { s/> (.*)/\1/; p }'
}

function remove_deleted_dirs_from_list() {
    local list=$1

    while read -r d; do
        list=$(echo "$list" | grep -Pv "^\Q$d\E/")
    done <<<"$deleted_dirs"
    echo "$list"
}

function delete_from_list() {
    local list=$1
    local name=$2

    if [[ "$list" ]]; then
        echo "Deleting $name ..."
        while read -r item; do
            echo "$item"
            ssh "$REMOTE_HOST" "cd '$DEST' && rm -r '$item'" </dev/null
        done <<<"$list"
    else
        echo "No $name to delete."
    fi
}

local_files=$(find_type_in_src f)
local_dirs=$(find_type_in_src d)
remote_files=$(find_type_in_dest f)
remote_dirs=$(find_type_in_dest d)
deleted_dirs=$(diff_find "$local_dirs" "$remote_dirs")
deleted_files=$(diff_find "$local_files" "$remote_files")

# Ignore subdirectories of deleted directories.
deleted_dirs=$(remove_deleted_dirs_from_list "$deleted_dirs")
# Ignore files in deleted directories.
deleted_files=$(remove_deleted_dirs_from_list "$deleted_files")

echo "Copying files ..."
cd "$SRC" && scp -r . "$REMOTE_HOST":"$DEST"

delete_from_list "$deleted_dirs" 'directories'
delete_from_list "$deleted_files" 'files'
