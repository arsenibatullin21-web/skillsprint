from django.shortcuts import get_object_or_404
from django.utils import timezone

from rest_framework import serializers

from goals.models import LearningGoals, Milestone, ProgressEntry

class MilestoneSerializer(serializers.ModelSerializer):
    position = serializers.ReadOnlyField()
    class Meta:
        model = Milestone
        fields = ['title', 'is_completed', 'due_date', 'position']




class ProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProgressEntry
        fields = ['progress_percent', 'note', 'created_at']

class GoalsListDetailSerializer(serializers.ModelSerializer):
    milestones = MilestoneSerializer(many=True, read_only=True)
    progress = ProgressSerializer(many=True, read_only=True)
    owner = serializers.SlugRelatedField(slug_field='username', read_only=True)
    class Meta:
        model = LearningGoals
        fields = ['owner', 'title', 'description', 'status', 'visibility', 'progress_percent', 'deadline', 'created_at', 'updated_at', 'milestones', 'progress']


class GoalsCreateSerializer(serializers.ModelSerializer):
    milestones = MilestoneSerializer(many=True, required=False)
    class Meta:
        model = LearningGoals
        fields = ['title', 'description', 'status', 'visibility', 'deadline', 'milestones']

    def create(self, validated_data):
        milestones = validated_data.pop('milestones', [])

        goal = LearningGoals.objects.create(owner=self.context['request'].user, **validated_data)
        for position, milestone_data in enumerate(milestones, start=1):
            Milestone.objects.create(
                goal=goal,
                position=position,
                **milestone_data
            )

        return goal

    def validate_title(self, value):
        if value == '':
            raise serializers.ValidationError({
                'error': "Title can't be empty."
            })
        return value

    def validate_deadline(self, value):
        if value and value < timezone.localdate():
            raise serializers.ValidationError({
                'error': "Deadline cannot be in the past."
            })
        return value

    def validate(self, attrs):
        deadline = attrs.get('deadline')
        milestones = attrs.get('milestones', [])

        for milestone in milestones:
            due_date = milestone.get('due_date')

            if deadline and due_date and deadline < due_date:
                raise serializers.ValidationError({
                    'error': "Due date of milestone cannot be after deadline date."
                })
        return attrs

class GoalUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = LearningGoals
        fields = ['title', 'description', 'status', 'deadline', 'visibility']

    def validate_deadline(self, value):
        if value and value < timezone.localdate():
            raise serializers.ValidationError({
                'error': "Deadline cannot be in the past."
            })
        return value

class ProgressCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProgressEntry
        fields = ['progress_percent', 'note']



