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

    def test_create_comment(self):
        content_type = ContentType.objects.get_for_model(Post)
        post = Post.objects.create(title='custom title', body='body')
        data = {'body': 'interesting',
                'user': self.authorized_user.id,
                'content_type': content_type.id,
                'object_id': post.id,
                }
        response = self.client.post('/api/comment/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        result = response.data
        # pass
        self.assertEqual(result['body'], data['body'])
        self.assertEqual(result['user'], data['user'])
        self.assertEqual(result['content_type'], data['content_type'])
        self.assertEqual(result['object_id'], data['object_id'])
        self.assertTrue('created' in result)

    def test_get_comments_for_entity_comment_if_child_comments_not_exists(self):
        post = Post.objects.create(title='custom title', body='body')
        c_type = ContentType.objects.get_for_model(post)
        parent_comment = Comment.objects.create(body='parent',
                                                user=self.authorized_user,
                                                content_type=c_type,
                                                object_id=post.id)
        response = self.client.get(f'/api/comment/{parent_comment.id}/comment/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])

    def test_get_comments_for_entity_comment_if_child_comments_exists(self):
        post = Post.objects.create(title='custom title', body='body')
        parent_comment = Comment.objects.create(body='parent',
                                                user=self.authorized_user,
                                                content_type=ContentType.objects.get_for_model(post),
                                                object_id=post.id)
        c_type = ContentType.objects.get_for_model(Comment)
        child1 = Comment.objects.create(body='parent',
                                        user=self.authorized_user,
                                        content_type=c_type,
                                        object_id=parent_comment.id)
        child2 = Comment.objects.create(body='parent',
                                        user=self.authorized_user,
                                        content_type=c_type,
                                        object_id=parent_comment.id)
        child3 = Comment.objects.create(body='parent',
                                        user=self.authorized_user,
                                        content_type=c_type,
                                        object_id=parent_comment.id)
        response = self.client.get(f'/api/comment/{parent_comment.id}/comment/')
        child_list = [child1, child2, child3]
        self.assertEqual(len(response.data), len(child_list))

    # def test_get_comments_for_entity_post(self):
    #     # content_type = ContentType.objects.get_for_model(Post)
    #     # post = Post.objects.create(title='custom title', body='body')
    #     # data = {'body': 'interesting',
    #     #         'user': self.authorized_user.id,
    #     #         'content_type': content_type.id,
    #     #         'object_id': post.id,
    #     #         }
    #     response = self.client.post(f'/api/post/{post_id}/comment/', data, format='json')
    #     # self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    #     # result = response.data
    #     # # pass
    #     # self.assertEqual(result['body'], data['body'])
    #     # self.assertEqual(result['user'], data['user'])
    #     # self.assertEqual(result['content_type'], data['content_type'])
    #     # self.assertEqual(result['object_id'], data['object_id'])
    #     # self.assertTrue('created' in result)
    #
    # def test_get_comments_for_entity_user(self):
    #     # content_type = ContentType.objects.get_for_model(Post)
    #     # post = Post.objects.create(title='custom title', body='body')
    #     # data = {'body': 'interesting',
    #     #         'user': self.authorized_user.id,
    #     #         'content_type': content_type.id,
    #     #         'object_id': post.id,
    #     #         }
    #     response = self.client.post(f'/api/user/{user_id}/comment/', data, format='json')
    #     # self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    #     # result = response.data
    #     # # pass
    #     # self.assertEqual(result['body'], data['body'])
    #     # self.assertEqual(result['user'], data['user'])
    #     # self.assertEqual(result['content_type'], data['content_type'])
    #     # self.assertEqual(result['object_id'], data['object_id'])
    #     # self.assertTrue('created' in result)
