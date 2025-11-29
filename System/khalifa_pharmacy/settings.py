"""
Django settings for Khalifa Pharmacy Conversation Management System
نظام إدارة محادثات صيدليات خليفة

المرحلة 1: SQLite (Development)
المرحلة 2: PostgreSQL/MySQL (Production)
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Build paths inside the project
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from parent directory (override existing env vars)
load_dotenv(os.path.join(BASE_DIR.parent, '.env'), override=True)

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'django-insecure-khalifa-pharmacy-2025-change-in-production')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DJANGO_DEBUG', 'True') == 'True'

ALLOWED_HOSTS = os.getenv('DJANGO_ALLOWED_HOSTS', '*').split(',')


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third Party Apps
    'rest_framework',

    # Our Apps
    'conversations',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'conversations.middleware.PermanentSessionMiddleware',  # جلسة دائمة
    'conversations.middleware.UserActivityMiddleware',  # تتبع نشاط المستخدم
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'khalifa_pharmacy.urls'

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

WSGI_APPLICATION = 'khalifa_pharmacy.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

# Dynamic Database Configuration from Environment Variables
DB_ENGINE = os.getenv('DB_ENGINE', 'sqlite3')

if DB_ENGINE == 'postgresql':
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.getenv('DB_NAME', 'khalifa_pharmacy_db'),
            'USER': os.getenv('DB_USER', 'postgres'),
            'PASSWORD': os.getenv('DB_PASSWORD', ''),
            'HOST': os.getenv('DB_HOST', 'localhost'),
            'PORT': os.getenv('DB_PORT', '5432'),
            'CONN_MAX_AGE': int(os.getenv('DB_CONN_MAX_AGE', '600')),
            'OPTIONS': {
                'connect_timeout': int(os.getenv('DB_CONN_TIMEOUT', '10')),
            },
        }
    }
elif DB_ENGINE == 'mysql':
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': os.getenv('DB_NAME', 'khalifa_pharmacy_db'),
            'USER': os.getenv('DB_USER', 'root'),
            'PASSWORD': os.getenv('DB_PASSWORD', ''),
            'HOST': os.getenv('DB_HOST', 'localhost'),
            'PORT': os.getenv('DB_PORT', '3306'),
            'CONN_MAX_AGE': int(os.getenv('DB_CONN_MAX_AGE', '600')),
            'OPTIONS': {
                'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
                'charset': 'utf8mb4',
            },
        }
    }
else:
    # SQLite (Default for Development)
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / os.getenv('DB_NAME', 'db.sqlite3'),
            'OPTIONS': {
                'timeout': 30,
            },
            'CONN_MAX_AGE': 600,
        }
    }


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

# Custom Authentication Backend
AUTHENTICATION_BACKENDS = [
    'conversations.authentication.CustomUserBackend',  # Custom backend للـ User model
    'django.contrib.auth.backends.ModelBackend',  # Default backend
]

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 8,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'ar'  # Arabic

LANGUAGES = [
    ('ar', 'العربية'),
    ('en', 'English'),
]

LOCALE_PATHS = [
    BASE_DIR / 'locale',
]

TIME_ZONE = 'Africa/Cairo'  # Egypt timezone

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# Media files (Uploaded files)
MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'


# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# Session Configuration - جلسة دائمة لا تنتهي أبداً
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_AGE = 86400 * 365 * 10  # 10 years - جلسة شبه دائمة
SESSION_SAVE_EVERY_REQUEST = True  # حفظ الجلسة مع كل طلب
SESSION_EXPIRE_AT_BROWSER_CLOSE = False  # لا تنتهي عند إغلاق المتصفح
SESSION_COOKIE_NAME = 'khalifa_sessionid'  # اسم مخصص للـ cookie
SESSION_COOKIE_HTTPONLY = True  # حماية من XSS
SESSION_COOKIE_SAMESITE = 'Lax'  # حماية من CSRF


# Security Settings
CSRF_COOKIE_SECURE = False  # True in production with HTTPS
SESSION_COOKIE_SECURE = False  # True in production with HTTPS
SECURE_SSL_REDIRECT = False  # True in production

# CSRF Trusted Origins
CSRF_TRUSTED_ORIGINS = [
    'http://localhost:8888',
    'http://127.0.0.1:8888',
    'http://localhost:8000',
    'http://127.0.0.1:8000',
    'https://bloodlike-filiberto-collaboratively.ngrok-free.dev',
]


# Logging Configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'django.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
        'conversations': {
            'handlers': ['file', 'console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}


# Custom Settings for Khalifa Pharmacy System

# Auto-Assignment Settings
AUTO_ASSIGNMENT_ALGORITHM = 'least_loaded'  # حسب الإجابة س6

# Delay Settings
DELAY_THRESHOLD_MINUTES = 3  # حسب الإجابة س11

# KPI Calculation
KPI_UPDATE_MODE = 'realtime'  # حسب الإجابة س2

# Phone Number Settings
DEFAULT_COUNTRY_CODE = '20'  # Egypt

# Agent Settings
DEFAULT_MAX_CONCURRENT_TICKETS = 15  # حسب الإجابة س9


# Django REST Framework Settings
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_FILTER_BACKENDS': [
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],
    'DATETIME_FORMAT': '%Y-%m-%d %H:%M:%S',
    'DATE_FORMAT': '%Y-%m-%d',
    'TIME_FORMAT': '%H:%M:%S',
    'EXCEPTION_HANDLER': 'rest_framework.views.exception_handler',
}

# Throttling (Rate Limiting)
if DEBUG:
    REST_FRAMEWORK.update({
        'DEFAULT_THROTTLE_CLASSES': [],
        'DEFAULT_THROTTLE_RATES': {},
    })
else:
    REST_FRAMEWORK.update({
        'DEFAULT_THROTTLE_CLASSES': [
            'rest_framework.throttling.AnonRateThrottle',
            'rest_framework.throttling.UserRateThrottle',
        ],
        'DEFAULT_THROTTLE_RATES': {
            'anon': '1000/hour',
            'user': '10000/hour',
        },
    })


# ============================================================================
# WhatsApp Integration Settings
# ============================================================================

# WhatsApp Driver: 'wppconnect' أو 'cloud_api' أو 'elmujib_cloud'
WHATSAPP_DRIVER = 'elmujib_cloud'

# WPPConnect Settings
WPPCONNECT_PORT = os.getenv('WPPCONNECT_PORT', '3000')
WPPCONNECT_HOST = os.getenv('WPPCONNECT_HOST', 'localhost')
WPPCONNECT_BASE_URL = f'http://{WPPCONNECT_HOST}:{WPPCONNECT_PORT}'
WPPCONNECT_API_KEY = os.getenv('WHATSAPP_API_KEY', 'khalifa-pharmacy-secret-key-2025')
WPPCONNECT_TIMEOUT = 30

# WhatsApp Cloud API Settings (للمرحلة 2 - الجزء الثاني)
WHATSAPP_CLOUD_ACCESS_TOKEN = os.getenv('WHATSAPP_CLOUD_ACCESS_TOKEN', '')
WHATSAPP_CLOUD_PHONE_NUMBER_ID = os.getenv('WHATSAPP_CLOUD_PHONE_NUMBER_ID', '')
WHATSAPP_CLOUD_BUSINESS_ACCOUNT_ID = os.getenv('WHATSAPP_CLOUD_BUSINESS_ACCOUNT_ID', '')
WHATSAPP_CLOUD_WEBHOOK_VERIFY_TOKEN = os.getenv('WHATSAPP_CLOUD_WEBHOOK_VERIFY_TOKEN', '')

# Elmujib Cloud Business API Settings
ELMUJIB_API_BASE_URL = os.getenv('ELMUJIB_API_BASE_URL', 'https://elmujib.com/api')
ELMUJIB_VENDOR_UID = os.getenv('ELMUJIB_VENDOR_UID', '')
ELMUJIB_BEARER_TOKEN = os.getenv('ELMUJIB_BEARER_TOKEN', '')
ELMUJIB_FROM_PHONE_NUMBER_ID = os.getenv('ELMUJIB_FROM_PHONE_NUMBER_ID', '')
ELMUJIB_AUTH_METHOD = os.getenv('ELMUJIB_AUTH_METHOD', 'header')
ELMUJIB_TIMEOUT = 30

# WhatsApp Media Domain - للوصول إلى الصور المرفوعة من الخارج
# استخدم رابط IP أو domain عام عند النشر على الإنترنت
WHATSAPP_MEDIA_DOMAIN = os.getenv('WHATSAPP_MEDIA_DOMAIN', 'http://localhost:8888')

# WPPConnect Configuration
WHATSAPP_CONFIG = {
    'base_url': f"http://{os.getenv('WPPCONNECT_HOST', 'localhost')}:{os.getenv('WPPCONNECT_PORT', '3000')}",
    'api_key': os.getenv('WHATSAPP_API_KEY', 'khalifa-pharmacy-secret-key-2025'),
    'timeout': 30,
    'session_name': os.getenv('WPPCONNECT_SESSION_NAME', 'khalifa-pharmacy')
}
