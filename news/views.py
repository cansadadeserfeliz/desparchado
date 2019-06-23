from django.views.generic import ListView

from .models import PressArticle


class PressArticleListView(ListView):
    model = PressArticle
    context_object_name = 'press_articles'
    paginate_by = 50
