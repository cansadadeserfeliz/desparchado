import json
import re
import logging
from dateutil.parser import parse

import gspread
from django.conf import settings
from django.contrib.gis.geos import Point

from dashboard.data.filbo import ORGANIZERS_MAP
from events.models import Event, Organizer, Speaker
from places.models import Place, City

logger = logging.getLogger(__name__)

def get_organizers(organizer_name, request_user):
    """
    Retrieves FILBo organizers.
    
    This function returns a list that always includes the default FILBo organizer.
    If the provided organizer name is mapped to a canonical name, the corresponding
    organizer is retrieved or created with the provided user as the creator.
    A warning is logged when a new organizer is created.
        
    Args:
        organizer_name (str): The organizer name used to look up a canonical organizer.
        request_user: The user performing this operation.
        
    Returns:
        list: A list of organizer objects.
    """
    default_organizer = Organizer.objects.get(
        name='Feria Internacional del Libro de Bogotá - FILBo'
    )
    organizers = [default_organizer]

    canonical_organizer_name = ORGANIZERS_MAP.get(organizer_name)
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
    """
    Retrieve speakers matching names specified in a comma-separated list.
    
    Splits the input string into individual name fragments and queries for the first Speaker 
    object whose name contains each fragment. Returns a list of all Speaker objects found.
    
    Args:
        participants: A comma-separated string of speaker name fragments.
    
    Returns:
        A list of Speaker objects corresponding to the matched names.
    """
    participants = participants.split(',')
    speakers = []

    for participant in participants:
        speaker = Speaker.objects.filter(name__icontains=participant).first()
        if speaker:
            speakers.append(speaker)

    return speakers

def get_place(place_name, request_user):
    """
    Retrieves or creates a Place object for a given base name.
    
    This function appends " | Corferias" to the specified place name and attempts to
    retrieve the corresponding Place from the database. If no such Place exists, it
    creates a new one with default details for the Corferias venue, including the city
    ("Bogotá"), a preset description, and geographic coordinates. The provided user
    is recorded as the creator of the new Place.
    
    Args:
        place_name: The base name of the venue.
        request_user: The user who initiated the request and is set as the creator.
    
    Returns:
        The existing or newly created Place instance.
    """
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


def sync_filbo_event(event_data, request_user):
    """
    Synchronizes a FILBo event entry from the provided event data.
    
    This function extracts event details—such as title, date, start/end times, place, and description—from
    a sequence of values (columns A–L). It appends a FILBo label to the title, parses date and time fields,
    and extracts a unique FILBo ID from the event link. Using these details, the function updates or creates
    an Event record in the database and associates it with relevant organizers and speakers.
    
    Args:
        event_data: A sequence of field values corresponding to event columns A to L.
        request_user: The user initiating the synchronization, used for record tracking.
    """
    logger.info(f'Started sync for FILBo event: {event_data}')

    def _get_event_field(col):
        """
        Retrieves the event field for the specified column letter.
        
        Computes a zero-based index from the provided column letter and returns the corresponding element
        from event_data. If the computed index is out of range, an empty string is returned.
        """
        zero_based_index = ord(col) - ord('A')
        try:
            return event_data[zero_based_index]
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
    logger.info(f'FILBo event ID extracted: {filbo_id}, {event_start_date} - {event_end_date}')

    defaults = dict(
        title=f'{title} | FILBo 2025',
        description=description,
        # event_type=,
        # topic=,
        event_date=event_start_date,
        event_end_date=event_end_date,
        event_source_url=link,
        place=get_place(place_name=place, request_user=request_user),
    )
    logger.info(f'FILBo event {filbo_id} defaults', extra=defaults)
    event, created = Event.objects.update_or_create(
        filbo_id=filbo_id,
        defaults=defaults,
        create_defaults=dict(created_by=request_user, **defaults),
    )
    event.organizers.set(get_organizers(organizer_name=organizer, request_user=request_user))
    event.speakers.set(get_speakers(participants=participants, request_user=request_user))
    status = 'created' if created else 'updated'
    logger.info(f'FILBo event {filbo_id} was {status}: {event}')


def sync_filbo_events(
    spreadsheet_id: str,
    worksheet_number: int,
    worksheet_range: str,
    request_user,
) -> None:
    """
    Synchronize FILBo events from a Google Sheets spreadsheet.
    
    This function retrieves event data from a specified range in a worksheet of a
    Google Sheets document using credentials stored in a JSON file. It then iterates
    over each data row to update or create events by invoking sync_filbo_event.
    
    Args:
        spreadsheet_id (str): The ID of the Google Sheets spreadsheet containing event data.
        worksheet_number (int): The index of the worksheet to read data from.
        worksheet_range (str): The cell range within the worksheet to retrieve event data.
        request_user: The user initiating the synchronization process.
    """
    with open(settings.BASE_DIR / 'spreadsheet_credentials.json', 'r', encoding='utf-8') as file:
        credentials = json.load(file)

    gc = gspread.service_account_from_dict(credentials)
    spreadsheet = gc.open_by_key(spreadsheet_id)
    sheet = spreadsheet.get_worksheet(worksheet_number)
    results = sheet.get(worksheet_range)
    logger.info(results)

    for event_data in results:
        sync_filbo_event(event_data=event_data, request_user=request_user)
