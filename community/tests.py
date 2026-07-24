from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase

from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.test import APITestCase

from community.models import Comment, Reaction, Bookmark
from community.services import toggle_reaction, toggle_bookmark, user_can_access_group, user_can_manage_post
from goals.forms import GoalCreateForm, MilestoneFormSet
from goals.models import LearningGoals
from goals.services import create_goal_with_milestone
from study_groups.models import GroupPost, StudyGroup, GroupMembership


# Create your tests here.

# class PostListDetailPermissionsTest(APITestCase):
#     def setUp(self):
#         self.user_owner = get_user_model().objects.create_user(
#             username='test123',
#             email='test123@mail.com',
#             password='test123'
#         )
#
#         self.member_user = get_user_model().objects.create_user(
#             username='member123',
#             email='member@mail.ru',
#             password='member123'
#         )
#
#         self.other_user = get_user_model().objects.create_user(
#             username='other',
#             email='other@mail.com',
#             password='otherpass123'
#         )
#
#         self.public_group = StudyGroup.objects.create(
#             owner=self.user_owner,
#             name='Learning Django',
#             description='LEarning Django',
#         )
#         self.private_group = StudyGroup.objects.create(
#             owner=self.user_owner,
#             name='Learning Django',
#             description='LEarning Django',
#             visibility=StudyGroup.Visibility.PRIVATE
#         )
#
#         self.public_post = GroupPost.objects.create(
#             group=self.public_group,
#             author=self.member_user,
#             title='Test public post',
#             content='Content public...'
#         )
#
#
#         self.private_post = GroupPost.objects.create(
#             group=self.private_group,
#             author=self.member_user,
#             title='Test private post',
#             content='Content private...'
#         )
#
#         GroupMembership.objects.create(
#             group=self.private_group,
#             user=self.member_user,
#             status=GroupMembership.Status.ACTIVE,
#             role=GroupMembership.Role.MEMBER
#         )
#
#
#     def test_post_list_of_logged_user_in_public_group(self):
#         '''To check logged user(not member) can see posts of public group'''
#         self.client.force_authenticate(user=self.other_user)
#
#         response = self.client.get(reverse('community:api_posts_list', kwargs={'group_id': self.public_group.id}))
#
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         titles = [post['title'] for post in response.data]
#
#         self.assertIn('Test public post', titles)
#
#     def test_logged_user_cant_see_posts_of_private_group(self):
#         '''To check logged user(not member) can't see posts of private group'''
#         self.client.force_authenticate(user=self.other_user)
#         response = self.client.get(reverse('community:api_posts_list', kwargs={'group_id': self.private_group.id}))
#
#         self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
#
#     def test_logged_member_can_see_posts_of_private_group(self):
#         '''Member can see posts of private group'''
#         self.client.force_authenticate(user=self.member_user)
#         response = self.client.get(reverse('community:api_posts_list', kwargs={'group_id': self.private_group.id}))
#
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#
#     def test_anonymous_user_cant_access_post_list(self):
#         '''To check unauthorized user can't see list of posts of any group'''
#         response = self.client.get(reverse('community:api_posts_list', kwargs={'group_id': self.public_group.id}))
#
#         self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
#
#     def test_view_returns_one_post_with_pk(self):
#         self.client.force_authenticate(user=self.member_user)
#
#         response = self.client.get(reverse('community:api_posts_detail', kwargs={'group_id': self.private_group.id, 'pk': self.private_post.id}))
#
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(response.data['id'], self.private_post.id)
#         self.assertEqual(response.data['title'], self.private_post.title)
#
#     def test_not_member_cant_see_detail_of_private_group_post(self):
#         self.client.force_authenticate(user=self.other_user)
#
#         response = self.client.get(reverse('community:api_posts_detail', kwargs={'group_id': self.private_group.id, 'pk': self.private_post.id}))
#
#         self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
#
#
#
#
#
#
# class PostCreateUpdateDeletePermissionTest(APITestCase):
#     def setUp(self):
#         self.user_owner = get_user_model().objects.create_user(
#             username='test123',
#             email='test123@mail.com',
#             password='test123'
#         )
#
#         self.member_user = get_user_model().objects.create_user(
#             username='member123',
#             email='member@mail.ru',
#             password='member123'
#         )
#
#         self.moderator_user = get_user_model().objects.create_user(
#             username='moder123',
#             email='moder@mail.ru',
#             password='moder123'
#         )
#
#         self.other_user = get_user_model().objects.create_user(
#             username='other',
#             email='other@mail.com',
#             password='otherpass123'
#         )
#
#         self.public_group = StudyGroup.objects.create(
#             owner=self.user_owner,
#             name='Learning Django',
#             description='LEarning Django',
#         )
#         self.private_group = StudyGroup.objects.create(
#             owner=self.user_owner,
#             name='Learning Django',
#             description='LEarning Django',
#             visibility=StudyGroup.Visibility.PRIVATE
#         )
#
#         self.public_post = GroupPost.objects.create(
#             group=self.public_group,
#             author=self.member_user,
#             title='Test public post',
#             content='Content public...'
#         )
#
#         self.private_post = GroupPost.objects.create(
#             group=self.private_group,
#             author=self.member_user,
#             title='Test private post',
#             content='Content private...'
#         )
#
#         self.private_post_moder = GroupPost.objects.create(
#             group=self.private_group,
#             author=self.moderator_user,
#             title='Moder post title',
#             content='Content of moderator'
#         )
#
#         GroupMembership.objects.create(
#             group=self.private_group,
#             user=self.member_user,
#             status=GroupMembership.Status.ACTIVE,
#             role=GroupMembership.Role.MEMBER
#         )
#
#         GroupMembership.objects.create(
#             group=self.private_group,
#             user=self.moderator_user,
#             status=GroupMembership.Status.ACTIVE,
#             role=GroupMembership.Role.MODERATOR
#         )
#
#     def test_member_can_create_post(self):
#         self.client.force_authenticate(user=self.member_user)
#
#         response = self.client.post(reverse('community:api_posts_create', kwargs={'group_id': self.private_group.id}), data={
#             'title': "Drf Learning title",
#             'content': "Drf Learning content"
#         })
#
#         self.assertEqual(response.status_code, status.HTTP_201_CREATED)
#         self.assertTrue(GroupPost.objects.filter(
#             title="Drf Learning title"
#         ).exists())
#         post = GroupPost.objects.get(title="Drf Learning title")
#         self.assertEqual(post.group, self.private_group)
#         self.assertEqual(post.author, self.member_user)
#
#     def test_not_member_cant_create_post(self):
#         self.client.force_authenticate(user=self.other_user)
#
#         response = self.client.post(reverse('community:api_posts_create', kwargs={'group_id': self.private_group.id}),
#                                     data={
#                                         'title': "Drf Learning title",
#                                         'content': "Drf Learning content"
#                                     })
#
#         self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
#         self.assertFalse(GroupPost.objects.filter(
#             title="Drf Learning title"
#         ).exists())
#
#     def test_post_author_can_update_post(self):
#         self.client.force_authenticate(user=self.member_user)
#
#         response = self.client.put(reverse('community:api_posts_update', kwargs={'group_id': self.private_group.id,'pk': self.private_post.id}), data={
#             'title': "Update title",
#             'content': "Update content"
#         })
#
#         self.private_post.refresh_from_db()
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertTrue(GroupPost.objects.filter(title='Update title').exists())
#         post = GroupPost.objects.filter(title="Update title").first()
#         self.assertEqual(post.title, "Update title")
#
#
#
#     def test_not_post_author_cant_update_post(self):
#         self.client.force_authenticate(user=self.user_owner)
#
#         response = self.client.put(reverse('community:api_posts_update', kwargs={'group_id': self.private_group.id ,'pk': self.private_post.id}),
#                                     data={
#                                         'title': "Update title",
#                                         'content': "Update content"
#                                     })
#
#         self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
#
#     def test_author_can_delete_post(self):
#         self.client.force_authenticate(user=self.member_user)
#
#         response = self.client.delete(reverse('community:api_posts_delete', kwargs={'group_id': self.private_group.id, 'pk': self.private_post.id}))
#
#         self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
#
#         self.assertFalse(GroupPost.objects.filter(title='Learning Django').exists())
#
#
#     def test_owner_can_delete_post(self):
#         self.client.force_authenticate(user=self.user_owner)
#
#         response = self.client.delete(reverse('community:api_posts_delete',
#                                               kwargs={'group_id': self.private_group.id, 'pk': self.private_post.id}))
#
#         self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
#
#         self.assertFalse(GroupPost.objects.filter(title='Learning Django').exists())
#
#     def test_moderator_can_delete_post(self):
#         self.client.force_authenticate(user=self.moderator_user)
#
#         response = self.client.delete(reverse('community:api_posts_delete',
#                                               kwargs={'group_id': self.private_group.id, 'pk': self.private_post.id}))
#
#         self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
#
#         self.assertFalse(GroupPost.objects.filter(title='Learning Django').exists())
#
#     def test_member_cant_delete_others_post(self):
#         self.client.force_authenticate(user=self.member_user)
#
#         response = self.client.delete(reverse('community:api_posts_delete',
#                                               kwargs={'group_id': self.private_group.id, 'pk': self.private_post_moder.id}))
#
#         self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
#
# class CommentListPermissionsTest(APITestCase):
#     def setUp(self):
#         self.user_owner = get_user_model().objects.create_user(
#             username='test123',
#             email='test123@mail.com',
#             password='test123'
#         )
#
#         self.member_user = get_user_model().objects.create_user(
#             username='member123',
#             email='member@mail.ru',
#             password='member123'
#         )
#
#         self.moderator_user = get_user_model().objects.create_user(
#             username='moder123',
#             email='moder@mail.ru',
#             password='moder123'
#         )
#
#         self.other_user = get_user_model().objects.create_user(
#             username='other',
#             email='other@mail.com',
#             password='otherpass123'
#         )
#
#         self.public_group = StudyGroup.objects.create(
#             owner=self.user_owner,
#             name='Learning Django',
#             description='LEarning Django',
#         )
#         self.private_group = StudyGroup.objects.create(
#             owner=self.user_owner,
#             name='Learning Django',
#             description='LEarning Django',
#             visibility=StudyGroup.Visibility.PRIVATE
#         )
#
#         self.public_post = GroupPost.objects.create(
#             group=self.public_group,
#             author=self.member_user,
#             title='Test public post',
#             content='Content public...'
#         )
#
#         self.private_post = GroupPost.objects.create(
#             group=self.private_group,
#             author=self.member_user,
#             title='Test private post',
#             content='Content private...'
#         )
#
#
#         GroupMembership.objects.create(
#             group=self.private_group,
#             user=self.member_user,
#             status=GroupMembership.Status.ACTIVE,
#             role=GroupMembership.Role.MEMBER
#         )
#
#         GroupMembership.objects.create(
#             group=self.private_group,
#             user=self.moderator_user,
#             status=GroupMembership.Status.ACTIVE,
#             role=GroupMembership.Role.MODERATOR
#         )
#
#         self.comment1_private_post = Comment.objects.create(
#             post=self.private_post,
#             author=self.member_user,
#             context="Comment 1 private"
#         )
#
#         self.comment2_private_post = Comment.objects.create(
#             post=self.private_post,
#             author=self.user_owner,
#             context="Comment 2 private"
#         )
#
#         self.comment1_public_post = Comment.objects.create(
#             post=self.public_post,
#             author=self.member_user,
#             context="Comment 1 public"
#         )
#
#         self.comment2_public_post = Comment.objects.create(
#             post=self.public_post,
#             author=self.user_owner,
#             context="Comment 2 public"
#         )
#     def test_logged_user_can_see_public_group_comments(self):
#         self.client.force_authenticate(user=self.other_user)
#
#         response = self.client.get(reverse('community:api_comments', kwargs={'post_id': self.public_post.id}))
#
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#
#         contexts = [comment['context'] for comment in response.data]
#         self.assertIn('Comment 1 public', contexts)
#
#     def test_member_can_see_comment_of_private_group(self):
#         self.client.force_authenticate(user=self.member_user)
#         response = self.client.get(reverse('community:api_comments', kwargs={'post_id': self.private_post.id}))
#
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         contexts = [comment['context'] for comment in response.data]
#         self.assertIn(self.comment1_private_post.context, contexts)
#
#     def test_not_member_cant_see_comment_of_private_group(self):
#         self.client.force_authenticate(user=self.other_user)
#         response = self.client.get(reverse('community:api_comments', kwargs={'post_id': self.private_post.id}))
#
#         self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
#
#     def test_comment_list_returns_replies_nested(self):
#         self.client.force_authenticate(user=self.member_user)
#
#         parent_comment = Comment.objects.create(
#             post=self.private_post,
#             author=self.member_user,
#             context='Parent comment'
#         )
#
#         reply_comment = Comment.objects.create(
#             post=self.private_post,
#             author=self.user_owner,
#             parent=parent_comment,
#             context='Reply comment'
#         )
#         response = self.client.get(reverse('community:api_comments', kwargs={'post_id': self.private_post.id}))
#
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(len(response.data), 3)
#         self.assertEqual(response.data[0]['context'], 'Comment 1 private')
#         self.assertEqual(response.data[1]['context'], 'Comment 2 private')
#         self.assertEqual(response.data[2]['context'], 'Parent comment')
#
#         replies = [reply for reply in response.data[2]['replies']]
#
#         self.assertEqual(len(replies), 1)
#         self.assertEqual(replies[0]['id'], reply_comment.id)
#         self.assertIn(reply_comment.context, replies[0]['context'])
#
#         comment_ids = [comment['id'] for comment in response.data]
#
#         self.assertIn(parent_comment.id, comment_ids)
#         self.assertNotIn(reply_comment.id, comment_ids)
#
#     def test_right_comments_of_the_post(self):
#         self.client.force_authenticate(user=self.member_user)
#
#         response = self.client.get(reverse('community:api_comments', kwargs={'post_id': self.private_post.id}))
#
#         context = [comment['context'] for comment in response.data]
#         self.assertIn('Comment 1 private', context)
#         self.assertIn('Comment 2 private', context)
#
#         self.assertEqual(len(response.data), 2)
#         self.assertNotIn('Comment 1 public', context)
#
# class CommentCreatePermissionsTest(APITestCase):
#     def setUp(self):
#         self.user_owner = get_user_model().objects.create_user(
#             username='test123',
#             email='test123@mail.com',
#             password='test123'
#         )
#
#         self.member_user = get_user_model().objects.create_user(
#             username='member123',
#             email='member@mail.ru',
#             password='member123'
#         )
#
#         self.moderator_user = get_user_model().objects.create_user(
#             username='moder123',
#             email='moder@mail.ru',
#             password='moder123'
#         )
#
#         self.other_user = get_user_model().objects.create_user(
#             username='other',
#             email='other@mail.com',
#             password='otherpass123'
#         )
#
#         self.public_group = StudyGroup.objects.create(
#             owner=self.user_owner,
#             name='Learning Django',
#             description='LEarning Django',
#         )
#         self.private_group = StudyGroup.objects.create(
#             owner=self.user_owner,
#             name='Learning Django',
#             description='LEarning Django',
#             visibility=StudyGroup.Visibility.PRIVATE
#         )
#
#         self.public_post = GroupPost.objects.create(
#             group=self.public_group,
#             author=self.member_user,
#             title='Test public post',
#             content='Content public...'
#         )
#
#         self.private_post = GroupPost.objects.create(
#             group=self.private_group,
#             author=self.member_user,
#             title='Test private post',
#             content='Content private...'
#         )
#
#         GroupMembership.objects.create(
#             group=self.private_group,
#             user=self.member_user,
#             status=GroupMembership.Status.ACTIVE,
#             role=GroupMembership.Role.MEMBER
#         )
#
#         GroupMembership.objects.create(
#             group=self.private_group,
#             user=self.moderator_user,
#             status=GroupMembership.Status.ACTIVE,
#             role=GroupMembership.Role.MODERATOR
#         )
#
#     def test_member_can_create_comment_in_private_group(self):
#         self.client.force_authenticate(user=self.member_user)
#
#         response = self.client.post(reverse('community:api_comments_create', kwargs={'post_id': self.private_post.id}), data={
#             'context': "Comment for private post"
#         })
#
#         self.assertEqual(response.status_code, status.HTTP_201_CREATED)
#         self.assertTrue(Comment.objects.filter(post=self.private_post, context='Comment for private post').exists())
#
#     def test_comment_gets_author_automatically(self):
#         self.client.force_authenticate(user=self.member_user)
#
#         response = self.client.post(reverse('community:api_comments_create', kwargs={'post_id': self.private_post.id}), data={
#             'context': "Comment for private post"
#         })
#
#         self.assertEqual(response.status_code, status.HTTP_201_CREATED)
#         comment = Comment.objects.filter(post=self.private_post, context='Comment for private post').first()
#         self.assertEqual(self.member_user, comment.author)
#         self.assertEqual(self.private_post, comment.post)
#
#     def test_create_reply_comment_with_parent(self):
#         self.client.force_authenticate(user=self.member_user)
#
#         parent_comment = Comment.objects.create(
#             post=self.private_post,
#             author=self.member_user,
#             context="Comment 1 private"
#         )
#         response = self.client.post(reverse('community:api_comments_create', kwargs={'post_id': self.private_post.id}), data={
#             'context': "Comment for private post",
#             'parent': parent_comment.id
#         })
#
#         self.assertEqual(response.status_code, status.HTTP_201_CREATED)
#         self.assertTrue(Comment.objects.filter(post=self.private_post, context='Comment for private post').exists())
#         comment = Comment.objects.filter(post=self.private_post, context='Comment for private post').first()
#
#         self.assertEqual(comment.parent, parent_comment)
#         self.assertIsNotNone(comment.parent)
#
#     def test_cant_create_comment_with_parent_from_other_post(self):
#         self.client.force_authenticate(user=self.member_user)
#         parent_comment = Comment.objects.create(
#             context="Public post comment",
#             post=self.public_post,
#             author=self.other_user
#         )
#
#         response = self.client.post(reverse('community:api_comments_create', kwargs={'post_id': self.private_post.id}), data={
#             'context': "Private post comment",
#             'parent': parent_comment.id
#         })
#
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#         self.assertIn('parent', response.data)
#         self.assertFalse(Comment.objects.filter(post=self.private_post, context='Private post comment').exists())
#
#     def test_not_member_cant_create_comment_of_private_group_post(self):
#         self.client.force_authenticate(user=self.other_user)
#
#         response = self.client.post(reverse('community:api_comments_create', kwargs={'post_id': self.private_post.id}),
#                                     data={
#                                         'context': "Private post comment",
#                                     }, format='json')
#         self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
#         self.assertFalse(Comment.objects.filter(post=self.private_post, context='Private post comment').exists())
#
#
# class CommentUpdateDeletePermissionsTest(APITestCase):
#     def setUp(self):
#         self.user_owner = get_user_model().objects.create_user(
#             username='test123',
#             email='test123@mail.com',
#             password='test123'
#         )
#
#         self.member_user = get_user_model().objects.create_user(
#             username='member123',
#             email='member@mail.ru',
#             password='member123'
#         )
#
#         self.moderator_user = get_user_model().objects.create_user(
#             username='moder123',
#             email='moder@mail.ru',
#             password='moder123'
#         )
#
#         self.other_user = get_user_model().objects.create_user(
#             username='other',
#             email='other@mail.com',
#             password='otherpass123'
#         )
#
#         self.public_group = StudyGroup.objects.create(
#             owner=self.user_owner,
#             name='Learning Django',
#             description='LEarning Django',
#         )
#         self.private_group = StudyGroup.objects.create(
#             owner=self.user_owner,
#             name='Learning Django',
#             description='LEarning Django',
#             visibility=StudyGroup.Visibility.PRIVATE
#         )
#
#         self.public_post = GroupPost.objects.create(
#             group=self.public_group,
#             author=self.member_user,
#             title='Test public post',
#             content='Content public...'
#         )
#
#         self.private_post = GroupPost.objects.create(
#             group=self.private_group,
#             author=self.member_user,
#             title='Test private post',
#             content='Content private...'
#         )
#
#         GroupMembership.objects.create(
#             group=self.private_group,
#             user=self.member_user,
#             status=GroupMembership.Status.ACTIVE,
#             role=GroupMembership.Role.MEMBER
#         )
#
#         GroupMembership.objects.create(
#             group=self.private_group,
#             user=self.moderator_user,
#             status=GroupMembership.Status.ACTIVE,
#             role=GroupMembership.Role.MODERATOR
#         )
#
#         self.comment1_private_post = Comment.objects.create(
#             post=self.private_post,
#             author=self.member_user,
#             context="Comment 1 private"
#         )
#
#         self.comment2_private_post = Comment.objects.create(
#             post=self.private_post,
#             author=self.user_owner,
#             context="Comment 2 private"
#         )
#
#         self.comment1_public_post = Comment.objects.create(
#             post=self.public_post,
#             author=self.member_user,
#             context="Comment 1 public"
#         )
#
#         self.comment2_public_post = Comment.objects.create(
#             post=self.public_post,
#             author=self.user_owner,
#             context="Comment 2 public"
#         )
#
#
#     def test_comment_author_can_update(self):
#         self.client.force_authenticate(user=self.member_user)
#
#         response = self.client.put(reverse('community:api_comments_update', kwargs={'post_id': self.private_post.id, 'pk': self.comment1_private_post.id}), data={
#             'context': "Updated comment"
#         }, format='json')
#         self.comment1_private_post.refresh_from_db()
#
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         comment = Comment.objects.filter(post=self.private_post, context='Updated comment').first()
#         self.assertEqual('Updated comment', comment.context)
#         self.assertEqual(self.member_user, comment.author)
#
#     def test_not_author_cant_update_comment(self):
#         self.client.force_authenticate(user=self.user_owner)
#
#         response = self.client.put(reverse('community:api_comments_update', kwargs={'post_id': self.private_post.id,
#                                                                                     'pk': self.comment1_private_post.id}),
#                                    data={
#                                        'context': "Updated comment"
#                                    }, format='json')
#
#         self.comment1_private_post.refresh_from_db()
#         self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
#         self.assertNotEqual("Updated comment", self.comment1_private_post.context)
#
#     def test_author_can_delete_comment(self):
#         self.client.force_authenticate(user=self.member_user)
#         response = self.client.delete(reverse('community:api_comments_delete', kwargs={'post_id': self.private_post.id, 'pk': self.comment1_private_post.id}))
#
#         self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
#         self.assertFalse(Comment.objects.filter(post=self.private_post, context='Comment 1 private').exists())
#
#     def test_owner_group_can_delete_any_comment(self):
#         self.client.force_authenticate(user=self.moderator_user)
#
#         response = self.client.delete(reverse('community:api_comments_delete', kwargs={'post_id': self.private_post.id, 'pk': self.comment1_private_post.id}))
#
#         self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
#         self.assertFalse(Comment.objects.filter(post=self.private_post, context='Comment 1 private').exists())
#
#     def test_owner_group_can_delete_any_comment(self):
#         self.client.force_authenticate(user=self.user_owner)
#
#         response = self.client.delete(reverse('community:api_comments_delete', kwargs={'post_id': self.private_post.id,
#                                                                                        'pk': self.comment1_private_post.id}))
#         self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
#         self.assertFalse(Comment.objects.filter(post=self.private_post, context='Comment 1 private').exists())
#
#     def test_member_cant_delete_any_comment(self):
#         self.client.force_authenticate(user=self.member_user)
#
#         response = self.client.delete(reverse('community:api_comments_delete', kwargs={'post_id': self.private_post.id, 'pk': self.comment2_private_post.id}))
#
#         self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
#         self.assertTrue(Comment.objects.filter(post=self.private_post.id, context='Comment 2 private').exists())
#
#     def test_cant_delete_comment_with_invalid_other_post_id(self):
#         self.client.force_authenticate(user=self.member_user)
#
#         response = self.client.delete(reverse('community:api_comments_delete', kwargs={'post_id': self.public_post.id, 'pk': self.comment2_private_post.id}))
#
#         self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
#         self.assertTrue(Comment.objects.filter(post=self.private_post.id, context='Comment 2 private').exists())
#
#     def test_cant_update_comment_with_invalid_other_post_id(self):
#         self.client.force_authenticate(user=self.member_user)
#
#         response = self.client.delete(reverse('community:api_comments_update', kwargs={'post_id': self.public_post.id, 'pk': self.comment2_private_post.id}))
#
#         self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
#         self.assertTrue(Comment.objects.filter(post=self.private_post.id, context='Comment 2 private').exists())
#
#
#
# class ReactionListPermissionsTest(APITestCase):
#     def setUp(self):
#         self.owner_user = get_user_model().objects.create_user(
#             username='owner123',
#             email='owner123@mail.com',
#             password='test123'
#         )
#
#         self.member_user = get_user_model().objects.create_user(
#             username='member123',
#             email='member123@mail.com',
#             password='test123'
#         )
#
#         self.other_user = get_user_model().objects.create_user(
#             username='other123',
#             email='other123@mail.com',
#             password='test123'
#         )
#
#         self.private_group = StudyGroup.objects.create(
#             owner=self.owner_user,
#             name='Private Test Group',
#             description='Private group for reaction tests',
#             visibility=StudyGroup.Visibility.PRIVATE,
#             topic='Django'
#         )
#
#         self.public_group = StudyGroup.objects.create(
#             owner=self.owner_user,
#             name='Public Test Group',
#             description='Public group for reaction tests',
#             visibility=StudyGroup.Visibility.PUBLIC,
#             topic='DRF'
#         )
#
#         GroupMembership.objects.create(
#             group=self.private_group,
#             user=self.member_user,
#             role=GroupMembership.Role.MEMBER,
#             status=GroupMembership.Status.ACTIVE
#         )
#
#         self.private_post = GroupPost.objects.create(
#             group=self.private_group,
#             author=self.member_user,
#             title='Private post',
#             content='Private post content'
#         )
#
#         self.private_post_other = GroupPost.objects.create(
#             group=self.private_group,
#             author=self.member_user,
#             title='Other private post',
#             content='Other private post content'
#         )
#
#         self.public_post = GroupPost.objects.create(
#             group=self.public_group,
#             author=self.owner_user,
#             title='Public post',
#             content='Public post content'
#         )
#
#         self.private_post_reaction_1 = Reaction.objects.create(
#             post=self.private_post,
#             user=self.member_user,
#             type=Reaction.Type.LIKE
#         )
#
#         self.private_post_reaction_2 = Reaction.objects.create(
#             post=self.private_post,
#             user=self.owner_user,
#             type=Reaction.Type.HELPFUL
#         )
#
#         self.other_post_reaction = Reaction.objects.create(
#             post=self.private_post_other,
#             user=self.member_user,
#             type=Reaction.Type.CELEBRATE
#         )
#
#         self.public_post_reaction = Reaction.objects.create(
#             post=self.public_post,
#             user=self.other_user,
#             type=Reaction.Type.LIKE
#         )
#
#     def test_returns_reactions_of_current_post(self):
#         self.client.force_authenticate(user=self.member_user)
#
#         response = self.client.get(reverse('community:api_reactions', kwargs={'post_id': self.private_post.id}))
#
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         reaction_ids = [reaction['id'] for reaction in response.data]
#         reaction_users = [reaction['user'] for reaction in response.data]
#
#         self.assertIn(self.private_post_reaction_1.id, reaction_ids)
#         self.assertIn(self.private_post_reaction_2.id, reaction_ids)
#         self.assertIn(str(self.private_post_reaction_1.user), reaction_users)
#         self.assertIn(str(self.private_post_reaction_2.user), reaction_users)
#         self.assertEqual(len(response.data), 2)
#
#     def test_not_returns_reactions_of_other_post(self):
#         self.client.force_authenticate(user=self.member_user)
#
#         response = self.client.get(reverse('community:api_reactions', kwargs={'post_id': self.private_post.id}))
#
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         reaction_ids = [reaction['id'] for reaction in response.data]
#
#         self.assertNotIn(self.other_post_reaction.id, reaction_ids)
#         self.assertNotIn(self.public_post_reaction, reaction_ids)
#
#     def test_not_members_cant_see_reactions_of_private_group_post(self):
#         self.client.force_authenticate(user=self.other_user)
#
#
#         response = self.client.get(reverse('community:api_reactions', kwargs={'post_id': self.private_post.id}))
#
#         self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
#
#
#     def test_not_members_can_see_reactions_of_public_group_post(self):
#         self.client.force_authenticate(user=self.other_user)
#
#         response = self.client.get(reverse('community:api_reactions', kwargs={'post_id': self.public_post.id}))
#
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         ids = [reaction['id'] for reaction in response.data]
#         self.assertIn(self.public_post_reaction.id, ids)
#
#
# class ReactionTogglePermissionsTest(APITestCase):
#     def setUp(self):
#         self.owner_user = get_user_model().objects.create_user(
#             username='owner123',
#             email='owner123@mail.com',
#             password='test123'
#         )
#
#         self.member_user = get_user_model().objects.create_user(
#             username='member123',
#             email='member123@mail.com',
#             password='test123'
#         )
#
#         self.member2_user = get_user_model().objects.create_user(
#             username='member2123',
#             email='member2123@mail.com',
#             password='test2123'
#         )
#
#
#         self.other_user = get_user_model().objects.create_user(
#             username='other123',
#             email='other123@mail.com',
#             password='test123'
#         )
#
#         self.private_group = StudyGroup.objects.create(
#             owner=self.owner_user,
#             name='Private Test Group',
#             description='Private group for reaction tests',
#             visibility=StudyGroup.Visibility.PRIVATE,
#             topic='Django'
#         )
#
#         self.public_group = StudyGroup.objects.create(
#             owner=self.owner_user,
#             name='Public Test Group',
#             description='Public group for reaction tests',
#             visibility=StudyGroup.Visibility.PUBLIC,
#             topic='DRF'
#         )
#
#         GroupMembership.objects.create(
#             group=self.private_group,
#             user=self.member_user,
#             role=GroupMembership.Role.MEMBER,
#             status=GroupMembership.Status.ACTIVE
#         )
#
#         GroupMembership.objects.create(
#             group=self.private_group,
#             user=self.member2_user,
#             role=GroupMembership.Role.MEMBER,
#             status=GroupMembership.Status.ACTIVE
#         )
#
#         self.private_post = GroupPost.objects.create(
#             group=self.private_group,
#             author=self.member_user,
#             title='Private post',
#             content='Private post content'
#         )
#
#         self.private_post_other = GroupPost.objects.create(
#             group=self.private_group,
#             author=self.member_user,
#             title='Other private post',
#             content='Other private post content'
#         )
#
#         self.public_post = GroupPost.objects.create(
#             group=self.public_group,
#             author=self.owner_user,
#             title='Public post',
#             content='Public post content'
#         )
#
#         self.private_post_reaction_1 = Reaction.objects.create(
#             post=self.private_post,
#             user=self.member_user,
#             type=Reaction.Type.LIKE
#         )
#
#
#         self.other_post_reaction = Reaction.objects.create(
#             post=self.private_post_other,
#             user=self.member_user,
#             type=Reaction.Type.CELEBRATE
#         )
#
#         self.public_post_reaction = Reaction.objects.create(
#             post=self.public_post,
#             user=self.other_user,
#             type=Reaction.Type.LIKE
#         )
#
#     def test_member_can_put_reaction(self):
#         self.client.force_authenticate(user=self.owner_user)
#
#         response = self.client.post(reverse('community:api_reactions_toggle', kwargs={'post_id': self.private_post.id}), data={
#             'type': Reaction.Type.CELEBRATE
#         })
#
#         self.assertEqual(response.status_code, status.HTTP_201_CREATED)
#         self.assertTrue(Reaction.objects.filter(post=self.private_post.id, user=self.owner_user).exists())
#
#     def test_member_reclick_deletes_reaction(self):
#         self.client.force_authenticate(user=self.member_user)
#
#         response = self.client.post(reverse('community:api_reactions_toggle', kwargs={'post_id': self.private_post.id}),
#                                     data={
#                                         'type': Reaction.Type.LIKE
#                                     }, format='json')
#
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertFalse(Reaction.objects.filter(post=self.private_post.id, user=self.member_user).exists())
#
#     def test_one_user_can_have_one_reaction_per_post(self):
#         self.client.force_authenticate(user=self.member2_user)
#
#         url = reverse(
#             'community:api_reactions_toggle',
#             kwargs={'post_id': self.private_post.id}
#         )
#
#         response1 = self.client.post(
#             url,
#             data={'type': Reaction.Type.LIKE},
#             format='json'
#         )
#
#         response2 = self.client.post(
#             url,
#             data={'type': Reaction.Type.HELPFUL},
#             format='json'
#         )
#
#         self.assertEqual(response1.status_code, status.HTTP_201_CREATED)
#         self.assertEqual(response2.status_code, status.HTTP_200_OK)
#
#         reactions = Reaction.objects.filter(
#             post=self.private_post,
#             user=self.member2_user
#         )
#         self.assertEqual(reactions.count(), 1)
#         self.assertEqual(reactions.first().type, Reaction.Type.HELPFUL)
#
#
#
# class BookmarkListPermissionsTest(APITestCase):
#     def setUp(self):
#         self.user = get_user_model().objects.create_user(
#             username='user123',
#             email='user123@mail.com',
#             password='test123'
#         )
#
#         self.empty_user = get_user_model().objects.create_user(
#             username='empty123',
#             email='empty123@mail.com',
#             password='test123'
#         )
#
#         self.other_user = get_user_model().objects.create_user(
#             username='other123',
#             email='other123@mail.com',
#             password='test123'
#         )
#
#         self.group_1 = StudyGroup.objects.create(
#             owner=self.user,
#             name='Django Group',
#             description='Django practice group',
#             visibility=StudyGroup.Visibility.PUBLIC,
#             topic='Django'
#         )
#
#         self.group_2 = StudyGroup.objects.create(
#             owner=self.other_user,
#             name='DRF Group',
#             description='DRF practice group',
#             visibility=StudyGroup.Visibility.PUBLIC,
#             topic='DRF'
#         )
#
#         self.post_1 = GroupPost.objects.create(
#             group=self.group_1,
#             author=self.user,
#             title='Django bookmark post',
#             content='Django content'
#         )
#
#         self.post_2 = GroupPost.objects.create(
#             group=self.group_2,
#             author=self.other_user,
#             title='DRF bookmark post',
#             content='DRF content'
#         )
#
#         self.other_post = GroupPost.objects.create(
#             group=self.group_1,
#             author=self.other_user,
#             title='Other user bookmark post',
#             content='Other content'
#         )
#
#         self.bookmark_1 = Bookmark.objects.create(
#             post=self.post_1,
#             user=self.user
#         )
#
#         self.bookmark_2 = Bookmark.objects.create(
#             post=self.post_2,
#             user=self.user
#         )
#
#         self.other_user_bookmark = Bookmark.objects.create(
#             post=self.other_post,
#             user=self.other_user
#         )
#
#     def test_logged_user_sees_all_his_bookmarks(self):
#         self.client.force_authenticate(user=self.user)
#
#         response = self.client.get(reverse('community:api_my_bookmarks'))
#
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         ids = [bookmark['id'] for bookmark in response.data]
#         posts = [bookmark['post'] for bookmark in response.data]
#
#         self.assertIn(self.bookmark_1.id, ids)
#         self.assertIn(self.bookmark_2.id, ids)
#         self.assertNotIn(self.other_user_bookmark.id, ids)
#         self.assertIn(str(self.post_1), posts)
#         self.assertIn(str(self.post_2), posts)
#         self.assertTrue(posts[0] != posts[1])
#
#     def test_user_with_0_bookmarks_works_correct(self):
#         self.client.force_authenticate(user=self.empty_user)
#
#         response = self.client.get(reverse('community:api_my_bookmarks'))
#
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(len(response.data), 0)
#
#
#
# class BookmarksTogglePermissionsTest(APITestCase):
#     def setUp(self):
#         self.owner_user = get_user_model().objects.create_user(
#             username='owner123',
#             email='owner123@mail.com',
#             password='test123'
#         )
#
#         self.member_user = get_user_model().objects.create_user(
#             username='member123',
#             email='member123@mail.com',
#             password='test123'
#         )
#
#         self.other_user = get_user_model().objects.create_user(
#             username='other123',
#             email='other123@mail.com',
#             password='test123'
#         )
#
#         self.public_user = get_user_model().objects.create_user(
#             username='public123',
#             email='public123@mail.com',
#             password='test123'
#         )
#
#         self.public_group = StudyGroup.objects.create(
#             owner=self.owner_user,
#             name='Public Bookmark Group',
#             description='Public group for bookmark toggle tests',
#             visibility=StudyGroup.Visibility.PUBLIC,
#             topic='Django'
#         )
#
#         self.private_group = StudyGroup.objects.create(
#             owner=self.owner_user,
#             name='Private Bookmark Group',
#             description='Private group for bookmark toggle tests',
#             visibility=StudyGroup.Visibility.PRIVATE,
#             topic='DRF'
#         )
#
#         GroupMembership.objects.create(
#             group=self.private_group,
#             user=self.member_user,
#             role=GroupMembership.Role.MEMBER,
#             status=GroupMembership.Status.ACTIVE
#         )
#
#         self.public_post = GroupPost.objects.create(
#             group=self.public_group,
#             author=self.owner_user,
#             title='Public bookmark post',
#             content='Public bookmark content'
#         )
#
#         self.private_post = GroupPost.objects.create(
#             group=self.private_group,
#             author=self.member_user,
#             title='Private bookmark post',
#             content='Private bookmark content'
#         )
#
#         self.existing_bookmark = Bookmark.objects.create(
#             post=self.private_post,
#             user=self.member_user
#         )
#
#     def test_member_can_create_bookmark(self):
#         self.client.force_authenticate(user=self.owner_user)
#
#         response = self.client.post(reverse('community:api_bookmarks_toggle', kwargs={'post_id': self.private_post.id}))
#
#         self.assertEqual(response.status_code, status.HTTP_201_CREATED)
#         self.assertTrue(Bookmark.objects.filter(user=self.owner_user, post=self.private_post).exists())
#
#     def test_reclick_deletes_bookmark(self):
#         self.client.force_authenticate(user=self.member_user)
#
#         response = self.client.post(reverse('community:api_bookmarks_toggle', kwargs={'post_id': self.private_post.id}))
#
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertFalse(Bookmark.objects.filter(user=self.member_user, post=self.private_post).exists())
#
#     def test_repeated_bookmark_request_does_not_create_duplicate(self):
#         self.client.force_authenticate(user=self.public_user)
#
#         url = reverse(
#             'community:api_bookmarks_toggle',
#             kwargs={'post_id': self.public_post.id}
#         )
#
#         self.client.post(url, format='json')
#
#         bookmarks_count_after_first_request = Bookmark.objects.filter(
#             post=self.public_post,
#             user=self.public_user
#         ).count()
#
#         self.client.post(url, format='json')
#
#         bookmarks_count_after_second_request = Bookmark.objects.filter(
#             post=self.public_post,
#             user=self.public_user
#         ).count()
#
#         self.assertEqual(bookmarks_count_after_first_request, 1)
#         self.assertEqual(bookmarks_count_after_second_request, 0)
#
#     def test_user_can_bookmark_public_group_post(self):
#         self.client.force_authenticate(user=self.member_user)
#
#         response = self.client.post(reverse('community:api_bookmarks_toggle', kwargs={'post_id': self.public_post.id}))
#
#         self.assertEqual(response.status_code, status.HTTP_201_CREATED)
#         self.assertTrue(Bookmark.objects.filter(post=self.public_post, user=self.member_user).exists())
#
#     def test_not_member_cant_bookmark_private_group_post(self):
#         self.client.force_authenticate(user=self.other_user)
#
#         response = self.client.post(reverse('community:api_bookmarks_toggle', kwargs={'post_id': self.private_post.id}))
#
#         self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
#         self.assertFalse(Bookmark.objects.filter(post=self.private_post, user=self.other_user).exists())
#
#     def test_moderator_group_can_bookmark_private_group_post(self):
#         self.client.force_authenticate(user=self.owner_user)
#
#         response = self.client.post(reverse('community:api_bookmarks_toggle', kwargs={'post_id': self.private_post.id}))
#
#         self.assertEqual(response.status_code, status.HTTP_201_CREATED)
#         self.assertTrue(Bookmark.objects.filter(user=self.owner_user, post=self.private_post).exists())
#
#     def test_anonymous_user_cant_bookmark_any_post(self):
#         response = self.client.post(reverse('community:api_bookmarks_toggle', kwargs={'post_id': self.public_post.id}))
#
#         self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
#
#
#
#
# class GroupFeedViewTest(TestCase):
#     def setUp(self):
#         self.owner_user = get_user_model().objects.create_user(
#             username='owner123',
#             email='owner123@mail.com',
#             password='test123'
#         )
#
#         self.member_user = get_user_model().objects.create_user(
#             username='member123',
#             email='member123@mail.com',
#             password='test123'
#         )
#
#         self.other_user = get_user_model().objects.create_user(
#             username='other123',
#             email='other123@mail.com',
#             password='test123'
#         )
#
#         self.public_group = StudyGroup.objects.create(
#             owner=self.owner_user,
#             name='Public Bookmark Group',
#             description='Public group for bookmark toggle tests',
#             visibility=StudyGroup.Visibility.PUBLIC,
#             topic='Django'
#         )
#
#         self.private_group = StudyGroup.objects.create(
#             owner=self.owner_user,
#             name='Private Bookmark Group',
#             description='Private group for bookmark toggle tests',
#             visibility=StudyGroup.Visibility.PRIVATE,
#             topic='DRF'
#         )
#
#         GroupMembership.objects.create(
#             group=self.private_group,
#             user=self.member_user,
#             role=GroupMembership.Role.MEMBER,
#             status=GroupMembership.Status.ACTIVE
#         )
#
#         self.public_post = GroupPost.objects.create(
#             group=self.public_group,
#             author=self.owner_user,
#             title='Public bookmark post',
#             content='Public bookmark content'
#         )
#
#         self.private_post = GroupPost.objects.create(
#             group=self.private_group,
#             author=self.member_user,
#             title='Private bookmark post',
#             content='Private bookmark content'
#         )
#
#
#
#     def test_member_can_see_feed(self):
#         self.client.login(username='member123', password='test123')
#
#         response = self.client.get(reverse('community:feed', kwargs={'group_id': self.private_group.id}))
#
#         self.assertEqual(response.status_code, 200)
#         self.assertContains(response, 'Private bookmark post')
#         self.assertIn('group',response.context)
#         self.assertIn('posts',response.context)
#         self.assertTemplateUsed(response,'community/feed.html')
#
#         self.assertIn(self.private_post, response.context['posts'])
#         self.assertNotIn(self.public_post, response.context['posts'])
#
#     def test_not_member_cant_see_feed(self):
#         self.client.login(username='other123', password='test123')
#
#         response = self.client.get(reverse('community:feed', kwargs={'group_id': self.private_group.id}))
#
#         self.assertEqual(response.status_code, 403)
#
#     def test_user_can_see_public_group_feed(self):
#         self.client.login(username='other123', password='test123')
#
#         response = self.client.get(reverse('community:feed', kwargs={'group_id': self.public_group.id}))
#
#         self.assertEqual(response.status_code, 200)
#         self.assertIn('posts', response.context)
#         self.assertIn('group', response.context)
#         self.assertContains(response,'Public bookmark post')
#
#
#
# class PostDetailViewTest(TestCase):
#     def setUp(self):
#         self.owner_user = get_user_model().objects.create_user(
#             username='owner123',
#             email='owner123@mail.com',
#             password='test123'
#         )
#
#         self.member_user = get_user_model().objects.create_user(
#             username='member123',
#             email='member123@mail.com',
#             password='test123'
#         )
#
#         self.moderator_user = get_user_model().objects.create_user(
#             username='moder123',
#             email='moder123@mail.com',
#             password='test123'
#         )
#
#         self.other_user = get_user_model().objects.create_user(
#             username='other123',
#             email='other123@mail.com',
#             password='test123'
#         )
#
#         self.public_group = StudyGroup.objects.create(
#             owner=self.owner_user,
#             name='Public Bookmark Group',
#             description='Public group for bookmark toggle tests',
#             visibility=StudyGroup.Visibility.PUBLIC,
#             topic='Django'
#         )
#
#         self.private_group = StudyGroup.objects.create(
#             owner=self.owner_user,
#             name='Private Bookmark Group',
#             description='Private group for bookmark toggle tests',
#             visibility=StudyGroup.Visibility.PRIVATE,
#             topic='DRF'
#         )
#
#         GroupMembership.objects.create(
#             group=self.private_group,
#             user=self.member_user,
#             role=GroupMembership.Role.MEMBER,
#             status=GroupMembership.Status.ACTIVE
#         )
#
#         GroupMembership.objects.create(
#             group=self.private_group,
#             user=self.moderator_user,
#             role=GroupMembership.Role.MODERATOR,
#             status=GroupMembership.Status.ACTIVE
#         )
#
#         self.public_post = GroupPost.objects.create(
#             group=self.public_group,
#             author=self.owner_user,
#             title='Public bookmark post',
#             content='Public bookmark content'
#         )
#
#         self.private_post = GroupPost.objects.create(
#             group=self.private_group,
#             author=self.member_user,
#             title='Private bookmark post',
#             content='Private bookmark content'
#         )
#
#         self.comment = Comment.objects.create(
#             post=self.private_post,
#             author=self.member_user,
#             context='Test comment'
#         )
#
#         self.reaction = Reaction.objects.create(
#             post=self.private_post,
#             user=self.member_user,
#             type=Reaction.Type.LIKE
#         )
#
#         self.bookmark = Bookmark.objects.create(
#             post=self.private_post,
#             user=self.member_user
#         )
#
#     def test_member_can_see_detail(self):
#         self.client.login(username='member123', password='test123')
#
#         response = self.client.get(reverse('community:post_detail', kwargs={'post_id': self.private_post.id}))
#
#         self.assertEqual(response.status_code, 200)
#         self.assertContains(response,'Private bookmark post')
#         self.assertContains(response,'Private bookmark content')
#         self.assertContains(response, self.comment.context)
#
#         self.assertEqual(response.context['comments_count'], 1)
#         self.assertEqual(response.context['reactions_count'], 1)
#         self.assertEqual(response.context['bookmarks_count'], 1)
#
#         self.assertIn('post', response.context)
#         self.assertTemplateUsed(response,'community/post_detail.html')
#
#     def test_owner_and_moderator_sees_manage_button(self):
#         self.client.login(username='owner123', password='test123')
#         response_owner = self.client.get(reverse('community:post_detail', kwargs={'post_id': self.private_post.id}))
#         self.client.logout()
#
#         self.client.login(username='moder123', password='test123')
#         response_moder = self.client.get(reverse('community:post_detail', kwargs={'post_id': self.private_post.id}))
#
#         self.assertEqual(response_moder.status_code, 200)
#         self.assertEqual(response_owner.status_code, 200)
#         self.assertTrue(response_owner.context['can_manage_post'])
#         self.assertTrue(response_moder.context['can_manage_post'])
#
#
#
# class PostCreateViewTest(TestCase):
#     def setUp(self):
#         self.owner_user = get_user_model().objects.create_user(
#             username='owner123',
#             email='owner123@mail.com',
#             password='test123'
#         )
#
#         self.member_user = get_user_model().objects.create_user(
#             username='member123',
#             email='member123@mail.com',
#             password='test123'
#         )
#
#         self.moderator_user = get_user_model().objects.create_user(
#             username='moder123',
#             email='moder123@mail.com',
#             password='test123'
#         )
#
#         self.other_user = get_user_model().objects.create_user(
#             username='other123',
#             email='other123@mail.com',
#             password='test123'
#         )
#
#         self.public_group = StudyGroup.objects.create(
#             owner=self.owner_user,
#             name='Public Bookmark Group',
#             description='Public group for bookmark toggle tests',
#             visibility=StudyGroup.Visibility.PUBLIC,
#             topic='Django'
#         )
#
#         self.private_group = StudyGroup.objects.create(
#             owner=self.owner_user,
#             name='Private Bookmark Group',
#             description='Private group for bookmark toggle tests',
#             visibility=StudyGroup.Visibility.PRIVATE,
#             topic='DRF'
#         )
#
#         GroupMembership.objects.create(
#             group=self.private_group,
#             user=self.member_user,
#             role=GroupMembership.Role.MEMBER,
#             status=GroupMembership.Status.ACTIVE
#         )
#
#         GroupMembership.objects.create(
#             group=self.private_group,
#             user=self.moderator_user,
#             role=GroupMembership.Role.MODERATOR,
#             status=GroupMembership.Status.ACTIVE
#         )
#
#         self.public_post = GroupPost.objects.create(
#             group=self.public_group,
#             author=self.owner_user,
#             title='Public bookmark post',
#             content='Public bookmark content'
#         )
#
#         self.private_post = GroupPost.objects.create(
#             group=self.private_group,
#             author=self.member_user,
#             title='Private bookmark post',
#             content='Private bookmark content'
#         )
#
#     def test_member_can_open_create_post_page(self):
#         self.client.login(username='member123', password='test123')
#
#         response = self.client.get(reverse('community:post_create', kwargs={'group_id': self.private_group.id}))
#
#         self.assertEqual(response.status_code, 200)
#         self.assertTemplateUsed(response, 'community/post_create.html')
#         self.assertIn('form', response.context)
#
#     def test_member_can_create_post_page(self):
#         self.client.login(username='member123', password='test123')
#
#         response = self.client.post(reverse('community:post_create', kwargs={'group_id': self.private_group.id}), data={
#             'title': "Creating post",
#             'content': "Content of post"
#         })
#
#         self.assertEqual(response.status_code, 302)
#         self.assertRedirects(response, reverse('community:feed', kwargs={'group_id': self.private_group.id}))
#
#     def test_not_member_can_create_post(self):
#         self.client.login(username='other123', password='test123')
#
#         response = self.client.post(reverse('community:post_create', kwargs={'group_id': self.private_group.id}), data={
#             'title': "Creating post",
#             'content': "Content of post"
#         })
#
#         self.assertEqual(response.status_code, 403)
#         self.assertFalse(GroupPost.objects.filter(group=self.private_group, title="Creating post").exists())
#
#
# class PostUpdateViewTest(TestCase):
#     def setUp(self):
#         self.owner_user = get_user_model().objects.create_user(
#             username='owner123',
#             email='owner123@mail.com',
#             password='test123'
#         )
#         self.author_user = get_user_model().objects.create_user(
#             username='author123',
#             email='author123@mail.com',
#             password='test123'
#         )
#         self.other_user = get_user_model().objects.create_user(
#             username='other123',
#             email='other123@mail.com',
#             password='test123'
#         )
#
#         self.private_group = StudyGroup.objects.create(
#             owner=self.owner_user,
#             name='Private Group',
#             description='Private group',
#             visibility=StudyGroup.Visibility.PRIVATE,
#             topic='Django'
#         )
#
#         GroupMembership.objects.create(
#             group=self.private_group,
#             user=self.author_user,
#             role=GroupMembership.Role.MEMBER,
#             status=GroupMembership.Status.ACTIVE
#         )
#
#         self.post = GroupPost.objects.create(
#             group=self.private_group,
#             author=self.author_user,
#             title='Old title',
#             content='Old content'
#         )
#
#     def test_author_can_open_update_page(self):
#         self.client.login(username='author123', password='test123')
#
#         response = self.client.get(
#             reverse('community:post_update', kwargs={'post_id': self.post.id})
#         )
#
#         self.assertEqual(response.status_code, 200)
#         self.assertTemplateUsed(response, 'community/post_create.html')
#         self.assertIn('form', response.context)
#         self.assertTrue(response.context['is_update'])
#
#     def test_author_can_update_post(self):
#         self.client.login(username='author123', password='test123')
#
#         response = self.client.post(
#             reverse('community:post_update', kwargs={'post_id': self.post.id}),
#             data={
#                 'title': 'Updated web title',
#                 'content': 'Updated web content'
#             }
#         )
#
#         self.assertEqual(response.status_code, 302)
#
#         self.post.refresh_from_db()
#
#         self.assertEqual(self.post.title, 'Updated web title')
#         self.assertEqual(self.post.content, 'Updated web content')
#
#     def test_not_author_cannot_update_post(self):
#         self.client.login(username='other123', password='test123')
#
#         response = self.client.post(
#             reverse('community:post_update', kwargs={'post_id': self.post.id}),
#             data={
#                 'title': 'Wrong update',
#                 'content': 'Wrong content'
#             }
#         )
#
#         self.assertEqual(response.status_code, 403)
#
#         self.post.refresh_from_db()
#
#         self.assertEqual(self.post.title, 'Old title')
#         self.assertEqual(self.post.content, 'Old content')
#
#
# class PostDeleteViewTest(TestCase):
#     def setUp(self):
#         self.owner_user = get_user_model().objects.create_user(
#             username='owner123',
#             email='owner123@mail.com',
#             password='test123'
#         )
#         self.author_user = get_user_model().objects.create_user(
#             username='author123',
#             email='author123@mail.com',
#             password='test123'
#         )
#         self.moderator_user = get_user_model().objects.create_user(
#             username='moder123',
#             email='moder123@mail.com',
#             password='test123'
#         )
#         self.member_user = get_user_model().objects.create_user(
#             username='member123',
#             email='member123@mail.com',
#             password='test123'
#         )
#
#         self.private_group = StudyGroup.objects.create(
#             owner=self.owner_user,
#             name='Private Group',
#             description='Private group',
#             visibility=StudyGroup.Visibility.PRIVATE,
#             topic='Django'
#         )
#
#         GroupMembership.objects.create(
#             group=self.private_group,
#             user=self.author_user,
#             role=GroupMembership.Role.MEMBER,
#             status=GroupMembership.Status.ACTIVE
#         )
#
#         GroupMembership.objects.create(
#             group=self.private_group,
#             user=self.moderator_user,
#             role=GroupMembership.Role.MODERATOR,
#             status=GroupMembership.Status.ACTIVE
#         )
#
#         GroupMembership.objects.create(
#             group=self.private_group,
#             user=self.member_user,
#             role=GroupMembership.Role.MEMBER,
#             status=GroupMembership.Status.ACTIVE
#         )
#
#         self.post = GroupPost.objects.create(
#             group=self.private_group,
#             author=self.author_user,
#             title='Post to delete',
#             content='Post content'
#         )
#
#     def test_author_can_delete_post(self):
#         self.client.login(username='author123', password='test123')
#
#         response = self.client.post(
#             reverse('community:post_delete', kwargs={'post_id': self.post.id})
#         )
#
#         self.assertEqual(response.status_code, 302)
#         self.assertFalse(
#             GroupPost.objects.filter(id=self.post.id).exists()
#         )
#
#     def test_moderator_can_delete_post(self):
#         post = GroupPost.objects.create(
#             group=self.private_group,
#             author=self.author_user,
#             title='Post moderator deletes',
#             content='Post content'
#         )
#
#         self.client.login(username='moder123', password='test123')
#
#         response = self.client.post(
#             reverse('community:post_delete', kwargs={'post_id': post.id})
#         )
#
#         self.assertEqual(response.status_code, 302)
#         self.assertFalse(
#             GroupPost.objects.filter(id=post.id).exists()
#         )
#
#     def test_regular_member_cannot_delete_other_user_post(self):
#         self.client.login(username='member123', password='test123')
#
#         response = self.client.post(
#             reverse('community:post_delete', kwargs={'post_id': self.post.id})
#         )
#
#         self.assertEqual(response.status_code, 403)
#         self.assertTrue(
#             GroupPost.objects.filter(id=self.post.id).exists()
#         )
#
#     def test_owner_can_delete_post(self):
#         self.client.login(username='owner123', password='test123')
#
#         response = self.client.post(
#             reverse('community:post_delete', kwargs={'post_id': self.post.id})
#         )
#
#         self.assertEqual(response.status_code, 302)
#         self.assertFalse(
#             GroupPost.objects.filter(id=self.post.id).exists()
#         )
#
#     def test_regular_member_cannot_delete_other_user_post(self):
#         self.client.login(username='member123', password='test123')
#
#         response = self.client.post(
#             reverse('community:post_delete', kwargs={'post_id': self.post.id})
#         )
#
#         self.assertEqual(response.status_code, 403)
#         self.assertTrue(
#             GroupPost.objects.filter(id=self.post.id).exists()
#         )
#
#     class CommentWebViewTest(TestCase):
#         def setUp(self):
#             self.owner_user = get_user_model().objects.create_user(
#                 username='owner123', email='owner123@mail.com', password='test123'
#             )
#             self.author_user = get_user_model().objects.create_user(
#                 username='author123', email='author123@mail.com', password='test123'
#             )
#             self.member_user = get_user_model().objects.create_user(
#                 username='member123', email='member123@mail.com', password='test123'
#             )
#             self.moderator_user = get_user_model().objects.create_user(
#                 username='moder123', email='moder123@mail.com', password='test123'
#             )
#             self.other_user = get_user_model().objects.create_user(
#                 username='other123', email='other123@mail.com', password='test123'
#             )
#
#             self.private_group = StudyGroup.objects.create(
#                 owner=self.owner_user,
#                 name='Private Group',
#                 description='Private group',
#                 visibility=StudyGroup.Visibility.PRIVATE,
#                 topic='Django'
#             )
#
#             GroupMembership.objects.create(
#                 group=self.private_group,
#                 user=self.author_user,
#                 role=GroupMembership.Role.MEMBER,
#                 status=GroupMembership.Status.ACTIVE
#             )
#             GroupMembership.objects.create(
#                 group=self.private_group,
#                 user=self.member_user,
#                 role=GroupMembership.Role.MEMBER,
#                 status=GroupMembership.Status.ACTIVE
#             )
#             GroupMembership.objects.create(
#                 group=self.private_group,
#                 user=self.moderator_user,
#                 role=GroupMembership.Role.MODERATOR,
#                 status=GroupMembership.Status.ACTIVE
#             )
#
#             self.post = GroupPost.objects.create(
#                 group=self.private_group,
#                 author=self.author_user,
#                 title='Test post',
#                 content='Test post content'
#             )
#
#             self.comment = Comment.objects.create(
#                 post=self.post,
#                 author=self.author_user,
#                 context='Original comment'
#             )
#
#         def test_member_can_create_comment(self):
#             self.client.login(username='member123', password='test123')
#
#             response = self.client.post(
#                 reverse('community:comment_create', kwargs={'post_id': self.post.id}),
#                 data={'context': 'New comment'}
#             )
#
#             self.assertEqual(response.status_code, 302)
#             self.assertTrue(
#                 Comment.objects.filter(
#                     post=self.post,
#                     author=self.member_user,
#                     context='New comment'
#                 ).exists()
#             )
#
#         def test_not_member_cannot_create_comment(self):
#             self.client.login(username='other123', password='test123')
#
#             response = self.client.post(
#                 reverse('community:comment_create', kwargs={'post_id': self.post.id}),
#                 data={'context': 'Wrong comment'}
#             )
#
#             self.assertEqual(response.status_code, 403)
#             self.assertFalse(
#                 Comment.objects.filter(context='Wrong comment').exists()
#             )
#
#         def test_comment_author_can_update_comment(self):
#             self.client.login(username='author123', password='test123')
#
#             response = self.client.post(
#                 reverse(
#                     'community:comment_update',
#                     kwargs={
#                         'post_id': self.post.id,
#                         'comment_id': self.comment.id
#                     }
#                 ),
#                 data={'context': 'Updated comment'}
#             )
#
#             self.assertEqual(response.status_code, 302)
#
#             self.comment.refresh_from_db()
#             self.assertEqual(self.comment.context, 'Updated comment')
#
#         def test_comment_author_can_delete_comment(self):
#             self.client.login(username='author123', password='test123')
#
#             response = self.client.post(
#                 reverse(
#                     'community:comment_delete',
#                     kwargs={
#                         'post_id': self.post.id,
#                         'comment_id': self.comment.id
#                     }
#                 )
#             )
#
#             self.assertEqual(response.status_code, 302)
#             self.assertFalse(
#                 Comment.objects.filter(id=self.comment.id).exists()
#             )
#
#         def test_moderator_can_delete_comment(self):
#             comment = Comment.objects.create(
#                 post=self.post,
#                 author=self.member_user,
#                 context='Comment for moderator delete'
#             )
#
#             self.client.login(username='moder123', password='test123')
#
#             response = self.client.post(
#                 reverse(
#                     'community:comment_delete',
#                     kwargs={
#                         'post_id': self.post.id,
#                         'comment_id': comment.id
#                     }
#                 )
#             )
#
#             self.assertEqual(response.status_code, 302)
#             self.assertFalse(Comment.objects.filter(id=comment.id).exists())
#
#         def test_owner_can_delete_comment(self):
#             comment = Comment.objects.create(
#                 post=self.post,
#                 author=self.member_user,
#                 context='Comment for owner delete'
#             )
#
#             self.client.login(username='owner123', password='test123')
#
#             response = self.client.post(
#                 reverse(
#                     'community:comment_delete',
#                     kwargs={
#                         'post_id': self.post.id,
#                         'comment_id': comment.id
#                     }
#                 )
#             )
#
#             self.assertEqual(response.status_code, 302)
#             self.assertFalse(Comment.objects.filter(id=comment.id).exists())
#
#
# class ReactionBookmarkWebViewTest(TestCase):
#     def setUp(self):
#         self.owner_user = get_user_model().objects.create_user(
#             username='owner123', email='owner123@mail.com', password='test123'
#         )
#         self.member_user = get_user_model().objects.create_user(
#             username='member123', email='member123@mail.com', password='test123'
#         )
#         self.other_user = get_user_model().objects.create_user(
#             username='other123', email='other123@mail.com', password='test123'
#         )
#
#         self.private_group = StudyGroup.objects.create(
#             owner=self.owner_user,
#             name='Private Group',
#             description='Private group',
#             visibility=StudyGroup.Visibility.PRIVATE,
#             topic='Django'
#         )
#
#         GroupMembership.objects.create(
#             group=self.private_group,
#             user=self.member_user,
#             role=GroupMembership.Role.MEMBER,
#             status=GroupMembership.Status.ACTIVE
#         )
#
#         self.post = GroupPost.objects.create(
#             group=self.private_group,
#             author=self.member_user,
#             title='Reaction post',
#             content='Reaction post content'
#         )
#
#     def test_form_post_creates_reaction(self):
#         self.client.login(username='member123', password='test123')
#
#         response = self.client.post(
#             reverse('community:reaction_create', kwargs={'post_id': self.post.id}),
#             data={'type': Reaction.Type.LIKE}
#         )
#
#         self.assertEqual(response.status_code, 302)
#         self.assertTrue(
#             Reaction.objects.filter(
#                 post=self.post,
#                 user=self.member_user,
#                 type=Reaction.Type.LIKE
#             ).exists()
#         )
#
#     def test_repeated_reaction_post_deletes_reaction(self):
#         Reaction.objects.create(
#             post=self.post,
#             user=self.member_user,
#             type=Reaction.Type.LIKE
#         )
#
#         self.client.login(username='member123', password='test123')
#
#         response = self.client.post(
#             reverse('community:reaction_create', kwargs={'post_id': self.post.id}),
#             data={
#                 'type': Reaction.Type.LIKE,
#                 'remove': '1'
#             }
#         )
#
#         self.assertEqual(response.status_code, 302)
#         self.assertFalse(
#             Reaction.objects.filter(
#                 post=self.post,
#                 user=self.member_user
#             ).exists()
#         )
#
#     def test_reaction_post_changes_existing_reaction(self):
#         Reaction.objects.create(
#             post=self.post,
#             user=self.member_user,
#             type=Reaction.Type.LIKE
#         )
#
#         self.client.login(username='member123', password='test123')
#
#         response = self.client.post(
#             reverse('community:reaction_create', kwargs={'post_id': self.post.id}),
#             data={'type': Reaction.Type.HELPFUL}
#         )
#
#         self.assertEqual(response.status_code, 302)
#
#         reaction = Reaction.objects.get(post=self.post, user=self.member_user)
#         self.assertEqual(reaction.type, Reaction.Type.HELPFUL)
#
#     def test_not_member_private_group_cannot_react(self):
#         self.client.login(username='other123', password='test123')
#
#         response = self.client.post(
#             reverse('community:reaction_create', kwargs={'post_id': self.post.id}),
#             data={'type': Reaction.Type.LIKE}
#         )
#
#         self.assertEqual(response.status_code, 403)
#         self.assertFalse(
#             Reaction.objects.filter(post=self.post, user=self.other_user).exists()
#         )
#
#     def test_form_post_creates_bookmark(self):
#         self.client.login(username='member123', password='test123')
#
#         response = self.client.post(
#             reverse('community:bookmark_create', kwargs={'post_id': self.post.id})
#         )
#
#         self.assertEqual(response.status_code, 302)
#         self.assertTrue(
#             Bookmark.objects.filter(
#                 post=self.post,
#                 user=self.member_user
#             ).exists()
#         )
#
#     def test_repeated_bookmark_post_deletes_bookmark(self):
#         Bookmark.objects.create(
#             post=self.post,
#             user=self.member_user
#         )
#
#         self.client.login(username='member123', password='test123')
#
#         response = self.client.post(
#             reverse('community:bookmark_create', kwargs={'post_id': self.post.id}),
#             data={'remove': '1'}
#         )
#
#         self.assertEqual(response.status_code, 302)
#         self.assertFalse(
#             Bookmark.objects.filter(
#                 post=self.post,
#                 user=self.member_user
#             ).exists()
#         )
#
#     def test_not_member_private_group_cannot_bookmark(self):
#         self.client.login(username='other123', password='test123')
#
#         response = self.client.post(
#             reverse('community:bookmark_create', kwargs={'post_id': self.post.id})
#         )
#
#         self.assertEqual(response.status_code, 403)
#         self.assertFalse(
#             Bookmark.objects.filter(post=self.post, user=self.other_user).exists()
#         )
#
# class BookmarkedPostsListViewTest(TestCase):
#     def setUp(self):
#         self.user = get_user_model().objects.create_user(
#             username='user123', email='user123@mail.com', password='test123'
#         )
#         self.other_user = get_user_model().objects.create_user(
#             username='other123', email='other123@mail.com', password='test123'
#         )
#         self.empty_user = get_user_model().objects.create_user(
#             username='empty123', email='empty123@mail.com', password='test123'
#         )
#
#         self.group = StudyGroup.objects.create(
#             owner=self.user,
#             name='Bookmark Group',
#             description='Bookmark group',
#             visibility=StudyGroup.Visibility.PUBLIC,
#             topic='Django'
#         )
#
#         self.post = GroupPost.objects.create(
#             group=self.group,
#             author=self.user,
#             title='My bookmarked post',
#             content='Content'
#         )
#
#         self.other_post = GroupPost.objects.create(
#             group=self.group,
#             author=self.other_user,
#             title='Other bookmarked post',
#             content='Other content'
#         )
#
#         self.bookmark = Bookmark.objects.create(
#             post=self.post,
#             user=self.user
#         )
#
#         self.other_bookmark = Bookmark.objects.create(
#             post=self.other_post,
#             user=self.other_user
#         )
#
#     def test_user_sees_own_bookmarked_posts(self):
#         self.client.login(username='user123', password='test123')
#
#         response = self.client.get(reverse('community:posts_bookmarked'))
#
#         self.assertEqual(response.status_code, 200)
#         self.assertTemplateUsed(response, 'community/bookmarked_posts.html')
#         self.assertContains(response, 'My bookmarked post')
#
#     def test_user_does_not_see_other_users_bookmarks(self):
#         self.client.login(username='user123', password='test123')
#
#         response = self.client.get(reverse('community:posts_bookmarked'))
#
#         self.assertContains(response, 'My bookmarked post')
#         self.assertNotContains(response, 'Other bookmarked post')
#
#     def test_empty_bookmarks_page_works(self):
#         self.client.login(username='empty123', password='test123')
#
#         response = self.client.get(reverse('community:posts_bookmarked'))
#
#         self.assertEqual(response.status_code, 200)
#         self.assertEqual(list(response.context['bookmarks']), [])



class CommunityServicesTest(APITestCase):
    def setUp(self):
        self.owner_user = get_user_model().objects.create_user(
                    username='owner123', email='owner123@mail.com', password='test123'
                )
        self.member_user = get_user_model().objects.create_user(
                    username='member123', email='member123@mail.com', password='test123'
                )
        self.other_user = get_user_model().objects.create_user(
                    username='other123', email='other123@mail.com', password='test123'
                )

        self.private_group = StudyGroup.objects.create(
                    owner=self.owner_user,
                    name='Private Group',
                    description='Private group',
                    visibility=StudyGroup.Visibility.PRIVATE,
                    topic='Django'
                )

        GroupMembership.objects.create(
                    group=self.private_group,
                    user=self.member_user,
                    role=GroupMembership.Role.MEMBER,
                    status=GroupMembership.Status.ACTIVE
                )

        self.post = GroupPost.objects.create(
                    group=self.private_group,
                    author=self.member_user,
                    title='Reaction post',
                    content='Reaction post content'
                )

        self.reaction1 = Reaction.objects.create(
            post=self.post,
            user=self.owner_user,
            type=Reaction.Type.LIKE
        )

        self.bookmark = Bookmark.objects.create(
            post=self.post,
            user=self.owner_user
        )



    def test_invalid_toggle_reaction(self):

        reaction, result = toggle_reaction(user=self.member_user, post=self.post, reaction_type='bad', remove=False)

        self.assertIsNone(reaction)
        self.assertEqual(result, 'invalid')
        self.assertFalse(Reaction.objects.filter(post=self.post, user=self.member_user).exists())

    def test_deleted_toggle_reaction(self):
        reaction, result = toggle_reaction(user=self.owner_user, post=self.post, reaction_type=self.reaction1.type, remove=True)

        self.assertIsNone(reaction)
        self.assertEqual(result, 'deleted')
        self.assertFalse(Reaction.objects.filter(post=self.post, user=self.owner_user).exists())

    def test_created_toggle_reaction(self):
        reaction, result = toggle_reaction(user=self.member_user, post=self.post, reaction_type=Reaction.Type.CELEBRATE, remove=False)

        self.assertIsNotNone(reaction)
        self.assertEqual(result, 'created')
        self.assertTrue(Reaction.objects.filter(post=self.post, user=self.member_user).exists())
        self.assertEqual(reaction.type, Reaction.Type.CELEBRATE)

    def test_updated_toggle_reaction(self):
        reaction, result = toggle_reaction(user=self.owner_user, post=self.post, reaction_type=Reaction.Type.CELEBRATE, remove=False)

        self.assertIsNotNone(reaction)
        self.assertEqual(result, 'updated')
        self.reaction1.refresh_from_db()
        self.assertTrue(Reaction.objects.filter(post=self.post, user=self.owner_user).exists())
        self.assertEqual(reaction.type, Reaction.Type.CELEBRATE)
        self.assertEqual(reaction.user, self.owner_user)

    def test_delete_toggle_bookmark(self):
        result = toggle_bookmark(user=self.owner_user, post=self.post, remove=True)

        self.assertIsNone(result)
        self.assertFalse(Bookmark.objects.filter(user=self.owner_user, post=self.post).exists())

    def test_create_toggle_bookmark(self):
        result = toggle_bookmark(user=self.member_user, post=self.post, remove=False)

        self.assertIsNotNone(result)
        self.assertTrue(Bookmark.objects.filter(user=self.member_user, post=self.post).exists())
        self.assertEqual(result.post, self.post)
        self.assertEqual(result.user, self.member_user)

    def test_not_member_user_can_access_group(self):
        result = user_can_access_group(user=self.other_user, group=self.private_group)
        self.assertFalse(result)

    def test_member_user_can_access_group(self):
        result = user_can_access_group(user=self.member_user, group=self.private_group)
        self.assertTrue(result)

    def test_user_can_manage_post(self):
        result = user_can_manage_post(user=self.owner_user, post=self.post)
        self.assertTrue(result)






