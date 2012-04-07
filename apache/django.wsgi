import os, sys
sys.path.append('/var/opinn/www')
sys.path.append('/var/opinn/www/lib')
os.environ['DJANGO_SETTINGS_MODULE'] = 'stjornbord.settings'
import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
