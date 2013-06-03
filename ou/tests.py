#coding: utf8
from django.contrib.auth.models import User
from stjornbord.user.tests import StjornbordTestCase

class OUTestCase(StjornbordTestCase):
    def testConstants(self):
        """
        Double check that the constants used for testing make sense.
        """
        self.assertEqual(self.OU_STATUS_ACTIVE.active, True)
        self.assertEqual(self.OU_STATUS_INACTIVE.active, False)


    def testDelete(self):
        with self.assertRaises(Exception):
            self.OU_1.delete()


    def testAddUser(self):
        self.assertEqual(self.OU_1.userp.count(), 0)

        self._create_user(self.USERNAME_1, self.OU_1)
        self.assertEqual(self.OU_1.userp.count(), 1)

        self._create_user(self.USERNAME_2, self.OU_1)
        self._create_user(self.USERNAME_3, self.OU_1)
        self.assertEqual(self.OU_1.userp.count(), 3)

    def _create_users(self, ou, description):
        for username, status in description:
            self._create_user(username, ou, status)

    def _verify_user_state(self, description):
        for username, status in description:
            user = User.objects.get(username=username)
            self.assertEqual(user.get_profile().status, status)

    def testDeactivateOu(self):
        before = (
            (self.USERNAME_1, self.USTATUS_ACTIVE),
            (self.USERNAME_2, self.USTATUS_WCLOSURE),
            (self.USERNAME_3, self.USTATUS_INACTIVE),
            (self.USERNAME_4, self.USTATUS_DELETED),
            )

        after = (
            (self.USERNAME_1, self.USTATUS_WCLOSURE),
            (self.USERNAME_2, self.USTATUS_WCLOSURE),
            (self.USERNAME_3, self.USTATUS_INACTIVE),
            (self.USERNAME_4, self.USTATUS_DELETED),
            )

        # Create four users, one for each user status
        self._create_users(self.OU_1, before)
        self._verify_user_state(before)

        # Deactivate OU
        self.OU_1.status = self.OU_STATUS_INACTIVE
        self.OU_1.save()

        # Verify state after OU closure
        self._verify_user_state(after)


    def testActivateOu(self):
        before = (
            (self.USERNAME_1, self.USTATUS_ACTIVE),
            (self.USERNAME_2, self.USTATUS_WCLOSURE),
            (self.USERNAME_3, self.USTATUS_INACTIVE),
            (self.USERNAME_4, self.USTATUS_DELETED),
            )

        after = (
            (self.USERNAME_1, self.USTATUS_ACTIVE),
            (self.USERNAME_2, self.USTATUS_ACTIVE),
            (self.USERNAME_3, self.USTATUS_INACTIVE),
            (self.USERNAME_4, self.USTATUS_DELETED),
            )

        # Deactivate OU
        self.OU_1.status = self.OU_STATUS_INACTIVE
        self.OU_1.save()

        # Create four users, one for each user status
        self._create_users(self.OU_1, before)
        self._verify_user_state(before)

        # Activate OU
        self.OU_1.status = self.OU_STATUS_ACTIVE
        self.OU_1.save()


        # Verify state after OU closure
        self._verify_user_state(after)
