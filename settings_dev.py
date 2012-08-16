# Development settings
DEBUG           = True
TEMPLATE_DEBUG  = True

# Database settings
DATABASE_ENGINE = 'sqlite3'
DATABASE_NAME   = 'stjornbord.sdb'
EMAIL_HOST      = "iris.mr.is"

# Django secret key
SECRET_KEY = 'devsecretkey123'

# Secret key used for IPA/LDAP/Kerberos user and device synchronization
SYNC_SECRET = "devsecret123"

# Google API username/pass 
UPDATE_GOOGLE   = False
GOOGLE_SSO_ENABLE = False
GOOGLE_API_USER = "dontsync@example.com"
GOOGLE_API_PASS = "dontsync"
GOOGLE_TMP_DIR = "/tmp/stjornbord/google/"

# Temorary directory for Inna student files
INNA_ROOT = "/tmp/stjornbord/inna/"
