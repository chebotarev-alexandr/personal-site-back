"""Shared abstract models used across the project."""

from django.db import models


class TimeStampedModel(models.Model):
    """Adds created_at / updated_at to a model."""

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class SortableModel(models.Model):
    """Adds an ordering field (default ordering by sort_order, then id)."""

    sort_order = models.PositiveIntegerField(default=0, db_index=True)

    class Meta:
        abstract = True
        ordering = ["sort_order", "id"]


class ActiveModel(models.Model):
    """Adds a soft on/off switch for public visibility."""

    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        abstract = True


class SingletonModel(models.Model):
    """Enforces a single row (pk=1) — for site-wide settings blocks."""

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj
