"""
This script iterates through users awating closure or
deletion and updates status accordingly.
"""

import os
import sys
os.environ['DJANGO_SETTINGS_MODULE'] = 'stjornbord.settings'
import datetime
import logging

from stjornbord.user.models import UserProfile, send_deactivate_email, WCLOSURE_USER, INACTIVE_USER

DISABLE_WARN_DAYS = [30, 7, 1, ]

log = logging.getLogger("stjornbord.cron")
log.info("Running %s", sys.argv[0])

# First, let's warn users that are awating closure. We don't track
# which users we've sent messages, so this script isn't run on some
# particular day, then the user won't get a message.
today = datetime.date.today()
for disable_after in DISABLE_WARN_DAYS:
    disable_date = today + datetime.timedelta(days=disable_after)

    for userp in UserProfile.objects.filter(status=WCLOSURE_USER, deactivate=disable_date).select_related(depth=1):
        log.info("Sending %d day closure reminder to %s", disable_after, userp)
        send_deactivate_email(userp.user.username,
            userp.content_object.get_fullname(),
            userp.deactivate,
            reminder=True)

# Now, let's find users that have passed their closure deadline.
for userp in UserProfile.objects.filter(status=WCLOSURE_USER, deactivate__lte=today).select_related(depth=1):
    log.info("Setting user status for %s to INACTIVE_USER", userp)
    userp.status_id = INACTIVE_USER
    userp.save()

# And finally, find users that should be deleted from the system
# and archived
for userp in UserProfile.objects.filter(status=INACTIVE_USER, purge__lte=today).select_related(depth=1):
    log.info("Setting user status for %s to DELETED_USER", userp)
    userp.status_id = DELETED_USER
    userp.save()