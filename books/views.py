from django.views.generic import DetailView

from .models import Book


class BookDetailView(DetailView):
    model = Book

    def get_queryset(self):
        return Book.objects.published().all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['related_events'] = \
            list(self.object.related_events.published().all())
        return context
