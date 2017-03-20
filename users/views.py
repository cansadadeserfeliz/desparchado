from django.views.generic import DetailView

from django.contrib.auth import get_user_model

User = get_user_model()


class UserDetailView(DetailView):
    context_object_name = 'user_object'
    model = User
