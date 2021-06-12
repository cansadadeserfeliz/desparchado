import factory

from django.contrib.auth import get_user_model

User = get_user_model()


class UserFactory(factory.django.DjangoModelFactory):
    first_name = factory.Faker('name')
    email = factory.Faker('email')
    username = factory.Faker('user_name')
    is_superuser = False
    is_staff = False
    is_active = True

    class Meta:
        model = User
        django_get_or_create = ('username',)
