#!/bin/bash

# Script to update the application with latest changes
# Run as gisapp user: bash update_app.sh

set -e

APP_DIR="/var/www/gis-analysis"

echo "======================================"
echo "Updating GIS Analysis Application"
echo "======================================"
echo ""

cd "$APP_DIR"

# Pull latest changes
echo "Pulling latest changes from Git..."
git pull

# Update backend
echo ""
echo "Updating backend..."
cd backend
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
deactivate

# Update frontend
echo ""
echo "Updating frontend..."
cd "$APP_DIR/frontend"
npm install
npm run build

echo ""
echo "======================================"
echo "Update Complete!"
echo "======================================"
echo ""
echo "Don't forget to restart the service:"
echo "  sudo systemctl restart gis-analysis"
echo "  sudo systemctl reload nginx"
echo ""
