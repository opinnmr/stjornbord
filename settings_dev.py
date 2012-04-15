# Database settings
DATABASE_ENGINE = 'sqlite3'
DATABASE_NAME   = 'stjornbord.sdb'
EMAIL_HOST      = "iris.mr.is"

# Django secret key
SECRET_KEY = 'devsecretkey123'

# Secret key used for IPA/LDAP/Kerberos user and device synchronization
SYNC_SECRET = "devsecret123"

# Google API username/pass 
GOOGLE_SSO_ENABLE = False
GOOGLE_API_USER = "dontsync@example.com"
GOGGLE_API_PASS = "dontsync"

GOOGLE_API_USER = "adminapi@mr.is"
GOGGLE_API_PASS = "19876d63ed26d89cf1ec0e4"
GOOGLE_TMP_DIR = "/tmp/stjornbord/google/"

# Temorary directory for Inna student files
INNA_ROOT = "tmp/stjornbord/inna/"
