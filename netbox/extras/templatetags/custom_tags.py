from django import template
from django.conf import settings

register = template.Library()

@register.simple_tag(name="nb_version")
def get_netbox_version():
    return settings.VERSION