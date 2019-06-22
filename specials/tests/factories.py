import factory
import factory.fuzzy

from ..models import Special


class SpecialFactory(factory.django.DjangoModelFactory):
    title = factory.fuzzy.FuzzyText(length=100)
    subtitle = factory.fuzzy.FuzzyText(length=100)
    description = factory.fuzzy.FuzzyText(length=100)
    image = factory.django.ImageField()
    is_published = True

    @factory.post_generation
    def related_events(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        if extracted:
            # A list of groups were passed in, use them
            for event in extracted:
                self.related_events.add(event)

    class Meta:
        model = Special
