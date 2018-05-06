from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from comments.models import Post, Comment


class CreateCommentApiTest(TestCase):

    def setUp(self):
        self.authorized_user = User.objects.create(username='admin',
                                                   password='admin',
                                                   email='admin@mail.ru',
                                                   is_active=True,
                                                   is_staff=True,
                                                   is_superuser=True)
        self.client = APIClient()
        self.client.force_authenticate(user=self.authorized_user)

    def test_get_comments_recursively_for_entity_comment_if_child_comments_not_exists(self):
        post = Post.objects.create(title='custom title', body='body')
        c_type = ContentType.objects.get_for_model(post)
        comment = Comment.objects.create(body='parent',
                                         user=self.authorized_user,
                                         content_type=c_type,
                                         object_id=post.id)
        entity_type = ContentType.objects.get_for_model(Comment)
        response = self.client.get(f'/api/comment/tree/?entity={entity_type.model}&object_id={comment.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])

    def test_get_comments_recursively_for_entity_post_if_comments_not_exists(self):
        post = Post.objects.create(title='custom title', body='body')
        entity_type = ContentType.objects.get_for_model(post)
        response = self.client.get(f'/api/comment/tree/?entity={entity_type.model}&object_id={post.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])

    def test_get_comments_recursively_for_entity_user_if_comments_not_exists(self):
        entity_type = ContentType.objects.get_for_model(self.authorized_user)
        response = self.client.get(f'/api/comment/tree/?entity={entity_type.model}&object_id={self.authorized_user.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])

    def test_get_comments_recursively_for_entity_comment(self):
        post = Post.objects.create(title='custom title', body='body')
        c_type = ContentType.objects.get_for_model(post)
        entity_type = ContentType.objects.get_for_model(Comment)
        parent_comment = Comment.objects.create(body='parent',
                                                user=self.authorized_user,
                                                content_type=c_type,
                                                object_id=post.id)
        # level 2
        child1 = Comment.objects.create(body='com1',
                                        user=self.authorized_user,
                                        content_type=entity_type,
                                        object_id=parent_comment.id)
        # level 3
        child2 = Comment.objects.create(body='com2',
                                        user=self.authorized_user,
                                        content_type=entity_type,
                                        object_id=child1.id)
        # level 4
        child3 = Comment.objects.create(body='com3',
                                        user=self.authorized_user,
                                        content_type=entity_type,
                                        object_id=child2.id)

        child_list = [child1, child2, child3, ]

        response = self.client.get(f'/api/comment/tree/?entity={entity_type.model}&object_id={parent_comment.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(child_list), len(response.data))

        self.assertEqual([2, 3, 4], [i['level'] for i in response.data])

    def test_get_comments_recursively_for_entity_post(self):
        post = Post.objects.create(title='custom title', body='body')
        entity_type = ContentType.objects.get_for_model(post)

        # level 1
        child1 = Comment.objects.create(body='lev1',
                                        user=self.authorized_user,
                                        content_type=entity_type,
                                        object_id=post.id)
        # level 1
        child2 = Comment.objects.create(body='lev1',
                                        user=self.authorized_user,
                                        content_type=entity_type,
                                        object_id=post.id)
        # level 2
        child3 = Comment.objects.create(body='lev2',
                                        user=self.authorized_user,
                                        content_type=ContentType.objects.get_for_model(child2),
                                        object_id=child2.id)

        child_list = [child1, child2, child3]

        response = self.client.get(f'/api/comment/tree/?entity={entity_type.model}&object_id={post.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(child_list), len(response.data))

        self.assertEqual([1, 1, 2], [i['level'] for i in response.data])

    def test_get_comments_recursively_for_entity_user(self):
        entity_type = ContentType.objects.get_for_model(self.authorized_user)

        # level 1
        child1 = Comment.objects.create(body='lev1',
                                        user=self.authorized_user,
                                        content_type=entity_type,
                                        object_id=self.authorized_user.id)
        # level 2
        child2 = Comment.objects.create(body='lev2',
                                        user=self.authorized_user,
                                        content_type=ContentType.objects.get_for_model(child1),
                                        object_id=child1.id)
        # level 2
        child3 = Comment.objects.create(body='lev2',
                                        user=self.authorized_user,
                                        content_type=ContentType.objects.get_for_model(child1),
                                        object_id=child1.id)

        child_list = [child1, child2, child3]

        response = self.client.get(f'/api/comment/tree/?entity={entity_type.model}&object_id={self.authorized_user.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(child_list), len(response.data))

        self.assertEqual([1, 2, 2], [i['level'] for i in response.data])

    def test_get_comments_recursively_without_object_id(self):
        response = self.client.get(f'/api/comment/tree/')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_comments_recursively_for_entity_comment_without_sending_parameter_entity(self):
        post = Post.objects.create(title='custom title', body='body')
        c_type = ContentType.objects.get_for_model(post)
        comment = Comment.objects.create(body='parent',
                                         user=self.authorized_user,
                                         content_type=c_type,
                                         object_id=post.id)

        # level 2
        child = Comment.objects.create(body='lev2',
                                       user=self.authorized_user,
                                       content_type=ContentType.objects.get_for_model(comment),
                                       object_id=comment.id)

        response = self.client.get(f'/api/comment/tree/?object_id={comment.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual([2], [i['level'] for i in response.data])
