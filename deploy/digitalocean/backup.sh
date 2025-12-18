#!/bin/bash

# Backup script for GIS Analysis Application
# Run as root: sudo bash backup.sh

set -e

BACKUP_DIR="/var/backups/gis-analysis"
DATE=$(date +%Y%m%d_%H%M%S)
APP_DIR="/var/www/gis-analysis"

echo "======================================"
echo "GIS Analysis - Backup Script"
echo "======================================"
echo ""

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Backup database
echo "Backing up PostgreSQL database..."
sudo -u postgres pg_dump gis_analysis | gzip > "$BACKUP_DIR/db_$DATE.sql.gz"
echo "✓ Database backed up to: $BACKUP_DIR/db_$DATE.sql.gz"

# Backup uploaded images
echo ""
echo "Backing up uploaded images..."
if [ -d "$APP_DIR/backend/uploads" ]; then
    tar -czf "$BACKUP_DIR/uploads_$DATE.tar.gz" -C "$APP_DIR/backend" uploads
    echo "✓ Images backed up to: $BACKUP_DIR/uploads_$DATE.tar.gz"
else
    echo "⚠ No uploads directory found, skipping..."
fi

# Backup environment configuration
echo ""
echo "Backing up configuration..."
if [ -f "$APP_DIR/backend/.env" ]; then
    cp "$APP_DIR/backend/.env" "$BACKUP_DIR/env_$DATE"
    echo "✓ Config backed up to: $BACKUP_DIR/env_$DATE"
fi

# List all backups
echo ""
echo "======================================"
echo "Backup Complete!"
echo "======================================"
echo ""
echo "All backups in: $BACKUP_DIR"
ls -lh "$BACKUP_DIR"

# Clean up old backups (keep last 7 days)
echo ""
echo "Cleaning up old backups (keeping last 7 days)..."
find "$BACKUP_DIR" -name "db_*.sql.gz" -mtime +7 -delete
find "$BACKUP_DIR" -name "uploads_*.tar.gz" -mtime +7 -delete
find "$BACKUP_DIR" -name "env_*" -mtime +7 -delete

echo "✓ Cleanup complete"
echo ""
echo "To restore:"
echo "  Database: gunzip < $BACKUP_DIR/db_$DATE.sql.gz | sudo -u postgres psql gis_analysis"
echo "  Images: tar -xzf $BACKUP_DIR/uploads_$DATE.tar.gz -C $APP_DIR/backend"
echo ""
