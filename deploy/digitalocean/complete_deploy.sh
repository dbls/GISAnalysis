#!/bin/bash

# Complete GIS Analysis Deployment Script for DigitalOcean
# This script does EVERYTHING - from fresh droplet to running application
# Run as root: curl -fsSL <raw_github_url> | bash
# Or: wget -O - <raw_github_url> | bash

set -e

echo "=========================================="
echo "GIS Analysis - Complete Deployment"
echo "=========================================="
echo ""

# Configuration
APP_DIR="/var/www/gis-analysis"
APP_USER="gisapp"
REPO_URL="https://github.com/dbls/GISAnalysis.git"

# Get configuration from user or environment
if [ -z "$ANTHROPIC_API_KEY" ]; then
    read -p "Enter your Anthropic API key: " ANTHROPIC_API_KEY
fi

if [ -z "$DB_PASSWORD" ]; then
    read -sp "Enter PostgreSQL password for gisapp user: " DB_PASSWORD
    echo ""
fi

# Get server IP
SERVER_IP=$(curl -s ifconfig.me)
echo "Detected server IP: $SERVER_IP"
echo ""

# Update system
echo "Step 1/10: Updating system..."
apt-get update -qq
apt-get upgrade -y -qq

# Install Python 3.11
echo "Step 2/10: Installing Python 3.11..."
add-apt-repository ppa:deadsnakes/ppa -y >/dev/null 2>&1
apt-get update -qq
apt-get install -y -qq python3.11 python3.11-venv python3.11-dev python3-pip
update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1 >/dev/null 2>&1

# Install GDAL
echo "Step 3/10: Installing GDAL..."
add-apt-repository ppa:ubuntugis/ppa -y >/dev/null 2>&1
apt-get update -qq
apt-get install -y -qq gdal-bin libgdal-dev python3-gdal

# Install PostgreSQL
echo "Step 4/10: Installing PostgreSQL..."
apt-get install -y -qq postgresql postgresql-contrib postgresql-server-dev-all
systemctl start postgresql
systemctl enable postgresql >/dev/null 2>&1

# Install Node.js 18
echo "Step 5/10: Installing Node.js 18..."
curl -fsSL https://deb.nodesource.com/setup_18.x | bash - >/dev/null 2>&1
apt-get install -y -qq nodejs

# Install Nginx
echo "Step 6/10: Installing Nginx..."
apt-get install -y -qq nginx
systemctl start nginx
systemctl enable nginx >/dev/null 2>&1

# Install Certbot
echo "Installing Certbot..."
apt-get install -y -qq certbot python3-certbot-nginx

# Configure firewall
echo "Configuring firewall..."
ufw allow OpenSSH >/dev/null 2>&1
ufw allow 'Nginx Full' >/dev/null 2>&1
echo "y" | ufw enable >/dev/null 2>&1

# Create application user
echo "Step 7/10: Creating application user..."
if ! id -u $APP_USER > /dev/null 2>&1; then
    useradd -m -s /bin/bash $APP_USER
fi

# Create application directory
mkdir -p $APP_DIR
chown -R $APP_USER:$APP_USER $APP_DIR

# Setup PostgreSQL database
echo "Step 8/10: Setting up PostgreSQL database..."
sudo -u postgres psql << EOF >/dev/null 2>&1
DROP DATABASE IF EXISTS gis_analysis;
DROP USER IF EXISTS $APP_USER;
CREATE DATABASE gis_analysis;
CREATE USER $APP_USER WITH PASSWORD '$DB_PASSWORD';
GRANT ALL PRIVILEGES ON DATABASE gis_analysis TO $APP_USER;
ALTER DATABASE gis_analysis OWNER TO $APP_USER;
EOF

# Clone repository and setup application
echo "Step 9/10: Setting up application..."

sudo -u $APP_USER bash << USERSCRIPT
set -e

# Clone repository
cd $APP_DIR
if [ ! -d ".git" ]; then
    git clone $REPO_URL .
else
    git pull
fi

# Fix GDAL version
sed -i 's/GDAL==3.8.0/GDAL==3.4.1/' backend/requirements.txt

# Setup backend
cd backend
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip -q
pip install -r requirements.txt -q
deactivate

# Create backend .env
cat > .env << ENV
ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY
DATABASE_URL=postgresql://$APP_USER:$DB_PASSWORD@localhost/gis_analysis
ENV

# Create directories
mkdir -p uploads data

# Setup frontend
cd ../frontend

# Create frontend .env.production
cat > .env.production << FRONTENV
REACT_APP_API_URL=http://$SERVER_IP/api
FRONTENV

# Install and build
npm install -q
npm run build -q

USERSCRIPT

# Setup systemd service
echo "Step 10/10: Configuring services..."

# Create log directory
mkdir -p /var/log/gis-analysis
chown $APP_USER:$APP_USER /var/log/gis-analysis

# Copy systemd service
cp $APP_DIR/deploy/digitalocean/gis-analysis.service /etc/systemd/system/
systemctl daemon-reload
systemctl start gis-analysis
systemctl enable gis-analysis >/dev/null 2>&1

# Setup Nginx
cp $APP_DIR/deploy/digitalocean/nginx.conf /etc/nginx/sites-available/gis-analysis
sed -i "s/your-domain.com/$SERVER_IP/g" /etc/nginx/sites-available/gis-analysis
ln -sf /etc/nginx/sites-available/gis-analysis /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Test and restart nginx
nginx -t
systemctl restart nginx

echo ""
echo "=========================================="
echo "✓ Deployment Complete!"
echo "=========================================="
echo ""
echo "Your application is now running at:"
echo "  http://$SERVER_IP"
echo ""
echo "Useful commands:"
echo "  Check backend: systemctl status gis-analysis"
echo "  View logs:     journalctl -u gis-analysis -f"
echo "  Restart:       systemctl restart gis-analysis"
echo ""
echo "Next steps:"
echo "  1. Visit http://$SERVER_IP in your browser"
echo "  2. Upload a GeoTIFF image"
echo "  3. Try query: 'number of cars'"
echo ""
echo "For SSL/HTTPS setup with a domain:"
echo "  certbot --nginx -d your-domain.com"
echo ""
