# custom_filters.py
from django import template
from datetime import timedelta

register = template.Library()


@register.filter(name='add_days')
def add_days(value, days):
    if value:
        return value + timedelta(days=days)
    return value
