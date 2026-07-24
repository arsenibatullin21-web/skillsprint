from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from goals.forms import GoalCreateForm, MilestoneFormSet, MilestoneUpdateForm, GoalUpdateForm, ProgressCreateForm
from goals.models import LearningGoals, Milestone, ProgressEntry
from goals.services import create_goal_with_milestone, update_goal_with_milestones, create_progress_entry
from study_groups.models import StudyGroup, GroupMembership


class GoalTestServices(TestCase):
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

        self.other_user = get_user_model().objects.create_user(
            username='other123',
            email='other123@mail.com',
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

        self.goal = LearningGoals.objects.create(
            owner=self.user,
            title='Public Goal',
            status=LearningGoals.Status.ACTIVE,
            visibility=LearningGoals.Visibility.PUBLIC
        )

        self.milestone_1 = Milestone.objects.create(
            goal=self.goal,
            title='First milestone',
            due_date=timezone.localdate() + timedelta(days=3),
            position=1,
            is_completed=False
        )

        self.milestone_2 = Milestone.objects.create(
            goal=self.goal,
            title='Second milestone',
            due_date=timezone.localdate() + timedelta(days=5),
            position=2,
            is_completed=False
        )

    def test_create_goal_with_milestone(self):
        form = GoalCreateForm(data={
            'title': 'Goal',
            'description': 'Goal description',
            'visibility': LearningGoals.Visibility.PUBLIC,
            'status': LearningGoals.Status.ACTIVE,
            'deadline': (timezone.localdate() + timedelta(days=7)).isoformat(),
        })
        formset = MilestoneFormSet(data={
            'milestones-TOTAL_FORMS': '2',
            'milestones-INITIAL_FORMS': '0',
            'milestones-MIN_NUM_FORMS': '0',
            'milestones-MAX_NUM_FORMS': '1000',

            'milestones-0-title': 'First milestone',
            'milestones-0-due_date': '',

            'milestones-1-title': 'Second milestone',
            'milestones-1-due_date': '',
        }, prefix='milestones')

        self.assertTrue(form.is_valid(), form.errors)

        goal, result = create_goal_with_milestone(user=self.user, form=form, formset=formset)

        self.assertEqual(result, 'Created')
        self.assertIsNotNone(goal)

        self.assertTrue(
            LearningGoals.objects.filter(
                owner=self.user,
                title='Goal'
            ).exists()
        )

        self.assertEqual(goal.milestones.count(), 2)

        milestones = list(goal.milestones.order_by('position'))
        self.assertEqual(milestones[0].title, 'First milestone')
        self.assertEqual(milestones[0].position, 1)

        self.assertEqual(milestones[1].title, 'Second milestone')
        self.assertEqual(milestones[1].position, 2)


    def test_invalid_create_goal_with_milestone(self):
        form = GoalCreateForm({
            'title': 'Goal',
            'description': 'Goal description',
            'visibility': LearningGoals.Visibility.PUBLIC,
            'status': LearningGoals.Status.ACTIVE,
            'deadline': timezone.localdate() - timedelta(days=7)
        })


        formset = MilestoneFormSet(data={
            'milestones-TOTAL_FORMS': '2',
            'milestones-INITIAL_FORMS': '0',
            'milestones-MIN_NUM_FORMS': '0',
            'milestones-MAX_NUM_FORMS': '1000',

            'milestones-0-title': 'First milestone',
            'milestones-0-due_date': '',

            'milestones-1-title': 'Second milestone',
            'milestones-1-due_date': '',
        }, prefix='milestones')

        goal, result = create_goal_with_milestone(user=self.user, form=form, formset=formset)

        self.assertFalse(form.is_valid())
        self.assertEqual(result, 'Invalid Form')
        self.assertIsNone(goal)

    def test_invalid_update_goal_with_milestones(self):
        goal_object = LearningGoals.objects.create(
            owner=self.user,
            title='Public Goal',
            status=LearningGoals.Status.ACTIVE,
            visibility=LearningGoals.Visibility.PUBLIC
        )
        form = GoalCreateForm({
            'title': 'Changed Goal',
            'description': 'Goal description',
            'visibility': 'visible',
        })

        formset = MilestoneFormSet(data={
            'milestones-TOTAL_FORMS': '2',
            'milestones-INITIAL_FORMS': '0',
            'milestones-MIN_NUM_FORMS': '0',
            'milestones-MAX_NUM_FORMS': '1000',

            'milestones-0-title': 'First milestone',
            'milestones-0-due_date': '',

            'milestones-1-title': 'Second milestone',
            'milestones-1-due_date': '',
        }, prefix='milestones')

        self.assertFalse(form.is_valid())
        goal, result = update_goal_with_milestones(goal=goal_object, form=form, formset=formset)

        self.assertIsNone(goal)
        self.assertEqual(result, 'InvalidForm')

    def test_delete_in_formset_update_goal_with_milestones(self):

        form = GoalUpdateForm({
            'title': 'Changed Goal',
            'description': 'Goal description',
        }, instance=self.goal)

        formset = MilestoneUpdateForm(data={
            'milestone-TOTAL_FORMS': '1',
            'milestone-INITIAL_FORMS': '1',
            'milestone-MIN_NUM_FORMS': '0',
            'milestone-MAX_NUM_FORMS': '1000',

            'milestone-0-id': str(self.milestone_1.id),
            'milestone-0-title': self.milestone_1.title,
            'milestone-0-due_date': '',
            'milestone-0-is_completed': '',
            'milestone-0-DELETE': 'on',
        }, instance=self.goal, prefix='milestone')

        goal, result = update_goal_with_milestones(goal=self.goal, form=form, formset=formset)

        self.assertTrue(form.is_valid())
        self.assertIsNotNone(goal)
        self.assertEqual(result, 'Valid')

        self.goal.refresh_from_db()
        self.assertFalse(Milestone.objects.filter(title=self.milestone_1.title).exists())
        self.assertEqual(self.goal.milestones.count(), 1)
        self.assertEqual(self.goal.title, 'Changed Goal')

    def test_invalid_create_progress_entry(self):
        form = ProgressCreateForm(data={
            'progress_percent': 75,
            'note': 'Up to 75'
        })

        self.assertTrue(form.is_valid())
        progress, result = create_progress_entry(user=self.other_user, goal=self.goal, form=form)

        self.assertIsNone(progress)
        self.assertEqual(result, 'NotOwner')

    def test_valid_create_progress_entry(self):
        form = ProgressCreateForm(data={
            'progress_percent': 75,
            'note': 'Up to 75'
        })

        self.assertTrue(form.is_valid())
        progress, result = create_progress_entry(user=self.user, goal=self.goal, form=form)

        self.assertTrue(ProgressEntry.objects.filter(goal=self.goal, note='Up to 75').exists())
        self.assertIsNotNone(progress)
        self.assertEqual(result, 'Created')





