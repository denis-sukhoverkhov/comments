# Generated by Django 2.0.5 on 2018-05-12 14:56

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('comments', '0004_remove_comment_parent'),
    ]

    operations = [
        migrations.CreateModel(
            name='CommentHistory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('body', models.TextField(verbose_name='Body')),
                ('created', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Date created')),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL, verbose_name='User')),
                ('comment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='comments.Comment', verbose_name='Comment')),
            ],
            options={
                'verbose_name': 'Comment history',
                'verbose_name_plural': 'Comment history',
            },
        ),
    ]