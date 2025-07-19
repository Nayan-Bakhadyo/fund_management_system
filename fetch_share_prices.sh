#!/bin/bash

# Fetch Share Prices Script
# This script runs the Django management command to fetch latest share prices

echo "Starting share price fetch at $(date)"

# Activate virtual environment
source /home/ubuntu/fund_management_system/venv/bin/activate

# Navigate to project directory
cd /home/ubuntu/fund_management_system

# Run the Django management command to fetch share prices
python manage.py fetch_share_prices

# Check if the command was successful
if [ $? -eq 0 ]; then
    echo "Share prices fetched successfully at $(date)"
else
    echo "Error fetching share prices at $(date)" >&2
    exit 1
fi
