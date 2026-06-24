# PATH: Ztech/ztech/settings.py

import os
from pathlib import Path
from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY  = config('SECRET_KEY', default='dev-secret-key-change-in-production')
DEBUG = False

ALLOWED_HOSTS = ['ztech-opyu.onrender.com', 'localhost', '127.0.0.1']
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Third party
    'crispy_forms',
    'crispy_bootstrap5',
    # ZTech apps
    'core',
    'products',
    'accounts',
    'cart',
    'orders',
    'payments',
    'ai_builder',
    'gallery',
    'newsletter',
    'api',
    'dashboard',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'Ztech.urls'

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
                'core.context_processors.cart_context',
                'core.context_processors.theme_context',
                'dashboard.context_processors.dashboard_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'Ztech.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_USER_MODEL     = 'accounts.CustomUser'
LOGIN_URL           = '/accounts/login/'
LOGIN_REDIRECT_URL  = '/'
LOGOUT_REDIRECT_URL = '/'

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE     = 'Africa/Algiers'
USE_I18N      = True
USE_TZ        = True

STATIC_URL       = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT      = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL  = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# ── Email (Gmail SMTP) ──────────────────────────────────────────
# To activate: set EMAIL_HOST_USER and EMAIL_HOST_PASSWORD in your .env file.
# Gmail: enable 2FA → generate an App Password → paste it as EMAIL_HOST_PASSWORD.
EMAIL_BACKEND    = config('EMAIL_BACKEND', default='django.core.mail.backends.smtp.EmailBackend')
EMAIL_HOST       = config('EMAIL_HOST',    default='smtp.gmail.com')
EMAIL_PORT       = config('EMAIL_PORT',    default=587, cast=int)
EMAIL_USE_TLS    = True
EMAIL_HOST_USER  = config('EMAIL_HOST_USER',     default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL  = config('DEFAULT_FROM_EMAIL',  default='ZTech <noreply@ztech.dz>')

# Site URL used in emails
SITE_URL = config('SITE_URL', default='http://127.0.0.1:8000')

CRISPY_ALLOWED_TEMPLATE_PACKS = 'bootstrap5'
CRISPY_TEMPLATE_PACK          = 'bootstrap5'

STRIPE_PUBLIC_KEY     = config('STRIPE_PUBLIC_KEY', default='')
STRIPE_SECRET_KEY     = config('STRIPE_SECRET_KEY', default='')
STRIPE_WEBHOOK_SECRET = config('STRIPE_WEBHOOK_SECRET', default='')

ANTHROPIC_API_KEY = config('ANTHROPIC_API_KEY', default='')

# ZTech business rules
CART_DISCOUNT_THRESHOLD = 500000   # DZD — discount triggers at 500k
CART_DISCOUNT_RATE      = 0.10     # 10%

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'DEBUG',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}
INSTALLED_APPS += ['cloudinary', 'cloudinary_storage']

CLOUDINARY_STORAGE = {
    'CLOUD_NAME': os.environ.get('CLOUDINARY_CLOUD_NAME', 'dwlah6mw4'),
    'API_KEY': os.environ.get('CLOUDINARY_API_KEY', '844844414645432'),
    'API_SECRET': os.environ.get('CLOUDINARY_API_SECRET', 'PnhwIilles3YrxY-G80UruszUL8'),
}

DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'