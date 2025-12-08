from django import template
import math

register = template.Library()

# Discount for Niffler
@register.filter
def dis(price, discount):
    try:
        return math.ceil(price * (1 - discount))
    except(TypeError, ValueError):
        return None