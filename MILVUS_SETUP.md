# How to Run Milvus Database

Complete guide for setting up and running Milvus vector database for the ClassCare Chatbot.

---

## 🚀 Quick Start Options

### Option 1: Docker (Recommended - Easiest)

This is the easiest way to run Milvus, especially for development and testing.

#### Step 1: Install Docker

**Windows:**
- Download Docker Desktop from: https://www.docker.com/products/docker-desktop
- Install and start Docker Desktop
- Make sure Docker is running (you'll see the Docker icon in your system tray)

**Linux:**
```bash
# Install Docker
sudo apt-get update
sudo apt-get install docker.io
sudo systemctl start docker
sudo systemctl enable docker
```

**Mac:**
- Download Docker Desktop from: https://www.docker.com/products/docker-desktop
- Install and start Docker Desktop

#### Step 2: Pull Milvus Image

```bash
docker pull milvusdb/milvus:latest
```

#### Step 3: Start Milvus Container

```bash
docker run -d \
  --name milvus-standalone \
  -p 19530:19530 \
  -p 9091:9091 \
  milvusdb/milvus:latest
```

**Explanation:**
- `-d`: Run in detached mode (background)
- `--name milvus-standalone`: Name the container
- `-p 19530:19530`: Map port 19530 (Milvus gRPC port)
- `-p 9091:9091`: Map port 9091 (Milvus HTTP port)

#### Step 4: Verify Milvus is Running

**Check container status:**
```bash
docker ps | grep milvus
```

You should see the container running.

**Check Milvus health:**
```bash
curl http://localhost:19530/healthz
```

Or visit in browser: http://localhost:19530/healthz

**View logs:**
```bash
docker logs milvus-standalone
```

#### Step 5: Stop Milvus (when needed)

```bash
docker stop milvus-standalone
```

#### Step 6: Start Milvus Again (after stopping)

```bash
docker start milvus-standalone
```

#### Step 7: Remove Milvus Container (if needed)

```bash
docker stop milvus-standalone
docker rm milvus-standalone
```

---

### Option 2: Milvus Lite (For Development/Testing)

Milvus Lite is a lightweight version that runs embedded in Python - perfect for development and testing.

#### Step 1: Install Milvus Lite

```bash
pip install milvus
```

#### Step 2: Milvus Lite Auto-Starts

Milvus Lite will automatically start when you first use it in your Python code. No manual setup needed!

**Note:** The LangChain Milvus integration will automatically start Milvus Lite if it's installed and Milvus server is not available.

#### Step 3: Verify It's Working

When you start your Django server and upload a document, Milvus Lite will start automatically. Check the console output for confirmation.

---

### Option 3: Standalone Installation (Advanced)

For production or if you need more control, you can install Milvus standalone.

#### Windows (Using Docker is Recommended)

For Windows, Docker is the easiest option. Standalone installation on Windows is complex.

#### Linux/Mac Standalone Installation

**Step 1: Download Milvus**

```bash
# Download Milvus standalone
wget https://github.com/milvus-io/milvus/releases/download/v2.3.4/milvus-standalone-linux-amd64.tar.gz

# Extract
tar -xzf milvus-standalone-linux-amd64.tar.gz
cd milvus-standalone-linux-amd64
```

**Step 2: Start Milvus**

```bash
./milvus run standalone
```

**Step 3: Verify**

```bash
curl http://localhost:19530/healthz
```

---

## 🔧 Configuration

### Connection Settings

Make sure your `.env` file has these settings:

```env
MILVUS_HOST=localhost
MILVUS_PORT=19530
MILVUS_COLLECTION_NAME=classcare_documents
```

### Default Ports

- **19530**: gRPC port (used by LangChain)
- **9091**: HTTP port (for health checks and admin)

---

## ✅ Verification Steps

### 1. Check if Milvus is Running

**Using Docker:**
```bash
docker ps | grep milvus
```

**Using curl:**
```bash
curl http://localhost:19530/healthz
```

Expected response: `OK` or `{"status": "ok"}`

### 2. Test from Python

```python
from pymilvus import connections

# Connect to Milvus
connections.connect(
    alias="default",
    host="localhost",
    port="19530"
)

# List collections
from pymilvus import utility
collections = utility.list_collections()
print(f"Collections: {collections}")
```

### 3. Test from Django

Start your Django server:
```bash
python manage.py runserver
```

Check the console output. You should see:
```
✅ Connected to Milvus vector store (collection: classcare_documents)
```

---

## 🐛 Troubleshooting

### Issue: "Connection refused" or "Cannot connect to Milvus"

**Solution:**
1. Make sure Milvus is running:
   ```bash
   docker ps | grep milvus
   ```

2. Check if ports are available:
   ```bash
   # Windows
   netstat -an | findstr 19530
   
   # Linux/Mac
   lsof -i :19530
   ```

3. Restart Milvus:
   ```bash
   docker restart milvus-standalone
   ```

### Issue: "Port 19530 already in use"

**Solution:**
1. Find what's using the port:
   ```bash
   # Windows
   netstat -ano | findstr :19530
   
   # Linux/Mac
   lsof -i :19530
   ```

2. Stop the process or use a different port:
   ```bash
   docker run -d --name milvus-standalone -p 19531:19530 milvusdb/milvus:latest
   ```
   Then update `.env`: `MILVUS_PORT=19531`

### Issue: Docker container keeps stopping

**Solution:**
1. Check logs:
   ```bash
   docker logs milvus-standalone
   ```

2. Check Docker resources:
   - Make sure Docker has enough memory (at least 2GB)
   - Check Docker Desktop settings

3. Try with more memory:
   ```bash
   docker run -d --name milvus-standalone \
     -p 19530:19530 \
     -p 9091:9091 \
     --memory="2g" \
     milvusdb/milvus:latest
   ```

### Issue: "Collection not found" error

**Solution:**
- This is normal on first run. The collection will be created automatically when you upload your first document.
- If you see this error after uploading, check Milvus logs:
  ```bash
  docker logs milvus-standalone
  ```

### Issue: Milvus Lite not starting

**Solution:**
1. Make sure milvus is installed:
   ```bash
   pip install milvus
   ```

2. Check Python version (requires Python 3.8+):
   ```bash
   python --version
   ```

3. Try installing with verbose output:
   ```bash
   pip install -v milvus
   ```

---

## 📊 Monitoring Milvus

### View Container Stats

```bash
docker stats milvus-standalone
```

### View Logs

```bash
# All logs
docker logs milvus-standalone

# Follow logs (real-time)
docker logs -f milvus-standalone

# Last 100 lines
docker logs --tail 100 milvus-standalone
```

### Check Collection Status

```python
from pymilvus import connections, utility

connections.connect(host="localhost", port="19530")
collections = utility.list_collections()
print(f"Collections: {collections}")

# Get collection info
if collections:
    from pymilvus import Collection
    collection = Collection(collections[0])
    print(f"Number of entities: {collection.num_entities}")
```

---

## 🔄 Starting Milvus with Your Django Project

### Recommended Workflow

1. **Start Milvus first:**
   ```bash
   docker start milvus-standalone
   # Or if using Milvus Lite, it will start automatically
   ```

2. **Then start Django:**
   ```bash
   python manage.py runserver
   ```

3. **Verify connection:**
   - Check Django console for: `✅ Connected to Milvus vector store`
   - Upload a test document
   - Ask a question in the chat

### Auto-Start Script (Optional)

Create a `start_milvus.bat` (Windows) or `start_milvus.sh` (Linux/Mac):

**Windows (`start_milvus.bat`):**
```batch
@echo off
echo Starting Milvus...
docker start milvus-standalone
if %errorlevel% neq 0 (
    echo Milvus container not found. Creating new container...
    docker run -d --name milvus-standalone -p 19530:19530 -p 9091:9091 milvusdb/milvus:latest
)
echo Milvus is running!
pause
```

**Linux/Mac (`start_milvus.sh`):**
```bash
#!/bin/bash
echo "Starting Milvus..."
docker start milvus-standalone || docker run -d --name milvus-standalone -p 19530:19530 -p 9091:9091 milvusdb/milvus:latest
echo "Milvus is running!"
```

---

## 📝 Quick Reference

### Common Commands

```bash
# Start Milvus
docker start milvus-standalone

# Stop Milvus
docker stop milvus-standalone

# Restart Milvus
docker restart milvus-standalone

# View logs
docker logs milvus-standalone

# Check status
docker ps | grep milvus

# Remove container
docker stop milvus-standalone && docker rm milvus-standalone
```

### Connection String

- **Host:** localhost (or your server IP)
- **Port:** 19530
- **Collection:** classcare_documents (created automatically)

---

## 🎯 Next Steps

After Milvus is running:

1. ✅ Verify Milvus is accessible: `curl http://localhost:19530/healthz`
2. ✅ Start your Django server: `python manage.py runserver`
3. ✅ Upload a test document at: http://127.0.0.1:8000/upload/
4. ✅ Test chat functionality at: http://127.0.0.1:8000/

---

**Last Updated:** January 2025  
**Milvus Version:** Latest (via Docker) or Milvus Lite

