import logging

from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.db import transaction

from comments.models import Comment, Post
import random
from faker import Faker


def dict_fetchall(cursor):
    """Return all rows from a cursor as a dict"""
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]


def generate_tree_of_comments():
    fake = Faker()
    user = User.objects.first()
    post = Post.objects.create(title='custom title', body='body')
    c_type = ContentType.objects.get_for_model(post)
    comment_list = []
    count_top_level_comments = 1000
    logging.warning(f'Start creation top level comments: count - {count_top_level_comments}')
    for ct in range(count_top_level_comments):
        comment_list.append(Comment(body=fake.sentences(nb=3, ext_word_list=None),
                                    user=user,
                                    content_type=c_type,
                                    object_id=post.id)
                            )
    logging.warning(f'Saving top level comments!')
    Comment.objects.bulk_create(comment_list)
    logging.warning(f'End saving top level comments!')

    comment_content_type = ContentType.objects.get_for_model(Comment)
    number_of_child_nodes = 100
    for counter, comment in enumerate(Comment.objects.all().iterator()):
        if counter > count_top_level_comments:
            break
        logging.warning(f'Creation brunch {counter}')
        prev_obj = comment
        with transaction.atomic():
            for idx in range(number_of_child_nodes):
                prev_obj = Comment.objects.create(body=fake.sentences(nb=3, ext_word_list=None),
                                                  user=user,
                                                  content_type=comment_content_type,
                                                  object_id=prev_obj.object_id)
