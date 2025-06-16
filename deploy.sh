#!/bin/bash

echo "Starting deployment..."

# Activate your virtual environment
source /home/ubuntu/fund_management_system/venv/bin/activate

# Navigate to your project directory
cd /home/ubuntu/fund_management_system

# Pull latest changes from GitHub
git pull origin main

# Install new dependencies if any
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --noinput

# OPTIONAL: Run migrations manually when needed
# echo "Run migrations manually if you want."
# python manage.py migrate

# Restart your Gunicorn systemd service
sudo systemctl restart fund_management_system.service

echo "Deployment complete."