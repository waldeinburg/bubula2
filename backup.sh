#!/bin/bash
# Backup db and media. Not implemented in Fabric because we do not
# intend to install Fabric on the host but want to run it as a cron job.

source backup_settings.inc.sh || exit 1

source "$ENV/bin/activate" || exit 1

TIME=$(date +%y%m%d-%H%M)
BACKUP_DB_FILENAME="bubula2-db-$TIME.sql.gz"
BACKUP_MEDIA_FILENAME="bubula2-media-$TIME.tar.gz"

"$GIT/manage.py" dbdump --destination="$BACKUP_DIR" --filename="${BACKUP_DB_FILENAME%'.gz'}" --compress=gzip

echo "Creating media tarball ..." >&2
tar -vczf "$BACKUP_DIR/$BACKUP_MEDIA_FILENAME" "$MEDIA" 

# change latest
cd "$BACKUP_DIR" || exit 1
rm -f "$BACKUP_DB_LATEST_FILENAME" "$BACKUP_MEDIA_LATEST_FILENAME"
ln -s "$BACKUP_DB_FILENAME" "$BACKUP_DB_LATEST_FILENAME"
ln -s "$BACKUP_MEDIA_FILENAME" "$BACKUP_MEDIA_LATEST_FILENAME"
