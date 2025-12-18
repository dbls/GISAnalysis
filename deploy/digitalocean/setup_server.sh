#!/bin/bash

# DigitalOcean Droplet Setup Script for GIS Satellite Analysis Application
# Run this script on a fresh Ubuntu 22.04 droplet
# Usage: sudo bash setup_server.sh

set -e  # Exit on error

echo "======================================"
echo "GIS Analysis - Server Setup"
echo "======================================"
echo ""

# Update system
echo "Updating system packages..."
apt-get update
apt-get upgrade -y

# Install essential tools
echo "Installing essential tools..."
apt-get install -y \
    build-essential \
    curl \
    wget \
    git \
    unzip \
    software-properties-common \
    ca-certificates \
    gnupg \
    lsb-release

# Install Python 3.11
echo "Installing Python 3.11..."
add-apt-repository ppa:deadsnakes/ppa -y
apt-get update
apt-get install -y \
    python3.11 \
    python3.11-venv \
    python3.11-dev \
    python3-pip

# Set Python 3.11 as default
update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1

# Install GDAL
echo "Installing GDAL..."
add-apt-repository ppa:ubuntugis/ppa -y
apt-get update
apt-get install -y \
    gdal-bin \
    libgdal-dev \
    python3-gdal

# Verify GDAL installation
echo "GDAL version:"
gdalinfo --version

# Install PostgreSQL
echo "Installing PostgreSQL..."
apt-get install -y postgresql postgresql-contrib postgresql-server-dev-all

# Start PostgreSQL
systemctl start postgresql
systemctl enable postgresql

# Install Node.js 18.x
echo "Installing Node.js 18..."
curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
apt-get install -y nodejs

# Verify Node installation
echo "Node version:"
node --version
npm --version

# Install nginx
echo "Installing nginx..."
apt-get install -y nginx

# Install certbot for SSL
echo "Installing Certbot for SSL..."
apt-get install -y certbot python3-certbot-nginx

# Install PM2 for process management (optional, alternative to systemd)
echo "Installing PM2..."
npm install -g pm2

# Configure firewall
echo "Configuring firewall..."
ufw allow OpenSSH
ufw allow 'Nginx Full'
ufw --force enable

# Create application user
echo "Creating application user..."
if ! id -u gisapp > /dev/null 2>&1; then
    useradd -m -s /bin/bash gisapp
    echo "User 'gisapp' created"
else
    echo "User 'gisapp' already exists"
fi

# Create application directory
echo "Creating application directory..."
mkdir -p /var/www/gis-analysis
chown -R gisapp:gisapp /var/www/gis-analysis

# Create PostgreSQL database and user
echo "Setting up PostgreSQL database..."
sudo -u postgres psql -c "CREATE DATABASE gis_analysis;" || echo "Database already exists"
sudo -u postgres psql -c "CREATE USER gisapp WITH PASSWORD 'change_this_password';" || echo "User already exists"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE gis_analysis TO gisapp;"
sudo -u postgres psql -c "ALTER USER gisapp WITH SUPERUSER;" # For initial table creation

echo ""
echo "======================================"
echo "Server Setup Complete!"
echo "======================================"
echo ""
echo "Next steps:"
echo "1. Change PostgreSQL password: sudo -u postgres psql -c \"ALTER USER gisapp WITH PASSWORD 'your_secure_password';\""
echo "2. Clone your application: cd /var/www/gis-analysis && git clone <your-repo>"
echo "3. Run the application setup script: ./deploy/digitalocean/setup_app.sh"
echo ""
echo "Installed versions:"
python3 --version
node --version
gdalinfo --version
psql --version
nginx -v
echo ""
