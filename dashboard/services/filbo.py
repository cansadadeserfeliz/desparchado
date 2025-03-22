import json
import re
import logging
from dateutil.parser import parse

import gspread
from django.conf import settings
from django.contrib.gis.geos import Point
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError

from dashboard.data.filbo import ORGANIZERS_MAP, SPEAKERS_MAP
from events.models import Event, Organizer, Speaker
from places.models import Place, City
from specials.models import Special


logger = logging.getLogger(__name__)

def get_organizers(organizer_name, request_user):
    default_organizer = Organizer.objects.get(
        name='Feria Internacional del Libro de Bogotá - FILBo'
    )
    organizers = [default_organizer]

    canonical_organizer_name = ORGANIZERS_MAP.get(organizer_name.strip())
    if canonical_organizer_name:
        organizer, created = Organizer.objects.get_or_create(
            name=canonical_organizer_name,
            defaults=dict(
                description=canonical_organizer_name,
                created_by=request_user,
            ),
        )
        if created:
            logger.warning(f'FILBo organizer was created: {organizer}')
        organizers.append(organizer)

    return organizers

def get_speakers(participants, request_user):
    speakers = []

    for original_name, canonical_name in SPEAKERS_MAP.items():
        if original_name in participants:
            speaker = Speaker.objects.filter(name__iexact=canonical_name).first()
            if speaker and speaker not in speakers:
                speakers.append(speaker)

    return speakers

def get_place(place_name, request_user):
    formatted_place_name = f'{place_name} | Corferias'
    try:
        return Place.objects.get(name=formatted_place_name)
    except Place.DoesNotExist:
        return Place.objects.create(
            name=formatted_place_name,
            city=City.objects.get(name='Bogotá'),
            description='Cra. 37 #24-67, Bogotá',
            location=Point(-74.09004806440831, 4.6295913075934045),  # Corferias default
            created_by=request_user,
        )


def sync_filbo_event(event_data, special, request_user):
    logger.info(f'Started sync for FILBo event: {event_data}')

    def _get_event_field(col):
        zero_based_index = ord(col) - ord('A')
        try:
            return event_data[zero_based_index].strip()
        except IndexError:
            return ''

    title = _get_event_field('A')
    event_date = _get_event_field('B')
    start_time = _get_event_field('C')
    end_time = _get_event_field('D')
    place = _get_event_field('E')
    target_audience = _get_event_field('F')
    category = _get_event_field('G')
    link = _get_event_field('H')
    image_link = _get_event_field('I')
    description = _get_event_field('J')
    organizer = _get_event_field('K')
    participants = _get_event_field('L')

    match = re.search(r'/descripcion-actividad/(\d+)/', link)
    filbo_id = match.group(1) if match else None

    if filbo_id is None:
        logger.warning(f'FILBo ID was not found for {link}')

    event_start_date = parse(f'{event_date} {start_time}')
    event_end_date = parse(f'{event_date} {end_time}')
    logger.debug(f'FILBo event ID extracted: {filbo_id}, {event_start_date} - {event_end_date}')

    title = title.strip().rstrip('-')
    description = description.strip().rstrip('-')

    try:
        URLValidator()(link)
    except (ValidationError,) as e:
        logger.error(f'Invalid FILBo event URL', extra=dict(link=link), exc_info=e)
        return

    if len(link) > Event.EVENT_SOURCE_URL_MAX_LENGTH:
        logger.error(f'Invalid FILBo event URL', extra=dict(link=link))
        return

    event_type = None
    topic = None
    if category in [
        'Firma de Libros',
        'Presentaciones de libros',
        'FILBo Literatura',
        'FILBo Poesía',
    ]:
        topic = Event.EVENT_TOPIC_BOOKS
    elif category in ['FILBo Medio Ambiente']:
        topic = Event.EVENT_TOPIC_ENVIRONMENT
    elif category in ['FILBo Ciencia']:
        topic = Event.EVENT_TOPIC_SCIENCE
    elif category in ['FILBo Ilustrada']:
        topic = Event.EVENT_TOPIC_ART

    defaults = dict(
        title=f'{title} | FILBo 2025',
        description=description or title,
        event_type=event_type,
        topic=topic,
        event_date=event_start_date,
        event_end_date=event_end_date,
        event_source_url=link,
        place=get_place(place_name=place, request_user=request_user),
        is_published=True,
        is_approved=True,
    )
    logger.debug(f'FILBo event {filbo_id} defaults', extra=defaults)
    event, created = Event.objects.update_or_create(
        filbo_id=filbo_id,
        defaults=defaults,
        create_defaults=dict(created_by=request_user, **defaults),
    )

    event.organizers.set(get_organizers(organizer_name=organizer, request_user=request_user))
    event.speakers.set(get_speakers(participants=participants, request_user=request_user))
    event.save()

    special.related_events.add(event)

    status = 'created' if created else 'updated'
    logger.debug(f'FILBo event {filbo_id} was {status}: {event}')


def sync_filbo_events(
    spreadsheet_id: str,
    worksheet_number: int,
    worksheet_range: str,
    request_user,
) -> None:
    with open(settings.BASE_DIR / 'spreadsheet_credentials.json', 'r', encoding='utf-8') as file:
        credentials = json.load(file)

    gc = gspread.service_account_from_dict(credentials)
    spreadsheet = gc.open_by_key(spreadsheet_id)
    sheet = spreadsheet.get_worksheet(worksheet_number)
    results = sheet.get(worksheet_range)
    logger.info(results)

    special = Special.objects.filter(title='FILBo 2025').first()

    for event_data in results:
        sync_filbo_event(event_data=event_data, special=special, request_user=request_user)
