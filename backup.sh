#!/bin/bash

# Set paths
DB_FILE="/home/ubuntu/fund_management_system/db.sqlite3"
BACKUP_DIR="/home/ubuntu/db_backups"
FILENAME="db_backup_$(date +%F_%H-%M-%S).sqlite3"

# Ensure the backup directory exists
mkdir -p "$BACKUP_DIR"

# Copy the database file
cp --preserve=all "$DB_FILE" "$BACKUP_DIR/$FILENAME"

# Delete backups older than 30 days
find "$BACKUP_DIR" -name "db_backup_*.sqlite3" -type f -mtime +30 -exec rm -f {} \;
