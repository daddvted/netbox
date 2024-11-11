from django import template

register = template.Library()

@register.simple_tag(name="nb_version")
def get_netbox_version():
    #FOR CI, DO NOT CHANGE
    version = "__VERSION__"
    return version