from django.views.generic import ListView
from django.views.generic import DetailView

from .models import PressArticle


class PressArticleListView(ListView):
    model = PressArticle
    context_object_name = 'press_articles'
    paginate_by = 30


class PressArticleDetailView(DetailView):
    model = PressArticle
    context_object_name = 'press_article'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['related_books'] = list(self.object.books.published().all())
        return context
