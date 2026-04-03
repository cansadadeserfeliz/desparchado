import json
import logging
import re
from pathlib import Path

import gspread
from dateutil.parser import parse
from django.conf import settings
from django.contrib.gis.geos import Point
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator

from dashboard.data.filbo import ORGANIZERS_MAP
from events.models import Event, Organizer, Speaker
from places.models import City, Place
from specials.models import Special

logger = logging.getLogger(__name__)


FILBO_SPECIAL_TITLE = 'FILBo 2026'
SOURCE_ID_PREFIX = 'FILBO2026_'
EVENT_TITLE_SUFFIX = 'FILBo 2026'


def get_organizers(organizer_name, default_organizer, request_user):
    organizers = [default_organizer]

    canonical_organizer_name = ORGANIZERS_MAP.get(organizer_name.strip())
    if canonical_organizer_name:
        organizer, created = Organizer.objects.get_or_create(
            name=canonical_organizer_name,
            defaults={
                "description": canonical_organizer_name,
                "created_by": request_user,
            },
        )
        if created:
            logger.warning(f'FILBo organizer was created: {organizer}')
        organizers.append(organizer)

    return organizers


def _speaker_matches(
    speaker_record: dict,
    participants: str,
    event_title: str,
    event_description: str,
) -> bool:
    filbo_name = speaker_record['FILBO_NAME']
    canonical_name = speaker_record['CANONICAL_NAME']
    search_texts = (participants, event_title, event_description)
    return any(filbo_name in text or canonical_name in text for text in search_texts)


def get_speakers(
    participants, speakers_map, event_title, event_description, request_user,
):
    seen: set[str] = set()
    speakers = []

    for speaker_record in speakers_map:
        if not speaker_record['FILBO_NAME'] or not speaker_record['CANONICAL_NAME']:
            continue
        if not _speaker_matches(
            speaker_record, participants, event_title, event_description,
        ):
            continue

        canonical_name = speaker_record['CANONICAL_NAME']
        if canonical_name in seen:
            continue

        speaker, _ = Speaker.objects.get_or_create(
            name=canonical_name,
            defaults={
                "created_by": request_user,
                "description": speaker_record['DESCRIPTION'],
            },
        )
        seen.add(canonical_name)
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
            address='Cra. 37 #24-67, Bogotá',
            location=Point(-74.09004806440831, 4.6295913075934045),  # Corferias default
            created_by=request_user,
        )


# pylint: disable=too-many-locals
def sync_filbo_event(
    event_data,
    special,
    speakers_map,
    default_organizer,
    request_user,
):
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
    place = _get_event_field('E')
    # target_audience = _get_event_field('F')
    filbo_category = _get_event_field('G')
    link = _get_event_field('H')
    # image_link = _get_event_field('I')
    description = _get_event_field('J')
    organizer = _get_event_field('K')
    participants = _get_event_field('L')

    match = re.search(r'/descripcion-actividad/(\d+)/', link)
    filbo_id = match.group(1) if match else None

    if filbo_id is None:
        logger.error(f'FILBo ID was not found for {link}')
        return None

    filbo_id = SOURCE_ID_PREFIX + filbo_id

    event_start_date = parse(f'{event_date} {start_time}')
    logger.debug(
        f'FILBo event ID extracted: {filbo_id}, {event_start_date}',
    )

    title = title.strip().rstrip('-')
    description = description.strip().rstrip('-')

    try:
        URLValidator()(link)
    except (ValidationError,) as e:
        logger.error('Invalid FILBo event URL', extra={"link": link}, exc_info=e)
        return None

    if len(link) > Event.EVENT_SOURCE_URL_MAX_LENGTH:
        logger.error('Invalid FILBo event URL', extra={"link": link})
        return None

    category = {
        'Firma de Libros': Event.Category.LITERATURE,
        'Presentaciones de libros': Event.Category.LITERATURE,
        'FILBo Literatura': Event.Category.LITERATURE,
        'FILBo Poesía': Event.Category.LITERATURE,
        'FILBo Medio Ambiente': Event.Category.ENVIRONMENT,
        'FILBo Ciencia': Event.Category.SCIENCE,
        'FILBo Ilustrada': Event.Category.ART,
        'FILBo Música': Event.Category.ART,
    }.get(filbo_category, '')

    defaults = {
        'title': f'{title} | {EVENT_TITLE_SUFFIX}',
        'description': description or title,
        'category': category,
        'event_date': event_start_date,
        'event_source_url': link,
        'place': get_place(place_name=place, request_user=request_user),
        'is_published': True,
        'is_approved': True,
    }
    logger.debug(f'FILBo event {filbo_id} defaults', extra=defaults)
    event, created = Event.objects.update_or_create(
        source_id=filbo_id,
        defaults=defaults,
        create_defaults={"created_by": request_user, **defaults},
    )

    event.organizers.set(
        get_organizers(
            organizer_name=organizer,
            default_organizer=default_organizer,
            request_user=request_user,
        ),
    )
    event.speakers.set(
        get_speakers(
            participants=participants,
            speakers_map=speakers_map,
            event_title=title,
            event_description=description,
            request_user=request_user,
        ),
    )

    special.related_events.add(event)

    status = 'created' if created else 'updated'
    logger.debug(f'FILBo event {filbo_id} was {status}: {event}')

    return filbo_id


# pylint: disable=too-many-locals
def sync_filbo_events(
    spreadsheet_id: str,
    worksheet_number: int,
    worksheet_range: str,
    request_user,
) -> None:
    with Path.open(
        settings.BASE_DIR / 'spreadsheet_credentials.json', 'r', encoding='utf-8',
    ) as file:
        credentials = json.load(file)

    gc = gspread.service_account_from_dict(credentials)
    spreadsheet = gc.open_by_key(spreadsheet_id)
    sheet = spreadsheet.get_worksheet(worksheet_number)
    results = sheet.get(worksheet_range)
    logger.info(results)

    speakers_map = spreadsheet.get_worksheet(1).get_all_records()

    special = Special.objects.filter(title=FILBO_SPECIAL_TITLE).first()
    default_organizer = Organizer.objects.get(
        name='Feria Internacional del Libro de Bogotá - FILBo',
    )

    synced_filbo_ids = set()

    for event_data in results:
        filbo_id = sync_filbo_event(
            event_data=event_data,
            special=special,
            speakers_map=speakers_map,
            default_organizer=default_organizer,
            request_user=request_user,
        )
        if filbo_id is not None:
            synced_filbo_ids.add(filbo_id)

    all_events = Event.objects.filter(
        source_id__startswith=SOURCE_ID_PREFIX,
    )
    logger.info(f'>>> ALL FILBo events: {all_events.count()}')
    unpublished_events = all_events.exclude(source_id__in=synced_filbo_ids)
    logger.info(f'>>> UNPUBLISHED FILBo events: {unpublished_events.count()}')

    unpublished_events.update(is_published=False)
