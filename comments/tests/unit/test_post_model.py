from django.test import TestCase

from comments.models import Post


class PostModelTest(TestCase):

    def test_create_post(self):
        p = Post.objects.create(title='post1', body='body1')
        self.assertIsInstance(p, Post)

    def test_create_post_without_title(self):
        p = Post.objects.create(body='body1')
        self.assertIsInstance(p, Post)

    def test_create_post_without_body(self):
        p = Post.objects.create(title='title1')
        self.assertIsInstance(p, Post)
