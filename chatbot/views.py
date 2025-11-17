"""
Views for the ClassCare chatbot application.
"""
import os
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.conf import settings

from .models import Document, ChatSession, ChatMessage, ConversationMemory
from .langchain_service import rag_service


def index(request):
    """Main chatbot interface."""
    # Check for session_id in query parameters (from dashboard)
    query_session_id = request.GET.get('session_id')
    
    if query_session_id:
        try:
            chat_session = ChatSession.objects.get(id=query_session_id)
            request.session['chat_session_id'] = str(chat_session.id)
        except ChatSession.DoesNotExist:
            chat_session = ChatSession.objects.create(title="New Chat")
            request.session['chat_session_id'] = str(chat_session.id)
    else:
        # Get or create a chat session from session storage
        session_id = request.session.get('chat_session_id')
        
        if session_id:
            try:
                chat_session = ChatSession.objects.get(id=session_id)
            except ChatSession.DoesNotExist:
                chat_session = ChatSession.objects.create(title="New Chat")
                request.session['chat_session_id'] = str(chat_session.id)
        else:
            chat_session = ChatSession.objects.create(title="New Chat")
            request.session['chat_session_id'] = str(chat_session.id)
    
    # Get all chat sessions ordered by most recent for sidebar
    all_sessions = ChatSession.objects.all().order_by('-updated_at')[:50]
    
    # Get last message for each session
    sessions_with_preview = []
    for session in all_sessions:
        last_message = ChatMessage.objects.filter(session=session).order_by('-timestamp').first()
        sessions_with_preview.append({
            'session': session,
            'last_message': last_message.content[:60] + '...' if last_message and len(last_message.content) > 60 else (last_message.content if last_message else 'No messages yet'),
            'last_message_time': last_message.timestamp if last_message else session.updated_at,
        })
    
    # Get messages for current session
    messages = ChatMessage.objects.filter(session=chat_session).order_by('timestamp')
    messages_data = []
    for msg in messages:
        messages_data.append({
            'type': msg.message_type,
            'content': msg.content,
            'metadata': msg.metadata or {}
        })
    
    # Get uploaded documents
    documents = Document.objects.all()[:20]
    
    context = {
        'current_session': chat_session,
        'chat_sessions': sessions_with_preview,
        'documents': documents,
        'messages': messages_data,
    }
    
    return render(request, 'chatbot/index.html', context)


def upload_page(request):
    """Dedicated page for document upload."""
    # Get all documents for display
    documents = Document.objects.all().order_by('-uploaded_at')[:50]
    
    context = {
        'documents': documents,
    }
    
    return render(request, 'chatbot/upload.html', context)


@csrf_exempt
@require_http_methods(["POST"])
def upload_document(request):
    """Handle document upload and processing."""
    if not request.FILES.get('document'):
        return JsonResponse({
            'success': False,
            'error': 'No file uploaded'
        })
    
    uploaded_file = request.FILES['document']
    title = request.POST.get('title', uploaded_file.name)
    
    # Get file extension
    file_ext = uploaded_file.name.split('.')[-1].lower()
    
    # Save the file
    file_name = default_storage.save(
        f'documents/{uploaded_file.name}',
        uploaded_file
    )
    file_path = os.path.join(settings.MEDIA_ROOT, file_name)
    
    # Create document record
    document = Document.objects.create(
        title=title,
        file=file_name,
        file_type=file_ext,
        uploaded_by=request.user if request.user.is_authenticated else None
    )
    
    # Process the document with LangChain (pass document ID for tracking)
    result = rag_service.process_document(file_path, file_ext, document_id=str(document.id))
    
    if result['success']:
        document.processed = True
        document.num_chunks = result['num_chunks']
        document.save()
        
        return JsonResponse({
            'success': True,
            'message': f'Document uploaded and processed successfully. Created {result["num_chunks"]} chunks.',
            'document': {
                'id': str(document.id),
                'title': document.title,
                'file_type': document.file_type,
                'num_chunks': document.num_chunks
            }
        })
    else:
        document.delete()
        return JsonResponse({
            'success': False,
            'error': result.get('error', 'Failed to process document')
        })


@csrf_exempt
@require_http_methods(["POST"])
def send_message(request):
    """Handle chat message and get AI response."""
    try:
        data = json.loads(request.body)
        question = data.get('message', '').strip()
        session_id = data.get('session_id')
        
        if not question:
            return JsonResponse({
                'success': False,
                'error': 'Message cannot be empty'
            })
        
        # Get or create chat session
        if session_id:
            chat_session = get_object_or_404(ChatSession, id=session_id)
        else:
            chat_session = ChatSession.objects.create(
                title=question[:50] + '...' if len(question) > 50 else question
            )
        
        # Save user message
        user_message = ChatMessage.objects.create(
            session=chat_session,
            message_type='human',
            content=question
        )
        
        # Get chat history
        previous_messages = ChatMessage.objects.filter(
            session=chat_session
        ).order_by('timestamp')[:settings.MAX_CONVERSATION_HISTORY * 2]
        
        chat_history = []
        for i in range(0, len(previous_messages) - 1, 2):
            if previous_messages[i].message_type == 'human' and \
               i + 1 < len(previous_messages) and \
               previous_messages[i + 1].message_type == 'ai':
                chat_history.append((
                    previous_messages[i].content,
                    previous_messages[i + 1].content
                ))
        
        # Get answer from RAG service (using agent if available)
        result = rag_service.get_answer_with_agent(question, chat_history)
        
        if result['success']:
            # Save AI response
            ai_message = ChatMessage.objects.create(
                session=chat_session,
                message_type='ai',
                content=result['answer'],
                metadata={
                    'source_documents': result.get('source_documents', [])
                }
            )
            
            return JsonResponse({
                'success': True,
                'answer': result['answer'],
                'source_documents': result.get('source_documents', []),
                'session_id': str(chat_session.id),
                'message_id': str(ai_message.id)
            })
        else:
            return JsonResponse({
                'success': False,
                'error': result.get('error', 'Failed to get answer')
            })
            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


@require_http_methods(["GET"])
def get_session_messages(request, session_id):
    """Get all messages for a chat session."""
    chat_session = get_object_or_404(ChatSession, id=session_id)
    messages = ChatMessage.objects.filter(session=chat_session).order_by('timestamp')
    
    messages_data = []
    for msg in messages:
        messages_data.append({
            'id': str(msg.id),
            'type': msg.message_type,
            'content': msg.content,
            'timestamp': msg.timestamp.isoformat(),
            'metadata': msg.metadata
        })
    
    return JsonResponse({
        'success': True,
        'session': {
            'id': str(chat_session.id),
            'title': chat_session.title
        },
        'messages': messages_data
    })


@csrf_exempt
@require_http_methods(["POST"])
def create_session(request):
    """Create a new chat session."""
    data = json.loads(request.body)
    title = data.get('title', 'New Chat')
    
    chat_session = ChatSession.objects.create(
        title=title,
        user=request.user if request.user.is_authenticated else None
    )
    
    request.session['chat_session_id'] = str(chat_session.id)
    
    return JsonResponse({
        'success': True,
        'session': {
            'id': str(chat_session.id),
            'title': chat_session.title
        }
    })


@csrf_exempt
@require_http_methods(["DELETE"])
def delete_session(request, session_id):
    """Delete a chat session."""
    chat_session = get_object_or_404(ChatSession, id=session_id)
    chat_session.delete()
    
    return JsonResponse({
        'success': True,
        'message': 'Session deleted successfully'
    })


@require_http_methods(["GET"])
def list_documents(request):
    """List all uploaded documents."""
    documents = Document.objects.all()
    
    documents_data = []
    for doc in documents:
        documents_data.append({
            'id': str(doc.id),
            'title': doc.title,
            'file_type': doc.file_type,
            'uploaded_at': doc.uploaded_at.isoformat(),
            'processed': doc.processed,
            'num_chunks': doc.num_chunks
        })
    
    return JsonResponse({
        'success': True,
        'documents': documents_data
    })


@csrf_exempt
@require_http_methods(["DELETE"])
def delete_document(request, document_id):
    """Delete a document and remove it from vector store."""
    document = get_object_or_404(Document, id=document_id)
    
    # Delete from vector store first (before deleting the document record)
    if document.processed:
        try:
            vector_result = rag_service.delete_document_from_vector_store(str(document.id))
            if not vector_result.get('success'):
                print(f"⚠️ Warning: Could not delete from vector store: {vector_result.get('error')}")
        except Exception as e:
            print(f"⚠️ Warning: Error deleting from vector store: {e}")
            # Continue with file deletion even if vector store deletion fails
    
    # Delete the file
    if document.file:
        try:
            document.file.delete()
        except Exception as e:
            print(f"⚠️ Warning: Could not delete file: {e}")
    
    # Delete the document record
    document.delete()
    
    return JsonResponse({
        'success': True,
        'message': 'Document deleted successfully from database and vector store'
    })


