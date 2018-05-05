import logging

from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.timezone import now
from django.utils.translation import ugettext as _

logger = logging.getLogger(__name__)


class Comment(models.Model):
    body = models.TextField(verbose_name='Body')
    user = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name='User')
    created = models.DateTimeField(default=now, verbose_name=_('Date created'))
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    class Meta:
        verbose_name = _('Comment')
        verbose_name_plural = _('Comments')

    def __str__(self):
        return self.body[0:100]

    def delete(self, using=None, keep_parents=False):
        # before delete - need check existing child node
        is_exists_child_comment = Comment.objects.filter(object_id=self.id,
                                                         content_type=ContentType.objects.get_for_model(Comment)).exists()
        if is_exists_child_comment:
            message = f'You can not delete this comment, it has a child comments'
            logger.error(message)
            raise Exception(message)

        super().delete(using, keep_parents)


class Post(models.Model):
    title = models.CharField('Title', max_length=100, blank=False)
    body = models.TextField('Body', blank=False)

    class Meta:
        verbose_name = _('Post')
        verbose_name_plural = _('Posts')

    def __str__(self):
        return self.title
