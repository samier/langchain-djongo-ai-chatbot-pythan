"""
LangChain service for RAG pipeline and chatbot functionality.
"""
import os
import numpy as np
from typing import List, Dict, Any, Optional
from django.conf import settings

# Lazy imports to avoid PyTorch DLL errors at startup
# These will be imported when actually needed
RecursiveCharacterTextSplitter = None
PyPDFLoader = None
TextLoader = None
Docx2txtLoader = None
Milvus = None
HuggingFaceEmbeddings = None
ChatOpenAI = None  # For OpenAI support
ConversationalRetrievalChain = None
LLMChain = None
ConversationBufferWindowMemory = None
PromptTemplate = None
ChatPromptTemplate = None
MessagesPlaceholder = None
HumanMessage = None
AIMessage = None
Document = None
AgentExecutor = None
create_react_agent = None
import openpyxl

def _import_langchain_modules():
    """Lazy import of LangChain modules to avoid PyTorch DLL errors."""
    global RecursiveCharacterTextSplitter, PyPDFLoader, TextLoader, Docx2txtLoader
    global Milvus, HuggingFaceEmbeddings, ChatOpenAI
    global ConversationalRetrievalChain, LLMChain, ConversationBufferWindowMemory
    global PromptTemplate, ChatPromptTemplate, MessagesPlaceholder
    global HumanMessage, AIMessage, Document, AgentExecutor, create_react_agent
    
    if RecursiveCharacterTextSplitter is not None:
        return  # Already imported
    
    try:
        from langchain_text_splitters import RecursiveCharacterTextSplitter
        from langchain_community.document_loaders import (
            PyPDFLoader, 
            TextLoader, 
            Docx2txtLoader
        )
        from langchain_community.vectorstores import Milvus
        from langchain_community.embeddings import HuggingFaceEmbeddings
        # Import OpenAI chat model
        try:
            from langchain_openai import ChatOpenAI
        except ImportError:
            try:
                from langchain_community.chat_models import ChatOpenAI
            except ImportError:
                ChatOpenAI = None
        from langchain_classic.chains import ConversationalRetrievalChain, LLMChain
        from langchain_classic.memory import ConversationBufferWindowMemory
        from langchain_core.prompts import PromptTemplate, ChatPromptTemplate, MessagesPlaceholder
        from langchain_core.messages import HumanMessage, AIMessage
        from langchain_core.documents import Document
        try:
            from langchain.agents import AgentExecutor, create_react_agent
        except ImportError:
            try:
                from langchain.agents.agent import AgentExecutor
                from langchain.agents.react.agent import create_react_agent
            except ImportError:
                AgentExecutor = None
                create_react_agent = None
    except OSError as e:
        if "DLL" in str(e) or "c10.dll" in str(e) or "torch" in str(e).lower():
            error_msg = (
                f"⚠️ PyTorch DLL Error: {e}\n"
                "   This is a common Windows issue with PyTorch.\n"
                "   Solutions:\n"
                "   1. Install Visual C++ Redistributables: https://aka.ms/vs/17/release/vc_redist.x64.exe\n"
                "   2. Try older PyTorch version: .\\venv\\Scripts\\python.exe -m pip install torch==2.0.1 --index-url https://download.pytorch.org/whl/cpu\n"
                "   3. Restart your computer after installing Visual C++ Redistributables\n"
                "   4. Check if antivirus is blocking DLL files\n"
            )
            print(error_msg)
            # Don't raise - allow server to start but embeddings will be disabled
            print("⚠️ LangChain features will be disabled until PyTorch is fixed.")
            return  # Return without setting modules, they'll remain None
        else:
            raise
    except Exception as e:
        print(f"⚠️ Warning: Could not import LangChain modules: {e}")
        print("   This may be due to missing packages or PyTorch DLL issues.")
        print("   Try running: fix_torch_error.bat")
        raise

# Import tools for agent functionality
try:
    from .tools import get_tools
    TOOLS_AVAILABLE = True
except ImportError:
    TOOLS_AVAILABLE = False
    print("Warning: Tools module not found. Agent functionality disabled.")


class LangChainRAGService:
    """Service class for handling LangChain RAG operations."""
    
    def __init__(self):
        """Initialize the RAG service with embeddings and vector store."""
        self.local_embeddings = None  # Local embeddings (HuggingFace)
        self.vector_store = None
        self.llm = None  # LLM - OpenAI API only (GPT-3.5-turbo)
        self.agent = None
        self.agent_executor = None
        self._initialize_components()
        self._initialize_agent()
    
    def _initialize_components(self):
        """Initialize LangChain components."""
        # Import LangChain modules (lazy import to avoid PyTorch DLL errors)
        try:
            _import_langchain_modules()
        except ImportError as e:
            if "PyTorch DLL" in str(e):
                print("⚠️ PyTorch DLL error detected. Embeddings will be disabled.")
                print("   Please fix PyTorch installation (see error message above).")
                self.local_embeddings = None
                self.vector_store = None
                return  # Exit early, can't initialize without PyTorch
            else:
                raise  # Re-raise other import errors
        
        # Check if modules were imported successfully
        if HuggingFaceEmbeddings is None:
            print("⚠️ LangChain modules not available. Embeddings disabled.")
            self.local_embeddings = None
            self.vector_store = None
            return
        
        # Always initialize LOCAL embeddings first (NO API calls needed!)
        # Check if HuggingFaceEmbeddings is available (not None due to PyTorch DLL error)
        if HuggingFaceEmbeddings is None:
            print("⚠️ HuggingFaceEmbeddings is not available due to PyTorch DLL error.")
            print("   Embeddings will be disabled until PyTorch is fixed.")
            self.local_embeddings = None
        else:
            try:
                print("🔄 Initializing local embeddings (HuggingFace) - NO API calls needed...")
                self.local_embeddings = HuggingFaceEmbeddings(
                    model_name="sentence-transformers/all-MiniLM-L6-v2",
                    model_kwargs={'device': 'cpu'},
                    encode_kwargs={'normalize_embeddings': True}
                )
                print("✅ Local embeddings initialized successfully (for document processing and search)")
            except Exception as e:
                print(f"⚠️ Warning: Could not initialize local embeddings: {e}")
                print("   Please ensure sentence-transformers is installed: pip install sentence-transformers")
                self.local_embeddings = None
        
        # Initialize LLM: Only use OpenAI API (no Ollama)
        if ChatOpenAI is None:
            print("⚠️ ChatOpenAI is not available. LLM will be disabled.")
            print("   Install with: pip install langchain-openai")
            self.llm = None
        else:
            try:
                # Try to get API key from multiple sources
                openai_api_key = getattr(settings, 'OPENAI_API_KEY', '')
                if not openai_api_key or not openai_api_key.strip():
                    # Also check environment variable directly (in case .env wasn't loaded)
                    openai_api_key = os.environ.get('OPENAI_API_KEY', '').strip()
                
                openai_model = getattr(settings, 'OPENAI_MODEL', 'gpt-3.5-turbo')
                
                # Strip whitespace from API key
                if openai_api_key:
                    openai_api_key = openai_api_key.strip()
                
                # Debug: Show what we're reading (but don't print the full key for security)
                if openai_api_key:
                    key_preview = openai_api_key[:15] + "..." if len(openai_api_key) > 15 else "***"
                    print(f"🔧 Found OPENAI_API_KEY: {key_preview} (length: {len(openai_api_key)})")
                else:
                    print("⚠️ OPENAI_API_KEY is empty or not set")
                    print("   Checking environment variables...")
                    print(f"   os.environ.get('OPENAI_API_KEY'): {bool(os.environ.get('OPENAI_API_KEY'))}")
                    print(f"   settings.OPENAI_API_KEY: {bool(getattr(settings, 'OPENAI_API_KEY', None))}")
                
                if not openai_api_key:
                    print("⚠️ OPENAI_API_KEY not set. LLM will be disabled.")
                    print("   Set OPENAI_API_KEY in .env file to use OpenAI")
                    print("   Make sure:")
                    print("   1. .env file is in the project root directory")
                    print("   2. OPENAI_API_KEY=sk-... is set (no quotes, no spaces around =)")
                    print("   3. You've restarted the Django server after adding the key")
                    self.llm = None
                else:
                    print(f"🔄 Initializing OpenAI LLM - model: {openai_model}...")
                    # Try both parameter names for compatibility with different langchain versions
                    try:
                        # Try with openai_api_key first (langchain-openai)
                        self.llm = ChatOpenAI(
                            model=openai_model,
                            temperature=0.7,
                            openai_api_key=openai_api_key
                        )
                    except TypeError:
                        # Fall back to api_key parameter (older versions)
                        try:
                            self.llm = ChatOpenAI(
                                model=openai_model,
                                temperature=0.7,
                                api_key=openai_api_key
                            )
                        except Exception as e2:
                            # Last resort: set environment variable and initialize without explicit key
                            os.environ['OPENAI_API_KEY'] = openai_api_key
                            self.llm = ChatOpenAI(
                                model=openai_model,
                                temperature=0.7
                            )
                    print(f"✅ OpenAI LLM initialized successfully!")
            except Exception as e:
                print(f"⚠️ Warning: Could not initialize OpenAI LLM: {e}")
                print("   Please check your OPENAI_API_KEY in .env file")
                import traceback
                traceback.print_exc()
                self.llm = None
        
        # Initialize or connect to Milvus vector store (use local embeddings)
        if self.local_embeddings is not None:
            try:
                # Get Milvus connection settings
                milvus_host = getattr(settings, 'MILVUS_HOST', 'localhost')
                milvus_port = str(getattr(settings, 'MILVUS_PORT', '19530'))
                collection_name = getattr(settings, 'MILVUS_COLLECTION_NAME', 'classcare_documents')
                
                # Check if Milvus is available
                if Milvus is None:
                    print("⚠️ Milvus is not available. Please install: pip install pymilvus langchain-community")
                    self.vector_store = None
                    return
                
                # Try to connect to existing collection or create new one
                try:
                    # Connect to Milvus - will create collection if it doesn't exist
                    # Port should be string for connection_args
                    self.vector_store = Milvus(
                        embedding_function=self.local_embeddings,
                        collection_name=collection_name,
                        connection_args={
                            "host": milvus_host,
                            "port": milvus_port
                        }
                    )
                    print(f"✅ Connected to Milvus vector store (collection: {collection_name})")
                except Exception as e:
                    print(f"⚠️ Could not connect to Milvus: {e}")
                    print(f"   Make sure Milvus is running on {milvus_host}:{milvus_port}")
                    print("   Or install Milvus: https://milvus.io/docs/install_standalone-docker.md")
                    self.vector_store = None
            except Exception as e:
                print(f"❌ Error connecting to Milvus vector store: {e}")
                import traceback
                traceback.print_exc()
                self.vector_store = None
        else:
            print("ℹ️ Vector store initialization skipped (local embeddings not available)")
            self.vector_store = None
    
    def _initialize_llm_if_needed(self):
        """Re-initialize OpenAI LLM if it's None."""
        if self.llm is not None:
            return  # Already initialized
        
        print("🔧 Re-initializing OpenAI LLM...")
        
        if ChatOpenAI is None:
            print("⚠️ ChatOpenAI is not available. LLM will remain disabled.")
            print("   Install with: pip install langchain-openai")
            self.llm = None
            return
        
        try:
            # Try to get API key from multiple sources
            openai_api_key = getattr(settings, 'OPENAI_API_KEY', '')
            if not openai_api_key or not openai_api_key.strip():
                openai_api_key = os.environ.get('OPENAI_API_KEY', '').strip()
            
            openai_model = getattr(settings, 'OPENAI_MODEL', 'gpt-3.5-turbo')
            
            if openai_api_key:
                openai_api_key = openai_api_key.strip()
                key_preview = openai_api_key[:15] + "..." if len(openai_api_key) > 15 else "***"
                print(f"🔧 Found OPENAI_API_KEY: {key_preview} (length: {len(openai_api_key)})")
            else:
                print("⚠️ OPENAI_API_KEY is empty or not set")
                self.llm = None
                return
            
            print(f"🔄 Initializing OpenAI LLM - model: {openai_model}...")
            # Try both parameter names for compatibility
            try:
                self.llm = ChatOpenAI(
                    model=openai_model,
                    temperature=0.7,
                    openai_api_key=openai_api_key
                )
            except TypeError:
                try:
                    self.llm = ChatOpenAI(
                        model=openai_model,
                        temperature=0.7,
                        api_key=openai_api_key
                    )
                except Exception as e2:
                    os.environ['OPENAI_API_KEY'] = openai_api_key
                    self.llm = ChatOpenAI(
                        model=openai_model,
                        temperature=0.7
                    )
            print(f"✅ OpenAI LLM initialized successfully!")
        except Exception as e:
            print(f"⚠️ Warning: Could not initialize OpenAI LLM: {e}")
            import traceback
            traceback.print_exc()
            self.llm = None
    
    def _initialize_agent(self):
        """Initialize simple function calling with local LLM."""
        if not TOOLS_AVAILABLE or not self.llm:
            print("Agent not initialized: Tools or LLM not available")
            return
        
        try:
            # Import the tool functions directly
            from .tools import (
                create_student_api, 
                validate_student_data, 
                get_student_requirements
            )
            
            # Store tools for manual invocation
            self.tools_map = {
                'create_student_api': create_student_api,
                'validate_student_data': validate_student_data,
                'get_student_requirements': get_student_requirements,
            }
            
            self.agent_executor = True  # Simple flag to indicate tools are available
            
            print("Agent tools initialized successfully")
            
        except Exception as e:
            print(f"Error initializing agent tools: {str(e)}")
            self.agent_executor = None
            self.tools_map = {}
    
    def process_document(self, file_path: str, file_type: str, document_id: str = None) -> Dict[str, Any]:
        """
        Process a document and add it to the vector store.
        Uses LOCAL embeddings (HuggingFace) - NO OpenAI API calls!
        
        Args:
            file_path: Path to the document file
            file_type: Type of the document (pdf, txt, docx, etc.)
        
        Returns:
            Dictionary containing processing results
        """
        try:
            # Use LOCAL embeddings (HuggingFace) - NO API calls!
            # Check if HuggingFaceEmbeddings is available (not None due to PyTorch DLL error)
            if HuggingFaceEmbeddings is None:
                return {
                    'success': False,
                    'error': 'PyTorch DLL initialization failed. Embeddings are not available. Please fix PyTorch installation:\n1. Install Visual C++ Redistributables: https://aka.ms/vs/17/release/vc_redist.x64.exe\n2. Restart your computer\n3. Or try: .\\venv\\Scripts\\python.exe -m pip install torch==2.0.1 --index-url https://download.pytorch.org/whl/cpu'
                }
            
            # Initialize local embeddings if not already initialized
            if self.local_embeddings is None:
                try:
                    print("🔄 Initializing local embeddings (HuggingFace) for document processing...")
                    self.local_embeddings = HuggingFaceEmbeddings(
                        model_name="sentence-transformers/all-MiniLM-L6-v2",
                        model_kwargs={'device': 'cpu'},
                        encode_kwargs={'normalize_embeddings': True}
                    )
                    print("✅ Local embeddings initialized successfully (NO API calls needed!)")
                except Exception as e:
                    return {
                        'success': False,
                        'error': f'Failed to initialize local embeddings: {str(e)}. Please ensure sentence-transformers is installed: pip install sentence-transformers'
                    }
            
            # Use local embeddings for document processing
            embeddings_to_use = self.local_embeddings
            
            # Validate that file exists
            if not os.path.exists(file_path):
                return {
                    'success': False,
                    'error': f'File not found: {file_path}'
                }
            
            # Import LangChain modules if not already imported
            try:
                _import_langchain_modules()
            except Exception as e:
                return {
                    'success': False,
                    'error': f'Failed to import LangChain modules: {str(e)}. Please fix PyTorch installation.'
                }
            
            # Check if required modules are available
            if PyPDFLoader is None or TextLoader is None or Docx2txtLoader is None:
                return {
                    'success': False,
                    'error': 'Document loaders are not available due to PyTorch DLL error. Please fix PyTorch installation.'
                }
            
            # Load document based on file type
            if file_type == 'pdf':
                loader = PyPDFLoader(file_path)
                documents = loader.load()
            elif file_type == 'txt':
                loader = TextLoader(file_path, encoding='utf-8')
                documents = loader.load()
            elif file_type in ['docx', 'doc']:
                loader = Docx2txtLoader(file_path)
                documents = loader.load()
            elif file_type in ['xlsx', 'xls']:
                # Handle Excel files with openpyxl
                try:
                    workbook = openpyxl.load_workbook(file_path, read_only=True, data_only=True)
                    text_content = []
                    for sheet in workbook.worksheets:
                        for row in sheet.iter_rows(values_only=True):
                            row_text = ' '.join([str(cell) if cell is not None else '' for cell in row])
                            if row_text.strip():
                                text_content.append(row_text)
                    workbook.close()
                    # Check if Document class is available
                    if Document is None:
                        return {
                            'success': False,
                            'error': 'Document class is not available due to PyTorch DLL error.'
                        }
                    documents = [Document(page_content='\n'.join(text_content), metadata={'source': file_path})]
                except Exception as e:
                    return {
                        'success': False,
                        'error': f'Failed to load Excel file: {str(e)}'
                    }
            else:
                return {
                    'success': False,
                    'error': f'Unsupported file type: {file_type}'
                }
            
            # Check if text splitter is available
            if RecursiveCharacterTextSplitter is None:
                return {
                    'success': False,
                    'error': 'Text splitter is not available due to PyTorch DLL error. Please fix PyTorch installation.'
                }
            
            # Split documents into chunks
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=settings.CHUNK_SIZE,
                chunk_overlap=settings.CHUNK_OVERLAP,
                separators=["\n\n", "\n", " ", ""]
            )
            
            chunks = text_splitter.split_documents(documents)
            
            # Add document_id to metadata for tracking (if provided)
            if document_id:
                for chunk in chunks:
                    if chunk.metadata is None:
                        chunk.metadata = {}
                    chunk.metadata['document_id'] = str(document_id)
                    # Ensure source is set
                    if 'source' not in chunk.metadata:
                        chunk.metadata['source'] = file_path
            
            # Check if Milvus is available
            if Milvus is None:
                return {
                    'success': False,
                    'error': 'Milvus vector store is not available. Please install: pip install pymilvus langchain-community'
                }
            
            # Get Milvus connection settings
            milvus_host = getattr(settings, 'MILVUS_HOST', 'localhost')
            milvus_port = str(getattr(settings, 'MILVUS_PORT', '19530'))
            collection_name = getattr(settings, 'MILVUS_COLLECTION_NAME', 'classcare_documents')
            
            # Add to vector store with Milvus using LOCAL embeddings
            if self.vector_store is None:
                # Create new Milvus collection from documents using LOCAL embeddings
                print(f"📦 Creating new Milvus collection '{collection_name}' with {len(chunks)} chunks using LOCAL embeddings...")
                try:
                    self.vector_store = Milvus.from_documents(
                        documents=chunks,
                        embedding=embeddings_to_use,
                        collection_name=collection_name,
                        connection_args={
                            "host": milvus_host,
                            "port": milvus_port
                        }
                    )
                    print(f"✅ Created new Milvus collection with {len(chunks)} chunks (using local embeddings)")
                except Exception as e:
                    return {
                        'success': False,
                        'error': f'Failed to create Milvus collection: {str(e)}. Make sure Milvus is running on {milvus_host}:{milvus_port}'
                    }
            else:
                # Add documents to existing Milvus collection
                try:
                    self.vector_store.add_documents(chunks)
                    print(f"✅ Added {len(chunks)} chunks to existing Milvus collection (using local embeddings)")
                except Exception as e:
                    print(f"⚠️ Error adding documents to Milvus: {str(e)}")
                    return {
                        'success': False,
                        'error': f'Failed to add documents to Milvus: {str(e)}'
                    }
            
            return {
                'success': True,
                'num_chunks': len(chunks),
                'total_characters': sum(len(chunk.page_content) for chunk in chunks)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def create_conversation_chain(self, memory: Optional[ConversationBufferWindowMemory] = None):
        """
        Create a conversational retrieval chain.
        
        Args:
            memory: Optional conversation memory
        
        Returns:
            ConversationalRetrievalChain instance
        """
        if not self.vector_store or not self.llm:
            raise ValueError("Vector store and LLM must be initialized")
        
        # Create memory if not provided
        if memory is None:
            memory = ConversationBufferWindowMemory(
                k=settings.MAX_CONVERSATION_HISTORY,
                memory_key="chat_history",
                return_messages=True,
                output_key="answer"
            )
        
        # Custom prompt template
        prompt_template = """You are a helpful AI assistant for ClassCare software. 
        Use the following pieces of context to answer the question at the end. 
        If you don't know the answer based on the context, just say that you don't know, don't try to make up an answer.
        Always be friendly, professional, and helpful.
        
        Context: {context}
        
        Question: {question}
        
        Helpful Answer:"""
        
        PROMPT = PromptTemplate(
            template=prompt_template,
            input_variables=["context", "question"]
        )
        
        # Create the conversational retrieval chain
        # IMPORTANT: Milvus retriever automatically uses the SAME embeddings
        # that were used to create the vector store. Documents are stored with
        # local embeddings, so questions also use local embeddings (no API calls!)
        retriever = self.vector_store.as_retriever(
            search_kwargs={"k": 4}  # Return top 4 most relevant chunks
        )
        
        # Verify embeddings match (for debugging)
        if hasattr(self.vector_store, 'embeddings') and self.local_embeddings:
            print(f"🔍 Using local embeddings for similarity search (top 4 chunks)")
        
        chain = ConversationalRetrievalChain.from_llm(
            llm=self.llm,
            retriever=retriever,
            memory=memory,
            return_source_documents=True,
            combine_docs_chain_kwargs={"prompt": PROMPT}
        )
        
        return chain
    
    def get_answer(self, question: str, chat_history: List[tuple] = None) -> Dict[str, Any]:
        """
        Get an answer to a question using the RAG pipeline.
        Uses LOCAL embeddings and LOCAL LLM - NO API calls!
        
        Args:
            question: User's question
            chat_history: List of (question, answer) tuples
        
        Returns:
            Dictionary containing the answer and source documents
        """
        try:
            # Check if vector store exists
            if not self.vector_store:
                return {
                    'success': False,
                    'error': 'No documents have been uploaded yet. Please upload documents first.'
                }
            
            # Use Milvus similarity search (documents are stored with local embeddings)
            # Milvus automatically uses the same embeddings that were used to create the collection
            print("🔍 Searching Milvus vector store using local embeddings...")
            try:
                # Use Milvus similarity search - it uses the same embeddings as stored documents
                retrieved_docs = self.vector_store.similarity_search(question, k=4)
                print(f"✅ Found {len(retrieved_docs)} relevant chunks from Milvus")
            except Exception as e:
                print(f"⚠️ Error searching Milvus: {e}")
                return {
                    'success': False,
                    'error': f'Error searching vector store: {str(e)}. Make sure Milvus is running and collection exists.'
                }
            
            # Build context from retrieved documents
            context = "\n\n".join([doc.page_content for doc in retrieved_docs])
            
            # Build chat history string
            history_text = ""
            if chat_history:
                history_parts = []
                for human_msg, ai_msg in chat_history[-settings.MAX_CONVERSATION_HISTORY:]:
                    history_parts.append(f"Human: {human_msg}\nAI: {ai_msg}")
                history_text = "\n\n".join(history_parts)
            
            # Build prompt with context
            newline = '\n'
            history_section = f'Previous conversation:{newline}{history_text}{newline}{newline}' if history_text else ''
            prompt = f"""You are a helpful AI assistant for ClassCare software. 
Use the following pieces of context to answer the question at the end. 
If you don't know the answer based on the context, just say that you don't know, don't try to make up an answer.
Always be friendly, professional, and helpful.

{history_section}Context: {context}

Question: {question}

Helpful Answer:"""
            
            # Call OpenAI LLM
            # If LLM is not initialized, try to initialize it now
            if not self.llm:
                print("⚠️ LLM is not initialized. Attempting to initialize OpenAI now...")
                self._initialize_llm_if_needed()
            
            # Check again after re-initialization attempt
            if not self.llm:
                openai_key = os.environ.get('OPENAI_API_KEY', '').strip() or getattr(settings, 'OPENAI_API_KEY', '')
                if not openai_key:
                    return {
                        'success': False,
                        'error': 'OpenAI LLM is not available. Please:\n1. Set OPENAI_API_KEY in .env file\n2. Get your API key from: https://platform.openai.com/api-keys\n3. Restart your Django server'
                    }
                else:
                    return {
                        'success': False,
                        'error': 'OpenAI LLM failed to initialize. Please check:\n1. OPENAI_API_KEY is valid in .env file\n2. You have internet connection\n3. langchain-openai is installed: pip install langchain-openai\n4. Check server console for detailed error messages'
                    }
            
            print(f"🤖 Calling OpenAI LLM (GPT-3.5-turbo)...")
            try:
                response = self.llm.invoke(prompt)
                answer = response.content if hasattr(response, 'content') else str(response)
            except Exception as e:
                error_str = str(e)
                # OpenAI-specific errors
                if 'api key' in error_str.lower() or 'authentication' in error_str.lower():
                    return {
                        'success': False,
                        'error': f'OpenAI API key error: {error_str}\n\nPlease check:\n1. OPENAI_API_KEY is set correctly in .env file\n2. API key is valid and has credits\n3. Get your key from: https://platform.openai.com/api-keys'
                    }
                elif 'rate limit' in error_str.lower():
                    return {
                        'success': False,
                        'error': f'OpenAI rate limit exceeded: {error_str}\n\nPlease wait a moment and try again, or upgrade your OpenAI plan.'
                    }
                else:
                    return {
                        'success': False,
                        'error': f'OpenAI error: {error_str}\n\nPlease check:\n1. OPENAI_API_KEY is valid\n2. You have sufficient credits\n3. Internet connection is working'
                    }
            
            # Extract source documents info
            source_docs = []
            for doc in retrieved_docs:
                source_docs.append({
                    'content': doc.page_content[:200] + '...' if len(doc.page_content) > 200 else doc.page_content,
                    'metadata': doc.metadata
                })
            
            return {
                'success': True,
                'answer': answer,
                'source_documents': source_docs
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def delete_document_from_vector_store(self, document_id: str) -> Dict[str, Any]:
        """
        Delete all chunks belonging to a specific document from the vector store.
        
        Args:
            document_id: The document ID to delete
        
        Returns:
            Dictionary containing deletion results
        """
        try:
            if not self.vector_store:
                return {
                    'success': False,
                    'error': 'Vector store is not initialized'
                }
            
            # Delete chunks from Milvus using metadata filter expression
            try:
                # Milvus supports deleting by filter expression
                # The expression format: 'document_id == "value"'
                filter_expr = f'document_id == "{document_id}"'
                
                # Delete using filter expression
                self.vector_store.delete(expr=filter_expr)
                print(f"✅ Deleted chunks from Milvus for document {document_id}")
                
                return {
                    'success': True,
                    'message': f'Successfully deleted chunks from Milvus for document {document_id}',
                    'deleted_count': 'unknown'  # Milvus doesn't return count directly
                }
            except Exception as e:
                print(f"⚠️ Error deleting from Milvus: {e}")
                # Try alternative: search first to verify chunks exist
                try:
                    # Search to check if chunks exist
                    search_results = self.vector_store.similarity_search(
                        query="test",  # Dummy query
                        k=100,
                        expr=filter_expr
                    )
                    
                    if not search_results:
                        print(f"ℹ️ No chunks found for document ID: {document_id}")
                        return {
                            'success': True,
                            'message': 'No chunks found for this document (may have been already deleted)',
                            'deleted_count': 0
                        }
                    
                    # Try delete again with different syntax
                    try:
                        # Some Milvus versions use different syntax
                        from pymilvus import Collection
                        collection = self.vector_store._collection
                        if collection:
                            collection.delete(expr=filter_expr)
                            print(f"✅ Deleted chunks from Milvus collection for document {document_id}")
                            return {
                                'success': True,
                                'message': f'Successfully deleted chunks from Milvus for document {document_id}',
                                'deleted_count': len(search_results)
                            }
                    except Exception as e3:
                        return {
                            'success': False,
                            'error': f'Failed to delete from Milvus: {str(e3)}. Please check Milvus connection and collection permissions.'
                        }
                except Exception as e2:
                    return {
                        'success': False,
                        'error': f'Failed to delete from Milvus: {str(e2)}. Make sure Milvus is running and collection exists.'
                    }
                    
        except Exception as e:
            print(f"❌ Error in delete_document_from_vector_store: {e}")
            import traceback
            traceback.print_exc()
            return {
                'success': False,
                'error': f'Error deleting from vector store: {str(e)}'
            }
    
    def search_documents(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """
        Search for relevant documents in the vector store.
        
        Args:
            query: Search query
            k: Number of results to return
        
        Returns:
            List of relevant document chunks
        """
        if not self.vector_store:
            return []
        
        try:
            results = self.vector_store.similarity_search(query, k=k)
            return [
                {
                    'content': doc.page_content,
                    'metadata': doc.metadata
                }
                for doc in results
            ]
        except Exception as e:
            print(f"Search error: {e}")
            return []
    
    def get_answer_with_agent(self, question: str, chat_history: List = None) -> Dict[str, Any]:
        """
        Get answer using conversational flow with tool support for student creation.
        Falls back to regular RAG for informational queries.
        
        Args:
            question: User's question
            chat_history: List of (question, answer) tuples from previous conversation
        
        Returns:
            Dictionary containing answer and metadata
        """
        # Check if user wants to create something or call an API
        create_keywords = ['create', 'add', 'new', 'register', 'submit', 'student']
        is_action_request = any(keyword in question.lower() for keyword in create_keywords)
        
        # Use conversational student creation if requested and tools available
        if self.agent_executor and hasattr(self, 'tools_map') and is_action_request:
            try:
                # Use LLM with system prompt to guide student creation
                messages = [
                    {
                        "role": "system",
                        "content": """You are a helpful AI assistant for ClassCare school management system.

You help users create students by collecting information conversationally.

Required student information:
- Student Name (minimum 2 characters, letters only)
- Student ID (exactly 5 digits)
- Grade/Class (one of: KG, Grade 1-12)
- Email (valid email format)

Process:
1. If user wants to create a student, explain what you need
2. Ask for information one field at a time
3. Validate each input before proceeding
4. When all data is collected, confirm and create the student
5. Be friendly and conversational

Remember previous conversation context."""
                    }
                ]
                
                # Add chat history
                if chat_history:
                    for human, ai in chat_history[-3:]:
                        messages.append({"role": "user", "content": human})
                        messages.append({"role": "assistant", "content": ai})
                
                # Add current question
                messages.append({"role": "user", "content": question})
                
                # Get response from OpenAI LLM
                # If LLM is not initialized, try to initialize it now
                if not self.llm:
                    print("⚠️ LLM is not initialized in agent. Attempting to initialize OpenAI now...")
                    self._initialize_llm_if_needed()
                
                # Check again after re-initialization attempt
                if not self.llm:
                    openai_key = os.environ.get('OPENAI_API_KEY', '').strip() or getattr(settings, 'OPENAI_API_KEY', '')
                    if not openai_key:
                        return {
                            'success': False,
                            'error': 'OpenAI LLM not initialized. Please set OPENAI_API_KEY in .env file.'
                        }
                    else:
                        return {
                            'success': False,
                            'error': 'OpenAI LLM failed to initialize. Please check OPENAI_API_KEY is valid and langchain-openai is installed.'
                        }
                
                # Convert messages format for OpenAI
                try:
                    # OpenAI format: structured messages
                    from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
                    langchain_messages = []
                    for msg in messages:
                        if msg["role"] == "system":
                            langchain_messages.append(SystemMessage(content=msg['content']))
                        elif msg["role"] == "user":
                            langchain_messages.append(HumanMessage(content=msg['content']))
                        elif msg["role"] == "assistant":
                            langchain_messages.append(AIMessage(content=msg['content']))
                    response = self.llm.invoke(langchain_messages)
                    
                    answer = response.content if hasattr(response, 'content') else str(response)
                except Exception as e:
                    error_str = str(e)
                    # Fall back to regular RAG on any LLM error
                    print(f"LLM error in agent: {error_str}, falling back to regular RAG")
                    pass
                
                # Check if user is providing student data - simple pattern matching
                # This is a simplified version - in production, you'd use function calling
                if all(word not in question.lower() for word in ['create', 'want', 'need', 'help']):
                    # User might be providing data - try to detect complete student info
                    # For now, just return the conversational response
                    pass
                
                return {
                    'success': True,
                    'answer': answer,
                    'source_documents': [],
                    'used_agent': True
                }
                
            except Exception as e:
                print(f"Agent error: {str(e)}")
                import traceback
                traceback.print_exc()
                # Fall back to regular RAG
                pass
        
        # Use regular RAG for informational queries or if agent failed
        return self.get_answer(question, chat_history)


# Create a singleton instance (lazy initialization to avoid PyTorch DLL errors at startup)
_rag_service_instance = None

def get_rag_service():
    """Get or create the RAG service instance (lazy initialization)."""
    global _rag_service_instance
    if _rag_service_instance is None:
        _rag_service_instance = LangChainRAGService()
    return _rag_service_instance

# For backward compatibility, create the instance but delay initialization
rag_service = type('LazyRAGService', (), {
    '__getattr__': lambda self, name: getattr(get_rag_service(), name)
})()


