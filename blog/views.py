from django.views.generic import ListView
from django.views.generic import DetailView

from .models import Post


class PostListView(ListView):
    model = Post
    context_object_name = 'posts'
    paginate_by = 10

    def get_queryset(self):
        queryset = Post.objects.published().order_by('-created')
        return queryset.select_related('created_by')


class PostDetailView(DetailView):
    model = Post

    def get_queryset(self):
        return Post.objects.published().all()
