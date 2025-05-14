import markdown
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

from desparchado.utils import sanitize_html
from events.models import Event, Organizer, Speaker
from places.models import Place
from games.models import HuntingOfSnarkCriteria
from blog.models import Post

User = get_user_model()


class Command(BaseCommand):
    help = 'Migrates Markdown Event, Place, Organizer and Speaker descriptions fields to HTML'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE('Started migration'))

        for event in Event.objects.all():
            event.description = sanitize_html(markdown.markdown(event.description))
            event.save()

        for place in Place.objects.all():
            place.description = sanitize_html(markdown.markdown(place.description))
            place.save()

        for organizer in Organizer.objects.all():
            organizer.description = sanitize_html(markdown.markdown(organizer.description))
            organizer.save()

        for speaker in Speaker.objects.all():
            speaker.description = sanitize_html(markdown.markdown(speaker.description))
            speaker.save()

        for criteria in HuntingOfSnarkCriteria.objects.all():
            criteria.name = markdown.markdown(criteria.name)
            criteria.save()

        for post in Post.objects.all():
            post.content = markdown.markdown(post.content)
            post.save()

        self.stdout.write(self.style.SUCCESS('Successfully migrated to HTML'))
