import requests


def get_blaa_events_list():
    url = 'http://blaa.demodayscript.com/api/actividades?tid_raw_4=1192&page={page}'
    response = requests.get(url.format(page=1))
    data = response.json()
    nodes = data['nodes']
    view = data['view']
    pages = view['pages']
    events = []
    for page in range(1, pages + 1):
        if page == 1:
            for node in nodes:
                events.append(node)
        else:
            pass
            #response = requests.get(url.format(page=page))
            #data = response.json()
           # nodes = data['nodes']
            #for node in nodes:
            #    events.append(node)
    return events


def get_blaa_event(event_id):
    url = 'http://blaa.demodayscript.com/api/actividades/detalle?alias={event_id}'
    url = url.format(event_id=event_id.lstrip('/'))
    response = requests.get(url)
    data = response.json()
    return data['nodes'][0]
