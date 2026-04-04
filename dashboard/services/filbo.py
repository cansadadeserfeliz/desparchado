import json
import logging
import re
import urllib.parse
from pathlib import Path
from zoneinfo import ZoneInfo

import gspread
from dateutil.parser import parse
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.gis.geos import Point
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator

from dashboard.data.filbo import ORGANIZERS_MAP
from events.models import Event, Organizer, Speaker
from places.models import City, Place
from specials.models import Special

User = get_user_model()

logger = logging.getLogger(__name__)


FILBO_SPECIAL_TITLE = 'FILBo 2026'
SOURCE_ID_PREFIX = 'FILBO2026_'
EVENT_TITLE_SUFFIX = 'FILBo 2026'


def _normalize_filbo_url(url: str) -> str:
    """Return a valid, percent-encoded URL from a raw FILBo spreadsheet cell.

    Spreadsheet cells sometimes contain the URL split across multiple lines.
    Non-ASCII characters (accented slugs) also cause Django's URLValidator to
    reject otherwise legitimate URLs. This function:
      1. Removes newlines introduced by multi-line cells. Spaces are preserved
         because they are intentional parts of some slugs (encoded as %20).
      2. Percent-encodes non-ASCII and unsafe characters in the URL path while
         leaving the scheme, host, and already-encoded sequences intact.
    """
    # Remove newlines introduced by multi-line spreadsheet cells.
    # Spaces are preserved — they are intentional parts of some slugs and will
    # be percent-encoded as %20 by urllib.parse.quote below.
    url = url.replace('\r\n', '').replace('\n', '').replace('\r', '').strip()
    parsed = urllib.parse.urlsplit(url)
    # Re-encode the path: keep all standard URL-safe chars, encode everything else.
    encoded_path = urllib.parse.quote(parsed.path, safe='/:@!$&\'()*+,;=._~%-')
    return urllib.parse.urlunsplit(parsed._replace(path=encoded_path))


def get_organizers(
    organizer_name: str,
    default_organizer: Organizer,
    request_user: User,
) -> list[Organizer]:
    """Return the list of organizers for a FILBo event.

    Always includes the default FILBo organizer. Then attempts to resolve a
    second organizer in two ways:
    - If organizer_name maps to a canonical name in ORGANIZERS_MAP, that
      organizer is fetched or created and appended.
    - Otherwise, the database is searched case-insensitively for an existing
      organizer with that name; if found, it is appended (no creation).

    Args:
        organizer_name: Raw organizer string from the spreadsheet cell.
        default_organizer: The base FILBo Organizer instance, always included.
        request_user: User assigned as created_by when a new Organizer is created.

    Returns:
        List of Organizer instances (1 or 2 elements).
    """
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
            logger.info(f'FILBo organizer was created: {organizer}')
        organizers.append(organizer)
    else:
        try:
            organizer = Organizer.objects.get(name__iexact=organizer_name)
            organizers.append(organizer)
        except Organizer.DoesNotExist:
            pass

    return organizers


def _speaker_matches(
    speaker_record: dict[str, str],
    participants: str,
    event_title: str,
    event_description: str,
) -> bool:
    """Return True if the speaker's FILBo or canonical name appears in any event field.

    Checks participants, event title, and event description.
    """
    filbo_name = speaker_record['FILBO_NAME'].casefold()
    canonical_name = speaker_record['CANONICAL_NAME'].casefold()
    search_texts = (
        participants.casefold(),
        event_title.casefold(),
        event_description.casefold(),
    )
    return any(filbo_name in text or canonical_name in text for text in search_texts)


def get_speakers(
    participants: str,
    speakers_map: list[dict[str, str]],
    event_title: str,
    event_description: str,
    request_user: User,
) -> list[Speaker]:
    """Resolve Speaker instances for a FILBo event.

    Iterates the speakers map (worksheet 2) and matches each record against the
    participants field, event title, and description. Deduplicates by canonical
    name. Fetches or creates a Speaker for each match.

    Args:
        participants: Raw participants string from the spreadsheet cell.
        speakers_map: List of dicts from gspread.get_all_records(); each dict
            must have FILBO_NAME, CANONICAL_NAME, and DESCRIPTION keys.
        event_title: Event title used as a fallback match target.
        event_description: Event description used as a fallback match target.
        request_user: User assigned as created_by when a new Speaker is created.

    Returns:
        List of Speaker instances (may be empty).
    """
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


def get_place(place_name: str, request_user: User) -> Place:
    """Fetch or create a Place for the given FILBo venue name.

    All FILBo venues are inside Corferias, so the place name is suffixed with
    '| Corferias' and the location defaults to Corferias coordinates.

    Args:
        place_name: Venue name from the spreadsheet (e.g. 'Salón Ágora').
        request_user: User assigned as created_by when a new Place is created.

    Returns:
        A Place instance.
    """
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


def sync_filbo_event(  # noqa: PLR0915
    event_data: list[str],
    special: Special,
    speakers_map: list[dict[str, str]],
    default_organizer: Organizer,
    request_user: User,
    already_synced_ids: set[str] | None = None,
) -> str | None:
    """Upsert a single FILBo event from a spreadsheet row.

    Extracts fields from the positional column list, derives the FILBo ID from
    the event URL, and calls update_or_create on Event. Organizers and speakers
    are resolved and set via M2M. The event is linked to the FILBo Special.

    Column mapping: A=title, B=date, C=start_time, E=place, G=category,
    H=link, J=description, K=organizer, L=participants.

    Args:
        event_data: List of cell values for one spreadsheet row (0-indexed by column).
        special: The FILBo 2026 Special instance to link the event to.
        speakers_map: Passed through to get_speakers(); see that function.
        default_organizer: Passed through to get_organizers(); see that function.
        request_user: User used for any object creation.
        already_synced_ids: Source IDs already processed in this sync run. When a
            row's ID is already present the row is skipped, preserving the first
            occurrence. Needed for 2026 where corrupted source data caused some
            events (e.g. "Inauguración FILBo", ID 46028) to appear multiple times
            with the same /descripcion-actividad/ URL.

    Returns:
        The source_id string (e.g. 'FILBO2026_12345') on success, or None if the
        row is skipped (missing FILBo ID, invalid URL, or duplicate).
    """
    def _get_event_field(col):
        """Return stripped cell value for column letter, or '' if missing."""
        zero_based_index = ord(col) - ord('A')
        try:
            return event_data[zero_based_index].strip()
        except IndexError:
            return ''

    title = _get_event_field('A')
    event_date = _get_event_field('B')
    start_time = _get_event_field('C')
    place = _get_event_field('E')
    filbo_category = _get_event_field('G')
    link = _normalize_filbo_url(_get_event_field('H'))
    description = _get_event_field('J')
    organizer = _get_event_field('K')
    participants = _get_event_field('L')

    match = re.search(r'/descripcion-actividad/(\d+)/', link)
    filbo_id = match.group(1) if match else None

    if filbo_id is None:
        logger.warning(f'FILBo ID was not found for {link}')
        return None

    filbo_id = SOURCE_ID_PREFIX + filbo_id

    # Skip rows whose ID was already processed in this run. This handles the
    # 2026 data corruption where some events share the same source URL and would
    # otherwise overwrite the first (correctly dated) occurrence.
    if already_synced_ids and filbo_id in already_synced_ids:
        logger.warning(f'Skipping duplicate FILBo event: {filbo_id}')
        return None

    # parse() returns a naive datetime; attach Bogotá tz since that is the local
    # time zone used in the spreadsheet.
    event_start_date = parse(f'{event_date} {start_time}').replace(
        tzinfo=ZoneInfo('America/Bogota'),
    )
    logger.debug(
        f'FILBo event ID extracted: {filbo_id}, {event_start_date}',
    )

    title = title.strip().rstrip('-')
    description = description.strip().rstrip('-')

    try:
        URLValidator()(link)
    except ValidationError:
        logger.warning('Skipping FILBo event with invalid URL: %s', link)
        return None

    if len(link) > Event.EVENT_SOURCE_URL_MAX_LENGTH:
        logger.warning('Skipping FILBo event with URL exceeding max length: %s', link)
        return None

    category = {
        'Firma de Libros': Event.Category.LITERATURE,
        'Presentaciones de libros': Event.Category.LITERATURE,
        'FILBo Literatura': Event.Category.LITERATURE,
        'FILBo Poesía': Event.Category.LITERATURE,
        'FILBo Medio Ambiente': Event.Category.ENVIRONMENT,
        'FILBo Ciencia': Event.Category.SCIENCE,
        'FILBo Ilustrada': Event.Category.ART,
        'FILBo Cómic': Event.Category.ART,
        'FILBo Historia': Event.Category.ART,
        'FILBo Música': Event.Category.ART,
        'FILBo Incluyente': Event.Category.SOCIETY,
        'FILBo Diversa': Event.Category.SOCIETY,
        'FILBo Debates': Event.Category.SOCIETY,
        'FILBo Periodismo': Event.Category.SOCIETY,
    }.get(filbo_category, Event.Category.LITERATURE)

    event_description = description or title
    if participants:
        event_description += f'<br><br><b>Participan</b>: {participants}'
    defaults = {
        'title': f'{title} | {EVENT_TITLE_SUFFIX}',
        'description': event_description,
        'category': category,
        'event_date': event_start_date,
        'event_source_url': link,
        'place': get_place(place_name=place, request_user=request_user),
        'is_published': True,
        'is_approved': True,
    }
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


def sync_filbo_events(
    spreadsheet_id: str,
    worksheet_number: int,
    worksheet_range: str,
    request_user: User,
) -> None:
    """Sync all FILBo events from a Google Sheets spreadsheet.

    Reads event rows from worksheet_number using worksheet_range, then upserts
    each row via sync_filbo_event. After syncing, any existing FILBO2026_ events
    not present in the current sheet are unpublished (they were removed upstream).

    Worksheet 0 (or worksheet_number): event rows.
    Worksheet 1: speaker records used to resolve participants.

    Args:
        spreadsheet_id: Google Sheets document ID.
        worksheet_number: Zero-based index of the events worksheet.
        worksheet_range: A1 notation range to read (e.g. 'A2:L500').
        request_user: User passed through to all create/update operations.
    """
    with Path.open(
        settings.BASE_DIR / 'spreadsheet_credentials.json', 'r', encoding='utf-8',
    ) as file:
        credentials = json.load(file)

    gc = gspread.service_account_from_dict(credentials)
    spreadsheet = gc.open_by_key(spreadsheet_id)
    sheet = spreadsheet.get_worksheet(worksheet_number)
    results = sheet.get(worksheet_range)

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
            # Pass the running set so duplicate rows in the sheet are skipped
            # after the first occurrence has been synced.
            already_synced_ids=synced_filbo_ids,
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
