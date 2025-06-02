from django import template

register = template.Library()


@register.inclusion_tag('dashboard/includes/_pagination.html', takes_context=True)
def get_dashboard_pagination(context, first_last_amount=2, before_after_amount=4):
    # pylint: disable=too-many-branches
    page_obj = context['page_obj']
    paginator = context['paginator']
    is_paginated = context['is_paginated']
    page_numbers = []

    # Pages before current page
    if page_obj.number > first_last_amount + before_after_amount:
        for i in range(1, first_last_amount + 1):
            page_numbers.append(i)

        if first_last_amount + before_after_amount + 1 != paginator.num_pages:
            page_numbers.append(None)

        for i in range(page_obj.number - before_after_amount, page_obj.number):
            page_numbers.append(i)

    else:
        for i in range(1, page_obj.number):
            page_numbers.append(i)

    # Current page and pages after current page
    if page_obj.number + first_last_amount + before_after_amount < paginator.num_pages:
        for i in range(page_obj.number, page_obj.number + before_after_amount + 1):
            page_numbers.append(i)

        page_numbers.append(None)

        for i in range(
            paginator.num_pages - first_last_amount + 1, paginator.num_pages + 1
        ):
            page_numbers.append(i)

    else:
        for i in range(page_obj.number, paginator.num_pages + 1):
            page_numbers.append(i)

    search_query = ''
    for key, value in context['request'].GET.items():
        if key != 'page':
            search_query += '&' + key + '=' + value

    return {
        'paginator': paginator,
        'page_obj': page_obj,
        'page_numbers': page_numbers,
        'is_paginated': is_paginated,
        'search_query': search_query,
    }
