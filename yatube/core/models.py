from django.db import models


class CreatedModel(models.Model):
    """Abstract model, adds date of creation."""
    created = models.DateTimeField(
        'Date of creation',
        auto_now_add=True
    )

    class Meta:
        abstract = True
