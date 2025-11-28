# Deployment Guide - ClassCare Chatbot

This guide provides step-by-step instructions for deploying the ClassCare Chatbot application on a production server.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Server Requirements](#server-requirements)
3. [Initial Server Setup](#initial-server-setup)
4. [Install Dependencies](#install-dependencies)
5. [Setup Milvus (Docker)](#setup-milvus-docker)
6. [Configure Environment Variables](#configure-environment-variables)
7. [Database Setup](#database-setup)
8. [Static Files Collection](#static-files-collection)
9. [Production Server Setup](#production-server-setup)
10. [Nginx Configuration](#nginx-configuration)
11. [SSL/HTTPS Setup](#sslhttps-setup)
12. [Systemd Service](#systemd-service)
13. [Monitoring and Maintenance](#monitoring-and-maintenance)
14. [Troubleshooting](#troubleshooting)

---

## Prerequisites

- Ubuntu 20.04/22.04 or similar Linux distribution
- Root or sudo access
- Domain name (optional, for HTTPS)
- Basic knowledge of Linux commands

---

## Server Requirements

### Minimum Requirements
- **CPU:** 2 cores
- **RAM:** 4 GB
- **Storage:** 20 GB
- **OS:** Ubuntu 20.04/22.04 LTS

### Recommended Requirements
- **CPU:** 4+ cores
- **RAM:** 8+ GB
- **Storage:** 50+ GB SSD
- **OS:** Ubuntu 22.04 LTS

### Software Requirements
- Python 3.10+
- Docker & Docker Compose
- Nginx
- PostgreSQL (optional, for production database)

---

## Initial Server Setup

### 1. Update System Packages

```bash
sudo apt update
sudo apt upgrade -y
```

### 2. Install Python and pip

```bash
sudo apt install -y python3.10 python3.10-venv python3-pip
```

### 3. Install Docker

```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add current user to docker group (optional, to run docker without sudo)
sudo usermod -aG docker $USER

# Install Docker Compose
sudo apt install -y docker-compose

# Start Docker service
sudo systemctl start docker
sudo systemctl enable docker

# Verify installation
docker --version
docker-compose --version
```

### 4. Install Nginx

```bash
sudo apt install -y nginx
sudo systemctl start nginx
sudo systemctl enable nginx
```

### 5. Install PostgreSQL (Optional - Recommended for Production)

```bash
sudo apt install -y postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Create database and user
sudo -u postgres psql
```

In PostgreSQL prompt:
```sql
CREATE DATABASE classcare_chatbot;
CREATE USER chatbot_user WITH PASSWORD 'your_secure_password';
ALTER ROLE chatbot_user SET client_encoding TO 'utf8';
ALTER ROLE chatbot_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE chatbot_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE classcare_chatbot TO chatbot_user;
\q
```

---

## Install Dependencies

### ⚠️ Important: Virtual Environment Usage

**Throughout this guide, you must activate the virtual environment before running any Python or pip commands.**

**To activate virtual environment:**
```bash
cd /var/www/chatbot
source venv/bin/activate
```

**You'll know it's activated when you see `(venv)` at the start of your terminal prompt:**
```
(venv) user@server:/var/www/chatbot$
```

**To deactivate (when done):**
```bash
deactivate
```

**Remember:** Always activate venv before:
- Running `pip install`
- Running `python manage.py` commands
- Running any Python scripts
- Testing Milvus connection

---

### 1. Clone or Upload Project

```bash
# Option 1: Clone from Git
cd /var/www
sudo git clone https://github.com/samier/langchain-djongo-ai-chatbot-pythan.git chatbot
cd chatbot

# Option 2: Upload via SCP/SFTP
# Upload project files to /var/www/chatbot
```

### 2. Create Virtual Environment

```bash
cd /var/www/chatbot

# Create virtual environment
python3.10 -m venv venv

# Activate virtual environment
# IMPORTANT: You must activate venv before running any Python/pip commands
source venv/bin/activate

# Verify venv is activated (you should see (venv) in your prompt)
# Your prompt should look like: (venv) user@server:/var/www/chatbot$
```

**Note:** After activating, your terminal prompt will show `(venv)` at the beginning, indicating the virtual environment is active.

### 3. Install Python Dependencies

**IMPORTANT: Make sure virtual environment is activated before running these commands!**

```bash
# Verify venv is activated (check for (venv) in prompt)
# If not activated, run: source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install all Python packages from requirements.txt
# These packages will be installed INSIDE the virtual environment, NOT system-wide
pip install -r requirements.txt
```

**Note:** 
- If you encounter PyTorch DLL errors on Windows, they won't occur on Linux. The installation should proceed smoothly.
- All packages from `requirements.txt` are installed in the virtual environment (`venv/`), not system-wide.
- The virtual environment must be activated whenever you run Python commands or use pip.

---

## Setup Milvus (Docker)

### 1. Create Docker Compose File

The project includes `docker-compose.yml` for Milvus. Verify it exists:

```bash
ls -la docker-compose.yml
```

### 2. Start Milvus

```bash
# Start Milvus with Docker Compose
docker-compose up -d

# Verify Milvus is running
docker ps
curl http://localhost:9091/healthz
```

Expected output: `OK`

### 3. Verify Milvus Connection

```bash
# Navigate to project directory
cd /var/www/chatbot

# Activate virtual environment (REQUIRED for Python commands)
source venv/bin/activate

# Verify venv is active (should see (venv) in prompt)
# Test Milvus connection
python -c "from pymilvus import connections; connections.connect(host='localhost', port='19530'); print('✅ Milvus connected successfully')"
```

---

## Configure Environment Variables

### 1. Copy `.env.example` to `.env`

```bash
cd /var/www/chatbot
cp .env.example .env
```

### 2. Edit `.env` File

```bash
nano .env
```

Update the following values in `.env`:

- **SECRET_KEY:** Generate a new secret key (see step 3)
- **ALLOWED_HOSTS:** Replace with your domain name and server IP
- **DATABASE_URL:** Update with your PostgreSQL credentials (if using PostgreSQL)
- **OPENAI_API_KEY:** Add your OpenAI API key
- **MILVUS_HOST:** Usually `localhost` (change if Milvus is on a different host)
- **MILVUS_PORT:** Usually `19530` (change if using a different port)

### 3. Generate Secret Key

```bash
# Make sure you're in project directory
cd /var/www/chatbot

# Activate virtual environment (REQUIRED)
source venv/bin/activate

# Generate secret key
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Copy the output and use it as `SECRET_KEY` in `.env`.

---

## Database Setup

### Option 1: PostgreSQL (Recommended)

Update `classcare/settings.py` to use PostgreSQL:

```python
import os
from urllib.parse import urlparse

DATABASE_URL = os.environ.get('DATABASE_URL', '')

if DATABASE_URL.startswith('postgresql://'):
    import dj_database_url
    DATABASES = {
        'default': dj_database_url.config(default=DATABASE_URL)
    }
else:
    # Fallback to SQLite
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
```

Install PostgreSQL adapter:
```bash
# Navigate to project directory
cd /var/www/chatbot

# Activate virtual environment (REQUIRED)
source venv/bin/activate

# Install PostgreSQL adapter
pip install psycopg2-binary
```

### Option 2: SQLite (Development Only)

SQLite works out of the box but is not recommended for production.

### Run Migrations

```bash
# Navigate to project directory
cd /var/www/chatbot

# Activate virtual environment (REQUIRED)
source venv/bin/activate

# Run database migrations
python manage.py migrate

# Create superuser (admin account)
python manage.py createsuperuser
```

---

## Static Files Collection

```bash
# Navigate to project directory
cd /var/www/chatbot

# Activate virtual environment (REQUIRED)
source venv/bin/activate

# Update settings.py to include STATIC_ROOT (if not already set)
# STATIC_ROOT = '/var/www/chatbot/staticfiles'

# Collect static files for production
python manage.py collectstatic --noinput
```

---

## Production Server Setup

### 1. Install Gunicorn

```bash
# Navigate to project directory
cd /var/www/chatbot

# Activate virtual environment (REQUIRED)
source venv/bin/activate

# Install Gunicorn (production WSGI server)
# Note: Gunicorn is already in requirements.txt, but if you need to install separately:
pip install gunicorn
```

### 2. Create Gunicorn Service File

```bash
sudo nano /etc/systemd/system/chatbot.service
```

Add the following:

```ini
[Unit]
Description=ClassCare Chatbot Gunicorn daemon
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/chatbot
Environment="PATH=/var/www/chatbot/venv/bin"
ExecStart=/var/www/chatbot/venv/bin/gunicorn \
    --workers 3 \
    --bind 127.0.0.1:8000 \
    --timeout 120 \
    --access-logfile /var/log/chatbot/access.log \
    --error-logfile /var/log/chatbot/error.log \
    classcare.wsgi:application

[Install]
WantedBy=multi-user.target
```

### 3. Create Log Directory

```bash
sudo mkdir -p /var/log/chatbot
sudo chown www-data:www-data /var/log/chatbot
```

### 4. Start Gunicorn Service

```bash
sudo systemctl daemon-reload
sudo systemctl start chatbot
sudo systemctl enable chatbot
sudo systemctl status chatbot
```

---

## Nginx Configuration

### 1. Create Nginx Configuration

```bash
sudo nano /etc/nginx/sites-available/chatbot
```

Add the following:

```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;

    # Redirect HTTP to HTTPS (after SSL setup)
    # return 301 https://$server_name$request_uri;

    # For initial setup, use HTTP (remove after SSL setup)
    client_max_body_size 100M;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
    }

    location /static/ {
        alias /var/www/chatbot/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location /media/ {
        alias /var/www/chatbot/media/;
        expires 7d;
        add_header Cache-Control "public";
    }
}
```

### 2. Enable Site

```bash
sudo ln -s /etc/nginx/sites-available/chatbot /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 3. Set Permissions

```bash
sudo chown -R www-data:www-data /var/www/chatbot
sudo chmod -R 755 /var/www/chatbot
```

---

## SSL/HTTPS Setup

### 1. Install Certbot

```bash
sudo apt install -y certbot python3-certbot-nginx
```

### 2. Obtain SSL Certificate

```bash
sudo certbot --nginx -d your-domain.com -d www.your-domain.com
```

### 3. Auto-Renewal

Certbot sets up auto-renewal automatically. Test renewal:

```bash
sudo certbot renew --dry-run
```

### 4. Update Nginx Configuration

After SSL setup, uncomment the HTTPS redirect in Nginx config:

```nginx
return 301 https://$server_name$request_uri;
```

---

## Systemd Service

The Gunicorn service is already configured. Useful commands:

```bash
# Start service
sudo systemctl start chatbot

# Stop service
sudo systemctl stop chatbot

# Restart service
sudo systemctl restart chatbot

# Check status
sudo systemctl status chatbot

# View logs
sudo journalctl -u chatbot -f
```

---

## Monitoring and Maintenance

### 1. Log Monitoring

```bash
# Application logs
tail -f /var/log/chatbot/error.log
tail -f /var/log/chatbot/access.log

# System logs
sudo journalctl -u chatbot -f

# Nginx logs
sudo tail -f /var/log/nginx/error.log
sudo tail -f /var/log/nginx/access.log
```

### 2. Health Checks

```bash
# Check Django app
curl http://localhost:8000/

# Check Milvus
curl http://localhost:9091/healthz

# Check Nginx
curl http://your-domain.com/
```

### 3. Backup Strategy

```bash
# Backup database (PostgreSQL)
sudo -u postgres pg_dump classcare_chatbot > backup_$(date +%Y%m%d).sql

# Backup media files
tar -czf media_backup_$(date +%Y%m%d).tar.gz /var/www/chatbot/media/

# Backup Milvus data (Docker volume)
docker run --rm -v milvus-standalone_milvus_data:/data -v $(pwd):/backup alpine tar czf /backup/milvus_backup_$(date +%Y%m%d).tar.gz /data
```

### 4. Update Application

```bash
# Navigate to project directory
cd /var/www/chatbot

# Activate virtual environment (REQUIRED for all Python commands)
source venv/bin/activate

# Pull latest changes (if using Git)
git pull

# Install/update Python dependencies
# This installs packages INSIDE the virtual environment
pip install -r requirements.txt

# Run database migrations (if any new migrations exist)
python manage.py migrate

# Collect static files (if any static files changed)
python manage.py collectstatic --noinput

# Restart Gunicorn service
sudo systemctl restart chatbot
```

---

## Troubleshooting

### Issue: Gunicorn won't start

**Check:**
```bash
sudo systemctl status chatbot
sudo journalctl -u chatbot -n 50
```

**Common fixes:**
- Verify virtual environment path
- Check file permissions
- Ensure `.env` file exists
- Verify database connection

### Issue: 502 Bad Gateway

**Check:**
```bash
# Verify Gunicorn is running
sudo systemctl status chatbot

# Check if port 8000 is listening
sudo netstat -tlnp | grep 8000

# Restart Gunicorn
sudo systemctl restart chatbot
```

### Issue: Milvus connection failed

**Check:**
```bash
# Verify Milvus is running
docker ps
curl http://localhost:9091/healthz

# Check Milvus logs
docker logs milvus-standalone

# Restart Milvus
docker-compose restart
```

### Issue: Static files not loading

**Check:**
```bash
# Verify static files collected
ls -la /var/www/chatbot/staticfiles/

# Check Nginx configuration
sudo nginx -t

# Verify permissions
sudo chown -R www-data:www-data /var/www/chatbot/staticfiles
```

### Issue: Permission denied

**Fix:**
```bash
sudo chown -R www-data:www-data /var/www/chatbot
sudo chmod -R 755 /var/www/chatbot
```

---

## Security Checklist

- [ ] `DEBUG=False` in production
- [ ] Strong `SECRET_KEY` in `.env`
- [ ] `ALLOWED_HOSTS` configured correctly
- [ ] SSL/HTTPS enabled
- [ ] Firewall configured (UFW)
- [ ] Database credentials secured
- [ ] API keys in `.env` (not in code)
- [ ] Regular security updates
- [ ] Backup strategy in place
- [ ] Log rotation configured

### Configure Firewall

```bash
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp     # HTTP
sudo ufw allow 443/tcp    # HTTPS
sudo ufw enable
```

---

## Quick Deployment Checklist

1. [ ] Server updated and dependencies installed
2. [ ] Project files uploaded/cloned
3. [ ] Virtual environment created and activated
4. [ ] Python dependencies installed
5. [ ] Milvus running in Docker
6. [ ] `.env` file configured
7. [ ] Database created and migrations run
8. [ ] Static files collected
9. [ ] Gunicorn service configured and running
10. [ ] Nginx configured and running
11. [ ] SSL certificate installed (optional)
12. [ ] Firewall configured
13. [ ] Health checks passing
14. [ ] Backup strategy in place

---

## Support

For issues or questions:
1. Check logs: `/var/log/chatbot/`
2. Review Django logs: `sudo journalctl -u chatbot`
3. Check Milvus: `docker logs milvus-standalone`
4. Verify Nginx: `sudo nginx -t`

---

## Additional Resources

- [Django Deployment Checklist](https://docs.djangoproject.com/en/stable/howto/deployment/checklist/)
- [Gunicorn Documentation](https://gunicorn.org/)
- [Nginx Documentation](https://nginx.org/en/docs/)
- [Milvus Documentation](https://milvus.io/docs)
- [Let's Encrypt Documentation](https://letsencrypt.org/docs/)

---

**Last Updated:** 2024
**Version:** 1.0

