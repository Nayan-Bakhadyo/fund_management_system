from django import template
from mainapp.views import indian_number_format  # or your function name

register = template.Library()

@register.filter
def indian_format(value):
    try:
        return indian_number_format(float(value))
    except Exception:
        return value