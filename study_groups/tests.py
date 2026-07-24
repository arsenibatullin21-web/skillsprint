from django.contrib.auth import get_user_model
from django.test import TestCase

from study_groups.models import StudyGroup, GroupMembership
from study_groups.services import join_group, leave_group, accept_membership, reject_membership, make_moderator, \
    transfer_ownership, remove_member


class StudyGroupTestServices(TestCase):
    def setUp(self):
        self.owner_user = get_user_model().objects.create_user(
            username='owner123',
            email='owner123@mail.ru',
            password='test123'
        )
        self.user = get_user_model().objects.create_user(
            username='user123',
            email='user123@mail.com',
            password='test123'
        )
        self.members_user2 = get_user_model().objects.create_user(
            username='member123',
            email='member123@mail.com',
            password='test123'
        )
        self.moderator_user = get_user_model().objects.create_user(
            username='moder123',
            email='moder123@mail.com',
            password='test123'
        )

        self.other_user = get_user_model().objects.create_user(
            username='other123',
            email='other123@mail.com',
            password='test123'
        )

        self.rejected_user = get_user_model().objects.create_user(
            username='rejec123',
            email='reject123@mail.com',
            password='test123'
        )
        self.request_user = get_user_model().objects.create_user(
            username='request123',
            email='request123@mail.com',
            password='test123'
        )

        self.public_group = StudyGroup.objects.create(
            owner=self.owner_user,
            name='Public Group',
            visibility=StudyGroup.Visibility.PUBLIC
        )
        self.private_group = StudyGroup.objects.create(
            owner=self.owner_user,
            name='Private Group',
            visibility=StudyGroup.Visibility.PRIVATE
        )

        self.membership = GroupMembership.objects.create(
            group=self.private_group,
            user=self.user,
            status=GroupMembership.Status.ACTIVE,
            role=GroupMembership.Role.MEMBER
        )

        self.membership2 = GroupMembership.objects.create(
            group=self.private_group,
            user=self.members_user2,
            status=GroupMembership.Status.ACTIVE,
            role=GroupMembership.Role.MEMBER
        )

        self.membership_pending = GroupMembership.objects.create(
            group=self.private_group,
            user=self.other_user,
            status=GroupMembership.Status.PENDING,
            role=GroupMembership.Role.MEMBER
        )

        self.membership_rejected = GroupMembership.objects.create(
            group=self.private_group,
            user=self.rejected_user,
            status=GroupMembership.Status.REJECTED,
            role=GroupMembership.Role.MEMBER
        )
        self.membership_moderator = GroupMembership.objects.create(
            group=self.private_group,
            user=self.moderator_user,
            status=GroupMembership.Status.ACTIVE,
            role=GroupMembership.Role.MODERATOR
        )
        self.membership_owner = GroupMembership.objects.get(
            group=self.private_group,
            user=self.owner_user,
        )

    def test_NotOwner_join_group(self):
        membership, result = join_group(user=self.owner_user, group=self.public_group)

        self.assertIsNone(membership)
        self.assertEqual(result, 'Owner')

    def test_Active_join_group(self):
        membership, result = join_group(user=self.user, group=self.private_group)

        self.assertIsNotNone(membership)
        self.assertEqual(result, 'Active')
        self.assertEqual(membership.status, GroupMembership.Status.ACTIVE)
        self.assertEqual(membership.user, self.user)
        self.assertEqual(membership.group, self.private_group)

    def test_Pending_join_group(self):
        membership, result = join_group(user=self.other_user, group=self.private_group)

        self.assertIsNotNone(membership)
        self.assertEqual(result, 'Pending')
        self.assertEqual(membership.status, GroupMembership.Status.PENDING)

    def test_RequestSentAgain(self):
        membership, result = join_group(user=self.rejected_user, group=self.private_group)

        self.assertIsNotNone(membership)
        self.assertEqual(result, 'RequestSentAgain')
        self.assertEqual(membership.status, GroupMembership.Status.PENDING)

    def test_Joined_join_group(self):
        membership, result = join_group(user=self.other_user, group=self.public_group)

        self.assertIsNotNone(membership)
        self.assertEqual(result, 'Joined')
        self.assertEqual(membership.status, GroupMembership.Status.ACTIVE)

    def test_Request_sent_join_group(self):
        membership, result = join_group(user=self.request_user, group=self.private_group)

        self.assertIsNotNone(membership)
        self.assertEqual(result, 'Request')
        self.assertEqual(membership.status, GroupMembership.Status.PENDING)

    def test_PassOwnership_leave_group(self):
        result = leave_group(user=self.owner_user, group=self.private_group)

        self.assertEqual(result, 'PassOwnership')
        self.assertEqual(self.private_group.owner, self.owner_user)

    def test_Left_leave_group(self):
        result = leave_group(user=self.user, group=self.private_group)

        self.assertEqual(result, 'Left')
        self.assertFalse(GroupMembership.objects.filter(group=self.private_group, user=self.user).exists())

    def test_NotMember_leave_group(self):
        result = leave_group(user=self.request_user, group=self.private_group)

        self.assertEqual(result, 'NotMember')
        self.assertFalse(GroupMembership.objects.filter(group=self.private_group, user=self.request_user, status=GroupMembership.Status.ACTIVE).exists())

    def test_NotPending_accept_membership(self):
        result = accept_membership(self.membership_rejected)

        self.assertEqual(result, 'NotPending')
        self.assertNotEqual(self.membership_rejected.status, GroupMembership.Status.PENDING)

    def test_Accepted_accept_membership(self):
        result = accept_membership(self.membership_pending)

        self.assertEqual(result, 'Accepted')
        self.membership_pending.refresh_from_db()
        self.assertEqual(self.membership_pending.status, GroupMembership.Status.ACTIVE)
        self.assertEqual(self.membership_pending.user, self.other_user)
        self.assertEqual(self.membership_pending.group, self.private_group)

    def test_NotPending_reject_membership(self):
        result = reject_membership(self.membership_rejected)

        self.assertEqual(result, 'NotPending')
        self.assertNotEqual(self.membership_rejected.status, GroupMembership.Status.PENDING)

    def test_Rejected_reject_membership(self):
        result = reject_membership(self.membership_pending)

        self.assertEqual(result, 'Rejected')
        self.membership_pending.refresh_from_db()
        self.assertEqual(self.membership_pending.status, GroupMembership.Status.REJECTED)
        self.assertEqual(self.membership_pending.user, self.other_user)
        self.assertEqual(self.membership_pending.group, self.private_group)

    def test_NoAccess_make_moderator(self):
        result = make_moderator(self.membership, group=self.private_group, membership=self.membership2)

        self.assertEqual(result, 'NoAccess')
        self.membership2.refresh_from_db()
        self.assertEqual(self.membership2.role, GroupMembership.Role.MEMBER)

    def test_NotActiveMember_make_moderator(self):
        result = make_moderator(self.membership_moderator, group=self.private_group, membership=self.membership_rejected)

        self.assertEqual(result, 'NotActiveMember')
        self.membership_rejected.refresh_from_db()
        self.assertEqual(self.membership_rejected.role, GroupMembership.Role.MEMBER)
        self.assertEqual(self.membership_rejected.status, GroupMembership.Status.REJECTED)

    def test_Moderator_make_moderator(self):
        result = make_moderator(self.membership_moderator, group=self.private_group, membership=self.membership)

        self.assertEqual(result, 'Moderator')
        self.membership.refresh_from_db()
        self.assertEqual(self.membership.role, GroupMembership.Role.MODERATOR)
        self.assertEqual(self.membership.status, GroupMembership.Status.ACTIVE)

    def test_owner_can_remove_member(self):
        username, result = remove_member(
            current_member=self.membership_owner,
            group=self.private_group,
            membership=self.membership2,
            current_user=self.owner_user
        )

        self.assertEqual(result, 'Removed')
        self.assertEqual(username, self.members_user2.username)
        self.assertFalse(
            GroupMembership.objects.filter(id=self.membership2.id).exists()
        )

    def test_moderator_can_remove_regular_member(self):
        username, result = remove_member(
            current_member=self.membership_moderator,
            group=self.private_group,
            membership=self.membership2,
            current_user=self.moderator_user
        )

        self.assertEqual(result, 'Removed')
        self.assertEqual(username, self.members_user2.username)
        self.assertFalse(
            GroupMembership.objects.filter(id=self.membership2.id).exists()
        )

    def test_regular_member_cannot_remove_member(self):
        username, result = remove_member(
            current_member=self.membership,
            group=self.private_group,
            membership=self.membership2,
            current_user=self.user
        )

        self.assertIsNone(username)
        self.assertEqual(result, 'NoAccess')
        self.assertTrue(
            GroupMembership.objects.filter(id=self.membership2.id).exists()
        )

    def test_owner_cannot_be_removed(self):
        username, result = remove_member(
            current_member=self.membership_moderator,
            group=self.private_group,
            membership=self.membership_owner,
            current_user=self.moderator_user
        )

        self.assertIsNone(username)
        self.assertEqual(result, 'Owner')
        self.assertTrue(
            GroupMembership.objects.filter(id=self.membership_owner.id).exists()
        )

    def test_owner_can_transfer_ownership_to_moderator(self):
        username, result = transfer_ownership(
            group=self.private_group,
            membership=self.membership_moderator,
            current_user=self.owner_user
        )

        self.assertEqual(result, 'Changed')
        self.assertEqual(username, self.moderator_user.username)

        self.private_group.refresh_from_db()
        self.membership_moderator.refresh_from_db()
        self.membership_owner.refresh_from_db()

        self.assertEqual(self.private_group.owner, self.moderator_user)
        self.assertEqual(self.membership_moderator.role, GroupMembership.Role.OWNER)
        self.assertEqual(self.membership_owner.role, GroupMembership.Role.MODERATOR)

    def test_not_owner_cannot_transfer_ownership(self):
        username, result = transfer_ownership(
            group=self.private_group,
            membership=self.membership_moderator,
            current_user=self.user
        )

        self.assertIsNone(username)
        self.assertEqual(result, 'NotOwner')

        self.private_group.refresh_from_db()
        self.membership_moderator.refresh_from_db()

        self.assertEqual(self.private_group.owner, self.owner_user)
        self.assertEqual(self.membership_moderator.role, GroupMembership.Role.MODERATOR)

    def test_owner_cannot_transfer_ownership_to_regular_member(self):
        username, result = transfer_ownership(
            group=self.private_group,
            membership=self.membership,
            current_user=self.owner_user
        )

        self.assertIsNone(username)
        self.assertEqual(result, 'NotModerator')

        self.private_group.refresh_from_db()
        self.membership.refresh_from_db()

        self.assertEqual(self.private_group.owner, self.owner_user)
        self.assertEqual(self.membership.role, GroupMembership.Role.MEMBER)

    def test_transfer_ownership_returns_owner_not_found(self):
        self.membership_owner.delete()

        username, result = transfer_ownership(
            group=self.private_group,
            membership=self.membership_moderator,
            current_user=self.owner_user
        )

        self.assertIsNone(username)
        self.assertEqual(result, 'OwnerNotFound')

