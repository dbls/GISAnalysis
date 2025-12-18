#!/bin/bash

# Application Setup Script
# Run this script as the gisapp user after server setup
# Usage: bash setup_app.sh

set -e

echo "======================================"
echo "GIS Analysis - Application Setup"
echo "======================================"
echo ""

# Get configuration
read -p "Enter your GitHub repository URL: " REPO_URL
read -p "Enter your Anthropic API key: " ANTHROPIC_API_KEY
read -sp "Enter PostgreSQL password for gisapp user: " DB_PASSWORD
echo ""
read -p "Enter your domain name (or server IP): " DOMAIN

APP_DIR="/var/www/gis-analysis"

# Clone repository
echo "Cloning repository..."
if [ ! -d "$APP_DIR/.git" ]; then
    git clone "$REPO_URL" "$APP_DIR"
else
    echo "Repository already cloned, pulling latest changes..."
    cd "$APP_DIR"
    git pull
fi

cd "$APP_DIR"

# Setup backend
echo ""
echo "Setting up backend..."
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Create .env file
echo "Creating backend .env file..."
cat > .env <<EOF
ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY
DATABASE_URL=postgresql://gisapp:$DB_PASSWORD@localhost/gis_analysis
EOF

# Create uploads and data directories
mkdir -p uploads data

echo "Backend setup complete!"

# Setup frontend
echo ""
echo "Setting up frontend..."
cd "$APP_DIR/frontend"

# Install dependencies
echo "Installing Node.js dependencies..."
npm install

# Create .env.production
echo "Creating frontend .env.production..."
cat > .env.production <<EOF
REACT_APP_API_URL=https://$DOMAIN/api
EOF

# Build frontend
echo "Building frontend..."
npm run build

echo "Frontend setup complete!"

# Set permissions
echo ""
echo "Setting permissions..."
cd "$APP_DIR"
sudo chown -R gisapp:gisapp "$APP_DIR"
chmod -R 755 "$APP_DIR"

echo ""
echo "======================================"
echo "Application Setup Complete!"
echo "======================================"
echo ""
echo "Next steps:"
echo "1. Copy systemd service file: sudo cp deploy/digitalocean/gis-analysis.service /etc/systemd/system/"
echo "2. Copy nginx config: sudo cp deploy/digitalocean/nginx.conf /etc/nginx/sites-available/gis-analysis"
echo "3. Enable nginx site: sudo ln -s /etc/nginx/sites-available/gis-analysis /etc/nginx/sites-enabled/"
echo "4. Start the service: sudo systemctl start gis-analysis"
echo "5. Enable on boot: sudo systemctl enable gis-analysis"
echo "6. Restart nginx: sudo systemctl restart nginx"
echo "7. Setup SSL: sudo certbot --nginx -d $DOMAIN"
echo ""
