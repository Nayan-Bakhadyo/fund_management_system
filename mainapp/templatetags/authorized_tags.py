from django import template
from mainapp.models import AuthorizedUser

register = template.Library()

@register.filter
def is_authorized(email):
    return AuthorizedUser.objects.filter(email=email).exists()