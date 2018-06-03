from django.db import models
from .managers import BulkModelManager


class BulkModel(models.Model):
    """
    An abstract model that provides bulk-model capabilities.
    This is optional to inherit from; if you don't inherit from it you'll want
    to use the BulkModelManager() by setting

        objects = BulkModelManager()

    on your model

    If you do inherit from it you'll need to run migrations to pick up an additional data field (bm_create_uuid)

    """

    class Meta:
        abstract = True

    bm_create_uuid = models.UUIDField(null=True, default=None, db_index=True)

    objects = BulkModelManager()

