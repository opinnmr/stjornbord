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

    def _assertDirty(self, username, expect_dirty):
        user = User.objects.get(username=username)
        if expect_dirty:
            self.assertGreater(user.get_profile().dirty, 0)
        else:
            self.assertEqual(user.get_profile().dirty, 0)

    def testUpdateMarksAllUsersAsDirty(self):
        users = (
            # username, user-status, should-be-marked-dirty
            (self.USERNAME_1, self.USTATUS_ACTIVE),
            (self.USERNAME_2, self.USTATUS_ACTIVE),
            (self.USERNAME_3, self.USTATUS_INACTIVE),
            )

        # Create a few users for this UO
        self._create_users(self.OU_1, users)

        # Clear the dirty bit on all of them
        for username, _ in users:
            user = User.objects.get(username=username)
            user.get_profile().clear_dirty(user.get_profile().dirty)

        # Validate that all users have been reset
        for username, _ in users:
            self._assertDirty(username, False)

        # Update the UO, expect all active users to be set dirty
        self.OU_1.save()
        self._assertDirty(self.USERNAME_1, True)
        self._assertDirty(self.USERNAME_2, True)
        self._assertDirty(self.USERNAME_3, False)
