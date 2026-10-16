# core/models.py  (create this app if you don't have it)

from django.db import models

class FeatureAccess(models.Model):
    key = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    is_enabled_for_employer = models.BooleanField(
        default=False,
        verbose_name="Visible / Allowed for Employer"
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Feature Access"
        verbose_name_plural = "Feature Access Controls"
        ordering = ['name']

    def __str__(self):
        status = "ON" if self.is_enabled_for_employer else "OFF"
        return f"{self.name} → {status}"