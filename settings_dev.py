import os

# Development settings
DEBUG           = True
TEMPLATE_DEBUG  = True

# Database settings
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'stjornbord.sdb',
    }
}

# python -m smtpd -n -c DebuggingServer localhost:1025
EMAIL_HOST      = "127.0.0.1"
EMAIL_PORT      = "1025"

# Django secret key
SECRET_KEY = 'devsecretkey123'

# Secret key used for IPA/LDAP/Kerberos user and device synchronization
SYNC_SECRET = "devsecret123"

# Google API username/pass 
UPDATE_GOOGLE   = False
GOOGLE_TMP_DIR = "/tmp/"
GOOGLE_TOKEN   = "/tmp/tokens.dat"
GOOGLE_SECRETS = os.path.join(os.path.dirname(__file__), "ssokeys", "client_secrets.json")

# Google Single Sign On
GOOGLE_SSO_ENABLE = False
SAML2IDP_PRIVATE_KEY_FILE = os.path.join(os.path.dirname(__file__), "ssokeys", "rsaprivkey.pem")
SAML2IDP_CERTIFICATE_FILE = os.path.join(os.path.dirname(__file__), "ssokeys", "rsacert.pem")

# Logging root
LOGGING_ROOT = "/tmp/"

# Temorary directory for Inna student files
INNA_ROOT = "/tmp/stjornbord/inna/"
