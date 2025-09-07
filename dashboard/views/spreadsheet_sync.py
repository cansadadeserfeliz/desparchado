from django.views.generic import FormView

from dashboard.forms import SpreadsheetSyncForm
from dashboard.mixins import SuperuserRequiredMixin
from dashboard.services.spreadsheet_sync import sync_events


class SpreadsheetSyncFormView(SuperuserRequiredMixin, FormView):
    form_class = SpreadsheetSyncForm
    template_name = "dashboard/spreadsheet_sync/form.html"

    def form_valid(self, form):
        """
        Handle a valid SpreadsheetSyncForm submission, run the spreadsheet sync, and render the response with sync results.
        
        This method calls the sync_events service using values from form.cleaned_data and the current request user, injects the returned sync results into the view context under the key "synced_events_data", and returns the rendered response (using the view's template and context).
        
        Parameters:
            form: A validated SpreadsheetSyncForm instance. Must provide cleaned_data keys:
                - 'spreadsheet_id'
                - 'worksheet_number'
                - 'worksheet_range'
                - 'event_id_field'
        
        Returns:
            HttpResponse: The rendered response containing the template context with "synced_events_data".
        """
        synced_events_data = sync_events(
            spreadsheet_id=form.cleaned_data['spreadsheet_id'],
            worksheet_number=form.cleaned_data['worksheet_number'],
            worksheet_range=form.cleaned_data['worksheet_range'],
            event_id_field=form.cleaned_data['event_id_field'],
            request_user=self.request.user,
        )

        context = self.get_context_data(form=form)
        context["synced_events_data"] = synced_events_data
        return self.render_to_response(context=context)
