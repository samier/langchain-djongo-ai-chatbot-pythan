# ClassCare Chatbot

A RAG (Retrieval-Augmented Generation) chatbot system built with Django, LangChain, and Milvus.

## Example GIF

![Example GIF](classcare/readme.gif)

## Overview

This is a **RAG (Retrieval-Augmented Generation)** chatbot system that:
- Uploads documents (PDF, TXT, DOCX, XLSX)
- Converts documents into searchable vectors
- Answers questions based on uploaded documents
- Remembers conversation history

## Features

- 📄 **Document Upload**: Support for PDF, TXT, DOCX, and XLSX files
- 🔍 **Vector Search**: Fast similarity search using Milvus vector database
- 🤖 **AI-Powered Answers**: Uses OpenAI GPT models for intelligent responses
- 💾 **Local Embeddings**: Free local embeddings using HuggingFace (no API costs for document processing)
- 📊 **Admin Interface**: Django admin for managing documents and users
- 🔄 **Conversation Memory**: Maintains conversation context

## Quick Start

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Setup Milvus** (using Docker)
   ```bash
   docker-compose up -d
   ```

3. **Configure Environment**
   Create a `.env` file with:
   ```
   OPENAI_API_KEY=your_api_key_here
   MILVUS_HOST=localhost
   MILVUS_PORT=19530
   ```

4. **Run Migrations**
   ```bash
   python manage.py migrate
   ```

5. **Create Admin User**
   ```bash
   python create_admin_user.py
   ```

6. **Start Server**
   ```bash
   python manage.py runserver
   ```

7. **Access Application**
   - Main App: http://localhost:8000
   - Admin Panel: http://localhost:8000/admin

## Documentation

- [System Flow Documentation](SYSTEM_FLOW_DOCUMENTATION.md) - Complete system architecture and flow
- [Deployment Guide](DEPLOYMENT_GUIDE.md) - Production deployment instructions
- [Packages Summary](PACKAGES_SUMMARY.md) - Overview of all packages used

## Tech Stack

- **Backend**: Django
- **Vector Database**: Milvus
- **AI/ML**: LangChain, OpenAI GPT
- **Embeddings**: HuggingFace (local, free)
- **Document Processing**: PyPDF, docx2txt, openpyxl

## License

[Add your license here]

