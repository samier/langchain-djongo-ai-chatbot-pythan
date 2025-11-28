# ClassCare Chatbot - Complete System Flow Documentation

## 📋 Table of Contents
1. [System Overview](#system-overview)
2. [Complete Flow Diagram](#complete-flow-diagram)
3. [Packages Used & When](#packages-used--when)
4. [How Memory Works](#how-memory-works)
5. [API Endpoints](#api-endpoints)
6. [Data Storage](#data-storage)

---

## 🎯 System Overview

This is a **RAG (Retrieval-Augmented Generation)** chatbot system that:
- Uploads documents (PDF, TXT, DOCX, XLSX)
- Converts documents into searchable vectors
- Answers questions based on uploaded documents
- Remembers conversation history

---

## 🔄 Complete Flow Diagram

### **Flow 1: Document Upload Process**

```
User Uploads Document
    ↓
Django receives file (views.py)
    ↓
File saved to: media/documents/
    ↓
Document record created in Database (Document model)
    ↓
LangChain processes document:
    ├─ Load document (PyPDFLoader/TextLoader/Docx2txtLoader)
    ├─ Split into chunks (RecursiveCharacterTextSplitter)
    ├─ Convert chunks to vectors (Local HuggingFace Embeddings - FREE)
    └─ Store vectors in FAISS database
    ↓
FAISS index saved to: vector_store/index.faiss
    ↓
Document marked as "processed" in Database
```

**What Happens:**
- Document → Text chunks → Vector embeddings → Stored in FAISS
- Each chunk = ~1000 characters
- **Uses Local HuggingFace Embeddings** for document upload (NO API calls!)
- No API calls needed for document processing
- **Requires:** `sentence-transformers` package installed

**Note:** Document upload uses local embeddings (HuggingFace) which are free and don't require API calls. This ensures fast, cost-free document processing.

---

### **Flow 2: Chat/Question Process**

```
User asks a question
    ↓
Django receives question (views.py)
    ↓
Load chat history from Database (ChatMessage model)
    ↓
LangChain RAG Pipeline:
    ├─ Convert question to vector (Local HuggingFace Embeddings - SAME as documents)
    ├─ Search FAISS for similar chunks (top 4 results)
    ├─ Load conversation memory (ConversationBufferWindowMemory)
    ├─ Build prompt with: Context + History + Question
    └─ Send to GPT-3.5-turbo (OpenAI API)
    ↓
Get answer from GPT
    ↓
Save to Database:
    ├─ User message → ChatMessage (type: 'human')
    └─ AI response → ChatMessage (type: 'ai')
    ↓
Return answer to user
```

**What Happens:**
- Question → Vector (local embeddings) → Search → Top 4 chunks → GPT → Answer
- **Uses Local HuggingFace Embeddings** (same as documents - NO API calls for search!)
- **1 API call:** Only for GPT answer generation (OpenAI API)
- **Requires:** `OPENAI_API_KEY` must be set for answer generation

**Important:** FAISS automatically uses the SAME embeddings that were used to store documents. Since documents are stored with local HuggingFace embeddings, questions also use local embeddings automatically (NO API calls for search).

---

## 📦 Packages Used & When

### **1. Django Framework**
**When Used:** Always
- Handles HTTP requests/responses
- Database management (SQLite/PostgreSQL)
- File uploads and storage
- Admin interface

**Files:** `views.py`, `models.py`, `urls.py`, `settings.py`

---

### **2. LangChain**
**When Used:** Document processing & Chat queries

**Purpose:**
- Orchestrates the RAG pipeline
- Manages document loading and splitting
- Handles conversation chains
- Manages memory

**Key Components:**
- `RecursiveCharacterTextSplitter` - Splits documents into chunks
- `ConversationalRetrievalChain` - Main RAG chain
- `ConversationBufferWindowMemory` - Stores chat history
- `PromptTemplate` - Formats prompts for GPT

**Files:** `langchain_service.py`

---

### **3. RAG (Retrieval-Augmented Generation)**
**When Used:** Every chat query

**What RAG Does:**
1. **Retrieval:** Finds relevant document chunks
2. **Augmentation:** Adds context to the question
3. **Generation:** GPT creates answer from context

**RAG Flow:**
```
Question → Embedding → Vector Search → Top Chunks → GPT → Answer
```

**Files:** `langchain_service.py` (get_answer method)

---

### **4. FAISS (Facebook AI Similarity Search)**
**When Used:** Document storage & Question search

**Purpose:**
- Stores document vectors (embeddings)
- Fast similarity search
- Finds most relevant chunks

**Storage Location:** `vector_store/index.faiss` and `vector_store/index.pkl`

**When:**
- **Save:** After document upload
- **Load:** When server starts
- **Search:** Every question asked

**Files:** `langchain_service.py` (process_document, get_answer)

---

### **5. Embeddings (Local HuggingFace - FREE)**

**When Used:** Document storage & Question search

**Local HuggingFace Embeddings (Always Used)**
- **Model:** `sentence-transformers/all-MiniLM-L6-v2`
- **Cost:** FREE (no API calls!)
- **Speed:** Fast (local processing)
- **Quality:** Good (384 dimensions)
- **Setup:** `sentence-transformers` package required
- **When:** 
  - **Document Upload:** Uses local HuggingFace embeddings (NO API calls)
  - **Question Search:** Uses local HuggingFace embeddings (NO API calls)
- **API Calls:** 
  - Document upload: 0 (completely free!)
  - Question search: 0 (completely free!)

**Note:** Document upload and question search both use local HuggingFace embeddings. This ensures:
- ✅ No API costs for embeddings
- ✅ Fast local processing
- ✅ Perfect matching between stored documents and search queries
- ✅ Works offline (except for GPT answer generation)

**Files:** `langchain_service.py`, `settings.py`

---

### **6. OpenAI API (GPT for Answers)**
**When Used:** Answer generation only

**Chat Questions:**
- **Chat Completions API:** Generates answer from context (1 call per question)
- **Model:** `gpt-3.5-turbo`
- **Required:** Yes (for answer generation)
- **Setup:** `OPENAI_API_KEY` required in `.env` file
- **Cost:** Paid per API call (only for answer generation)
- **Note:** Only used for generating answers. Embeddings are handled locally (free).

**Files:** `langchain_service.py`, `settings.py`

---

### **7. Other Packages**

| Package | When Used | Purpose |
|---------|-----------|---------|
| `pypdf` | PDF upload | Read PDF files |
| `python-docx` | DOCX upload | Read Word documents |
| `openpyxl` | XLSX upload | Read Excel files |
| `langchain-openai` | Always | OpenAI integration |
| `langchain-community` | Always | Community tools (FAISS, loaders) |

---

## 💾 How Memory Works

### **Three Types of Memory:**

#### **1. Database Memory (Permanent)**
**Storage:** SQLite/PostgreSQL Database
**Models:** `ChatSession`, `ChatMessage`, `ConversationMemory`

**What's Stored:**
- All chat sessions
- All messages (user + AI)
- Session metadata (title, timestamps)
- Conversation memory data (JSON)

**Location:** `db.sqlite3` (or PostgreSQL)

**When Saved:**
- Every message sent/received
- Automatically by Django ORM

**Files:** `models.py`, `views.py`

---

#### **2. LangChain Memory (Temporary)**
**Storage:** In-memory (ConversationBufferWindowMemory)
**Purpose:** Maintains conversation context for GPT

**What's Stored:**
- Last 10 conversation turns (configurable)
- Question-Answer pairs
- Used to build context for next question

**How It Works:**
```python
ConversationBufferWindowMemory(
    k=10,  # Keep last 10 turns
    memory_key="chat_history"
)
```

**When Used:**
- Every chat query
- Loaded from Database → Converted to LangChain format
- Sent to GPT with current question

**Files:** `langchain_service.py` (create_conversation_chain)

---

#### **3. Session Memory (Browser)**
**Storage:** Browser session storage
**Purpose:** Track current chat session

**What's Stored:**
- Current session ID
- UI state

**Location:** Browser cookies/session storage

**Files:** `views.py` (index view)

---

### **Memory Flow:**

```
User sends message
    ↓
Load from Database:
    ├─ ChatSession (session info)
    └─ ChatMessage (all previous messages)
    ↓
Convert to LangChain format:
    └─ List of (question, answer) tuples
    ↓
Add to ConversationBufferWindowMemory
    └─ Last 10 turns kept in memory
    ↓
Send to GPT with context
    ↓
Save new messages to Database
    ├─ User message → ChatMessage
    └─ AI response → ChatMessage
```

---

## 🌐 API Endpoints

### **Base URL:** `http://127.0.0.1:8000/`

### **1. Main Interface**
```
GET /
```
**Purpose:** Load chatbot web interface
**Response:** HTML page

---

### **2. Document Upload**
```
POST /api/upload/
```
**Purpose:** Upload and process a document

**Request:**
- Method: `POST`
- Content-Type: `multipart/form-data`
- Body:
  ```
  document: (file)
  title: (optional string)
  ```

**Response:**
```json
{
  "success": true,
  "message": "Document uploaded and processed successfully. Created 50 chunks.",
  "document": {
    "id": "uuid",
    "title": "Document Title",
    "file_type": "txt",
    "num_chunks": 50
  }
}
```

**What Happens:**
1. File saved to `media/documents/`
2. Document record created in Database
3. LangChain processes document
4. Vectors stored in FAISS (using local HuggingFace embeddings)
5. Document marked as processed

**Uses:** LangChain, Local HuggingFace Embeddings, FAISS
**API Calls:** 0 (completely free - no API calls needed!)
**Requires:** `sentence-transformers` package installed

---

### **3. Send Chat Message**
```
POST /api/send-message/
```
**Purpose:** Send a question and get AI answer

**Request:**
- Method: `POST`
- Content-Type: `application/json`
- Body:
```json
{
  "message": "What is ClassCare?",
  "session_id": "uuid (optional)"
}
```

**Response:**
```json
{
  "success": true,
  "answer": "ClassCare is a cloud-based ERP system...",
  "source_documents": [
    {
      "content": "Document chunk text...",
      "metadata": {...}
    }
  ],
  "session_id": "uuid",
  "message_id": "uuid"
}
```

**What Happens:**
1. Load chat history from Database
2. Convert question to embedding (Local HuggingFace - same as documents)
3. Search FAISS for similar chunks (top 4)
4. Send to GPT-3.5-turbo with context
5. Save messages to Database
6. Return answer

**Uses:** RAG, LangChain, Local HuggingFace Embeddings, OpenAI GPT, FAISS
**API Calls:** 1 (only for GPT answer generation - embeddings are free!)
**Requires:** `OPENAI_API_KEY` must be configured (for GPT only)

---

### **4. Get Session Messages**
```
GET /api/session/<session_id>/messages/
```
**Purpose:** Get all messages for a chat session

**Response:**
```json
{
  "success": true,
  "session": {
    "id": "uuid",
    "title": "Chat Title"
  },
  "messages": [
    {
      "id": "uuid",
      "type": "human",
      "content": "User message",
      "timestamp": "2025-01-01T12:00:00Z"
    },
    {
      "id": "uuid",
      "type": "ai",
      "content": "AI response",
      "timestamp": "2025-01-01T12:00:01Z"
    }
  ]
}
```

**Uses:** Django ORM (Database query)

---

### **5. Create New Session**
```
POST /api/session/create/
```
**Purpose:** Create a new chat session

**Request:**
```json
{
  "title": "New Chat (optional)"
}
```

**Response:**
```json
{
  "success": true,
  "session": {
    "id": "uuid",
    "title": "New Chat"
  }
}
```

**Uses:** Django ORM

---

### **6. Delete Session**
```
DELETE /api/session/<session_id>/delete/
```
**Purpose:** Delete a chat session and all messages

**Response:**
```json
{
  "success": true,
  "message": "Session deleted successfully"
}
```

**Uses:** Django ORM

---

### **7. List Documents**
```
GET /api/documents/
```
**Purpose:** Get list of all uploaded documents

**Response:**
```json
{
  "success": true,
  "documents": [
    {
      "id": "uuid",
      "title": "Document Title",
      "file_type": "txt",
      "uploaded_at": "2025-01-01T12:00:00Z",
      "processed": true,
      "num_chunks": 50
    }
  ]
}
```

**Uses:** Django ORM

---

### **8. Delete Document**
```
DELETE /api/documents/<document_id>/delete/
```
**Purpose:** Delete a document

**Response:**
```json
{
  "success": true,
  "message": "Document deleted successfully"
}
```

**Uses:** Django ORM, File system

---

## 💾 Data Storage

### **1. Database (SQLite/PostgreSQL)**
**Location:** `db.sqlite3` (or PostgreSQL)

**Tables:**
- `Document` - Uploaded documents metadata
- `ChatSession` - Chat sessions
- `ChatMessage` - All messages (permanent storage)
- `ConversationMemory` - Conversation memory data

---

### **2. Vector Database (FAISS)**
**Location:** `vector_store/`
**Files:**
- `index.faiss` - Vector embeddings
- `index.pkl` - Document metadata

**What's Stored:**
- All document chunks as vectors
- Fast similarity search index

---

### **3. File Storage**
**Location:** `media/documents/`
**What's Stored:**
- Original uploaded files (PDF, TXT, DOCX, XLSX)

---

## 📊 Summary Table

| Component | Package/Library | When Used | Purpose |
|-----------|----------------|-----------|---------|
| Web Framework | Django | Always | HTTP, Database, File handling |
| Document Processing | LangChain | Document upload | Load, split documents |
| Embeddings | Local HuggingFace | Upload + Chat | Convert text → vectors (FREE!) |
| Vector Storage | FAISS | Upload + Chat | Store/search vectors |
| RAG Pipeline | LangChain | Chat queries | Retrieve + Generate |
| LLM | OpenAI GPT-3.5 | Chat queries | Generate answers (paid) |
| Memory | Django ORM | Always | Store chat history |
| Memory (Context) | LangChain Memory | Chat queries | Maintain conversation context |

## ⚙️ Configuration Options

### **Embedding Configuration**

**Local HuggingFace Embeddings (Always Used):**
```python
# Automatically uses sentence-transformers
# Model: sentence-transformers/all-MiniLM-L6-v2
```
- **Document Upload:** Uses local HuggingFace embeddings
- **Question Search:** Uses local HuggingFace embeddings (same as documents)
- ✅ FREE (no API calls!)
- ✅ Fast local processing
- ✅ Works offline (except GPT)
- ✅ Perfect matching between storage and search
- **Installation:** `pip install sentence-transformers`

### **OpenAI Configuration (For Answer Generation Only)**

**OpenAI GPT-3.5-turbo:**
```python
# In settings.py or .env
OPENAI_API_KEY = "sk-..."  # REQUIRED for answer generation
OPENAI_MODEL = "gpt-3.5-turbo"  # Default model
```
- **When Used:** Only for generating answers (not for embeddings)
- 💰 Costs money per API call (only for answers)
- ✅ High-quality answers
- ❌ Requires internet connection
- ❌ Requires valid API key with sufficient quota

**Note:** Embeddings are handled locally (free), only answer generation uses OpenAI API.

---

## 🔑 Key Points

1. **Document Upload:** Uses LangChain + Local HuggingFace Embeddings + FAISS
   - **Uses local HuggingFace embeddings** for document storage (FREE!)
   - No API calls needed for document processing
   - Requires `sentence-transformers` package
2. **Chat Queries:** Uses RAG (Retrieval + Augmentation + Generation)
   - FAISS automatically uses SAME embeddings as documents (Local HuggingFace)
   - Questions use local HuggingFace embeddings (matching stored documents)
   - 1 API call per question (only for GPT answer generation)
3. **Memory:** Stored in Database (permanent) + LangChain (temporary context)
4. **Vector Search:** FAISS finds similar document chunks (top 4)
   - Uses local HuggingFace embeddings (same as document storage)
   - FREE - no API calls for search!
5. **Answer Generation:** GPT-3.5-turbo creates answers from context
   - Requires OpenAI API (only for answer generation)
   - Embeddings are handled locally (free)

## 💡 Embedding Model Matching

**Critical:** Documents and questions MUST use the same embedding model!

- ✅ **Current Setup:** Documents stored with Local HuggingFace embeddings → Questions use Local HuggingFace embeddings
- ✅ **Perfect Match:** FAISS ensures embeddings match automatically
- ✅ **Consistent Results:** Same embedding model for storage and search
- ✅ **Cost Effective:** No API calls for embeddings (completely free!)

**How It Works:**
- Documents are stored with local HuggingFace embeddings (`sentence-transformers/all-MiniLM-L6-v2`)
- FAISS stores the embedding model reference with the index
- When searching, FAISS automatically uses local HuggingFace embeddings (stored with documents)
- This ensures perfect matching between stored documents and search queries
- All embedding operations are local (no API calls, no costs)

---

**Document Version:** 3.0  
**Last Updated:** November 2025

## 🆕 Recent Updates (v3.0)

- ✅ Removed Ollama support - now uses OpenAI API only for answer generation
- ✅ Document upload uses local HuggingFace embeddings (FREE - no API calls!)
- ✅ Question search uses local HuggingFace embeddings (FREE - no API calls!)
- ✅ Consistent embedding model for storage and search (local HuggingFace)
- ✅ Simplified configuration (OpenAI API key only needed for answer generation)
- ✅ Cost-effective: Only 1 API call per question (for GPT answer generation)

## Previous Updates (v2.1)

- ✅ Document upload always used OpenAI embeddings
- ✅ Question search used OpenAI embeddings
- ✅ Consistent embedding model for storage and search

## Previous Updates (v2.0)

- ✅ Added local embeddings support (sentence-transformers)
- ✅ Improved error handling and validation
- ✅ Better logging and debugging information

