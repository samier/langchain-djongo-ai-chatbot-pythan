# Packages Summary - System vs Virtual Environment

This document provides a clear breakdown of all packages used in the ClassCare Chatbot project, categorized by installation method.

---

## 📊 Quick Summary

| Category | Count | Installation Method |
|----------|-------|-------------------|
| **System Packages (OS-level)** | **4 required + 2 optional** | `apt install` / `yum install` |
| **Python Packages (venv)** | **25+ packages** | `pip install -r requirements.txt` |

---

## 🖥️ System Packages (OS-Level Installation)

### Required System Packages: **4 packages**

These are installed using system package managers (`apt`, `yum`, etc.):

1. **python3.10** - Python interpreter
2. **python3.10-venv** - Python virtual environment support
3. **python3-pip** - Python package installer
4. **docker** - Container runtime
5. **docker-compose** - Docker orchestration tool
6. **nginx** - Web server and reverse proxy

**Installation Command:**
```bash
sudo apt install -y python3.10 python3.10-venv python3-pip docker-compose nginx
# Docker installed separately via script
curl -fsSL https://get.docker.com -o get-docker.sh && sudo sh get-docker.sh
```

---

### Optional System Packages: **2 packages**

1. **postgresql** - Database server (optional, SQLite works for development)
2. **postgresql-contrib** - PostgreSQL additional features
3. **certbot** - SSL certificate tool
4. **python3-certbot-nginx** - Certbot Nginx plugin

**Installation Command:**
```bash
sudo apt install -y postgresql postgresql-contrib certbot python3-certbot-nginx
```

---

## 🐍 Python Packages (Virtual Environment)

### Total Python Packages: **25+ packages**

All installed via: `pip install -r requirements.txt`

### Direct Dependencies (from requirements.txt): **20 packages**

#### 1. Django Framework (1 package)
- `Django==4.2.7`

#### 2. LangChain & AI (4 packages)
- `langchain==0.1.0`
- `langchain-community==0.0.10`
- `langchain-openai==0.0.2`
- `langchain-core==0.1.10`

#### 3. OpenAI (1 package)
- `openai==1.6.1`

#### 4. Hugging Face / Transformers (3 packages)
- `transformers==4.36.2`
- `sentence-transformers==2.2.2`
- `keras<3.0` (Keras 2.x for compatibility)

#### 5. Vector Store (1 package)
- `pymilvus==2.3.4`

#### 6. Document Processing (5 packages)
- `pypdf==3.17.4`
- `python-docx==1.1.0`
- `docx2txt==0.8`
- `openpyxl==3.1.2`
- `unstructured==0.11.8`

#### 7. Utilities (2 packages)
- `tiktoken==0.5.2`
- `python-dotenv==1.0.0`

#### 8. Web & API (2 packages)
- `requests==2.31.0`
- `Pillow==10.1.0`

#### 9. Production Server (1 package)
- `gunicorn==21.2.0`

#### 10. Database (Optional - 1 package, commented)
- `# psycopg2-binary==2.9.9` (uncomment if using PostgreSQL)

---

### Transitive Dependencies (Auto-installed): **100+ packages**

These are automatically installed when you install the packages above. Examples include:

- **PyTorch** (from `sentence-transformers` / `transformers`)
- **NumPy** (from multiple packages)
- **Pandas** (from `pymilvus`)
- **grpcio** (from `pymilvus`)
- **httpx** (from `langchain-openai`)
- **pydantic** (from `langchain-core`)
- **typing-extensions** (from multiple packages)
- **certifi** (from `requests`)
- **urllib3** (from `requests`)
- And many more...

**Total Python packages (including dependencies): ~100-150 packages**

---

## 📋 Complete Installation Breakdown

### Step 1: Install System Packages (6 required)

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python
sudo apt install -y python3.10 python3.10-venv python3-pip

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo apt install -y docker-compose

# Install Nginx
sudo apt install -y nginx
```

**Total: 6 system packages**

---

### Step 2: Create Virtual Environment

```bash
cd /var/www/chatbot
python3.10 -m venv venv
source venv/bin/activate
```

---

### Step 3: Install Python Packages (20 direct + 100+ transitive)

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Direct packages from requirements.txt: 20 packages**
**Total packages (with dependencies): ~100-150 packages**

---

## 📦 Package Count Summary

| Installation Location | Package Type | Count | Examples |
|----------------------|--------------|-------|----------|
| **System (OS)** | Required | 6 | python3.10, docker, nginx |
| **System (OS)** | Optional | 4 | postgresql, certbot |
| **Virtual Environment** | Direct (requirements.txt) | 20 | Django, langchain, pymilvus |
| **Virtual Environment** | Transitive (auto-installed) | ~100-150 | PyTorch, NumPy, pandas, grpcio |

---

## 🔍 Verification Commands

### Check System Packages

```bash
# Check Python
python3.10 --version
pip3 --version

# Check Docker
docker --version
docker-compose --version

# Check Nginx
nginx -v
```

### Check Python Packages in venv

```bash
# Activate virtual environment
source venv/bin/activate

# List all installed packages
pip list

# Count installed packages
pip list | wc -l

# List only direct dependencies
pip list --not-required
```

---

## 📝 Detailed Package Lists

### System Packages List

#### Required (6 packages):
1. `python3.10`
2. `python3.10-venv`
3. `python3-pip`
4. `docker`
5. `docker-compose`
6. `nginx`

#### Optional (4 packages):
1. `postgresql`
2. `postgresql-contrib`
3. `certbot`
4. `python3-certbot-nginx`

---

### Python Packages List (Direct Dependencies)

From `requirements.txt` (20 packages):

1. Django==4.2.7
2. langchain==0.1.0
3. langchain-community==0.0.10
4. langchain-openai==0.0.2
5. langchain-core==0.1.10
6. openai==1.6.1
7. transformers==4.36.2
8. sentence-transformers==2.2.2
9. keras<3.0
10. pymilvus==2.3.4
11. pypdf==3.17.4
12. python-docx==1.1.0
13. docx2txt==0.8
14. openpyxl==3.1.2
15. unstructured==0.11.8
16. tiktoken==0.5.2
17. python-dotenv==1.0.0
18. requests==2.31.0
19. Pillow==10.1.0
20. gunicorn==21.2.0

**Optional (1 package, commented):**
21. psycopg2-binary==2.9.9 (uncomment if using PostgreSQL)

---

## 🎯 Quick Reference

### System Installation (One-time setup)
```bash
# 6 required system packages
sudo apt install -y python3.10 python3.10-venv python3-pip docker-compose nginx
curl -fsSL https://get.docker.com | sudo sh
```

### Virtual Environment Installation (Per project)
```bash
# 20 direct + ~100-150 transitive Python packages
pip install -r requirements.txt
```

---

## 📊 Summary Table

| Category | Installation Method | Count | Location |
|----------|-------------------|-------|----------|
| **System Packages** | `apt install` | 6 required + 4 optional | System-wide |
| **Python Packages (Direct)** | `pip install -r requirements.txt` | 20 packages | Virtual environment |
| **Python Packages (All)** | Auto-installed dependencies | ~100-150 packages | Virtual environment |

---

**Last Updated:** 2024

