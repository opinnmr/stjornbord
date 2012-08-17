import os

ADMINS      = (("bjorn swift", "bjorn@swift.is"),)
MANAGERS    = ADMINS

try:
    from settings_prod import *
except ImportError:
    from settings_dev import *


# Template and media directories populated automatically
# from current dir. Makes this work on development
# machines as well as staging server
TEMPLATE_DIRS       = [os.path.join(os.path.dirname(__file__), "templates")]

STATICFILES_DIRS = (os.path.join(os.path.dirname(__file__), "media"), )
STATIC_URL       = "/media/"

# Locale stuff. No official locale support (translations)
USE_I18N        = False
TIME_ZONE       = 'Atlantic/Reykjavik'
LANGUAGE_CODE   = 'en'
LANGUAGES       = (
    ('en', 'English'),
    )

# Site confing
SITE_ID         = 1
ROOT_URLCONF    = 'stjornbord.urls'


# Adding request preprocessor and removing i18n
TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.static',
    'django.core.context_processors.request',
    'django.contrib.messages.context_processors.messages',
)

# Overriding MIDDLEWARE since we want transactions
MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.transaction.TransactionMiddleware',
)

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'stjornbord.user',
    'stjornbord.ou',
    'stjornbord.student',
    'stjornbord.devices',
    'stjornbord.saml2idp',
    'stjornbord.infoscreen',
)

AUTH_PROFILE_MODULE = "user.UserProfile"

LOGIN_URL = '/login/'
LOGOUT_URL = '/logout/'
LOGIN_REDIRECT_URL = '/?'

DOMAIN = "mr.is"
SERVER_EMAIL="admin@mr.is"

LAN_DOMAIN = "mr.lan"
MRNET_IP = "82.148.70.66"

AUTHENTICATION_BACKENDS = ('stjornbord.user.backend.TrimDomainBackend',)
