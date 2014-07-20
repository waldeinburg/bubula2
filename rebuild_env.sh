#!/bin/bash
# Creates python environment in env or first argument.
# Use -d to add requirements for developing (Fabric etc.)

ENV=env
DEV=

while getopts d OPT; do
    case $OPT in
    d) DEV=1;;
    esac
done

shift $((OPTIND - 1))

test -n "$1" && ENV=$1

rm -rf "$ENV"
virtualenv "$ENV"
source "$ENV/bin/activate" || exit 1
pip install -r envreq.txt --allow-external PIL --allow-unverified PIL
# Install developer requirements
test $DEV && pip install -r envreq-dev.txt
