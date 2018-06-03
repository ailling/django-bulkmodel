from django.db.models.signals import ModelSignal


# These signals are sent when model instances are created in bulk
pre_bulk_create = ModelSignal(providing_args=['instances'])
post_bulk_create = ModelSignal(providing_args=['instances'])


# These signals are sent when a model is updated homogeneously (i.e.: queryset.update(field=value)
pre_update = ModelSignal(providing_args=['instances'])
post_update = ModelSignal(providing_args=['instances'])


# These signals are sent when a model's fields are updated heterogeously (i.e.: queryset.update_fields(...))
pre_update_fields = ModelSignal(providing_args=[
    'instances',
    'field_names',
    'field_defaults',
    'batch_size'
])

post_update_fields = ModelSignal(providing_args=[
    'instances',
    'queryset',
    'field_names',
    'field_defaults',
    'batch_size',
    'n'
])


pre_copy_from_instances = ModelSignal(providing_args=[
    'instances'
])

post_copy_from_instances = ModelSignal(providing_args=[
    'instances'
])
