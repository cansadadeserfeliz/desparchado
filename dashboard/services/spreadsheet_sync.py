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
        # organizers = _get_cell_data(event_data, 'I')
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
        if image_url:
            save_image(event, image_url)
        synced_events_data.append(dict(data=event_data, event=event, created=created))

    return synced_events_data


def save_image(event, url):
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
    zero_based_index = ord(col_letter) - ord("A")
    try:
        return row[zero_based_index].strip()
    except IndexError:
        return ""
