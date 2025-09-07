import json
import logging
import mimetypes
from pathlib import Path
from typing import Any

import gspread
import requests
from dateutil.parser import parse
from django.conf import settings
from django.core.files.base import ContentFile
from django.utils import timezone

from desparchado.utils import sanitize_html
from events.models import Event, Organizer
from places.models import Place

logger = logging.getLogger(__name__)


def sync_events(
    spreadsheet_id: str,
    worksheet_number: int,
    worksheet_range: str,
    request_user,
    event_id_field: str = "event_source_url",
) -> list[dict[str, Any]]:
    """Sync events from a Google Sheets worksheet into the Django Event model.

    Reads rows from the given spreadsheet range, parses the event data. For new Events
    the function sets created_by to the provided request_user.

    Parameters:
        spreadsheet_id (str): Google Sheets spreadsheet key.
        worksheet_number (int): Zero-based worksheet index to open.
        worksheet_range (str): Range string to read (e.g., "B2:H100").
        request_user: User used as created_by for newly created Event records.
        event_id_field (str): Event model field used to identify records.

    Returns:
        list[dict]: Per-row result dictionaries. For successful rows each item contains:
            - data: original row data (list of cell values)
            - event: the Event instance
            - created: boolean indicating whether the Event was created
          For rows that failed validation (invalid date, missing Place), items contain:
            - data: original row data (when available)
            - error: human-readable error message

    Side effects:
        - Returns early with a single error dict if spreadsheet credentials
        cannot be loaded.
    """
    try:
        with Path.open(
            settings.BASE_DIR / "spreadsheet_credentials.json",
            "r",
            encoding="utf-8",
        ) as file:
            credentials = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logger.error("Failed to load spreadsheet credentials", exc_info=e)
        return [dict(error="Spreadsheet credentials could not be loaded")]

    gc = gspread.service_account_from_dict(credentials)
    spreadsheet = gc.open_by_key(spreadsheet_id)
    sheet = spreadsheet.get_worksheet(worksheet_number)
    results = sheet.get(worksheet_range)
    logger.debug(results)

    synced_events_data = []

    for event_data in results:
        # id = _get_cell_data(event_data, 'A')
        title = _get_cell_data(event_data, 'B')
        event_date = _get_cell_data(event_data, 'C')
        place_name = _get_cell_data(event_data, 'D')
        category = _get_cell_data(event_data, 'E')
        description_html = _get_cell_data(event_data, 'F')
        event_source_url = _get_cell_data(event_data, 'G')
        image_url = _get_cell_data(event_data, 'H')
        organizer_names = _get_cell_data(event_data, 'I')
        # speakers = _get_cell_data(event_data, 'J')

        try:
            parsed_dt = parse(event_date)
            if getattr(settings, "USE_TZ", False):
                if timezone.is_naive(parsed_dt):
                    parsed_dt = timezone.make_aware(
                        parsed_dt,
                        timezone.get_current_timezone(),
                    )
        except Exception:
            synced_events_data.append(dict(
                data=event_data,
                error=f'Invalid event_date: "{event_date}"',
            ))
            continue

        try:
            place = Place.objects.get(name__iexact=place_name.strip())
        except Place.DoesNotExist:
            synced_events_data.append(dict(
                data=event_data,
                error=f'Place "{place_name}" not found'),
            )
            continue

        organizers = []
        for organizer_name in organizer_names.split(","):
            try:
                organizer = Organizer.objects.get(name__iexact=organizer_name.strip())
                organizers.append(organizer)
            except Organizer.DoesNotExist:
                synced_events_data.append(
                    dict(
                        data=event_data,
                        error=f'Organizer "{organizer_name}" not found',
                    ),
                )
                continue

        defaults = {
            "title": title,
            "description": sanitize_html(description_html),
            "category": category,
            "event_date": parsed_dt,
            "place": place,
            "is_published": True,
            "is_approved": True,
        }

        lookup = {event_id_field: event_source_url}
        event, created = Event.objects.update_or_create(
            **lookup,
            defaults=defaults,
            create_defaults={
                "created_by": request_user,
                **defaults,
            },
        )
        event.organizers.set(organizers)

        if image_url:
            save_image(event, image_url)
        synced_events_data.append(dict(data=event_data, event=event, created=created))

    return synced_events_data


def save_image(event, url):
    """Download an image from a URL and attach it to the given Event's image field.

    If the HTTP response status is not 200 or the Content-Type is not an image,
    the function returns without modifying the event.
    The filename is constructed as "{event.slug}{ext}", where the extension is inferred
    from the response Content-Type (falls back to ".jpg").
    """
    try:
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            logger.warning(
                "Image fetch failed",
                extra={"url": url, "status": response.status_code},
            )
            return
        # Get content type from response
        content_type = (response.headers.get("Content-Type") or "").split(";")[0]
        if not content_type.startswith("image/"):
            logger.warning(
                "Non-image content-type",
                extra={"url": url, "content_type": content_type},
            )
            return

        ext = mimetypes.guess_extension(content_type) or ".jpg"
        filename = f"{event.slug}{ext}"

        # Save file
        file_content = ContentFile(response.content)
        event.image.save(filename, file_content, save=True)
    except requests.RequestException as e:
        logger.error("Image download error", extra={"url": url}, exc_info=e)


def _get_cell_data(row, col_letter):
    """Return the stripped string value from a worksheet row
    for the given Excel-style column letter.

    Parameters:
        row: Sequence of cell values (e.g., list or tuple)
            representing one worksheet row.
        col_letter (str): Uppercase column letter ("A", "B", ...).
            Only ASCII uppercase letters A–Z are supported.

    Returns:
        str: The cell value with surrounding whitespace removed,
            or an empty string if the column index is out of range.
    """
    zero_based_index = ord(col_letter) - ord("A")
    try:
        return row[zero_based_index].strip()
    except IndexError:
        return ""
