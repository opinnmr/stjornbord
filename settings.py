import os

ADMINS      = (("bjorn swift", "bjorn@swift.is"),)
MANAGERS    = (("opinn mr", "opinn@mr.is"),)

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
    'django_requestlogging.middleware.LogSetupMiddleware',
)

PASSWORD_HASHERS = (
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
    'django.contrib.auth.hashers.BCryptPasswordHasher',
    'stjornbord.user.auth.SaltlessSHA1PasswordHasher',
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
    'stjornbord.register',
    'stjornbord.devices',
    'stjornbord.saml2idp',
    'stjornbord.infoscreen',
    'django_requestlogging',
)

# Add more logging
# UPGRADE: When moving to Django 1.5, set disable_existing_loggers to False
#          and remove the defaults, as they will be merged in by Django.
#          For now, we have a full copy from global_settings.py
#          See https://docs.djangoproject.com/en/dev/topics/logging/#configuring-logging

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'filters': {
        'request': {
            '()': 'django_requestlogging.logging_filters.RequestFilter',
        },
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
    },
    # Project specific
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(remote_addr)s %(username)s %(asctime)s; %(message)s; pid:%(process)d tid:%(thread)d p:%(pathname)s:%(lineno)s',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
        'cron': {
            'format': '%(levelname)s %(asctime)s; %(message)s; pid:%(process)d tid:%(thread)d p:%(pathname)s:%(lineno)s',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },

        # Project specific
        'console': {
            'level':'DEBUG',
            'class':'logging.StreamHandler',
            'formatter': 'verbose',
            'filters': ['request', ],
        },
        'file_handler': {
            'level':'INFO',
            'class':'logging.handlers.TimedRotatingFileHandler',
            'filename': os.path.join(LOGGING_ROOT, 'stjornbord.log'),
            'when': 'w0', # weekly
            'formatter': 'verbose',
            'filters': ['request', ],
        },
        'cron_handler': {
            'level':'INFO',
            'class':'logging.handlers.TimedRotatingFileHandler',
            'filename': os.path.join(LOGGING_ROOT, 'stjornbord-cron.log'),
            'when': 'w0', # weekly
            'formatter': 'cron',
        },
        'auth_log_handler': {
            'level':'INFO',
            'class':'logging.handlers.TimedRotatingFileHandler',
            'filename': os.path.join(LOGGING_ROOT, 'stjornbord-saml-auth.log'),
            'when': 'w0', # weekly
            'formatter': 'verbose',
            'filters': ['request', ],
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },

        # Project specific
        'stjornbord': {
            'handlers': ['mail_admins', 'file_handler', ],
            'propagate': False,
            'level': 'INFO',

        },
        'stjornbord.saml': {
            'handlers': ['mail_admins', 'auth_log_handler', ],
            'propagate': False,
            'level': 'INFO',
        },

        'stjornbord.cron': {
            'handlers': ['mail_admins', 'cron_handler'],
            'propagate': False,
            'level': 'INFO',
        },
    }
}


AUTH_PROFILE_MODULE = "user.UserProfile"

LOGIN_URL = '/login/'
LOGOUT_URL = '/logout/'
LOGIN_REDIRECT_URL = '/'

DOMAIN = "mr.is"
SERVER_EMAIL="admin@mr.is"

LAN_DOMAIN = "mr.lan"
MRNET_IP = "82.148.70.66"

AUTHENTICATION_BACKENDS = ('stjornbord.user.backend.StjornbordBackend',)
