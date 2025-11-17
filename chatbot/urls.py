"""
URL patterns for the chatbot app.
"""
from django.urls import path
from . import views

app_name = 'chatbot'

urlpatterns = [
    # Main interface
    path('', views.index, name='index'),
    path('upload/', views.upload_page, name='upload_page'),
    
    # Chat endpoints
    path('api/send-message/', views.send_message, name='send_message'),
    path('api/session/<uuid:session_id>/messages/', views.get_session_messages, name='get_session_messages'),
    path('api/session/create/', views.create_session, name='create_session'),
    path('api/session/<uuid:session_id>/delete/', views.delete_session, name='delete_session'),
    
    # Document endpoints
    path('api/upload-document/', views.upload_document, name='upload_document'),
    path('api/documents/', views.list_documents, name='list_documents'),
    path('api/documents/<uuid:document_id>/delete/', views.delete_document, name='delete_document'),
]
