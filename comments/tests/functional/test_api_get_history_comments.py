from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from comments.models import Post, Comment


class UserHistoryCommentsTest(TestCase):

    def setUp(self):
        self.authorized_user = User.objects.create(username='admin',
                                                   password='admin',
                                                   email='admin@mail.ru',
                                                   is_active=True,
                                                   is_staff=True,
                                                   is_superuser=True)
        self.client = APIClient()
        self.client.force_authenticate(user=self.authorized_user)

    def test_get_history_comments_empty_answer(self):
        response = self.client.get(f'/api/user/{self.authorized_user.id}/comment/history/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'], [])

    def test_get_history_comments(self):
        c_type = ContentType.objects.get_for_model(self.authorized_user)
        com1 = Comment.objects.create(body='com1',
                                      user=self.authorized_user,
                                      content_type=c_type,
                                      object_id=self.authorized_user.id)
        com2 = Comment.objects.create(body='com2',
                                      user=self.authorized_user,
                                      content_type=c_type,
                                      object_id=self.authorized_user.id)

        comments_for_main_user = (com1, com2)

        another_user = User.objects.create(username='user',
                                           password='user',
                                           email='user@mail.ru')

        com3 = Comment.objects.create(body='com3',
                                      user=another_user,
                                      content_type=c_type,
                                      object_id=self.authorized_user.id)

        response = self.client.get(f'/api/user/{self.authorized_user.id}/comment/history/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), len(comments_for_main_user))
