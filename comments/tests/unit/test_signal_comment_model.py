from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_save
from django.test import TestCase

from comments.models import Comment, Post, CommentHistory
from comments.signals import save_comment_history


class CommentModelTest(TestCase):
    def setUp(self):
        post_save.connect(save_comment_history, sender=Comment)
        self.authorized_user = User.objects.create(username='admin',
                                                   password='admin',
                                                   email='admin@mail.ru',
                                                   is_active=True,
                                                   is_staff=True,
                                                   is_superuser=True)

    def test_create_comment_without_saving_history(self):
        post = Post.objects.create(title='custom title', body='body')
        c_type = ContentType.objects.get_for_model(post)
        comment = Comment.objects.create(body='body',
                                         user=self.authorized_user,
                                         content_type=c_type,
                                         object_id=post.id)
        self.assertIsInstance(comment.content_object, Post)

    def test_update_comment_and_save_history(self):
        c_type = ContentType.objects.get_for_model(self.authorized_user)
        comment = Comment.objects.create(body='parent',
                                         user=self.authorized_user,
                                         content_type=c_type,
                                         object_id=self.authorized_user.id)

        comment.body += 'new word'
        comment.save(user=self.authorized_user)

        history = CommentHistory.objects.first()
        self.assertIsNotNone(history)

    def test_delete_comment_and_save_history(self):
        c_type = ContentType.objects.get_for_model(self.authorized_user)
        comment = Comment.objects.create(body='parent',
                                         user=self.authorized_user,
                                         content_type=c_type,
                                         object_id=self.authorized_user.id)

        comment.delete(user=self.authorized_user)

        history = CommentHistory.objects.first()
        self.assertIsNotNone(history)
        self.assertTrue(history.is_deleted)
