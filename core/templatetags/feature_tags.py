from django import template
from core.models import FeatureAccess

register = template.Library()

@register.simple_tag
def is_feature_enabled(key):
    try:
        feature = FeatureAccess.objects.get(key=key)
        return feature.is_enabled_for_employer
    except FeatureAccess.DoesNotExist:
        return False