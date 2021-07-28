from django.views.generic import ListView
from django.views.generic import DetailView
from django.views.generic import TemplateView
from django.core.paginator import Paginator
from django.core.paginator import EmptyPage
from django.core.paginator import PageNotAnInteger
from django.http import HttpResponse
from django.http import JsonResponse
from django.template import loader
from django.shortcuts import get_object_or_404
from django.db.models import Q

from .services import get_posts_with_related_objects
from .models import HistoricalFigure
from .models import Post
from .models import Group
from .models import Event
from .forms import PostsSearchForm

POST_INDEX_PAGINATE_BY = 7


class HistoryIndexTemplateView(TemplateView):
    template_name = 'history/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        posts = get_posts_with_related_objects(Post.objects.all())

        posts_search_form = PostsSearchForm(self.request.GET)
        if posts_search_form.is_valid():
            start_date = posts_search_form.cleaned_data['start_date']
            end_date = posts_search_form.cleaned_data['end_date']
            if start_date:
                posts = posts.filter(post_date__gte=f'{start_date}-01-01 00:00')
            if end_date:
                posts = posts.filter(post_date__lte=f'{end_date}-01-01 00:00')

        posts = posts.order_by('-post_date')[:POST_INDEX_PAGINATE_BY]
        context['posts'] = posts
        context['posts_search_form'] = posts_search_form
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

    if page_number is None:
        return HttpResponse('You must use `page` query parameter.', status=422)

    try:
        page_obj = paginator.page(page_number)
    except EmptyPage:
        return HttpResponse(status=400)
    except PageNotAnInteger:
        return HttpResponse('Page number must be a positive integer', status=422)

    return JsonResponse(
        dict(posts=[
            loader.render_to_string('history/_post.html', dict(post=post, show_groups=True))
            for post in page_obj
        ]),
    )
