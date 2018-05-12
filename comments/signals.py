from django.db.models.signals import post_save
from django.dispatch import receiver
from comments.models import Comment, CommentHistory


@receiver(post_save, sender=Comment)
def save_comment_history(sender, instance, created, **kwargs):
    if not created:
        # CommentHistory.objects.create(comment=instance.id,
        #                               body=instance._original_body,
        #                               author=1)
        pass

