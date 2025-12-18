# DigitalOcean Droplet Deployment Guide

Complete guide to deploying your GIS Satellite Analysis application on a DigitalOcean droplet.

## Overview

This deployment uses:
- **Ubuntu 22.04 LTS** droplet
- **Nginx** as reverse proxy and static file server
- **PostgreSQL** for database
- **Systemd** for process management
- **Let's Encrypt** for free SSL certificates
- **Python 3.11** + **GDAL** for geospatial processing
- **Node.js 18** for frontend build

## Prerequisites

1. DigitalOcean account (sign up at https://www.digitalocean.com)
2. Domain name (optional but recommended for SSL)
3. SSH key for secure access
4. Anthropic API key

## Cost Estimate

**Recommended Droplet**: Basic - 2GB RAM / 1 CPU / 50GB SSD
- **Cost**: $12/month ($0.018/hour)
- Suitable for demo and moderate traffic

**Alternatives**:
- **$6/month** (1GB RAM): Minimum, may struggle with large images
- **$18/month** (2GB RAM + more CPU): Better performance
- **$24/month** (4GB RAM): Production-ready with scaling room

## Step 1: Create DigitalOcean Droplet

### 1.1 Create New Droplet

1. Log into DigitalOcean
2. Click "Create" → "Droplets"
3. **Choose Region**: Select closest to your users
4. **Choose Image**: Ubuntu 22.04 LTS x64
5. **Choose Size**:
   - Basic plan
   - Regular (2GB / 1 CPU) - $12/month
6. **Choose Authentication**:
   - SSH Key (recommended)
   - Or use password (less secure)
7. **Optional**: Enable backups ($2.40/month for peace of mind)
8. **Hostname**: gis-analysis
9. Click "Create Droplet"

### 1.2 Initial Access

Wait 1-2 minutes for droplet to be created, then:

```bash
# SSH into your droplet
ssh root@your_droplet_ip

# Update system
apt update && apt upgrade -y
```

## Step 2: Server Setup

### 2.1 Clone Your Repository (on your droplet)

```bash
cd /tmp
git clone https://github.com/yourusername/newGitTest.git
cd newGitTest
```

### 2.2 Run Server Setup Script

```bash
# Make script executable
chmod +x deploy/digitalocean/setup_server.sh

# Run as root
sudo bash deploy/digitalocean/setup_server.sh
```

This script will:
- ✅ Install Python 3.11
- ✅ Install GDAL for geospatial processing
- ✅ Install PostgreSQL database
- ✅ Install Node.js 18
- ✅ Install and configure Nginx
- ✅ Install Certbot for SSL
- ✅ Create application user (gisapp)
- ✅ Configure firewall

**Time**: 5-10 minutes

### 2.3 Secure PostgreSQL

After setup, change the default database password:

```bash
# Generate a secure password
openssl rand -base64 32

# Set new password (use the generated password)
sudo -u postgres psql -c "ALTER USER gisapp WITH PASSWORD 'your_secure_password_here';"
```

**Save this password** - you'll need it in the next step.

## Step 3: Application Setup

### 3.1 Switch to Application User

```bash
# Switch to gisapp user
sudo -i -u gisapp
cd /var/www/gis-analysis
```

### 3.2 Clone Your Repository

```bash
# Clone your repository
git clone https://github.com/yourusername/newGitTest.git .

# Or if using HTTPS with credentials:
git clone https://your_token@github.com/yourusername/newGitTest.git .
```

### 3.3 Run Application Setup

```bash
# Make script executable
chmod +x deploy/digitalocean/setup_app.sh

# Run setup
bash deploy/digitalocean/setup_app.sh
```

The script will prompt you for:
1. **Anthropic API key**: Your Claude API key
2. **PostgreSQL password**: The password you set earlier
3. **Domain name**: Your domain (or droplet IP for testing)

**Time**: 3-5 minutes

## Step 4: Configure Services

### 4.1 Set Up Systemd Service

```bash
# Exit from gisapp user back to root
exit

# Create log directory
sudo mkdir -p /var/log/gis-analysis
sudo chown gisapp:gisapp /var/log/gis-analysis

# Copy service file
sudo cp /var/www/gis-analysis/deploy/digitalocean/gis-analysis.service /etc/systemd/system/

# Reload systemd
sudo systemctl daemon-reload

# Start the service
sudo systemctl start gis-analysis

# Enable on boot
sudo systemctl enable gis-analysis

# Check status
sudo systemctl status gis-analysis
```

### 4.2 Configure Nginx

```bash
# Copy nginx config
sudo cp /var/www/gis-analysis/deploy/digitalocean/nginx.conf /etc/nginx/sites-available/gis-analysis

# Update domain in config
sudo nano /etc/nginx/sites-available/gis-analysis
# Replace "your-domain.com" with your actual domain or IP

# Create certbot directory
sudo mkdir -p /var/www/certbot

# Test configuration
sudo nginx -t

# Enable site
sudo ln -s /etc/nginx/sites-available/gis-analysis /etc/nginx/sites-enabled/

# Remove default site
sudo rm /etc/nginx/sites-enabled/default

# Restart nginx
sudo systemctl restart nginx
```

## Step 5: Set Up Domain (Optional but Recommended)

### 5.1 Point Domain to Droplet

In your domain registrar (Namecheap, GoDaddy, etc.):

1. Create an **A record**:
   - Host: `@` (or your subdomain)
   - Value: Your droplet IP address
   - TTL: 300

2. Create a **www CNAME** (optional):
   - Host: `www`
   - Value: `your-domain.com`
   - TTL: 300

Wait 5-30 minutes for DNS propagation.

### 5.2 Test Domain

```bash
# Test if domain resolves
ping your-domain.com

# Should return your droplet IP
```

## Step 6: Set Up SSL (HTTPS)

### 6.1 Obtain SSL Certificate

```bash
# Run certbot
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# Follow prompts:
# - Enter email address
# - Agree to terms
# - Choose whether to redirect HTTP to HTTPS (select 2 for redirect)
```

Certbot will:
- ✅ Obtain SSL certificate
- ✅ Update nginx config automatically
- ✅ Set up auto-renewal

### 6.2 Test Auto-Renewal

```bash
# Test renewal process
sudo certbot renew --dry-run

# If successful, certificates will auto-renew
```

## Step 7: Verify Deployment

### 7.1 Check Backend

```bash
# Check if backend is running
sudo systemctl status gis-analysis

# View logs
sudo journalctl -u gis-analysis -f

# Or check log files
tail -f /var/log/gis-analysis/error.log
```

### 7.2 Test API

```bash
# Test API endpoint
curl https://your-domain.com/api/

# Should return JSON with API info
```

### 7.3 Test Frontend

Open browser and visit:
- `https://your-domain.com`

You should see the GIS Analysis application!

## Step 8: Test the Application

1. **Upload an Image**:
   - Click "Upload Image"
   - Select a GeoTIFF file
   - Upload should complete successfully

2. **Run a Query**:
   - Select uploaded image
   - Enter: "number of cars"
   - Should receive AI-powered response

3. **Check Database**:
   ```bash
   sudo -u postgres psql -d gis_analysis -c "SELECT COUNT(*) FROM images;"
   ```

## Maintenance & Updates

### Update Application

```bash
# SSH into droplet
ssh root@your_droplet_ip

# Switch to app user
sudo -i -u gisapp

# Navigate to app directory
cd /var/www/gis-analysis

# Pull latest changes
git pull

# Update backend
cd backend
source venv/bin/activate
pip install -r requirements.txt

# Update frontend
cd ../frontend
npm install
npm run build

# Exit to root
exit

# Restart service
sudo systemctl restart gis-analysis

# Reload nginx (if frontend changed)
sudo systemctl reload nginx
```

### View Logs

```bash
# Backend logs
sudo journalctl -u gis-analysis -f

# Nginx access logs
sudo tail -f /var/log/nginx/gis-analysis-access.log

# Nginx error logs
sudo tail -f /var/log/nginx/gis-analysis-error.log
```

### Restart Services

```bash
# Restart backend
sudo systemctl restart gis-analysis

# Restart nginx
sudo systemctl restart nginx

# Restart PostgreSQL (if needed)
sudo systemctl restart postgresql
```

### Database Backup

```bash
# Create backup
sudo -u postgres pg_dump gis_analysis > /tmp/gis_backup_$(date +%Y%m%d).sql

# Restore from backup
sudo -u postgres psql gis_analysis < /tmp/gis_backup_YYYYMMDD.sql
```

## Troubleshooting

### Backend Won't Start

**Check logs**:
```bash
sudo journalctl -u gis-analysis -n 50
```

**Common issues**:
- Database connection error: Check DATABASE_URL in `/var/www/gis-analysis/backend/.env`
- Missing dependencies: Run `pip install -r requirements.txt` in venv
- Port already in use: Check if another service is using port 8000

### Frontend Not Loading

**Check nginx**:
```bash
sudo nginx -t
sudo systemctl status nginx
```

**Common issues**:
- Build not completed: Check if `frontend/build/` directory exists
- Wrong permissions: `sudo chown -R gisapp:gisapp /var/www/gis-analysis`

### API Requests Failing

**Check CORS**:
- Ensure frontend is using `/api/` prefix
- Check nginx proxy_pass configuration

**Check backend**:
```bash
curl http://127.0.0.1:8000/
```

### Database Connection Issues

**Test connection**:
```bash
sudo -u postgres psql -d gis_analysis
```

**Check credentials**:
```bash
cat /var/www/gis-analysis/backend/.env
```

### SSL Certificate Issues

**Renew manually**:
```bash
sudo certbot renew
sudo systemctl reload nginx
```

**Check expiry**:
```bash
sudo certbot certificates
```

## Security Best Practices

### 1. Firewall Configuration

```bash
# Check firewall status
sudo ufw status

# Should show:
# - 22/tcp (SSH) ALLOW
# - 80,443/tcp (Nginx Full) ALLOW
```

### 2. SSH Security

```bash
# Disable password authentication
sudo nano /etc/ssh/sshd_config
# Set: PasswordAuthentication no

# Restart SSH
sudo systemctl restart sshd
```

### 3. Regular Updates

```bash
# Update system weekly
sudo apt update && sudo apt upgrade -y

# Update application dependencies monthly
cd /var/www/gis-analysis/backend
source venv/bin/activate
pip install --upgrade -r requirements.txt
```

### 4. Monitor Disk Space

```bash
# Check disk usage
df -h

# If running low, clean up:
sudo apt autoremove
sudo journalctl --vacuum-time=7d
```

## Monitoring

### Set Up Basic Monitoring

```bash
# Install monitoring tools
sudo apt install -y htop iotop

# Monitor CPU/RAM
htop

# Monitor disk I/O
sudo iotop
```

### DigitalOcean Monitoring

Enable in DigitalOcean dashboard:
- Droplet → Monitoring tab
- View CPU, memory, disk, bandwidth graphs
- Set up alerts for high usage

## Scaling Considerations

### Vertical Scaling (Resize Droplet)

When you need more resources:
1. Power off droplet
2. Resize to larger plan
3. Power on
4. No code changes needed!

### Horizontal Scaling (Multiple Droplets)

For high traffic:
1. Set up load balancer
2. Deploy to multiple droplets
3. Use managed PostgreSQL database
4. Use Spaces for image storage

## Cost Optimization

### Current Setup Costs

- Droplet (2GB): **$12/month**
- Backups: **$2.40/month** (optional)
- **Total**: ~$14-15/month

### Reduce Costs

- Use $6/month droplet for testing
- Disable backups (use manual backups instead)
- Use monitoring to optimize resource usage

### When to Upgrade

Upgrade if:
- CPU usage consistently >80%
- Memory usage consistently >80%
- Response times >2 seconds
- Experiencing downtime

## Support Resources

- **DigitalOcean Docs**: https://docs.digitalocean.com
- **DigitalOcean Community**: https://www.digitalocean.com/community
- **Support Tickets**: Available with all plans

## Next Steps

After successful deployment:

1. ✅ Set up automated backups (DigitalOcean or custom script)
2. ✅ Configure monitoring and alerts
3. ✅ Add custom domain
4. ✅ Implement rate limiting
5. ✅ Add user authentication
6. ✅ Set up CDN for static assets (DigitalOcean Spaces)

---

**Questions?** Check the main README.md or open an issue on GitHub.

**Deployed successfully?** Your app is now live at `https://your-domain.com`! 🎉
