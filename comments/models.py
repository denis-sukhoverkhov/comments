import logging

from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.datetime_safe import datetime
from django.utils.timezone import now
from django.utils.translation import ugettext as _

from comments.libs.manager import NonTrashManager, TrashManager

logger = logging.getLogger(__name__)


class TrashField(models.Model):
    trashed_at = models.DateTimeField(blank=True, null=True, verbose_name=_('Removal date'))

    class Meta:
        abstract = True

    def delete(self, using=None, keep_parents=False, trash=True, user=None):
        if not self.trashed_at and trash:
            self.trashed_at = datetime.utcnow()
            self.save(user=user)
        else:
            super(TrashField, self).delete(using=using)

    def restore(self, commit: bool = True, user=None) -> None:
        if self.trashed_at is not None and commit:
            self.trashed_at = None
            self.save(user=user)

    objects = NonTrashManager()
    trash = TrashManager()
    admin_objects = models.Manager()


class Comment(TrashField):
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

    def delete(self, using=None, keep_parents=False, trash=True, user=None):
        # before delete - need check existing child node
        is_exists_child_comment = Comment.objects.filter(object_id=self.id,
                                                         content_type=ContentType.objects.get_for_model(Comment)).exists()
        if is_exists_child_comment:
            message = f'You can not delete this comment, it has a child comments'
            logger.error(message)
            raise Exception(message)

        super().delete(using, keep_parents, trash, user)

        if user is None:
            raise Exception('Unrecognized user!')
        CommentHistory.objects.create(comment=self,
                                      body=self._original_body,
                                      author=user,
                                      is_deleted=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._original_body = self.body

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None, user=None):

        # if inserting don't add the latest update at
        if self.id is not None:
            if user is None:
                raise Exception('Unrecognized user!')
            if self._original_body != self.body:
                CommentHistory.objects.create(comment=self,
                                              body=self._original_body,
                                              author=user)

        super().save(force_insert, force_update, using, update_fields)


class Post(models.Model):
    title = models.CharField('Title', max_length=100, blank=False)
    body = models.TextField('Body', blank=False)

    class Meta:
        verbose_name = _('Post')
        verbose_name_plural = _('Posts')

    def __str__(self):
        return self.title


class CommentHistory(models.Model):
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, verbose_name='Comment')
    body = models.TextField('Body', blank=False)
    created = models.DateTimeField(default=now, verbose_name=_('Date created'))
    author = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name='User')
    is_deleted = models.BooleanField(default=False)

    class Meta:
        verbose_name = _('Comment history')
        verbose_name_plural = _('Comment history')

    def __str__(self):
        return self.body
