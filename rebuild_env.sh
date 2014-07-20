#!/bin/bash
# Creates python environment.
# Use -d to add requirements for developing (Fabric etc.)

ENV=env
DEV=

while getopts d OPT; do
    case $OPT in
    d) DEV=1;;
    esac
done

rm -rf $ENV
virtualenv $ENV
. $ENV/bin/activate
pip install -r envreq.txt --allow-external PIL --allow-unverified PIL
# Install developer requirements
[ $DEV ] && pip install -r envreq-dev.txt
