from django import template

register = template.Library()

@register.filter
def multiply(value, arg):
    """Multiplies the value by the argument."""
    try:
        return value * arg
    except TypeError:
        return 0