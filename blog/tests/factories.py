import factory
import factory.fuzzy

from users.tests.factories import UserFactory

from ..models import Post


class PostFactory(factory.django.DjangoModelFactory):
    title = factory.fuzzy.FuzzyText(length=100)
    created_by = factory.SubFactory(UserFactory)
    is_published = True
    is_approved = True

    class Meta:
        model = Post
