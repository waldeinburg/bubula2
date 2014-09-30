#!/bin/bash
# Settings based on fabconfig.
BACKUP_DIR='{{ paths[dest].backup_dir }}'
BACKUP_DB_LATEST_FILENAME='{{ paths.backup_db_latest_filename }}'
BACKUP_MEDIA_LATEST_FILENAME='{{ paths.backup_media_latest_filename }}'
ENV='{{ paths[dest].env }}'
GIT='{{ paths[dest].git }}'
MEDIA='{{ paths[dest].media }}'
