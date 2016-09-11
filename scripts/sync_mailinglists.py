"""
This script synchronizes mailinglists stored at Google.
"""

import os
import re
import sys
import logging
os.environ['DJANGO_SETTINGS_MODULE'] = 'stjornbord.settings'

from stjornbord.ou.models import OrganizationalUnit
from stjornbord.student.models import Klass
from stjornbord.utils import create_google_api

log = logging.getLogger("stjornbord.cron")
log.info("Running %s", sys.argv[0])

google = create_google_api()

####
# Fetch teachers and other staff
kennarar = OrganizationalUnit.objects.filter(group=1, status__active=1)
adrirstm = OrganizationalUnit.objects.filter(group=2, status__active=1)

kennarar_members = []
for k in kennarar:
    for userp in k.userp.filter(status=1).select_related(depth=1):
        kennarar_members.append("%s@mr.is" % userp.user.username)

starfsmenn_members = kennarar_members[:]
for s in adrirstm:
    for userp in s.userp.filter(status=1).select_related(depth=1):
        starfsmenn_members.append("%s@mr.is" % userp.user.username)

google.list_sync("kennarar", kennarar_members)
google.list_sync("starfsmenn", starfsmenn_members)

####
# Sync class mailinglists
r_username = re.compile(r"([3-6]|iv|v|vi)([a-z]|usk)$")
klasses = Klass.objects.all()
for klass in klasses:
    username = klass.name.lower().replace(".", "")
    members = []

    if not username or not r_username.match(username):
        log.error("Whoops! This class doesn't have a valid username!, klass=%s", klass)
        continue

    for student in klass.students.filter(status=1):  # not status__active as we don't want
        for userp in student.userp.filter(status=1).select_related(depth=1):  # student on leave
            members.append("%s@mr.is" % userp.user.username)

    google.list_sync(username, members)
