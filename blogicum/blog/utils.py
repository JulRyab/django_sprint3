from django.core.paginator import Paginator
from django.db.models import Count, QuerySet
from django.utils import timezone

from blog.models import Post


def get_filtered_posts(
    *,
    apply_filters: bool = True,
    queryset: QuerySet = None,
) -> QuerySet:
    if queryset is None:
        queryset = Post.objects.all()

    queryset = queryset.select_related(
        'category', 'author', 'location'
    ).annotate(
        comment_count=Count('comments')
    ).order_by(*Post._meta.ordering)

    if apply_filters:
        queryset = queryset.filter(
            is_published=True,
            category__is_published=True,
            pub_date__lte=timezone.now(),
        )

    return queryset


def profile_posts_paginator(request, posts, per_page=10):
    paginator = Paginator(posts, per_page)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)
