from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from comments.models import Post


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

    def test_api_create_comment(self):
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
