"""Subtraction filter for Django templates."""
from django import template

register = template.Library()


@register.filter(name="sub")
def sub_filter(value, arg):
    """Subtract arg from value."""

    return int(value) - int(arg)
