import os,sys
sys.path.append("/home/www/django")
os.environ['DJANGO_SETTINGS_MODULE'] = 'stjornbord.settings'

from stjornbord.user.models import UserProfile, UserStatus, WCLOSURE_USER, INACTIVE_USER
import datetime

users = UserProfile.objects.filter(status=WCLOSURE_USER, deactivate__lte=datetime.date.today())

for user in users:
    print "Hendi notanda %s" % (user.username, )
    user.status_id = INACTIVE_USER
    user.save()
