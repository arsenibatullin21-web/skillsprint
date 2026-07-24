from django.db import transaction

from study_groups.models import GroupMembership, StudyGroup


def join_group(user, group):
    if group.owner == user:
        return None, 'Owner'

    membership, created = GroupMembership.objects.get_or_create(
        group=group,
        user=user,
        defaults={
            'role': GroupMembership.Role.MEMBER,
            'status': GroupMembership.Status.PENDING if group.visibility == StudyGroup.Visibility.PRIVATE else GroupMembership.Status.ACTIVE
        }
    )

    if not created:
        if membership.status == GroupMembership.Status.ACTIVE:
            return membership, 'Active'
        elif membership.status == GroupMembership.Status.PENDING:
            return membership, 'Pending'
        elif membership.status == GroupMembership.Status.REJECTED:
            membership.status = GroupMembership.Status.PENDING
            membership.save(update_fields=['status'])
            return membership, 'RequestSentAgain'

    if membership.status == GroupMembership.Status.ACTIVE:
        return membership, 'Joined'
    elif membership.status == GroupMembership.Status.PENDING:
        return membership, 'Request'

    return None


def leave_group(user, group):

    if group.owner == user:
        return 'PassOwnership'

    membership = GroupMembership.objects.filter(
        group=group,
        user=user
    ).first()

    if membership and membership.status == GroupMembership.Status.ACTIVE:
        membership.delete()
        return 'Left'
    return 'NotMember'


def accept_membership(membership):
    if membership.status != GroupMembership.Status.PENDING:
        return 'NotPending'
    membership.status = GroupMembership.Status.ACTIVE
    membership.save(update_fields=['status'])
    return "Accepted"

def reject_membership(membership):
    if membership.status != GroupMembership.Status.PENDING:
        return "NotPending"

    membership.status = GroupMembership.Status.REJECTED
    membership.save(update_fields=['status'])

    return "Rejected"

def make_moderator(current_member, group, membership):
    can_manage = (
        current_member
        and (
            group.owner == current_member.user
            or current_member.role == GroupMembership.Role.MODERATOR
        )
    )

    if not can_manage:
        return 'NoAccess'

    if membership.status != GroupMembership.Status.ACTIVE or membership.role != GroupMembership.Role.MEMBER:
        return 'NotActiveMember'

    membership.role = GroupMembership.Role.MODERATOR
    membership.save(update_fields=['role'])
    return 'Moderator'


def remove_member(current_member, group, membership, current_user):
    if membership.role == GroupMembership.Role.OWNER or membership.user == group.owner:
        return None, 'Owner'

    can_manage = group.owner == current_user or (
            current_member
            and current_member.role == GroupMembership.Role.MODERATOR
            and membership.role == GroupMembership.Role.MEMBER
    )
    if not can_manage:
        if current_member is None:
            return None, 'NotMember'
        return None, 'NoAccess'

    username = membership.user.username
    membership.delete()
    return username, 'Removed'


def transfer_ownership(group, membership, current_user):
    membership_owner = GroupMembership.objects.filter(group=group, role=GroupMembership.Role.OWNER).first()
    if group.owner != current_user:
        return None, 'NotOwner'

    if membership.status != GroupMembership.Status.ACTIVE or membership.role != GroupMembership.Role.MODERATOR:
        return None, 'NotModerator'

    if not membership_owner:
        return None, 'OwnerNotFound'

    with transaction.atomic():
        group.owner = membership.user
        group.save(update_fields=['owner'])

        membership.role = GroupMembership.Role.OWNER
        membership.save(update_fields=['role'])

        membership_owner.role = GroupMembership.Role.MODERATOR
        membership_owner.save(update_fields=['role'])

    return membership.user.username, "Changed"


