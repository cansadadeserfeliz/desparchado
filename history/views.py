from django.views.generic import ListView
from django.views.generic import DetailView
from django.views.generic import TemplateView
from django.core.paginator import Paginator
from django.core.paginator import EmptyPage
from django.http import HttpResponse
from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.db.models import Q

from .services import get_posts_with_related_objects
from .models import HistoricalFigure
from .models import Post
from .models import Group
from .models import Event

POST_INDEX_PAGINATE_BY = 2


class HistoryIndexTemplateView(TemplateView):
    template_name = 'history/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        posts = get_posts_with_related_objects(Post.objects.all()).order_by('-post_date')[:POST_INDEX_PAGINATE_BY]
        context['posts'] = posts
        return context


class HistoricalFigureListView(ListView):
    model = HistoricalFigure


class HistoricalFigureDetailView(DetailView):
    model = HistoricalFigure

    def get_object(self, queryset=None):
        return get_object_or_404(HistoricalFigure, token=self.kwargs.get('token'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        posts = Post.objects.filter(
            Q(historical_figure=self.object) | Q(historical_figure_mentions=self.object)
        )
        posts = get_posts_with_related_objects(posts)
        context['posts'] = posts.order_by('-post_date').distinct()
        return context


class PostDetailView(DetailView):
    model = Post

    def get_object(self, queryset=None):
        return get_object_or_404(Post, token=self.kwargs.get('token'))


class GroupDetailView(DetailView):
    model = Group

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        posts = self.object.posts.select_related(
            'historical_figure',
        ).prefetch_related(
            'historical_figure_mentions',
        ).order_by('post_date').distinct()
        context['posts'] = posts
        return context

    def get_object(self, queryset=None):
        return get_object_or_404(Group, token=self.kwargs.get('token'))


class EventsListView(ListView):
    model = Event


class EventDetailView(DetailView):
    model = Event

    def get_object(self, queryset=None):
        return get_object_or_404(Event, token=self.kwargs.get("token"))


def api_post_list(request):
    paginator = Paginator(
        get_posts_with_related_objects(Post.objects.all()).order_by('-post_date'),
        POST_INDEX_PAGINATE_BY
    )

    page_number = request.GET.get('page')

    try:
        page_obj = paginator.page(page_number)
    except EmptyPage:
        return HttpResponse(status=400)
    return render(request, 'history/_api_post_list.html', {'page_obj': page_obj})
