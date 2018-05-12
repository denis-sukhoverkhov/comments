from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_save
from django.test import TestCase
from comments.models import Comment, Post
from django.db import IntegrityError

from comments.signals import save_comment_history


class CommentModelTest(TestCase):
    def setUp(self):
        post_save.disconnect(save_comment_history, sender=Comment)
        self.authorized_user = User.objects.create(username='admin',
                                                   password='admin',
                                                   email='admin@mail.ru',
                                                   is_active=True,
                                                   is_staff=True,
                                                   is_superuser=True)

    def test_create_comment_without_binding_to_entity(self):
        with self.assertRaises(IntegrityError) as exc:
            Comment.objects.create(body='body', user=self.authorized_user, )

    def test_create_comment_with_binding_to_post_entity(self):
        post = Post.objects.create(title='custom title', body='body')
        c_type = ContentType.objects.get_for_model(post)
        comment = Comment.objects.create(body='body',
                                         user=self.authorized_user,
                                         content_type=c_type,
                                         object_id=post.id)
        self.assertIsInstance(comment.content_object, Post)

    def test_create_comment_with_binding_to_comment_entity(self):
        post = Post.objects.create(title='custom title', body='body')
        c_type = ContentType.objects.get_for_model(post)
        parent_comment = Comment.objects.create(body='parent',
                                                user=self.authorized_user,
                                                content_type=c_type,
                                                object_id=post.id)

        c_type_for_comment = ContentType.objects.get_for_model(parent_comment)
        child_comment = Comment.objects.create(body='child',
                                               user=self.authorized_user,
                                               content_type=c_type_for_comment,
                                               object_id=parent_comment.id)
        self.assertIsInstance(child_comment.content_object, Comment)

    def test_create_comment_with_binding_to_user_entity(self):
        c_type = ContentType.objects.get_for_model(User)
        comment = Comment.objects.create(body='text',
                                         user=self.authorized_user,
                                         content_type=c_type,
                                         object_id=self.authorized_user.id)
        self.assertIsInstance(comment.content_object, User)

    def test_create_comment_without_binding_for_user(self):
        post = Post.objects.create(title='custom title', body='body')
        c_type = ContentType.objects.get_for_model(post)
        with self.assertRaises(IntegrityError) as exc:
            Comment.objects.create(body='body',
                                   content_type=c_type,
                                   object_id=post.id)

    def test_exist_date_created(self):
        post = Post.objects.create(title='custom title', body='body')
        c_type = ContentType.objects.get_for_model(post)
        comment = Comment.objects.create(body='body',
                                         user=self.authorized_user,
                                         content_type=c_type,
                                         object_id=post.id)
        self.assertIsNotNone(comment.created)

    def test_tree_hierarchy(self):
        post = Post.objects.create(title='custom title', body='body')
        c_type = ContentType.objects.get_for_model(post)
        comment1 = Comment.objects.create(body='com1',
                                          user=self.authorized_user,
                                          content_type=c_type,
                                          object_id=post.id)

        comment2 = Comment.objects.create(body='com2',
                                          user=self.authorized_user,
                                          content_type=ContentType.objects.get_for_model(comment1),
                                          object_id=comment1.id)

        comment3 = Comment.objects.create(body='com3',
                                          user=self.authorized_user,
                                          content_type=ContentType.objects.get_for_model(comment2),
                                          object_id=comment2.id)

        self.assertEqual(comment2.content_object.id, comment1.id)
        self.assertEqual(comment3.content_object.id, comment2.id)

    def test_try_to_remove_comment_with_child_comment(self):
        post = Post.objects.create(title='custom title', body='body')
        c_type = ContentType.objects.get_for_model(post)
        comment1 = Comment.objects.create(body='com1',
                                          user=self.authorized_user,
                                          content_type=c_type,
                                          object_id=post.id)

        Comment.objects.create(body='com2',
                               user=self.authorized_user,
                               content_type=ContentType.objects.get_for_model(comment1),
                               object_id=comment1.id)

        with self.assertRaises(Exception) as exc:
            comment1.delete()
