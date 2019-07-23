from django.views.generic import DetailView
from django.views.generic import ListView
from django.views.generic import TemplateView

from .models import Book
from news.models import PressArticle
from news.models import MediaSource


class HomeTemplateView(TemplateView):
    template_name = 'books/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['books'] = Book.objects.published().order_by('-created')[:10]
        context['articles'] = PressArticle.objects.filter(
            media_source__source_type__in=[
                MediaSource.SOURCE_TYPE_BLOG,
                MediaSource.SOURCE_TYPE_BOOKTUBE,
                MediaSource.SOURCE_TYPE_PODCAST,
            ],
        ).select_related('media_source').order_by('-created')[:30]
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
        return context
