import factory
import factory.fuzzy

from ..models import HuntingOfSnarkCategory, HuntingOfSnarkCriteria, HuntingOfSnarkGame


class HuntingOfSnarkGameFactory(factory.django.DjangoModelFactory):
    player_name = factory.fuzzy.FuzzyText(length=100)
    total_points = factory.fuzzy.FuzzyInteger(low=1)

    @factory.post_generation
    def criteria(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        if extracted:
            # A list of groups were passed in, use them
            for criteria in extracted:
                self.criteria.add(criteria)

    class Meta:
        model = HuntingOfSnarkGame


class HuntingOfSnarkCategoryFactory(factory.django.DjangoModelFactory):
    name = factory.Sequence(lambda n: f'category title {n}')

    class Meta:
        model = HuntingOfSnarkCategory


class HuntingOfSnarkCriteriaFactory(factory.django.DjangoModelFactory):
    public_id = factory.Sequence(lambda n: n)
    name = factory.fuzzy.FuzzyText(length=100)
    category = factory.SubFactory(HuntingOfSnarkCategoryFactory)

    class Meta:
        model = HuntingOfSnarkCriteria
