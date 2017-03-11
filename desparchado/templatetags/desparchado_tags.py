from django import template

register = template.Library()


@register.filter()
def format_currency(value):
    """
    E.g. 543921.9354 becomes $543,921.94
    """
    try:
        value = float(value)
        return '${:,.0f}'.format(value)
    except (ValueError, TypeError):
        return value
