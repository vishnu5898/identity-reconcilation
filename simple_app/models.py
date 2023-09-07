from django.db import models
from django.db.models.fields import BigIntegerField, CharField, EmailField, IntegerField, DateTimeField

# Create your models here.
class Contact(models.Model):
    phone_number = BigIntegerField()
    email = EmailField()
    linked_id = IntegerField(null=True)
    link_precedence = CharField(
        max_length=255,
        choices=[
            ("primary", "Primary"),
            ("secondary", "Secondary"),
        ]
    )
    created_at = DateTimeField()
    updated_at = DateTimeField()
    deleted_at = DateTimeField(null=True)

    class Meta:
        unique_together = ('phone_number', 'email',)
    # pass
