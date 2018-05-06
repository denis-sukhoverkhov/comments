from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from comments.models import Post, Comment


class TopLevelCommentApiTest(TestCase):

    def setUp(self):
        self.authorized_user = User.objects.create(username='admin',
                                                   password='admin',
                                                   email='admin@mail.ru',
                                                   is_active=True,
                                                   is_staff=True,
                                                   is_superuser=True)
        self.client = APIClient()
        self.client.force_authenticate(user=self.authorized_user)

    def test_get_comments_for_entity_comment_if_child_comments_not_exists(self):
        post = Post.objects.create(title='custom title', body='body')
        c_type = ContentType.objects.get_for_model(post)
        parent_comment = Comment.objects.create(body='parent',
                                                user=self.authorized_user,
                                                content_type=c_type,
                                                object_id=post.id)
        response = self.client.get(f'/api/comment/comment/{parent_comment.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        res = response.data['results']
        self.assertEqual(res, [])

    def test_get_comments_for_entity_comment_if_child_comments_exists(self):
        post = Post.objects.create(title='custom title', body='body')
        parent_comment = Comment.objects.create(body='parent',
                                                user=self.authorized_user,
                                                content_type=ContentType.objects.get_for_model(post),
                                                object_id=post.id)
        c_type = ContentType.objects.get_for_model(Comment)
        child1 = Comment.objects.create(body='child1',
                                        user=self.authorized_user,
                                        content_type=c_type,
                                        object_id=parent_comment.id)
        child2 = Comment.objects.create(body='child2',
                                        user=self.authorized_user,
                                        content_type=c_type,
                                        object_id=parent_comment.id)
        child3 = Comment.objects.create(body='child3',
                                        user=self.authorized_user,
                                        content_type=c_type,
                                        object_id=parent_comment.id)
        response = self.client.get(f'/api/comment/comment/{parent_comment.id}/')
        child_list = [child1, child2, child3]
        self.assertEqual(len(response.data['results']), len(child_list))

    def test_get_comments_for_entity_post(self):
        post = Post.objects.create(title='custom title', body='body')
        c_type = ContentType.objects.get_for_model(post)
        child1 = Comment.objects.create(body='child1',
                                        user=self.authorized_user,
                                        content_type=c_type,
                                        object_id=post.id)
        child2 = Comment.objects.create(body='child2',
                                        user=self.authorized_user,
                                        content_type=c_type,
                                        object_id=post.id)
        child3 = Comment.objects.create(body='child3',
                                        user=self.authorized_user,
                                        content_type=c_type,
                                        object_id=post.id)

        response = self.client.get(f'/api/comment/post/{post.id}/')
        child_list = [child1, child2, child3]
        self.assertEqual(len(response.data['results']), len(child_list))

    def test_get_comments_for_entity_user(self):
        another_user = User.objects.create(username='user',
                                           password='user',
                                           email='user@mail.ru')
        c_type = ContentType.objects.get_for_model(another_user)
        child1 = Comment.objects.create(body='child1',
                                        user=self.authorized_user,
                                        content_type=c_type,
                                        object_id=another_user.id)
        child2 = Comment.objects.create(body='child2',
                                        user=self.authorized_user,
                                        content_type=c_type,
                                        object_id=another_user.id)
        child3 = Comment.objects.create(body='child3',
                                        user=self.authorized_user,
                                        content_type=c_type,
                                        object_id=another_user.id)
        response = self.client.get(f'/api/comment/user/{another_user.id}/')
        child_list = [child1, child2, child3]
        self.assertEqual(len(response.data['results']), len(child_list))
