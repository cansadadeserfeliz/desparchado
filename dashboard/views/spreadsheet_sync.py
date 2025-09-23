from django.views.generic import FormView

from dashboard.forms import SpreadsheetSyncForm
from dashboard.mixins import SuperuserRequiredMixin
from dashboard.services.spreadsheet_sync import sync_events


class SpreadsheetSyncFormView(SuperuserRequiredMixin, FormView):
    form_class = SpreadsheetSyncForm
    template_name = "dashboard/spreadsheet_sync/form.html"

    def form_valid(self, form):
        """Handle a valid SpreadsheetSyncForm submission, run the spreadsheet sync
        and render the response with sync results.
        """
        synced_events_data = sync_events(
            spreadsheet_sync=form.cleaned_data['spreadsheet_sync'],
            worksheet_range=form.cleaned_data['worksheet_range'],
            request_user=self.request.user,
        )

        context = self.get_context_data(form=form)
        context["synced_events_data"] = synced_events_data
        return self.render_to_response(context=context)
