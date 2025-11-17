"""
Tests for the chatbot application.
"""
from django.test import TestCase, Client
from django.urls import reverse
from .models import Document, ChatSession, ChatMessage
import os


class ChatbotModelTests(TestCase):
    """Test cases for chatbot models."""
    
    def test_create_chat_session(self):
        """Test creating a chat session."""
        session = ChatSession.objects.create(title="Test Session")
        self.assertIsNotNone(session.id)
        self.assertEqual(session.title, "Test Session")
    
    def test_create_chat_message(self):
        """Test creating a chat message."""
        session = ChatSession.objects.create(title="Test Session")
        message = ChatMessage.objects.create(
            session=session,
            message_type='human',
            content='Test question'
        )
        self.assertIsNotNone(message.id)
        self.assertEqual(message.content, 'Test question')
        self.assertEqual(message.session, session)
    
    def test_document_creation(self):
        """Test document model creation."""
        doc = Document.objects.create(
            title="Test Document",
            file="test.pdf",
            file_type="pdf"
        )
        self.assertIsNotNone(doc.id)
        self.assertEqual(doc.title, "Test Document")
        self.assertFalse(doc.processed)


class ChatbotViewTests(TestCase):
    """Test cases for chatbot views."""
    
    def setUp(self):
        """Set up test client."""
        self.client = Client()
    
    def test_index_view(self):
        """Test the index view."""
        response = self.client.get(reverse('chatbot:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'ClassCare')
    
    def test_create_session_api(self):
        """Test creating a session via API."""
        response = self.client.post(
            reverse('chatbot:create_session'),
            data='{"title": "New Session"}',
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertIn('session', data)
    
    def test_list_documents_api(self):
        """Test listing documents via API."""
        response = self.client.get(reverse('chatbot:list_documents'))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertIn('documents', data)


