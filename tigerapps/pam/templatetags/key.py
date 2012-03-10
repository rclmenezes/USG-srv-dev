from django import template
register = template.Library()

def key(d, name):
    return d[name]
register.filter('key', key)