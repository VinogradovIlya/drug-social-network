"""
WhiteNoise configuration for serving static files.
"""

# Добавьте 'whitenoise.middleware.WhiteNoiseMiddleware' после SecurityMiddleware

# Настройки для статических файлов с WhiteNoise
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Дополнительные настройки WhiteNoise
WHITENOISE_USE_FINDERS = True
WHITENOISE_AUTOREFRESH = True