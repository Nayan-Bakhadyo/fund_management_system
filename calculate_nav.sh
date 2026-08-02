#!/bin/bash

# NAV Calculation Script for BE Investment Firm
# Delegates to the Django management command to ensure a single calculation path.
# Usage: ./calculate_nav.sh

# Set script directory and Django project path
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$SCRIPT_DIR"
SHARE_PRICE_CSV="$PROJECT_DIR/mainapp/utilities/share_price.csv"

# Check if share_price.csv exists
if [ ! -f "$SHARE_PRICE_CSV" ]; then
    echo "Error: Share price CSV file not found at $SHARE_PRICE_CSV"
    exit 1
fi

# Activate virtual environment if it exists
if [ -f "$PROJECT_DIR/venv/bin/activate" ]; then
    source "$PROJECT_DIR/venv/bin/activate"
    echo "Virtual environment activated"
elif [ -f "$HOME/anaconda3/envs/BE_inv/bin/activate" ]; then
    source "$HOME/anaconda3/envs/BE_inv/bin/activate"
    echo "Conda environment activated"
fi

# Change to Django project directory
cd "$PROJECT_DIR"

# Export Django settings
export DJANGO_SETTINGS_MODULE=be_inv_project.settings

# Run the Django management command (single source of truth for NAV calculation)
echo "Starting NAV calculation..."
python manage.py calculate_nav --verbose

# Store exit code
exit_code=$?

# Exit with the same code as the management command
if [ $exit_code -eq 0 ]; then
    echo "NAV calculation completed successfully!"
else
    echo "NAV calculation failed! Check the logs above."
fi

exit $exit_code
