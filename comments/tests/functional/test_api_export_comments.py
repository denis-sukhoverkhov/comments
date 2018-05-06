import datetime
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from comments.models import Comment
from freezegun import freeze_time


class ExportCommentApiTest(TestCase):

    def setUp(self):
        self.authorized_user = User.objects.create(username='admin',
                                                   password='admin',
                                                   email='admin@mail.ru',
                                                   is_active=True,
                                                   is_staff=True,
                                                   is_superuser=True)
        self.client = APIClient()
        self.client.force_authenticate(user=self.authorized_user)

    @freeze_time("2018-05-01 00:00:00")
    def test_export_csv(self):
        c_type = ContentType.objects.get_for_model(self.authorized_user)
        com1 = Comment.objects.create(body='com1',
                                      user=self.authorized_user,
                                      content_type=c_type,
                                      object_id=self.authorized_user.id)
        com2 = Comment.objects.create(body='com2',
                                      user=self.authorized_user,
                                      content_type=c_type,
                                      object_id=self.authorized_user.id)

        response = self.client.get(f'/api/user/{self.authorized_user.id}/comment/history/export/csv/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEquals(
            response.get('Content-Disposition'),
            f'attachment; filename="export_comments_user_{self.authorized_user.id}_{datetime.datetime.now()}.csv"'
        )

    @freeze_time("2018-05-01 00:00:00")
    def test_export_csv_with_wrong_dates(self):
        c_type = ContentType.objects.get_for_model(self.authorized_user)
        com1 = Comment.objects.create(body='com1',
                                      user=self.authorized_user,
                                      content_type=c_type,
                                      object_id=self.authorized_user.id)
        com2 = Comment.objects.create(body='com2',
                                      user=self.authorized_user,
                                      content_type=c_type,
                                      object_id=self.authorized_user.id)

        response = self.client.get(f'/api/user/{self.authorized_user.id}/comment/history/export/csv/?'
                                   f'date_start=09.05.2018&date_end=10.05.2018')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEquals(
            response.get('Content-Disposition'),
            f'attachment; filename="export_comments_user_{self.authorized_user.id}_{datetime.datetime.now()}.csv"'
        )

    @freeze_time("2018-05-01 00:00:00")
    def test_export_csv(self):
        c_type = ContentType.objects.get_for_model(self.authorized_user)
        com1 = Comment.objects.create(body='com1',
                                      user=self.authorized_user,
                                      content_type=c_type,
                                      object_id=self.authorized_user.id)
        com2 = Comment.objects.create(body='com2',
                                      user=self.authorized_user,
                                      content_type=c_type,
                                      object_id=self.authorized_user.id)

        response = self.client.get(f'/api/user/{self.authorized_user.id}/comment/history/export/xml/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEquals(
            response.get('Content-Disposition'),
            f'attachment; filename="export_comments_user_{self.authorized_user.id}_{datetime.datetime.now()}.xml"'
        )