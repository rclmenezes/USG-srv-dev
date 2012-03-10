from django import template
register = template.Library()

def contains(event_list, club):
    if len(event_list[club]) == 0:
        return False
    else:
        return True
register.filter('contains', contains)