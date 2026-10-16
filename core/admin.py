# core/admin.py

from django.contrib import admin
from .models import FeatureAccess

@admin.register(FeatureAccess)
class FeatureAccessAdmin(admin.ModelAdmin):
    list_display = ('name', 'key', 'is_enabled_for_employer', 'updated_at')
    list_editable = ('is_enabled_for_employer',)   # ← Instant Toggle
    list_filter = ('is_enabled_for_employer',)
    search_fields = ('name', 'key')
    ordering = ('name',)