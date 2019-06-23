import factory
import factory.fuzzy

from ..models import Book
from ..models import Author
from events.tests.factories import SpeakerFactory


class AuthorFactory(factory.django.DjangoModelFactory):
    name = factory.fuzzy.FuzzyText(length=100)
    speaker = factory.SubFactory(SpeakerFactory)

    class Meta:
        model = Author


class BookFactory(factory.django.DjangoModelFactory):
    title = factory.fuzzy.FuzzyText(length=100)
    description = factory.fuzzy.FuzzyText(length=100)

    @factory.post_generation
    def related_events(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        if extracted:
            # A list of groups were passed in, use them
            for related_event in extracted:
                self.related_events.add(related_event)

    @factory.post_generation
    def authors(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        if extracted:
            # A list of groups were passed in, use them
            for author in extracted:
                self.authors.add(author)

    class Meta:
        model = Book
