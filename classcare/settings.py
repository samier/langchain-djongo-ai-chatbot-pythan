"""
Django settings for ClassCare chatbot project.
"""

from pathlib import Path
import os
from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from .env file
load_dotenv(BASE_DIR / '.env')

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-change-this-in-production-key-12345')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG', 'True').lower() == 'true'

# Comma-separated list of allowed hosts
ALLOWED_HOSTS_STR = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1,*')
ALLOWED_HOSTS = [host.strip() for host in ALLOWED_HOSTS_STR.split(',') if host.strip()]


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders',  # Added for CORS support
    'chatbot',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',  # Added for CORS support - must be before CommonMiddleware
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'classcare.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'classcare.wsgi.application'


# Database
# Use PostgreSQL if environment variables are set, otherwise use SQLite
if os.environ.get('DB_ENGINE') == 'django.db.backends.postgresql':
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.environ.get('DB_NAME', 'classcare_chatbot'),
            'USER': os.environ.get('DB_USER', 'classcare_user'),
            'PASSWORD': os.environ.get('DB_PASSWORD', ''),
            'HOST': os.environ.get('DB_HOST', 'localhost'),
            'PORT': os.environ.get('DB_PORT', '5432'),
        }
    }
else:
    # Default to SQLite
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }


# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
LANGUAGE_CODE = os.environ.get('LANGUAGE_CODE', 'en-us')

TIME_ZONE = os.environ.get('TIME_ZONE', 'UTC')

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']

# Media files (User uploads)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# LangChain and AI Configuration
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', '')
HUGGINGFACE_API_KEY = os.environ.get('HUGGINGFACE_API_KEY', '')

# LLM Configuration: Choose between Ollama (local, free) or OpenAI (cloud, paid)
# Set to True to use Ollama (local LLM - free, no API key needed)
# Set to False to use OpenAI (requires API key, costs money, better quality)
USE_OLLAMA = os.environ.get('USE_OLLAMA', 'True').lower() == 'true'
OLLAMA_MODEL = os.environ.get('OLLAMA_MODEL', 'llama2')
OLLAMA_BASE_URL = os.environ.get('OLLAMA_BASE_URL', 'http://localhost:11434')

# OpenAI Configuration (used when USE_OLLAMA=False)
OPENAI_MODEL = os.environ.get('OPENAI_MODEL', 'gpt-3.5-turbo')

# Use local embeddings instead of OpenAI (NO API CALLS for document storage!)
# Set to True to use sentence-transformers (free, local, no API needed)
# Set to False to use OpenAI embeddings (requires API key, costs money)
USE_LOCAL_EMBEDDINGS = os.environ.get('USE_LOCAL_EMBEDDINGS', 'True').lower() == 'true'
USE_QUESTION_LOCAL_EMBEDDINGS = os.environ.get('USE_QUESTION_LOCAL_EMBEDDINGS', 'True').lower() == 'true'

# Vector Store Configuration (Using Milvus)
MILVUS_HOST = os.environ.get('MILVUS_HOST', 'localhost')
MILVUS_PORT = os.environ.get('MILVUS_PORT', '19530')
MILVUS_COLLECTION_NAME = os.environ.get('MILVUS_COLLECTION_NAME', 'classcare_documents')

# Chatbot Configuration
CHUNK_SIZE = int(os.environ.get('CHUNK_SIZE', '1000'))
CHUNK_OVERLAP = int(os.environ.get('CHUNK_OVERLAP', '200'))
MAX_CONVERSATION_HISTORY = int(os.environ.get('MAX_CONVERSATION_HISTORY', '10'))

# CORS Configuration
CORS_ALLOW_ALL_ORIGINS = os.environ.get('CORS_ALLOW_ALL_ORIGINS', 'True').lower() == 'true'
CORS_ALLOW_CREDENTIALS = os.environ.get('CORS_ALLOW_CREDENTIALS', 'True').lower() == 'true'

# CORS Allowed Origins (comma-separated)
CORS_ALLOWED_ORIGINS_STR = os.environ.get(
    'CORS_ALLOWED_ORIGINS',
    'http://localhost:3000,http://localhost:8000,http://127.0.0.1:3000,http://127.0.0.1:8000'
)
CORS_ALLOWED_ORIGINS = [origin.strip() for origin in CORS_ALLOWED_ORIGINS_STR.split(',') if origin.strip()]

# CORS Allowed Methods (comma-separated)
CORS_ALLOW_METHODS_STR = os.environ.get('CORS_ALLOW_METHODS', 'DELETE,GET,OPTIONS,PATCH,POST,PUT')
CORS_ALLOW_METHODS = [method.strip() for method in CORS_ALLOW_METHODS_STR.split(',') if method.strip()]

# CORS Allowed Headers (comma-separated)
CORS_ALLOW_HEADERS_STR = os.environ.get(
    'CORS_ALLOW_HEADERS',
    'accept,accept-encoding,authorization,content-type,dnt,origin,user-agent,x-csrftoken,x-requested-with'
)
CORS_ALLOW_HEADERS = [header.strip() for header in CORS_ALLOW_HEADERS_STR.split(',') if header.strip()]


