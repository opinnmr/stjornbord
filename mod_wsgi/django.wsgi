import os
import sys
import site

# Add the virtual-env site packages (this borrows from virtualenv's activate_this.py)
base = os.path.normpath(os.path.join(os.path.abspath(__file__), "../../../"))
site_packages = os.path.join(base, 'lib', 'python%s' % sys.version[:3], 'site-packages')
site.addsitedir(site_packages)

# Add our project to path
sys.path.append(base)

os.environ['DJANGO_SETTINGS_MODULE'] = 'stjornbord.settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
