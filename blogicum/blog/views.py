from django.shortcuts import get_object_or_404, render
from blog.models import Post, Category
from django.utils import timezone


# Create your views here.


def index(request):
    template = 'blog/index.html'
    post_list = (
        Post.objects.select_related('category')
        .only(
            'title',
            'pub_date',
            'is_published',
            'category__title',
            'category__is_published',
            'category__description',
            'category__slug'
        )
        .filter(
            is_published=True,
            category__is_published=True,
            pub_date__lt=timezone.now())
    )[:5]
    context = {'post_list': post_list}
    return render(request, template, context)


def post_detail(request, id):
    template = 'blog/detail.html'
    post = get_object_or_404(
        Post.objects.select_related(
            'location',
            'author',
            'category'
        ).only(
            'title',
            'text',
            'pub_date',
            'location__name',
            'location__is_published',
            'author__username',
            'category__title',
            'category__description',
            'category__slug'
        ),
        pk=id,
        is_published=True,
        category__is_published=True,
        pub_date__lt=timezone.now()
    )
    context = {'post': post}
    return render(request, template, context)


def category_posts(request, category_slug):
    template = 'blog/category.html'
    category_obj = get_object_or_404(
        Category.objects.all(),
        slug=category_slug,
        is_published=True
    )

    post_list = Post.objects.select_related(
        'location',
        'author',
        'category'
    ).only(
        'title',
        'pub_date',
        'location__is_published',
        'location__name',
        'text',
        'author__username',
        'category__title',
        'category__description',
        'category__slug'
    ).filter(
        is_published=True,
        category=category_obj,
        pub_date__lt=timezone.now()
    )

    context = {
        'category': category_obj,
        'post_list': post_list}
    return render(request, template, context)
