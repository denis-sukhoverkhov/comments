from django.db import models


class NonTrashManager(models.Manager):
    """ Query only objects which have not been trashed. """

    def get_queryset(self):
        query_set = super(NonTrashManager, self).get_queryset()
        return query_set.filter(trashed_at__isnull=True)


class TrashManager(models.Manager):
    """ Query only objects which have been trashed. """

    def get_queryset(self):
        query_set = super(TrashManager, self).get_queryset()
        return query_set.filter(trashed_at__isnull=False)