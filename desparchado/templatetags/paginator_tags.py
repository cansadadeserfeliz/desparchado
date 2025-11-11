from django import template

register = template.Library()


@register.inclusion_tag('includes/_simple_pagination.html', takes_context=True)
def get_simple_pagination(context):
    page_obj = context['page_obj']
    paginator = context['paginator']
    is_paginated = context['is_paginated']

    search_query = ''
    for key, value in context['request'].GET.items():
        if key != 'page':
            search_query += '&' + key + '=' + value

    return {
        'paginator': paginator,
        'page_obj': page_obj,
        'is_paginated': is_paginated,
        'search_query': search_query,
    }
