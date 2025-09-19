"""
Railway deployment settings.
"""

from .base import *
import os

# Основные настройки
DEBUG = False
ALLOWED_HOSTS = [
    '.up.railway.app',
    '.railway.app',
    'localhost',
    '127.0.0.1',
]

# База данных для Railway - определяем правильный хост автоматически
DATABASE_URL = os.environ.get('DATABASE_PRIVATE_URL') or os.environ.get('DATABASE_URL')

# Определяем хост для PostgreSQL в Railway
def get_postgres_host():
    """Определяет правильный хост для PostgreSQL в Railway"""
    # Проверяем есть ли приватный домен
    private_host = os.environ.get('RAILWAY_PRIVATE_DOMAIN')
    if private_host:
        return private_host
    
    # Проверяем стандартные имена сервисов Railway
    possible_hosts = ['postgres', 'postgresql', 'database']
    for host in possible_hosts:
        if os.environ.get(f'{host.upper()}_HOST'):
            return os.environ.get(f'{host.upper()}_HOST')
    
    # Если ничего не найдено, пытаемся извлечь из PGHOST
    pghost = os.environ.get('PGHOST', '')
    if pghost and pghost not in ['localhost', '127.0.0.1']:
        return pghost
    
    # Последний шанс - стандартное имя сервиса
    return 'postgres'

postgres_host = get_postgres_host()

if DATABASE_URL and DATABASE_URL.strip() and 'postgresql://' in DATABASE_URL:
    try:
        import dj_database_url
        DATABASES = {
            'default': dj_database_url.parse(DATABASE_URL)
        }
        print(f"Используем DATABASE_URL с хостом: {DATABASES['default']['HOST']}")
    except (ValueError, ImportError) as e:
        print(f"Error parsing DATABASE_URL: {e}")
        # Fallback к отдельным переменным
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.postgresql',
                'NAME': os.environ.get('PGDATABASE', 'railway'),
                'USER': os.environ.get('PGUSER', 'postgres'),
                'PASSWORD': os.environ.get('PGPASSWORD', ''),
                'HOST': postgres_host,
                'PORT': os.environ.get('PGPORT', '5432'),
            }
        }
else:
    # Используем отдельные переменные PostgreSQL
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.environ.get('PGDATABASE', 'railway'),
            'USER': os.environ.get('PGUSER', 'postgres'),  
            'PASSWORD': os.environ.get('PGPASSWORD', ''),
            'HOST': postgres_host,
            'PORT': os.environ.get('PGPORT', '5432'),
        }
    }

print(f"Django подключается к БД на хосте: {DATABASES['default']['HOST']}")
print(f"База данных: {DATABASES['default']['NAME']}")
print(f"Пользователь: {DATABASES['default']['USER']}")

# Статические файлы
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Media файлы
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Добавляем WhiteNoise в middleware если его нет
if 'whitenoise.middleware.WhiteNoiseMiddleware' not in MIDDLEWARE:
    # Вставляем после SecurityMiddleware
    security_index = MIDDLEWARE.index('django.middleware.security.SecurityMiddleware')
    MIDDLEWARE.insert(security_index + 1, 'whitenoise.middleware.WhiteNoiseMiddleware')

# Логирование - минимальное для Railway
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'handlers': {
        'console': {
            'level': 'ERROR',
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
        'django.db.backends': {
            'handlers': [],
            'level': 'CRITICAL',
            'propagate': False,
        },
        'django.contrib.staticfiles': {
            'handlers': [],
            'level': 'CRITICAL',
            'propagate': False,
        },
        'PIL': {
            'handlers': [],
            'level': 'CRITICAL',
            'propagate': False,
        },
    },
}

# Security настройки
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = True

# CORS для Railway
CORS_ALLOWED_ORIGINS = [
    f"https://{os.environ.get('RAILWAY_PUBLIC_DOMAIN', 'localhost')}",
]
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_ALL_ORIGINS = False

# CSRF для Railway  
CSRF_TRUSTED_ORIGINS = [
    f"https://{os.environ.get('RAILWAY_PUBLIC_DOMAIN', 'localhost')}",
]

# Cache простой
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'railway-cache',
    }
}

# Email
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Сессии в БД
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# Убираем ненужные приложения
INSTALLED_APPS = [app for app in INSTALLED_APPS if 'debug_toolbar' not in app.lower()]

# Отключаем автоперезагрузку в продакшене
if 'django.utils.autoreload' in INSTALLED_APPS:
    INSTALLED_APPS.remove('django.utils.autoreload')