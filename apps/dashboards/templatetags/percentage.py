from django import template

register = template.Library()

@register.filter
def percentage(value):
    try:
        return f"{round(value * 100)}%"
    except:
        return ""