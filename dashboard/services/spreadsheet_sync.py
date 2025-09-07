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

from desparchado.utils import sanitize_html
from events.models import Event
from places.models import Place

logger = logging.getLogger(__name__)


def sync_events(
    spreadsheet_id: str,
    worksheet_number: int,
    worksheet_range: str,
    request_user,
    event_id_field: str = "event_source_url",
) -> list[dict[str, Any]]:
    with Path.open(
        settings.BASE_DIR / "spreadsheet_credentials.json",
        "r",
        encoding="utf-8",
    ) as file:
        credentials = json.load(file)

    gc = gspread.service_account_from_dict(credentials)
    spreadsheet = gc.open_by_key(spreadsheet_id)
    sheet = spreadsheet.get_worksheet(worksheet_number)
    results = sheet.get(worksheet_range)
    logger.info(results)

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
        # organizers = _get_cell_data(event_data, 'I')
        # speakers = _get_cell_data(event_data, 'J')

        try:
            place = Place.objects.get(name=place_name)
        except Place.DoesNotExist:
            synced_events_data.append(dict(
                data=event_data,
                error=f'Place "{place_name}" not found'),
            )
            continue

        defaults = {
            "title": title,
            "description": sanitize_html(description_html),
            "category": category,
            "event_date": parse(event_date),
            "place": place,
            "is_published": True,
            "is_approved": True,
        }

        event, created = Event.objects.update_or_create(
            event_source_url=event_source_url,
            defaults=defaults,
            create_defaults={
                "created_by": request_user,
                **defaults,
            },
        )
        save_image(event, image_url)
        synced_events_data.append(dict(data=event_data, event=event, created=created))

    return synced_events_data


def save_image(event, url):
    response = requests.get(url, timeout=5)
    if response.status_code == 200:
        # Get content type from response
        content_type = response.headers.get("Content-Type", "")
        ext = mimetypes.guess_extension(content_type.split(";")[0])

        filename = event.slug + ext

        # Save file
        file_content = ContentFile(response.content)
        event.image.save(filename, file_content, save=True)


def _get_cell_data(row, col_letter):
    zero_based_index = ord(col_letter) - ord("A")
    try:
        return row[zero_based_index].strip()
    except IndexError:
        return ""
