from django.contrib.auth.models import User
from django.db import models
from django.utils.timezone import now
from django.utils.translation import ugettext as _


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name='User')
    created = models.DateTimeField(default=now, verbose_name=_('Date created'))
    parent = models.ForeignKey('self', blank=True, null=True, on_delete=models.PROTECT, verbose_name='Parent')


class Post(models.Model):
    title = models.CharField('Title', max_length=100)
    text = models.TextField('Text')
