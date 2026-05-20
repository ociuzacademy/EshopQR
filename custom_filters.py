# custom_filters.py
from django import template

register = template.Library()

@register.filter(name='generate_stars')
def generate_stars(rating):
    full_stars = int(rating)
    half_star = 1 if rating % 1 >= 0.5 else 0
    empty_stars = 5 - full_stars - half_star

    return {
        'full_stars': range(full_stars),
        'half_star': half_star,
        'empty_stars': range(empty_stars),
    }