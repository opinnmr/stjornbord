import os, platform

DEVELOPMENT_MODE = ("athena" not in platform.node())

ADMINS      = (("bjorn swift", "bjorn@mr.is"),)
MANAGERS    = ADMINS

if DEVELOPMENT_MODE:
    from settings_dev import *
    DEBUG           = True
    TEMPLATE_DEBUG  = True
    UPDATE_GOOGLE   = False
else:
    from settings_prod import *
    DEBUG               = False
    TEMPLATE_DEBUG      = False
    UPDATE_GOOGLE       = True


# Template and media directories populated automatically
# from current dir. Makes this work on development
# machines as well as staging server
TEMPLATE_DIRS       = [os.path.join(os.path.dirname(__file__), "templates")]
MEDIA_ROOT          = os.path.join(os.path.dirname(__file__), "media")

ADMIN_MEDIA_PREFIX  = '/admin_media/'
MEDIA_URL           = '/media/'

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
    'django.core.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.media',
    'django.core.context_processors.request',
)

# Overriding MIDDLEWARE since we want transactions
MIDDLEWARE_CLASSES = (
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.csrf.CsrfResponseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.transaction.TransactionMiddleware',
)

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
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

SAML2IDP_PRIVATE_KEY_FILE = os.path.join(os.path.dirname(__file__), "ssokeys", "rsaprivkey.pem")
SAML2IDP_CERTIFICATE_FILE = os.path.join(os.path.dirname(__file__), "ssokeys", "rsacert.pem")

