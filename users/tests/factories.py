import factory

from django.contrib.auth import get_user_model

User = get_user_model()


class UserFactory(factory.django.DjangoModelFactory):
    first_name = factory.Faker('name')
    username = factory.Faker('user_name')

    class Meta:
        model = User
        django_get_or_create = ('username',)
