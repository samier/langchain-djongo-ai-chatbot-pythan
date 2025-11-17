# ClassCare Chatbot - Setup Guide

Complete step-by-step guide to set up and run the ClassCare Chatbot project.

---

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installation Steps](#installation-steps)
3. [Environment Configuration](#environment-configuration)
4. [Database Setup](#database-setup)
5. [Running the Project](#running-the-project)
6. [Verification](#verification)
7. [Troubleshooting](#troubleshooting)

---

## 🔧 Prerequisites

Before starting, ensure you have the following installed:

### Required Software

1. **Python 3.8 or higher**
   - Check version: `python --version` or `python3 --version`
   - Download from: https://www.python.org/downloads/

2. **pip** (Python package manager)
   - Usually comes with Python
   - Check version: `pip --version`

3. **Git** (optional, if cloning from repository)
   - Download from: https://git-scm.com/downloads

### System Requirements

- **RAM:** Minimum 4GB (8GB recommended for better performance)
- **Storage:** At least 2GB free space
- **Internet:** Required for:
  - Installing packages
  - OpenAI API calls (for answer generation)
  - Downloading HuggingFace models (first time only)

---

## 📦 Installation Steps

### Step 1: Navigate to Project Directory

```bash
cd C:\projects\chatbot
# Or your project path
```

### Step 2: Create Virtual Environment

**Windows:**
```bash
python -m venv venv
```

**Linux/Mac:**
```bash
python3 -m venv venv
```

### Step 3: Activate Virtual Environment

**Windows (PowerShell):**
```powershell
.\venv\Scripts\Activate.ps1
```

**Windows (Command Prompt):**
```cmd
venv\Scripts\activate.bat
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

You should see `(venv)` in your terminal prompt when activated.

### Step 4: Install Dependencies

```bash
pip install -r requirements.txt
```

**Note:** This may take several minutes as it installs:
- Django framework
- LangChain and AI libraries
- Document processing libraries (PyPDF, python-docx, etc.)
- Vector database (Milvus)
- Sentence transformers (for local embeddings)

### Step 5: Install Milvus (Vector Database)

**Option 1: Using Docker (Recommended)**

```bash
# Pull Milvus standalone image
docker pull milvusdb/milvus:latest

# Start Milvus
docker run -d --name milvus-standalone -p 19530:19530 -p 9091:9091 milvusdb/milvus:latest
```

**Option 2: Using Milvus Lite (For Development)**

```bash
pip install milvus
```

Then start Milvus in your Python code (it will start automatically when you use it).

**Verify Milvus is Running:**

```bash
# Check if Milvus is accessible
curl http://localhost:19530/healthz
```

### Step 6: Install Additional Requirements

Some packages may need additional setup:

**For sentence-transformers (Local Embeddings):**
```bash
pip install sentence-transformers
```

**If you encounter issues with PyTorch:**
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
```

---

## ⚙️ Environment Configuration

### Step 1: Create `.env` File

Create a `.env` file in the project root directory (same level as `manage.py`).

### Step 2: Configure Environment Variables

Copy the following template into your `.env` file:

```env
# Django Settings
SECRET_KEY=your-secret-key-here-change-this-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# OpenAI Configuration (REQUIRED for answer generation)
OPENAI_API_KEY=sk-your-openai-api-key-here
OPENAI_MODEL=gpt-3.5-turbo

# Milvus Vector Database Configuration
MILVUS_HOST=localhost
MILVUS_PORT=19530
MILVUS_COLLECTION_NAME=classcare_documents

# Database (Optional - defaults to SQLite)
# DATABASE_URL=postgresql://user:password@localhost:5432/chatbot_db
```

### Step 3: Get OpenAI API Key

1. Go to: https://platform.openai.com/api-keys
2. Sign up or log in to your OpenAI account
3. Click "Create new secret key"
4. Copy the key (starts with `sk-`)
5. Paste it in your `.env` file as `OPENAI_API_KEY`

**Important:** 
- Keep your API key secure and never commit it to version control
- The `.env` file is already in `.gitignore` (if using Git)
- You'll need a valid OpenAI account with sufficient credits

### Step 4: Generate Django Secret Key (Optional but Recommended)

You can generate a secure secret key using Python:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Copy the output and use it as `SECRET_KEY` in your `.env` file.

---

## 💾 Database Setup

### SQLite (Default - No Setup Required)

The project uses SQLite by default, which requires no additional configuration. The database file (`db.sqlite3`) will be created automatically when you run migrations.

### PostgreSQL (Optional)

If you want to use PostgreSQL instead:

1. **Install PostgreSQL:**
   - Download from: https://www.postgresql.org/download/

2. **Create Database:**
   ```sql
   CREATE DATABASE chatbot_db;
   CREATE USER chatbot_user WITH PASSWORD 'your_password';
   GRANT ALL PRIVILEGES ON DATABASE chatbot_db TO chatbot_user;
   ```

3. **Update `.env` file:**
   ```env
   DATABASE_URL=postgresql://chatbot_user:your_password@localhost:5432/chatbot_db
   ```

4. **Install PostgreSQL adapter:**
   ```bash
   pip install psycopg2-binary
   ```

5. **Update `requirements.txt`** (uncomment the psycopg2 line)

### Run Database Migrations

After configuring your database, run:

```bash
python manage.py migrate
```

This creates all necessary database tables.

---

## 🚀 Running the Project

### Step 1: Collect Static Files (First Time Only)

```bash
python manage.py collectstatic --noinput
```

### Step 2: Create Superuser (Optional - for Django Admin)

```bash
python manage.py createsuperuser
```

Follow the prompts to create an admin account.

### Step 3: Start Development Server

```bash
python manage.py runserver
```

You should see output like:
```
Starting development server at http://127.0.0.1:8000/
Quit the server with CTRL-BREAK.
```

### Step 4: Access the Application

Open your web browser and navigate to:
- **Main Chat Interface:** http://127.0.0.1:8000/
- **Upload Documents:** http://127.0.0.1:8000/upload/
- **Django Admin:** http://127.0.0.1:8000/admin/

---

## ✅ Verification

### Test 1: Check Server is Running

1. Open http://127.0.0.1:8000/ in your browser
2. You should see the ClassCare AI chat interface

### Test 2: Upload a Document

1. Go to http://127.0.0.1:8000/upload/
2. Click "Choose File" or drag and drop a document
3. Supported formats: PDF, TXT, DOCX, XLSX
4. Click "Upload Document"
5. Wait for processing (may take a few seconds)
6. You should see a success message

### Test 3: Ask a Question

1. Go back to http://127.0.0.1:8000/
2. Type a question related to your uploaded document
3. Press Enter or click Send
4. You should receive an AI-generated answer

**Note:** The first question may take longer as it initializes the LLM and loads the vector store.

---

## 🔍 Troubleshooting

### Issue: "ModuleNotFoundError" or "No module named 'X'"

**Solution:**
```bash
# Make sure virtual environment is activated
# Then reinstall requirements
pip install -r requirements.txt
```

### Issue: "OPENAI_API_KEY not found" or "OpenAI LLM is not available"

**Solution:**
1. Check that `.env` file exists in project root
2. Verify `OPENAI_API_KEY` is set correctly in `.env`
3. Restart the Django server after changing `.env`
4. Make sure there are no spaces around the `=` sign in `.env`

### Issue: "sentence-transformers" not working

**Solution:**
```bash
pip install sentence-transformers
# If still having issues, try:
pip install --upgrade sentence-transformers
```

### Issue: Database migration errors

**Solution:**
```bash
# Delete existing database (if using SQLite)
rm db.sqlite3

# Recreate migrations
python manage.py makemigrations
python manage.py migrate
```

### Issue: Port 8000 already in use

**Solution:**
```bash
# Use a different port
python manage.py runserver 8001
```

### Issue: "Milvus connection failed" or vector store errors

**Solution:**
1. Make sure Milvus is running:
   ```bash
   # Check if Milvus container is running (if using Docker)
   docker ps | grep milvus
   
   # Or check Milvus health
   curl http://localhost:19530/healthz
   ```

2. Verify Milvus connection settings in `.env`:
   ```env
   MILVUS_HOST=localhost
   MILVUS_PORT=19530
   ```

3. If using Docker, restart Milvus:
   ```bash
   docker restart milvus-standalone
   ```

4. The collection will be created automatically on first document upload

### Issue: Slow document processing

**Solution:**
- This is normal for the first document (downloads HuggingFace models)
- Subsequent documents will be faster
- Large documents may take several minutes

### Issue: "CSRF verification failed"

**Solution:**
- Make sure you're accessing via `http://127.0.0.1:8000/` (not `localhost`)
- Clear browser cookies and try again
- Check that `DEBUG=True` in `.env` for development

---

## 📝 Quick Start Checklist

- [ ] Python 3.8+ installed
- [ ] Virtual environment created and activated
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Milvus installed and running (Docker or Milvus Lite)
- [ ] `.env` file created with `OPENAI_API_KEY` and Milvus settings
- [ ] Database migrations run (`python manage.py migrate`)
- [ ] Server running (`python manage.py runserver`)
- [ ] Can access http://127.0.0.1:8000/
- [ ] Successfully uploaded a test document
- [ ] Successfully asked a question and received an answer

---

## 🎯 Next Steps

After setup is complete:

1. **Upload Documents:**
   - Go to http://127.0.0.1:8000/upload/
   - Upload your documents (PDF, TXT, DOCX, XLSX)
   - Wait for processing to complete

2. **Start Chatting:**
   - Go to http://127.0.0.1:8000/
   - Ask questions about your uploaded documents
   - The AI will use RAG to answer based on your documents

3. **Read Documentation:**
   - See `SYSTEM_FLOW_DOCUMENTATION.md` for detailed system architecture
   - Understand how RAG, embeddings, and vector search work

---

## 📚 Additional Resources

- **Django Documentation:** https://docs.djangoproject.com/
- **LangChain Documentation:** https://python.langchain.com/
- **OpenAI API Documentation:** https://platform.openai.com/docs/
- **Milvus Documentation:** https://milvus.io/docs

---

## ⚠️ Important Notes

1. **API Costs:** OpenAI API calls cost money. Monitor your usage at https://platform.openai.com/usage
2. **Security:** Never commit `.env` file to version control
3. **Production:** Change `DEBUG=False` and set a secure `SECRET_KEY` for production
4. **Backup:** Regularly backup your `db.sqlite3` and Milvus data (if using Docker, backup the volume)
5. **Performance:** First document upload may be slow (downloads models). Subsequent uploads are faster.
6. **Milvus:** Make sure Milvus is running before starting the Django server. The vector store connects to Milvus on startup.

---

## 🆘 Getting Help

If you encounter issues not covered in this guide:

1. Check the error messages in the terminal
2. Review `SYSTEM_FLOW_DOCUMENTATION.md` for system details
3. Verify all prerequisites are met
4. Ensure all environment variables are set correctly
5. Try restarting the server after configuration changes

---

**Last Updated:** January 2025  
**Project Version:** 3.0

