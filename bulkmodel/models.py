from django.db import models
from .managers import BulkModelManager


class BulkModel(models.Model):

    class Meta:
        abstract = True

    create_uuid = models.UUIDField(null=True, default=None, db_index=True)

    objects = BulkModelManager()

