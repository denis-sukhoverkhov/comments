from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.timezone import now
from django.utils.translation import ugettext as _


class Comment(models.Model):
    body = models.TextField(verbose_name='Body')
    user = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name='User')
    created = models.DateTimeField(default=now, verbose_name=_('Date created'))
    parent = models.ForeignKey('self', blank=True, null=True, on_delete=models.PROTECT, verbose_name='Parent')
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    class Meta:
        verbose_name = _('Comment')
        verbose_name_plural = _('Comments')

    def __str__(self):
        return self.body[0:100]


class Post(models.Model):
    title = models.CharField('Title', max_length=100, blank=False)
    body = models.TextField('Body', blank=False)

    class Meta:
        verbose_name = _('Post')
        verbose_name_plural = _('Posts')

    def __str__(self):
        return self.title
