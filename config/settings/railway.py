"""
Railway deployment settings.
"""

from .base import *
import dj_database_url

# Основные настройки
DEBUG = False
ALLOWED_HOSTS = [
    '.up.railway.app',
    '.railway.app',
    'localhost',
    '127.0.0.1',
]

# База данных (Railway автоматически предоставляет DATABASE_URL)
DATABASES = {
    'default': dj_database_url.parse(os.environ.get('DATABASE_URL'))
}

# Статические файлы
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

# Media файлы (для Railway лучше использовать внешнее хранилище)
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Логирование - СИЛЬНО УПРОЩЕННОЕ для Railway
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'level': 'ERROR',  # Только ошибки
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'formatters': {
        'simple': {
            'format': '{levelname}: {message}',
            'style': '{',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'ERROR',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': False,
        },
        # Отключаем логи миграций и статики
        'django.db.backends': {
            'handlers': [],
            'level': 'ERROR',
            'propagate': False,
        },
        'django.contrib.staticfiles': {
            'handlers': [],
            'level': 'ERROR',
            'propagate': False,
        },
    },
}

# Security настройки
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = True
USE_TLS = True

# CORS для Railway
CORS_ALLOWED_ORIGINS = [
    f"https://{os.environ.get('RAILWAY_PUBLIC_DOMAIN', 'your-app.up.railway.app')}",
]

CORS_ALLOW_CREDENTIALS = True

# CSRF для Railway
CSRF_TRUSTED_ORIGINS = [
    f"https://{os.environ.get('RAILWAY_PUBLIC_DOMAIN', 'your-app.up.railway.app')}",
]

# Cache (простой in-memory для Railway)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}

# Email (консольный бэкенд для тестов)  
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Добавьте в requirements.txt:
# dj-database-url==2.1.0

# Сессии в БД
SESSION_ENGINE = 'django.contrib.sessions.backends.db'

# Отключаем debug toolbar и ненужные приложения
INSTALLED_APPS = [app for app in INSTALLED_APPS if 'debug_toolbar' not in app]
MIDDLEWARE = [mw for mw in MIDDLEWARE if 'debug_toolbar' not in mw]