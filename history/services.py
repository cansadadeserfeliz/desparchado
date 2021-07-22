def get_posts_with_related_objects(posts):
    """
    Applied `select_related` and `prefetch_related` methods to given Post's queryset
    for attributes used in `_post.html` template.
    :param posts: Post's queryset
    :return: Post's queryset
    """
    return posts.select_related(
        'historical_figure',
    ).prefetch_related(
        'historical_figure_mentions',
        'published_in_groups',
    )
