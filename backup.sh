#!/bin/bash

# Set variables
BACKUP_DIR="/home/ubuntu/db_backups"
DB_PATH="/home/ubuntu/fund_management_system/db.sqlite3"
DATE=$(date +"%Y%m%d_%H%M%S")
BACKUP_NAME="db_backup_$DATE.sqlite3"

# Make sure backup directory exists
mkdir -p $BACKUP_DIR

# Copy DB file to backup directory with timestamp
cp $DB_PATH $BACKUP_DIR/$BACKUP_NAME
