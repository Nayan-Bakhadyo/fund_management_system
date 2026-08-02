from .settings import *

DEBUG = False

ALLOWED_HOSTS = ['beinvestmentfirm.com', 'http://52.15.154.89/', 'www.beinvestmentfirm.com']

# Security settings
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# Static files
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')  # or any folder outside your app directories

# Media files (optional, if you use media)
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'



# Secret key from environment
SECRET_KEY = os.environ.get('SECRET_KEY')