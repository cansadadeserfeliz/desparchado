from django.urls import reverse_lazy
from django.views.generic import FormView

from dashboard.forms import FilboEventCreateForm
from dashboard.mixins import SuperuserRequiredMixin
from dashboard.services import sync_filbo_events


class FilboEventFormView(SuperuserRequiredMixin, FormView):
    form_class = FilboEventCreateForm
    template_name = 'dashboard/filbo/events_form.html'
    success_url = reverse_lazy('dashboard:filbo_event_form')

    def form_valid(self, form):
        sync_filbo_events(
            spreadsheet_id=form.cleaned_data['spreadsheet_id'],
            worksheet_number=form.cleaned_data['worksheet_number'],
            worksheet_range=form.cleaned_data['worksheet_range'],
            request_user=self.request.user,
        )

        return super().form_valid(form)
