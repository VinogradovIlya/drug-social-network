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

# Получаем данные базы данных с fallback значениями
DB_NAME = os.environ.get('PGDATABASE') or os.environ.get('DB_NAME', 'railway')
DB_USER = os.environ.get('PGUSER') or os.environ.get('DB_USER', 'postgres')
DB_PASSWORD = os.environ.get('PGPASSWORD') or os.environ.get('DB_PASSWORD', '')
DB_PORT = os.environ.get('PGPORT') or os.environ.get('DB_PORT', '5432')

print(f"=== DATABASE DEBUG ===")
print(f"DATABASE_URL exists: {DATABASE_URL is not None}")
if DATABASE_URL:
    print(f"DATABASE_URL length: {len(DATABASE_URL)}")
    # Безопасно показываем начало и конец URL
    if len(DATABASE_URL) > 20:
        print(f"DATABASE_URL preview: {DATABASE_URL[:20]}...{DATABASE_URL[-20:]}")
    else:
        print(f"DATABASE_URL: {DATABASE_URL}")
print(f"DB_NAME: '{DB_NAME}'")
print(f"DB_USER: '{DB_USER}'")
print(f"DB_HOST: '{postgres_host}'")
print(f"DB_PORT: '{DB_PORT}'")
print(f"===================")

if DATABASE_URL and DATABASE_URL.strip() and 'postgresql://' in DATABASE_URL:
    try:
        import dj_database_url
        parsed_db = dj_database_url.parse(DATABASE_URL)
        print(f"Parsed DATABASE_URL:")
        print(f"  ENGINE: {parsed_db.get('ENGINE', 'NOT SET')}")
        print(f"  NAME: '{parsed_db.get('NAME', 'NOT SET')}'")
        print(f"  USER: '{parsed_db.get('USER', 'NOT SET')}'")
        print(f"  HOST: '{parsed_db.get('HOST', 'NOT SET')}'")
        print(f"  PORT: '{parsed_db.get('PORT', 'NOT SET')}'")
        
        # Проверяем что все важные поля заполнены
        if parsed_db.get('NAME') and parsed_db.get('USER') and parsed_db.get('HOST'):
            DATABASES = {
                'default': parsed_db
            }
            print(f"✅ Используем DATABASE_URL")
        else:
            print(f"❌ DATABASE_URL неполный, используем fallback")
            raise ValueError("Incomplete DATABASE_URL")
            
    except (ValueError, ImportError) as e:
        print(f"Error parsing DATABASE_URL: {e}")
        # Fallback к отдельным переменным
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.postgresql',
                'NAME': DB_NAME,
                'USER': DB_USER,
                'PASSWORD': DB_PASSWORD,
                'HOST': postgres_host,
                'PORT': DB_PORT,
            }
        }
        print(f"✅ Используем отдельные переменные")
else:
    # Используем отдельные переменные PostgreSQL
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': DB_NAME,
            'USER': DB_USER,
            'PASSWORD': DB_PASSWORD,
            'HOST': postgres_host,
            'PORT': DB_PORT,
        }
    }

# Проверяем что у нас есть все необходимые данные
final_db_name = DATABASES['default'].get('NAME', '')
if not final_db_name or final_db_name.strip() == '':
    print(f"WARNING: Database NAME is empty after parsing!")
    print(f"Raw DATABASE_URL: {DATABASE_URL}")
    # Принудительно устанавливаем имя базы
    DATABASES['default']['NAME'] = DB_NAME or 'railway'
    print(f"Set database name to: {DATABASES['default']['NAME']}")

print(f"Django подключается к БД на хосте: {DATABASES['default']['HOST']}")
print(f"База данных: {DATABASES['default']['NAME']}")
print(f"Пользователь: {DATABASES['default']['USER']}")

# Статические файлы
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Убеждаемся что папка staticfiles существует
import os
os.makedirs(STATIC_ROOT, exist_ok=True)

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Media файлы
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Убеждаемся что папка media существует
os.makedirs(MEDIA_ROOT, exist_ok=True)

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