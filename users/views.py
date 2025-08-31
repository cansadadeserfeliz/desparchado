from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils import timezone
from django.views.generic import DetailView, FormView, ListView

from events.models import Event

from .forms import RegisterForm

User = get_user_model()


class UserDetailView(LoginRequiredMixin, DetailView):
    context_object_name = 'user_object'
    model = User
    template_name = 'auth/user_detail.html'

    def get_object(self):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        added_events_count = (
            Event.objects.filter(created_by=self.object).published().count()
        )
        context['added_events_count'] = added_events_count
        days_on_page = (timezone.now() - self.object.date_joined).days
        context['days_on_page'] = days_on_page

        return context


class UserCreationFormView(FormView):
    form_class = RegisterForm
    template_name = 'registration/register_form.html'

    def dispatch(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            return HttpResponseRedirect(
                reverse(
                    'users:user_detail',
                ),
            )
        return super().dispatch(*args, **kwargs)

    def form_valid(self, form):
        user = User.objects.create_user(
            form.cleaned_data['username'],
            password=form.cleaned_data['password1'],
            is_active=True,
            first_name=form.cleaned_data['first_name'],
            email=form.cleaned_data['email'],
        )
        authenticate(
            self.request,
            username=user.username,
            password=form.cleaned_data['password1'],
        )
        return HttpResponseRedirect(reverse('users:login'))


class UserAddedEventsListView(LoginRequiredMixin, ListView):
    model = Event
    paginate_by = 30
    template_name = 'auth/user_added_events_list.html'
    context_object_name = 'events'
    ordering = 'modified'

    def get_queryset(self):
        return Event.objects.filter(created_by=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_object'] = self.request.user
        return context
