import marimo

__generated_with = "0.25.2"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Universal imports and constants
    """)
    return


@app.cell(hide_code=True)
def _():
    import datetime
    from dataclasses import dataclass
    import os

    from colorama import init
    from colorama import Fore, Back, Style
    import requests
    from pyquery import PyQuery as pq

    # turn off color changes at the end of every print
    init(autoreset=True)

    TODAY = datetime.date.today()

    CATEGORY_LITERATURE = 'literature'
    CATEGORY_SOCIETY = 'society'
    CATEGORY_ENVIRONMENT = 'environment'
    CATEGORY_SCIENCE = 'science'
    CATEGORY_ART = 'art'

    @dataclass
    class Event:
        '''Maps event object that will be synced with a spreadsheet'''
        event_id: str
        title: str
        date: str  # YYYY-MM-DD HH:MM
        place: str
        category: str
        description: str
        url: str
        image_url: str
        organizer: str
        speakers: str = ''


    return (
        CATEGORY_ART,
        CATEGORY_LITERATURE,
        CATEGORY_SOCIETY,
        Event,
        Fore,
        TODAY,
        datetime,
        os,
        pq,
        requests,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Base scraper definition
    """)
    return


@app.cell(hide_code=True)
def _(Event, Fore, requests):
    from abc import ABC, abstractmethod
    import json
    from typing import Optional
    from pathlib import Path

    import gspread


    with Path.open('../spreadsheet_credentials.json', 'r', encoding='utf-8') as file:
        credentials = json.load(file)
    gc = gspread.service_account_from_dict(credentials)


    class BaseEventScraper(ABC):
        spreadsheet_id: str

        def __init__(self):
            self.session = requests.Session()
            headers = self.get_headers()
            if headers:
                self.session.headers.update(headers)

        def run(self):
            raw_events = self.get_events_list()
            events = []

            for raw_event in raw_events:
                event = self.build_event(raw_event)
                if event:
                    print(Fore.GREEN, event)
                    events.append(event)

            self.save_event_rows(events=events)

            print(f'Check https://docs.google.com/spreadsheets/d/{self.spreadsheet_id}/edit?gid=0#gid=0')

        def save_event_rows(self, events: list[Event]):
            # Open the Google Spreadsheet using the ID
            # https://docs.gspread.org/en/latest/user-guide.html
            spreadsheet = gc.open_by_key(self.spreadsheet_id)
            sheet = spreadsheet.sheet1  # Select the first sheet

            # Clear all existing data
            sheet.clear()

            rows = []

            header_row = [
                'ID',
                'TITLE',
                'DATE',
                'PLACE',
                'CATEGORY',
                'DESCRIPTION',
                'URL',
                'IMAGE URL',
                'ORGANIZERS',
                'SPEAKERS',
            ]
            rows.append(header_row)

            for event in events:
                event_row = [
                    event.event_id,
                    event.title.strip(),
                    event.date,
                    event.place,
                    event.category,
                    event.description.strip(),
                    event.url,
                    event.image_url,
                    event.organizer,
                    event.speakers,
                ]
                rows.append(event_row)

            # Append new rows to the sheet
            sheet.append_rows(rows)


        def get_headers(self) -> dict:
            """Return headers for the requests calls"""
            return {}

        @abstractmethod
        def get_events_list(self) -> list:
            """Return iterable of raw event items"""
            pass

        @abstractmethod
        def build_event(self, raw_event) -> Optional[Event]:
            """Return Event instance"""
            pass

    return BaseEventScraper, Optional


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Helpers
    """)
    return


@app.function(hide_code=True)
def place_name_mapping(place_map: dict[str, str], place_name_raw: str) -> str:
    """Returns mapped place name if found"""
    return next(
        (
            standard
            for original, standard in place_map.items()
            if original.lower() in place_name_raw.lower()),
        place_name_raw  # Return original if no match found
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # ✅ Scraper for Filarmónica de Bogotá

    Result are stored in https://docs.google.com/spreadsheets/d/1bpv_anloTMzOQ-uOUs1v_qpPyzyjl57sdNES0Ycla-E/edit?gid=0#gid=0
    """)
    return


@app.cell(hide_code=True)
def _(BaseEventScraper, CATEGORY_ART, Event, Optional, TODAY, datetime):
    FILARMONICA_PLACE_MAP = {
        'Teatro Mayor JM Santo Domingo': 'Teatro Mayor Julio Mario Santo Domingo',
        'Teatro Mayor JM  Santo Domingo': 'Teatro Mayor Julio Mario Santo Domingo',
        'Auditorio León de Greiff UNAL': 'Auditorio León de Greiff',
        'Auditorio Fabio Lozano U Tadeo Lozano': 'Auditorio Fabio Lozano',
        'Biblioteca Pública Virgilio Barco': 'Biblioteca Virgilio Barco',
        'Teatro Estudio  Teatro Mayor Julio Mario Santo Domingo': 'Teatro Mayor Julio Mario Santo Domingo',
        'Iglesia San Ignacio Calle 10 No. 6 - 26': 'Iglesia San Ignacio',
        'Iglesia San Ignacio': 'Iglesia San Ignacio',
        'Museo de Arte Moderno de Bogotá - MAMBO-': 'Museo de Arte Moderno de Bogotá (MAMBO)',
        'Museo de Arte Moderno de Bogotá': 'Museo de Arte Moderno de Bogotá (MAMBO)',

    }


    class FilarmonicaScraper(BaseEventScraper):
        spreadsheet_id = '1bpv_anloTMzOQ-uOUs1v_qpPyzyjl57sdNES0Ycla-E'

        def get_events_list(self):
            from_date = TODAY.strftime('%Y-%m-%d')
            to_date = (TODAY + datetime.timedelta(days=60)) .strftime('%Y-%m-%d')
            events_list_url = (
                f'https://orquesta-filarmonica-de-bogota.micolombiadigital.gov.co/api/v1/contents'
                f'?contentType=2&fromDate={from_date}'
                f'&includeTags=true&labels=56,54,53,60,59&page=0&pageSize=6&rangeType=Events'
                f'&toDate={to_date}'
            )
            events_list_response = self.session.get(events_list_url)
            events_list_json = events_list_response.json()

            print(events_list_json['meta'])
            events_list = events_list_json['results']

            print(len(events_list))

            return events_list

        def build_event(self, raw_event) -> Optional[Event]:
            event_datetime_str = raw_event['startingDate']
            event_datetime = datetime.datetime.fromisoformat(event_datetime_str)

            print(raw_event['friendlyName'])

            event_detail_response = self.session.get(
                'https://orquesta-filarmonica-de-bogota.micolombiadigital.gov.co/api/v1/contents/' + raw_event['friendlyName'],
            )
            event_detail_json = event_detail_response.json()

            place_name_raw = next((a['value'] for a in raw_event['attributes'] if a['attribute'] == 'EventLocation'), '')

            place_name = place_name_mapping(place_map=FILARMONICA_PLACE_MAP, place_name_raw=place_name_raw)

            return Event(
                event_id=raw_event['contentID'],
                title=raw_event['name'],
                date=event_datetime.strftime("%Y-%m-%d %H:%M"),
                place=place_name,
                category=CATEGORY_ART,
                description=event_detail_json['body'],
                url='https://www.filarmonicabogota.gov.co/calendario-de-actividades/' + raw_event['friendlyName'],
                image_url=raw_event['defaultImage'],
                organizer='Orquesta Filarmónica de Bogotá',
            )

    return (FilarmonicaScraper,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # ✅ Scraper for Idartes

    Results are stored in https://docs.google.com/spreadsheets/d/11TtkDbUdPtqLPfpYp5dXhuT2adsw-lnV_or8_EULzgE/edit?gid=0#gid=0
    """)
    return


@app.cell(hide_code=True)
def _(
    BaseEventScraper,
    CATEGORY_ART,
    CATEGORY_LITERATURE,
    CATEGORY_SOCIETY,
    Event,
    Fore,
    Optional,
    datetime,
    pq,
    requests,
):
    IDARTES_CATEGORY_MAP = {
        'Música': CATEGORY_ART,
        'Artes Plásticas y Visuales': CATEGORY_ART,
        'Artes Audiovisuales': CATEGORY_ART,
        'Multidisciplinar': CATEGORY_ART,
        'Niños y Jóvenes': CATEGORY_SOCIETY,
        'Teatro': CATEGORY_ART,
        'Literatura': CATEGORY_LITERATURE,
    }
    IDARTES_PLACE_MAP = {
        'Nuestro Nido': 'Hogar Infantil Nuestro Nido',
        'Sala Gaitán': 'Teatro Jorge Eliécer Gaitán',
        'Museo Nacional de Colombia': 'Museo Nacional de Colombia',
        'Corporación La Mascarada': 'Corporación Mascarada',
        'Palacio San Francisco': 'Palacio de San Francisco',
        'Auditorio IED Misael Pastrana': 'Auditorio IED Misael Pastrana',
        'Biblioteca Francisco José de Caldas': 'Biblioteca Francisco José de Caldas',
        'Casa de los 7 balcones': 'Museo de Bogotá - Casa de los Siete Balcones',
        'Museo de Arte Miguel Urrutia': 'Museo de Arte Miguel Urrutia (MAMU)',
        'Centro Felicidad Chapinero / Calle 82': 'Centro Felicidad Chapinero / Calle 82',
        'CEFE Chapinero - Calle 82': 'Centro Felicidad Chapinero / Calle 82',
        'Teatro la Victoria': 'Teatro la Victoria',
        'Teatro Comunitario FUCCA': 'Teatro Comunitario FUCCA',
        'Biblioteca Pública Virgilio Barco': 'Biblioteca Virgilio Barco',
        'Parque Zonal Villa Mayor': 'Parque Villa Mayor',
        'Parque de los Novios': 'Parque De Los Novios',
        'Centro de Desarrollo Comunitario Lago Timiza': 'Centro de Desarrollo Comunitario Lago Timiza',
        'Teatro Estudio Julio Mario Santo Domingo': 'Teatro Mayor Julio Mario Santo Domingo',
        'Museo de la Independencia - Casa del Florero': 'Museo de la Independencia - Casa del Florero',
        'Biblioteca Pública Julio Mario Santo Domingo': 'Centro Cultural y Biblioteca Pública Julio Mario Santo Domingo',
        'I.E.D Rodrigo Lara Bonilla - Carrera 43A No. 66 – 51 Sur': 'I.E.D Rodrigo Lara Bonilla - Sede A',
        'Casa de la Cultura de Fontibón': 'Casa de la Cultura de Fontibón',
    }


    class IdartesScraper(BaseEventScraper):
        spreadsheet_id = '11TtkDbUdPtqLPfpYp5dXhuT2adsw-lnV_or8_EULzgE'

        def get_events_list(self):
            response = self.session.get('https://www.idartes.gov.co/es/agenda')
            assert response.status_code == 200, f'Failed to fetch events list: status code {response.status_code}'

            content_pq = pq(response.content.decode('utf-8'))
            events_list = content_pq('.item-ev')
            return events_list

        def build_event(self, raw_event) -> Optional[Event]:
            event_pq = pq(raw_event)

            image_url = f"https://www.idartes.gov.co{event_pq('img').attr('src')}"
            idartes_category = str(event_pq('.ctg-ev-24').text())
            event_datetime_str = str(event_pq('.fecha-ev24  time').attr('datetime'))
            event_datetime = datetime.datetime.fromisoformat(event_datetime_str)
            event_url = f"https://www.idartes.gov.co{event_pq('.titulo_cajashomeeventos a').attr('href')}"

            response = requests.get(event_url)
            assert response.status_code == 200, f'Failed to fetch event: status code {response.status_code}'

            event_detail_pq = pq(response.content.decode('utf-8'))
            place1 = event_detail_pq('.field--name-field-evento-escenario .field__item').text()
            place2 = event_detail_pq('.field--name-field-lugar-del-evento .field__item').text()
            place_name_raw = str(place1 or place2)

            if place_name_raw == 'Escenarios móviles':
                print(Fore.RED, f'Skipping {place_name_raw}')
                return None

            place_name = place_name_mapping(place_map=IDARTES_PLACE_MAP, place_name_raw=place_name_raw)
            description = event_detail_pq('.field--name-field-evento-contenido').html()

            return Event(
                event_id='',
                title=str(event_pq('.titulo_cajashomeeventos a').text()),
                date=event_datetime.strftime("%Y-%m-%d %H:%M"),
                place=place_name,
                category=IDARTES_CATEGORY_MAP.get(idartes_category, ''),
                description=str(description),
                url=event_url,
                image_url=image_url,
                organizer='Idartes',
            )

    return (IdartesScraper,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # ✅ Scraper for Alianza Francesa de Bogotá

    Results are stored in https://docs.google.com/spreadsheets/d/1BT3ZmoFwKxMoZovxAwBjIFmIHWCaIr9mcYuL9uVRJ38/edit?gid=0#gid=0
    """)
    return


@app.cell(hide_code=True)
def _(BaseEventScraper, CATEGORY_ART, Event, Fore, Optional, datetime, os):
    class AlianzaFrancesaDeBogotaScraper(BaseEventScraper):
        spreadsheet_id = '1BT3ZmoFwKxMoZovxAwBjIFmIHWCaIr9mcYuL9uVRJ38'

        def get_headers(self) -> dict:
                return {
                'api_key': os.environ['SCRAPER_ALIANZA_FRANCESA_DE_BOGOTA_API_KEY'],
                'auth_token': os.environ['SCRAPER_ALIANZA_FRANCESA_DE_BOGOTA_AUTH_TOKEN'],
            }

        def get_events_list(self):
            response = self.session.get(
                'https://afbogota.aec-app.com/arc-en-ciel/api/public/core/v1/events/availableEventsToday?eventType=6&etablishmentBranchId=&CURRENT_LANG=es_CO',
            )
            assert response.status_code == 200
            events_list = response.json()
            return events_list

        def build_event(self, raw_event) -> Optional[Event]:
            event_id = raw_event['reference']
            image_url = 'https://res.cloudinary.com/aec/image/upload/w_300,h_300,c_thumb//v1/' + raw_event['image_resource_id'] + '.' + raw_event['image_extension']
            event_datetime = datetime.datetime.fromisoformat(raw_event['event_date'])

            response = self.session.get(
                f'https://afbogota.aec-app.com/arc-en-ciel/api/public/core/v1/events/{event_id}?CURRENT_LANG=es_CO',
            )
            assert response.status_code == 200

            event_details = response.json()

            event_location_name = raw_event['event_location_name']
            if event_location_name == 'all_etablishment_branchs' or 'A distancia' in event_location_name:
                print(Fore.RED, f'Skipping {event_location_name}')
                return None

            return Event(
                event_id='AFBOG_' + event_id,
                title=event_details['product_name'],
                date=event_datetime.strftime("%Y-%m-%d %H:%M"),
                place='Alianza Francesa de Bogotá | ' + raw_event['event_location_name'],
                category=CATEGORY_ART,
                description=event_details['product_description'],
                url=f'https://bogota.alianzafrancesa.edu.co/detalle-evento/?eventId={event_id}',
                image_url=image_url,
                organizer='Alianza Francesa de Bogotá',
            )

    return (AlianzaFrancesaDeBogotaScraper,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # 🚧 Scraper for Secretaría de Cultura, Recreación y Deporte

    Results are stored in https://docs.google.com/spreadsheets/d/1mzmCgnnKgwJxWWFy58joTNdZgI4Fj2-u0OUlsotDRKk/edit?gid=0#gid=0

    WIP: missing event date, description and category
    """)
    return


@app.cell(hide_code=True)
def _(BaseEventScraper, CATEGORY_ART, Event, Optional, pq, requests):
    class CulturaRecreacionDeporteScraper(BaseEventScraper):
        spreadsheet_id = '1mzmCgnnKgwJxWWFy58joTNdZgI4Fj2-u0OUlsotDRKk'

        def get_events_list(self):
            response = requests.get('https://www.culturarecreacionydeporte.gov.co/es/eventos')
            assert response.status_code == 200

            content_pq = pq(response.content.decode('utf-8'))
            events_list = content_pq('.evbox')
            return events_list

        def build_event(self, raw_event) -> Optional[Event]:
            event_pq = pq(raw_event)

            event_title = event_pq('.vistas-titulos a').text()

            image_url = f"https://www.culturarecreacionydeporte.gov.co{event_pq('.vistas-imagenes img').attr('src')}"
            event_url = f"https://www.culturarecreacionydeporte.gov.co{event_pq('.vistas-titulos a').attr('href')}"

            event_category = ''
            category_map = {}

            response = requests.get(event_url)
            assert response.status_code == 200, f'Failed to fetch {event_url}: status code {response.status_code}'

            event_detail_pq = pq(response.content.decode('utf-8'))

            start_date = event_detail_pq("time.start").text()
            end_date = event_detail_pq("time.end").text()

            start_time = event_detail_pq("span.start-time").text()
            end_time = event_detail_pq("span.end-time").text()

            start_datetime_text = f'{start_date} {start_time}'
            end_datetime_text = f'{end_date} {end_time}'


            place = event_detail_pq('.field--name-field-evento-escenario .field__item').text()
            place_name_raw = event_title.split(' - ')[-1]
            place_mapping = {
                'Nuestro Nido': 'Hogar Infantil Nuestro Nido',
            }
            place_name = place_name_mapping(place_map=place_mapping, place_name_raw=place_name_raw)

            description = event_detail_pq('.field--name-field-evento-escenario .field--type-text-with-summary').html()
            return Event(
                event_id='',
                title=str(event_title),
                date=str(event_detail_pq(".field__label:contains('Fecha')").next(".field__items").text()),
                place=place_name,
                category=category_map.get(event_category, CATEGORY_ART),
                description=str(description),
                url=event_url,
                image_url=image_url,
                organizer='Secretaría de Cultura, Recreación y Deporte',
            )

    return (CulturaRecreacionDeporteScraper,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # 🐛 Scraper for Goethe-Institut Kolumbien

    Source: https://www.goethe.de/ins/co/es/ver.cfm

    List: https://www.goethe.de/rest/objeventcalendarRedesign/events/fetchEvents?configData=%7B%22category_ID%22%3A%22178926_178927_178937_178936_178935_178934_178933_178932_178931_178930_178929_178928_178938%22%2C%22elementsperpage%22%3A20%2C%22frontendfilter%22%3A%22adress_IDtxt%2Ccategory_IDtxt%2Cdate_range%22%2C%22headline%22%3A%22Calendario%22%2C%22outputtype%22%3A%22standardkalender%22%2C%22weekend_day_start%22%3A5%2C%22institute_ID%22%3A%22336_420%22%2C%22week_day_start%22%3A0%2C%22timezone%22%3A12%7D&langId=158&viewMode=-1&filterData=%7B%22start%22%3A0%7D

    Detail: https://www.goethe.de/ins/co/es/ver.cfm?event_id=27236898
    ⚠ Se abre sólo desde Colombia

    https://docs.google.com/spreadsheets/d/1B-QPzjCQbnMIbcSfd9aqyOAzeynSX1TogZWKgRTF10w/edit?gid=0#gid=0
    """)
    return


@app.cell(hide_code=True)
def _(
    BaseEventScraper,
    CATEGORY_ART,
    CATEGORY_SOCIETY,
    Event,
    Fore,
    Optional,
    pq,
):
    class GoetheInstitutKolumbienScraper(BaseEventScraper):
        spreadsheet_id = '1B-QPzjCQbnMIbcSfd9aqyOAzeynSX1TogZWKgRTF10w'

        API_URL = "https://www.goethe.de/rest/objeventcalendarRedesign/events/fetchEvents"
        PARAMS = {
            "configData": '{"category_ID":"178926_178927_178937_178936_178935_178934_178933_178932_178931_178930_178929_178928_178938","elementsperpage":20,"frontendfilter":"adress_IDtxt,category_IDtxt,date_range","headline":"Calendario","outputtype":"standardkalender","weekend_day_start":5,"institute_ID":"336_420","week_day_start":0,"timezone":12}',
            "langId": "158",
            "viewMode": "-1",
            "filterData": '{"start":0}'
        }

        def get_headers(self) -> dict:
            return {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
                'Referer': 'https://www.goethe.de/ins/co/es/ver.cfm',
                'Connection': 'keep-alive'
            }

        def get_events_list(self):
            response = self.session.get(self.API_URL, params=self.PARAMS)
            assert response.status_code == 200

            data = response.json()

            # adjust key if needed after inspecting response
            return data.get("eventItems", [])

        def build_event(self, raw_event) -> Optional[Event]:
            event_city = raw_event['event_city']  # Bogotá
            location_IDtxt = raw_event.get('location_IDtxt')  # Goethe-Institut Kolumbien
            date_start = raw_event['date_start_ical']  # 2026-04-22
            time_start = raw_event['time_start_raw']  # 16:00
            event_title = raw_event['headline']
            event_id = raw_event['object_id']
            event_type = raw_event['event_type']
            is_online = bool(raw_event['is_online'])  # 0 or 1
            price = raw_event['price']  # Gratis con inscripción previa; Entrada libre hasta completar aforo
            subheadline = raw_event['subheadline']  # Los miércoles son de cine alemán. Con entrada libre y para todo público.

            secondary_categories = raw_event.get('secondary_categories', [])
            if secondary_categories:
                event_type = secondary_categories[0]['category_text']
            category_map = {
                'Taller': '',
                'Proyección de película': CATEGORY_ART,
                'Danza': CATEGORY_ART,
                'Música': CATEGORY_ART,
                'Sesión online': '',
                'Sociedad y temas de actualidad': CATEGORY_SOCIETY,
                'Cine': CATEGORY_ART,
            }

            eventSeries = raw_event.get('eventSeries', [])
            if eventSeries:
                event_series = eventSeries[0]['series_text']  # Miércoles de cine alemán; Alemania en escena
            else:
                event_series = ''

            event_url = f"https://www.goethe.de/ins/co/es/ver.cfm?event_id={event_id}"

            # Use self.session to inherit the browser headers
            response = self.session.get(event_url)
            assert response.status_code == 200, f'Failed to fetch {event_url}: status code {response.status_code}'

            event_detail_pq = pq(response.content.decode('utf-8'))

            image_url = f"https://www.goethe.de{event_detail_pq('.event-calendar .image-wrapper img').attr('src')}"

            place_name_raw = location_IDtxt
            if not place_name_raw:
                print(Fore.RED, f'Skipping: no place {place_name_raw}')
                return None
            place_mapping = {
                'Goethe-Institut Kolumbien': 'Goethe-Institut Kolumbien',
                'Teatro Mayor Julio Mario Santo Domingo, ': 'Teatro Mayor Julio Mario Santo Domingo',
            }
            place_name = place_name_mapping(place_map=place_mapping, place_name_raw=place_name_raw)

            description = event_detail_pq('.event-calendar-infotext-container').html()
            return Event(
                event_id=f'GoetheCOL_{event_id}',
                title=str(event_title),
                date=f'{date_start} {time_start}',  # YYYY-MM-DD HH:MM
                place=place_name,
                category=category_map.get(event_type, CATEGORY_ART),
                description=str(description),
                url=event_url,
                image_url=image_url,
                organizer='Goethe-Institut Kolumbien',
            )

    return (GoetheInstitutKolumbienScraper,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # 🚧 UNAL Patrimonio Cultural

    Source: https://patrimoniocultural.bogota.unal.edu.co/calendario/

    https://docs.google.com/spreadsheets/d/1-gzaSsWp31gMnMKSZi-Zzt495-bchEO0Cd4LIZ73Bjs/edit?gid=0#gid=0
    """)
    return


@app.cell
def _(
    BaseEventScraper,
    CATEGORY_ART,
    Event,
    Fore,
    Optional,
    TODAY,
    datetime,
    pq,
):
    import re


    class UnalPatrimonioCulturalScraper(BaseEventScraper):
        spreadsheet_id = '1-gzaSsWp31gMnMKSZi-Zzt495-bchEO0Cd4LIZ73Bjs'

        def get_headers(self) -> dict:
            return {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }

        def _parse_date(self, date_text: str) -> str:
            """
            Parses Spanish date formats like:
            'Sábado 31 de octubre de 2026 — 4:00 p. m.' or 'Miércoles 25 de noviembre de 2026 — 7:00 p. m.'
            into 'YYYY-MM-DD HH:MM'
            """
            try:
                # Clean text
                date_text = date_text.strip().lower()

                # Extract components: day_num, month_name, year, hour, minute, am_pm
                months_map = {
                    'enero': 1, 'febrero': 2, 'marzo': 3, 'abril': 4, 'mayo': 5, 'junio': 6,
                    'julio': 7, 'agosto': 8, 'septiembre': 9, 'octubre': 10, 'noviembre': 11, 'diciembre': 12
                }

                # Match pattern: de [month] de [year] — [hour]:[minute] [a. m. / p. m.]
                pattern = r'(\d+)\s+de\s+([a-z]+)\s+de\s+(\d{4})\s*—?\s*(\d+):(\d+)\s*(a\.?\s*m\.?|p\.?\s*m\.?)'
                match = re.search(pattern, date_text)
                if not match:
                    # Fallback to date without time if pattern fails
                    pattern_no_time = r'(\d+)\s+de\s+([a-z]+)\s+de\s+(\d{4})'
                    match_no_time = re.search(pattern_no_time, date_text)
                    if match_no_time:
                        day = int(match_no_time.group(1))
                        month = months_map.get(match_no_time.group(2), 1)
                        year = int(match_no_time.group(3))
                        return f"{year:04d}-{month:02d}-{day:02d} 00:00"
                    return ''

                day = int(match.group(1))
                month_name = match.group(2)
                month = months_map.get(month_name, 1)
                year = int(match.group(3))
                hour = int(match.group(4))
                minute = int(match.group(5))
                ampm = match.group(6).replace('.', '').replace(' ', '')

                if 'p' in ampm and hour < 12:
                    hour += 12
                elif 'a' in ampm and hour == 12:
                    hour = 0

                return f"{year:04d}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}"
            except Exception as e:
                print(Fore.RED, f"Error parsing date '{date_text}': {e}")
                return ''

        def get_events_list(self):
            # Query the calendar today date
            start_date = TODAY.strftime('%Y-%m-%d')
            end_date = (TODAY + datetime.timedelta(days=60)).strftime('%Y-%m-%d')
            cal_month = TODAY.month
            cal_year = TODAY.year

            url = f'https://patrimoniocultural.bogota.unal.edu.co/calendario/?start_date={start_date}&end_date={end_date}&cal_month={cal_month}&cal_year={cal_year}'
            response = self.session.get(url)
            assert response.status_code == 200, f'Failed to load calendar: status code {response.status_code}'

            content_pq = pq(response.content.decode('utf-8'))
            # Find event container blocks in the calendar view
            events_list = content_pq('.calfront-dialog__contenido')
            print(f'Total {len(events_list)} events for {start_date} - {end_date}, {cal_month}, {cal_year}')
            return events_list

        def build_event(self, raw_event) -> Optional[Event]:
            event_pq = pq(raw_event)

            event_title = event_pq('.titlemodbox strong').text().strip()
            if not event_title:
                print(Fore.RED, 'No title found')
                return None

            event_path = event_pq('.botonvermas a').attr('href')
            event_url = f'https://patrimoniocultural.bogota.unal.edu.co{event_path}' if event_path.startswith('/') else event_path

            image_url = event_pq('.divrighth img').attr('src')

            # Example: Sábado 31 de octubre de 2026 — 4:00 p. m.
            date_text = event_pq('.datemodbox').text().strip()
            event_date = self._parse_date(date_text)

            # If date is invalid or couldn't be parsed, skip this row
            if not event_date:
                print(Fore.RED, f"Skipping event '{event_title}' due to unparseable date: '{date_text}'")
                return None

            place_name = 'Auditorio Leon De Greiff'

            # Fetch detail page
            response = self.session.get(event_url)
            if response.status_code != 200:
                print(Fore.RED, f'Failed to load details for: {event_title}')
                return None

            detail_pq = pq(response.content.decode('utf-8'))

            description_blocks = detail_pq('.wp-post .elementor-element-6731595 .elementor-widget[data-element_type=widget]')
            description = '<br />'.join([pq(block).html() for block in description_blocks if pq(block).html()])

            # Generate a stable unique ID based on the URL suffix
            event_id = f"UNAL_{event_path.strip('/')}"

            return Event(
                event_id=event_id,
                title=event_title,
                date=event_date,
                place=place_name,
                category=CATEGORY_ART,
                description=description,
                url=event_url,
                image_url=image_url,
                organizer='Universidad Nacional de Colombia'
            )

    return (UnalPatrimonioCulturalScraper,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # 🏃 Scrapper runner
    """)
    return


@app.cell(hide_code=True)
def _(
    AlianzaFrancesaDeBogotaScraper,
    CulturaRecreacionDeporteScraper,
    FilarmonicaScraper,
    GoetheInstitutKolumbienScraper,
    IdartesScraper,
    UnalPatrimonioCulturalScraper,
):
    SCRAPERS_MAP = {
        'filarmonica_de_bogota': FilarmonicaScraper,
        'idartes': IdartesScraper,
        'alianza_francesa_de_bogota': AlianzaFrancesaDeBogotaScraper,
        'secretaria_de_cultura_recreacion_y_deporte': CulturaRecreacionDeporteScraper,
        'goethe_institut_kolumbien': GoetheInstitutKolumbienScraper,
        'unal_patrimonio_cultural': UnalPatrimonioCulturalScraper,
    }
    return (SCRAPERS_MAP,)


@app.cell(hide_code=True)
def selector(SCRAPERS_MAP, mo):
    dropdown = mo.ui.dropdown(options=SCRAPERS_MAP.keys(), label='Choose a source')
    return (dropdown,)


@app.cell
def _(dropdown, mo):
    mo.hstack([dropdown, mo.md(f"Has value: {dropdown.value}")])
    return


@app.cell
def _(Fore, SCRAPERS_MAP, dropdown):
    scrapper_runner_class = SCRAPERS_MAP.get(dropdown.value, None)
    if scrapper_runner_class is not None:
        try:
            scrapper_runner_class().run()
        except AssertionError as e:
            print(Fore.RED + f"Execution stopped due to restriction: {e}")
            print(Fore.YELLOW + "Suggestion: The website is blocking automated requests. Try running again in a few moments, or check if the target URLs are accessible via your browser.")
    else:
        print('No source is selected')
    return


if __name__ == "__main__":
    app.run()
