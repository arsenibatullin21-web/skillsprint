from django.shortcuts import get_object_or_404
from rest_framework import serializers

from study_groups.models import StudyGroup, GroupMembership, GroupPost, GroupResource


class UserGroupsSerializer(serializers.ModelSerializer):
    '''User's all groups'''
    owner = serializers.StringRelatedField()
    class Meta:
        model = StudyGroup
        fields = ['owner', 'name', 'slug', 'description', 'visibility', 'rules', 'topic', 'updated_at', 'created_at']

class ExploreGroupsSerializer(serializers.ModelSerializer):
    '''Explore other groups'''
    owner = serializers.StringRelatedField()
    members_count = serializers.SerializerMethodField(read_only=True)
    posts_count = serializers.SerializerMethodField(read_only=True)
    resources_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = StudyGroup
        fields = ['owner', 'name', 'description', 'topic', 'visibility', 'created_at', 'members_count', 'posts_count', 'resources_count']

    def get_members_count(self, obj):
        members = obj.membership.filter(status=GroupMembership.Status.ACTIVE)
        return members.count()

    def get_posts_count(self, obj):
        posts = obj.posts
        return posts.count()

    def get_resources_count(self, obj):
        resources = obj.resources
        return resources.count()


class GroupDetailSerializer(serializers.ModelSerializer):
    owner = serializers.StringRelatedField()
    active_members = serializers.SerializerMethodField()
    class Meta:
        model = StudyGroup
        fields = ['owner', 'name', 'description', 'visibility', 'avatar', 'rules', 'topic', 'updated_at', 'created_at', 'active_members']

    def get_active_members(self, obj):
        memberships = obj.active_members
        return {
            "members": [
                membership.user.username
                for membership in memberships
            ]
        }

class GroupCreateUpdateSerializer(serializers.ModelSerializer):
    owner = serializers.StringRelatedField(read_only=True)
    class Meta:
        model = StudyGroup
        fields = ['owner','name', 'description', 'visibility', 'rules', 'topic']


class MembershipSerializer(serializers.ModelSerializer):
    '''To see all members of the group (pending, active, rejected)'''
    user = serializers.StringRelatedField(read_only=True)
    group = serializers.StringRelatedField(read_only=True)
    class Meta:
        model = GroupMembership
        fields = ['user', 'group','status', 'role', 'joined_at']


class MembershipCreateSerializer(serializers.ModelSerializer):
    '''To Create and Update memberships'''
    class Meta:
        model = GroupMembership
        fields = ['group']

    def create(self, validated_data):
        group = validated_data.get('group')

        if GroupMembership.objects.filter(group=group, user=self.context['request'].user).exists():
            raise serializers.ValidationError({
                'error': 'You already have a membership in this group.'
            })

        if group.owner == self.context['request'].user:
            raise serializers.ValidationError({
                'error': "You are the owner of the group."
            })

        if group.visibility == StudyGroup.Visibility.PUBLIC:
            membership = GroupMembership.objects.create(
                status=GroupMembership.Status.ACTIVE,
                group=group,
                user=self.context['request'].user,
                role=GroupMembership.Role.MEMBER
            )
        else:
            membership = GroupMembership.objects.create(
                status=GroupMembership.Status.PENDING,
                group=group,
                user=self.context['request'].user,
                role=GroupMembership.Role.MEMBER
            )
        return membership

class MembershipUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupMembership
        fields = ['user', 'group', 'status', 'role', 'joined_at']
        read_only_fields = ['user', 'group', 'joined_at']

    def validate_role(self, value):
        if value == GroupMembership.Role.OWNER:
            raise serializers.ValidationError({
                'error': "You can't make other member an owner"
            })
        return value

    def validate(self, attrs):
        if self.instance and self.instance.role == GroupMembership.Role.OWNER:
            raise serializers.ValidationError(
                "Owner membership cannot be changed here."
            )
        return attrs


class ResourceDetailListSerializer(serializers.ModelSerializer):
    '''To see all resources of the group and detail of one resource'''
    group = serializers.SlugRelatedField('name', read_only=True)
    class Meta:
        model = GroupResource
        fields = ['id','group', 'title', 'url', 'description', 'created_by', 'created_at']

class ResourceCreateSerializer(serializers.ModelSerializer):
    group = serializers.SlugRelatedField('name', read_only=True)
    created_at = serializers.ReadOnlyField()
    class Meta:
        model = GroupResource
        fields = ['group','title', 'url', 'description', 'created_by', 'created_at']

class ResourceUpdateSerializer(serializers.ModelSerializer):
    group = serializers.SlugRelatedField('name', read_only=True)
    class Meta:
        model = GroupResource
        fields = ['group','title', 'url', 'description', 'created_by', 'created_at']
        read_only_fields = ['created_by', 'created_at']





