# Running Milvus with Docker Compose

This guide explains how to run Milvus database using Docker Compose.

---

## 🚀 Quick Start

### Option 1: Simple Setup (Recommended for Development)

This uses the latest Milvus image with built-in dependencies:

```bash
# Start Milvus
docker compose -f docker-compose.simple.yml up -d

# Check status
docker compose -f docker-compose.simple.yml ps

# View logs
docker compose -f docker-compose.simple.yml logs -f milvus

# Stop Milvus
docker compose -f docker-compose.simple.yml down
```

### Option 2: Full Setup (For Production)

This uses separate containers for etcd and MinIO (more control):

```bash
# Start all services (Milvus, etcd, MinIO)
docker compose up -d

# Check status
docker compose ps

# View logs
docker compose logs -f milvus

# Stop all services
docker compose down
```

---

## 📋 Available Commands

### Start Services

```bash
# Start in background (detached mode)
docker compose up -d

# Start and view logs
docker compose up

# Start specific service
docker compose up -d milvus
```

### Stop Services

```bash
# Stop all services
docker compose down

# Stop and remove volumes (⚠️ deletes all data)
docker compose down -v

# Stop without removing containers
docker compose stop
```

### View Logs

```bash
# All services
docker compose logs

# Specific service
docker compose logs milvus

# Follow logs (real-time)
docker compose logs -f milvus

# Last 100 lines
docker compose logs --tail 100 milvus
```

### Check Status

```bash
# List running containers
docker compose ps

# Check health
docker compose ps --format json | grep -i health
```

### Restart Services

```bash
# Restart all
docker compose restart

# Restart specific service
docker compose restart milvus
```

---

## ✅ Verification

### 1. Check if Milvus is Running

```bash
docker compose ps
```

You should see all services with status "Up" or "Up (healthy)".

### 2. Test Milvus Health Endpoint

```bash
curl http://localhost:9091/healthz
```

Expected response: `OK` or `{"status": "ok"}`

### 3. Test from Python

```python
from pymilvus import connections

# Connect to Milvus
connections.connect(
    alias="default",
    host="localhost",
    port="19530"
)

print("✅ Connected to Milvus!")
```

### 4. Test from Django

Start your Django server:
```bash
python manage.py runserver
```

Check console output for:
```
✅ Connected to Milvus vector store (collection: classcare_documents)
```

---

## 🔧 Configuration

### Ports

- **19530**: Milvus gRPC port (used by LangChain)
- **9091**: Milvus HTTP port (health checks)
- **9000**: MinIO API (only in full setup)
- **9001**: MinIO Console (only in full setup)

### Environment Variables

You can customize Milvus by editing `docker-compose.yml` or `docker-compose.simple.yml`.

**Common settings:**
```yaml
environment:
  COMMON_STORAGETYPE: local
  COMMON_WALPATH: /var/lib/milvus/wal
  COMMON_STORAGEPATH: /var/lib/milvus/storage
```

### Data Persistence

Data is stored in Docker volumes:
- `milvus_data`: Milvus data
- `etcd_data`: etcd data (full setup only)
- `minio_data`: MinIO data (full setup only)

**View volumes:**
```bash
docker volume ls
```

**Backup volume:**
```bash
docker run --rm -v milvus_data:/data -v $(pwd):/backup alpine tar czf /backup/milvus_backup.tar.gz /data
```

**Restore volume:**
```bash
docker run --rm -v milvus_data:/data -v $(pwd):/backup alpine tar xzf /backup/milvus_backup.tar.gz -C /
```

---

## 🐛 Troubleshooting

### Issue: Services won't start

**Solution:**
```bash
# Check logs
docker compose logs

# Check if ports are in use
netstat -an | grep 19530

# Remove old containers
docker compose down
docker compose up -d
```

### Issue: "Port already in use"

**Solution:**
1. Find what's using the port:
   ```bash
   # Windows
   netstat -ano | findstr :19530
   
   # Linux/Mac
   lsof -i :19530
   ```

2. Stop the conflicting service or change ports in `docker-compose.yml`

### Issue: Milvus container keeps restarting

**Solution:**
```bash
# Check logs
docker compose logs milvus

# Check health status
docker compose ps

# Restart with fresh volumes (⚠️ deletes data)
docker compose down -v
docker compose up -d
```

### Issue: "Cannot connect to Milvus" from Django

**Solution:**
1. Verify Milvus is running:
   ```bash
   docker compose ps
   curl http://localhost:9091/healthz
   ```

2. Check `.env` file has correct settings:
   ```env
   MILVUS_HOST=localhost
   MILVUS_PORT=19530
   ```

3. Restart Django server after starting Milvus

### Issue: Out of memory

**Solution:**
Increase Docker memory limit:
- Docker Desktop: Settings → Resources → Memory (at least 4GB)
- Or reduce Milvus resources in `docker-compose.yml`

---

## 🔄 Daily Workflow

### Starting Development Session

```bash
# 1. Start Milvus
docker compose -f docker-compose.simple.yml up -d

# 2. Verify it's running
curl http://localhost:9091/healthz

# 3. Start Django
python manage.py runserver
```

### Ending Development Session

```bash
# Stop Milvus (keeps data)
docker compose -f docker-compose.simple.yml stop

# Or stop and remove containers (keeps data in volumes)
docker compose -f docker-compose.simple.yml down
```

### Complete Cleanup (⚠️ Deletes All Data)

```bash
docker compose -f docker-compose.simple.yml down -v
```

---

## 📊 Monitoring

### View Resource Usage

```bash
docker stats milvus-standalone
```

### Access MinIO Console (Full Setup Only)

1. Start services: `docker compose up -d`
2. Open browser: http://localhost:9001
3. Login:
   - Username: `minioadmin`
   - Password: `minioadmin`

### View Collection Info

```python
from pymilvus import connections, utility

connections.connect(host="localhost", port="19530")
collections = utility.list_collections()
print(f"Collections: {collections}")

if collections:
    from pymilvus import Collection
    collection = Collection(collections[0])
    print(f"Entities: {collection.num_entities}")
```

---

## 🎯 Quick Reference

### Most Common Commands

```bash
# Start
docker compose -f docker-compose.simple.yml up -d

# Stop
docker compose -f docker-compose.simple.yml down

# Logs
docker compose -f docker-compose.simple.yml logs -f milvus

# Status
docker compose -f docker-compose.simple.yml ps

# Restart
docker compose -f docker-compose.simple.yml restart
```

### Files

- `docker-compose.yml`: Full setup with separate etcd and MinIO
- `docker-compose.simple.yml`: Simple setup (recommended)
- `.env`: Django/Milvus configuration

---

## ⚠️ Important Notes

1. **Data Persistence**: Data is stored in Docker volumes and persists even after `docker compose down`
2. **Port Conflicts**: Make sure ports 19530 and 9091 are not in use
3. **Memory**: Milvus needs at least 2GB RAM
4. **Start Order**: Always start Milvus before Django server
5. **Backup**: Regularly backup volumes if you have important data

---

**Last Updated:** January 2025

