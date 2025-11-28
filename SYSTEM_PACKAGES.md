# System Packages Required

This document lists all system-level packages (operating system packages) required for the ClassCare Chatbot project.

## System Packages (Operating System Level)

### Required System Packages

#### 1. Python 3.10+
**Package:** `python3.10`, `python3.10-venv`, `python3-pip`
**Installation:**
```bash
sudo apt install -y python3.10 python3.10-venv python3-pip
```
**Purpose:** Python runtime environment
**Required:** Yes

---

#### 2. Docker & Docker Compose
**Package:** `docker`, `docker-compose`
**Installation:**
```bash
# Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Docker Compose
sudo apt install -y docker-compose
```
**Purpose:** Run Milvus vector database in containers
**Required:** Yes (for Milvus)

---

#### 3. Nginx
**Package:** `nginx`
**Installation:**
```bash
sudo apt install -y nginx
```
**Purpose:** Reverse proxy and web server (production)
**Required:** Yes (for production deployment)

---

### Optional System Packages

#### 4. PostgreSQL
**Package:** `postgresql`, `postgresql-contrib`
**Installation:**
```bash
sudo apt install -y postgresql postgresql-contrib
```
**Purpose:** Production database (alternative to SQLite)
**Required:** No (SQLite works for development)
**Note:** If using PostgreSQL, you also need `psycopg2-binary` Python package

---

#### 5. Certbot (for SSL/HTTPS)
**Package:** `certbot`, `python3-certbot-nginx`
**Installation:**
```bash
sudo apt install -y certbot python3-certbot-nginx
```
**Purpose:** SSL certificate management (Let's Encrypt)
**Required:** No (only for HTTPS setup)

---

## Python Packages (pip installable)

All Python packages are listed in `requirements.txt` and installed via pip:
```bash
pip install -r requirements.txt
```

### Key Python Packages with System Dependencies

#### 1. psycopg2-binary
**Python Package:** `psycopg2-binary`
**System Dependency:** PostgreSQL client libraries
**Installation:**
```bash
pip install psycopg2-binary
```
**Note:** The `-binary` version includes pre-compiled binaries, so no system PostgreSQL development libraries needed.

---

#### 2. Pillow
**Python Package:** `Pillow`
**System Dependency:** Image processing libraries (libjpeg, zlib, etc.)
**Installation:**
```bash
pip install Pillow
```
**Note:** Usually works out of the box, but may require:
```bash
sudo apt install -y libjpeg-dev zlib1g-dev
```

---

#### 3. sentence-transformers / transformers
**Python Package:** `sentence-transformers`, `transformers`
**System Dependency:** PyTorch (CPU version usually sufficient)
**Installation:**
```bash
pip install sentence-transformers transformers
```
**Note:** PyTorch is installed automatically as a dependency. CPU version works fine.

---

#### 4. pymilvus
**Python Package:** `pymilvus`
**System Dependency:** gRPC libraries
**Installation:**
```bash
pip install pymilvus==2.3.4
```
**Note:** Usually works out of the box, gRPC libraries are included.

---

## Production Server Packages

### Gunicorn
**Python Package:** `gunicorn`
**Installation:**
```bash
pip install gunicorn
```
**Purpose:** Production WSGI HTTP server
**Required:** Yes (for production)
**Note:** This is a Python package, but runs as a systemd service

---

## Complete System Setup Command

For Ubuntu/Debian systems, install all required system packages:

```bash
# Update system
sudo apt update
sudo apt upgrade -y

# Install Python
sudo apt install -y python3.10 python3.10-venv python3-pip

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo apt install -y docker-compose

# Install Nginx
sudo apt install -y nginx

# Optional: Install PostgreSQL
sudo apt install -y postgresql postgresql-contrib

# Optional: Install Certbot for SSL
sudo apt install -y certbot python3-certbot-nginx
```

---

## Summary

### Required System Packages:
1. ✅ Python 3.10+ (`python3.10`, `python3.10-venv`, `python3-pip`)
2. ✅ Docker (`docker`)
3. ✅ Docker Compose (`docker-compose`)
4. ✅ Nginx (`nginx`)

### Optional System Packages:
1. ⚠️ PostgreSQL (`postgresql`, `postgresql-contrib`) - Recommended for production
2. ⚠️ Certbot (`certbot`, `python3-certbot-nginx`) - For SSL/HTTPS

### Python Packages (from requirements.txt):
- All Python packages are installed via `pip install -r requirements.txt`
- No manual system package installation needed for Python packages
- `psycopg2-binary` includes binaries (no system PostgreSQL dev libraries needed)

---

## Notes

1. **Windows Development:** On Windows, you don't need system packages - just Python and Docker Desktop
2. **Linux Production:** All system packages listed above are required
3. **Docker:** Milvus runs in Docker, so Docker is essential
4. **Nginx:** Only needed for production deployment (not for development)
5. **PostgreSQL:** Optional - SQLite works for development and small deployments

---

**Last Updated:** 2024

