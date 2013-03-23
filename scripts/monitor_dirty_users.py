#coding: utf-8
"""
This script alerts on dirty users (users with pending updates).
"""

import os
import sys
import time
import logging

os.environ['DJANGO_SETTINGS_MODULE'] = 'stjornbord.settings'
from stjornbord.user.models import UserProfile

ALERT_AFTER_MIN = 60

log = logging.getLogger("stjornbord.cron")
log.info("Running %s", sys.argv[0])


# Check for dirty users:
now = time.time()
dirty_total = 0
dirty_alarm = 0
for userp in UserProfile.objects.filter(dirty__gt=0).select_related(depth=1):
    dirty_delta = now - userp.dirty

    dirty_total += 1
    if dirty_delta > (ALERT_AFTER_MIN * 60):
        dirty_alarm += 1

log.info("Dirty scan complete, total=%s, in alarm=%s")

if dirty_alarm:
    log.error(u"""\
Alls bíða %d notendur eftir uppfærslu, þar af hafa %d beðið
í yfir %d mínútur.

Líklega er uppfærsluþjónninn á eftir áætlun, hugsanlega liggur
hann hreinlega niðri.

Hvernig er þetta leyst?
 1) Tengja sig inn á auth
 2) Skoða logga í /var/log/stjornbord
 3) Kanna hvort uppfærsluþjónninn sé í gangi eða hvort hann sé bara
    að vinna sig í gegnum slatta af dóti - nú eða hvort þetta sé
    eitthvað annað.

Kveðja,
Stjórnborðið
""" % (dirty_total, dirty_alarm, ALERT_AFTER_MIN))
