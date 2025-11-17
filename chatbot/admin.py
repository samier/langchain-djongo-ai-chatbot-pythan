"""
Admin configuration for chatbot models.
"""
from django.contrib import admin
from django.utils.html import format_html
from .models import Document, ChatSession, ChatMessage, ConversationMemory


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    """Admin interface for Document model."""
    list_display = ['title', 'file_type', 'uploaded_at', 'processed_status', 'num_chunks', 'uploaded_by']
    list_filter = ['processed', 'file_type', 'uploaded_at']
    search_fields = ['title', 'file_type']
    readonly_fields = ['id', 'uploaded_at', 'file_size_display']
    date_hierarchy = 'uploaded_at'
    list_per_page = 25
    
    def processed_status(self, obj):
        """Display processed status with color coding."""
        if obj.processed:
            return format_html('<span style="color: green;">✓ Processed</span>')
        return format_html('<span style="color: orange;">⧗ Pending</span>')
    processed_status.short_description = 'Status'
    
    def file_size_display(self, obj):
        """Display file size in human-readable format."""
        try:
            size = obj.file.size
            for unit in ['B', 'KB', 'MB', 'GB']:
                if size < 1024.0:
                    return f"{size:.2f} {unit}"
                size /= 1024.0
            return f"{size:.2f} TB"
        except Exception:
            return "N/A"
    file_size_display.short_description = 'File Size'


@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    """Admin interface for ChatSession model."""
    list_display = ['title', 'user', 'message_count', 'created_at', 'updated_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['title', 'user__username']
    readonly_fields = ['id', 'created_at', 'updated_at']
    date_hierarchy = 'created_at'
    list_per_page = 25
    
    def message_count(self, obj):
        """Display number of messages in session."""
        count = obj.messages.count()
        return f"{count} messages"
    message_count.short_description = 'Messages'


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    """Admin interface for ChatMessage model."""
    list_display = ['get_session_title', 'message_type_badge', 'content_preview', 'timestamp']
    list_filter = ['message_type', 'timestamp']
    search_fields = ['content', 'session__title']
    readonly_fields = ['id', 'timestamp', 'session', 'message_type']
    date_hierarchy = 'timestamp'
    list_per_page = 50
    
    def get_session_title(self, obj):
        """Get the session title safely."""
        try:
            return obj.session.title
        except Exception:
            return "Unknown Session"
    get_session_title.short_description = 'Session'
    
    def message_type_badge(self, obj):
        """Display message type with color coding."""
        colors = {
            'human': 'blue',
            'ai': 'green',
            'system': 'gray'
        }
        color = colors.get(obj.message_type, 'black')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px;">{}</span>',
            color,
            obj.message_type.upper()
        )
    message_type_badge.short_description = 'Type'
    
    def content_preview(self, obj):
        """Display truncated content."""
        try:
            if len(obj.content) > 100:
                return obj.content[:100] + '...'
            return obj.content
        except Exception:
            return "Error displaying content"
    content_preview.short_description = 'Content'


@admin.register(ConversationMemory)
class ConversationMemoryAdmin(admin.ModelAdmin):
    """Admin interface for ConversationMemory model."""
    list_display = ['get_session_title', 'updated_at', 'memory_size']
    readonly_fields = ['updated_at', 'session']
    date_hierarchy = 'updated_at'
    list_per_page = 25
    
    def get_session_title(self, obj):
        """Get the session title safely."""
        try:
            return obj.session.title
        except Exception:
            return "Unknown Session"
    get_session_title.short_description = 'Session'
    
    def memory_size(self, obj):
        """Display memory data size."""
        try:
            import json
            size = len(json.dumps(obj.memory_data))
            if size < 1024:
                return f"{size} bytes"
            elif size < 1024 * 1024:
                return f"{size/1024:.2f} KB"
            else:
                return f"{size/(1024*1024):.2f} MB"
        except Exception:
            return "N/A"
    memory_size.short_description = 'Memory Size'


