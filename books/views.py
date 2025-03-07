from django.views.generic import DetailView
from django.views.generic import ListView
from django.views.generic import TemplateView

from .models import Book
from .data import BOOKSHOPS_LIST


class HomeTemplateView(TemplateView):
    template_name = 'books/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['books'] = Book.objects.published().order_by('-created')[:10]
        return context


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
        context['book_price_tags_list'] = [
            {
                'url': bookshop['search_by_isbn_url'].format(isbn=self.object.isbn),
                'title': bookshop['name']
            }
            for bookshop in BOOKSHOPS_LIST
        ]
        return context
