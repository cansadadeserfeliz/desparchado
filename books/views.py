from django.views.generic import DetailView
from django.views.generic import ListView

from .models import Book
from .services import goodreads_get_book_info


class BookListView(ListView):
    model = Book
    context_object_name = 'books'
    paginate_by = 50

    def get_queryset(self):
        queryset = Book.objects.published().order_by('-created')
        return queryset.prefetch_related('authors')


class BookDetailView(DetailView):
    model = Book

    def get_queryset(self):
        return Book.objects.published().all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['related_events'] = \
            list(self.object.related_events.published().all())
        # context['goodreads_info'] = goodreads_get_book_info(self.object.isbn)
        return context
