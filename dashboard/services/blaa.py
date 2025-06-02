import requests


def get_blaa_events_list(page):
    url = (
        f'https://admin.banrepcultural.org/api/actividades?'
        f'/api/taxonomias/etiquetas?tid_raw_4=1192&page={page}'
    )
    response = requests.get(url.format(page=page), timeout=10, verify=False)
    data = response.json()
    nodes = data['nodes']
    pager = data['pager']
    pages_count = pager['pages']
    events = []
    for node in nodes:
        events.append(node)
    return events, pages_count


def get_blaa_event(event_slug):
    url = (
        f'https://admin.banrepcultural.org/api/actividades/detalle'
        f'?alias={event_slug}'
    )
    url = url.format(event_slug=event_slug)
    response = requests.get(url, timeout=10, verify=False)
    data = response.json()
    return data['nodes'][0]
