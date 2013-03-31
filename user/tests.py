#coding: utf8
import datetime

import django.test
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.forms import ValidationError

from stjornbord.user import models as m
from stjornbord.ou.models import (OrganizationalUnit, Status as OuStatus, Group as OuGroup)

class UserStatusTest(django.test.TestCase):
    def testParserValid(self):
        """
        This is a legacy hack. The UserStatus model should at some point be
        changed to an enum/choices.
        """
        self.assertEqual(m.UserStatus.objects.get(pk=m.ACTIVE_USER).name,   u"Virkur")
        self.assertEqual(m.UserStatus.objects.get(pk=m.WCLOSURE_USER).name, u"Bíður lokunar")
        self.assertEqual(m.UserStatus.objects.get(pk=m.INACTIVE_USER).name, u"Óvirkur")
        self.assertEqual(m.UserStatus.objects.get(pk=m.DELETED_USER).name,  u"Fjarlægður")


# TODO: See whether it makes sense to have a parent test case, and then
# figure out where it should be stored.
class StjornbordTestCase(django.test.TestCase):
    def setUp(self):
        super(StjornbordTestCase, self).setUp()
        # user/sql/posixuidpool.sql
        m.PosixUidPool.objects.create(user_type=ContentType.objects.get_for_model(OrganizationalUnit), next_uid=500000)

        self.OU_STATUS_ACTIVE   = OuStatus.objects.get(pk=1)
        self.OU_STATUS_INACTIVE = OuStatus.objects.get(pk=2)
        self.OU_GROUP_1         = OuGroup.objects.get(pk=1)
        self.OU_1 = OrganizationalUnit.objects.create(kennitala=1, first_name="John",
                last_name="Doe", status=self.OU_STATUS_ACTIVE, group=self.OU_GROUP_1)

        self.USTATUS_ACTIVE   = m.UserStatus.objects.get(pk=m.ACTIVE_USER)
        self.USTATUS_WCLOSURE = m.UserStatus.objects.get(pk=m.WCLOSURE_USER)
        self.USTATUS_INACTIVE = m.UserStatus.objects.get(pk=m.INACTIVE_USER)
        self.USTATUS_DELETED  = m.UserStatus.objects.get(pk=m.DELETED_USER)

        self.USERNAME_1 = "some-username-a"
        self.USERNAME_2 = "some-username-b"
        self.USERNAME_3 = "some-username-c"
        self.USERNAME_4 = "some-username-d"


    def _create_user(self, username, content_object, status=None):
        user = User.objects.create_user(username)
        userp = m.UserProfile(
                user      = user,
                kennitala = content_object.kennitala,
                user_type = ContentType.objects.get_for_model(content_object),
                status    = status if status else self.USTATUS_ACTIVE,
            )
        userp.save()
        return user


    def _transition_user(self, user, from_state, to_state):
        userp = user.get_profile()
        self.assertEqual(userp.status, from_state)

        # Transition
        userp.status = to_state
        userp.save()

        # Re-fetch and return
        userp = user.get_profile()
        return userp




class UserTest(StjornbordTestCase):
    def testCreateUserProfile(self):
        self._create_user(self.USERNAME_1, self.OU_1)
        self.assertEqual(User.objects.get(username=self.USERNAME_1).username, self.USERNAME_1)


    def testReservedUsername(self):
        reserved_username = m.ReserverdUsername.objects.all()[0].username

        with self.assertRaises(ValidationError):
            self._create_user(reserved_username, self.OU_1)


    def testDirtyBit(self):
        user = self._create_user(self.USERNAME_1, self.OU_1)
        userp = user.get_profile()
        self.assertNotEqual(0, userp.dirty)
        userp.clear_dirty(userp.dirty)

        # Re-read from db
        userp = User.objects.get(username=self.USERNAME_1).get_profile()
        self.assertEqual(0, userp.dirty)

        # Should be set dirtu when saved
        userp.save()
        userp = User.objects.get(username=self.USERNAME_1).get_profile()
        self.assertNotEqual(0, userp.dirty)


    def testUidIncreasingPool(self):
        # Create users
        users = []
        for i in range(5):
            users.append(self._create_user("%s-%d" % (self.USERNAME_1, i), self.OU_1))

        # Make sure uid's are strictly increasing
        last_uid = users[0].get_profile().posix_uid
        for user in users[1:]:
            uid = user.get_profile().posix_uid
            self.assertEqual(last_uid, uid - 1)
            last_uid = uid


    def _assertActive(self, userp):
        self.assertEqual(userp.status, self.USTATUS_ACTIVE)
        self.assertEqual(userp.deactivate, None)
        self.assertEqual(userp.purge, None)

    def _assertWClosure(self, userp):
        self.assertEqual(userp.status, self.USTATUS_WCLOSURE)
        self.assertEqual(userp.deactivate, datetime.date.today() + datetime.timedelta(m.DEACTIVATE_GRACE_PERIOD))
        self.assertEqual(userp.purge, None)

    def _assertInactive(self, userp):
        self.assertEqual(userp.status, self.USTATUS_INACTIVE)
        self.assertEqual(userp.deactivate, None)
        self.assertEqual(userp.purge, datetime.date.today() + datetime.timedelta(m.DELETE_GRACE_PERIOD))

    def _assertDeleted(self, userp):
        self.assertEqual(userp.status, self.USTATUS_DELETED)
        self.assertEqual(userp.deactivate, None)
        self.assertEqual(userp.deactivate, None)


    # State transitions, from ACTIVE

    def testFromActiveToWClosure(self):
        user  = self._create_user(self.USERNAME_1, self.OU_1)
        userp = self._transition_user(user, self.USTATUS_ACTIVE, self.USTATUS_WCLOSURE)

        self._assertWClosure(userp)


    def testFromActiveToInactive(self):
        user  = self._create_user(self.USERNAME_1, self.OU_1)
        userp = self._transition_user(user, self.USTATUS_ACTIVE, self.USTATUS_INACTIVE)

        self._assertInactive(userp)


    def testFromActiveToDeleted(self):
        user  = self._create_user(self.USERNAME_1, self.OU_1)

        with self.assertRaises(m.InvalidUserProfileStateChangeException):
            userp = self._transition_user(user, self.USTATUS_ACTIVE, self.USTATUS_DELETED)


    # State transitions, from WCLOSURE

    def testFromWClosureToActive(self):
        user  = self._create_user(self.USERNAME_1, self.OU_1, self.USTATUS_WCLOSURE)
        userp = self._transition_user(user, self.USTATUS_WCLOSURE, self.USTATUS_ACTIVE)

        self._assertActive(userp)


    def testFromWClosureToInactive(self):
        user  = self._create_user(self.USERNAME_1, self.OU_1, self.USTATUS_WCLOSURE)
        userp = self._transition_user(user, self.USTATUS_WCLOSURE, self.USTATUS_INACTIVE)

        self._assertInactive(userp)


    def testFromWClosureToDeleted(self):
        user  = self._create_user(self.USERNAME_1, self.OU_1, self.USTATUS_WCLOSURE)

        with self.assertRaises(m.InvalidUserProfileStateChangeException):
            userp = self._transition_user(user, self.USTATUS_WCLOSURE, self.USTATUS_DELETED)


    # State transitions, from INACTIVE

    def testFromInactiveToActive(self):
        user  = self._create_user(self.USERNAME_1, self.OU_1, self.USTATUS_INACTIVE)
        userp = self._transition_user(user, self.USTATUS_INACTIVE, self.USTATUS_ACTIVE)

        self._assertActive(userp)


    def testFromInactiveToWClosure(self):
        user  = self._create_user(self.USERNAME_1, self.OU_1, self.USTATUS_INACTIVE)

        with self.assertRaises(m.InvalidUserProfileStateChangeException):
            userp = self._transition_user(user, self.USTATUS_INACTIVE, self.USTATUS_WCLOSURE)


    def testFromInactiveToDeleted(self):
        user  = self._create_user(self.USERNAME_1, self.OU_1, self.USTATUS_INACTIVE)
        userp = self._transition_user(user, self.USTATUS_INACTIVE, self.USTATUS_DELETED)

        self._assertDeleted(userp)


    # State transitions, from DELETED

    def testFromDeletedToActive(self):
        user  = self._create_user(self.USERNAME_1, self.OU_1, self.USTATUS_DELETED)
        userp = self._transition_user(user, self.USTATUS_DELETED, self.USTATUS_ACTIVE)

        self._assertActive(userp)

    def testFromDeletedToWClosure(self):
        user  = self._create_user(self.USERNAME_1, self.OU_1, self.USTATUS_DELETED)

        with self.assertRaises(m.InvalidUserProfileStateChangeException):
            userp = self._transition_user(user, self.USTATUS_DELETED, self.USTATUS_WCLOSURE)

    def testFromDeletedToInactive(self):
        user  = self._create_user(self.USERNAME_1, self.OU_1, self.USTATUS_DELETED)

        with self.assertRaises(m.InvalidUserProfileStateChangeException):
            userp = self._transition_user(user, self.USTATUS_DELETED, self.USTATUS_INACTIVE)
