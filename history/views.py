from django.views.generic import ListView
from django.views.generic import DetailView
from django.shortcuts import get_object_or_404
from django.db.models import Q

from .models import HistoricalFigure
from .models import Post
from .models import Group
from .models import Event


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
        ).select_related(
            'historical_figure',
        ).prefetch_related(
            'historical_figure_mentions',
            'published_in_groups',
        ).order_by('-post_date').distinct()
        context['posts'] = posts
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
