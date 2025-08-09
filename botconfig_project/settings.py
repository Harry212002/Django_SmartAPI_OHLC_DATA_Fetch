import os
from pathlib import Path
from decouple import config  # ✅ add this

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config('SECRET_KEY', default='your-secret-key')  # ✅ from .env
DEBUG = config('DEBUG', default=True, cast=bool)
ALLOWED_HOSTS = []

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'config',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'botconfig_project.urls'

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

WSGI_APPLICATION = 'botconfig_project.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'trading_db',       # Database name
        'USER': 'postgres',            # Database username
        'PASSWORD': 'root',        # Database password
        'HOST': 'localhost',                 # Or your DB server IP
        'PORT': '5432',                       # Default PostgreSQL port
    }
}



LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ✅ ANGEL SMARTAPI CONFIGS
# SMARTAPI_API_KEY = config("SMARTAPI_API_KEY")
# SMARTAPI_CLIENT_ID = config("SMARTAPI_CLIENT_ID")
# SMARTAPI_PASSWORD = config("SMARTAPI_PASSWORD")
# SMARTAPI_TOTP = config("SMARTAPI_TOTP")
SMARTAPI_API_KEY = config("SMARTAPI_API_KEY")
SMARTAPI_CLIENT_ID = config("SMARTAPI_CLIENT_ID")
SMARTAPI_USERNAME = config("SMARTAPI_USERNAME")
SMARTAPI_PASSWORD = config("SMARTAPI_PASSWORD")
SMARTAPI_TOTP_SECRET = config("SMARTAPI_TOTP_SECRET")