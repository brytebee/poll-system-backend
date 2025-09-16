import uuid
from django.db import models

class BaseModel(models.Model):
    """Base model with UUID primary key and timestamps"""
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Unique identifier"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the record was created"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="When the record was last updated"
    )

    class Meta:
        abstract = True
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.__class__.__name__}({self.id})"

class SlugMixin(models.Model):
    """Mixin for models that need slug fields"""
    slug = models.SlugField(
        max_length=100,
        unique=True,
        help_text="URL-friendly identifier"
    )

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if not self.slug and hasattr(self, 'name'):
            from django.utils.text import slugify
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
