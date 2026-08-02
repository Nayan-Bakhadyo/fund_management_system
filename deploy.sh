#!/bin/bash
set -e

echo "Starting deployment..."

# Activate virtual environment
source /home/ubuntu/fund_management_system/venv/bin/activate

# Navigate to project directory
cd /home/ubuntu/fund_management_system

# Pull latest changes from GitHub
git pull origin server

# Install new dependencies if any
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --noinput

# Run database migrations
python manage.py migrate

# Restart Gunicorn service
sudo systemctl restart fund_management_system.service

echo "Deployment complete."