from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
                                  UpdateView)


from blog.forms import CommentForm, PostForm, UserUpdateForm
from blog.models import Category, Comment, Post

User = get_user_model()


class PostListView(ListView):
    model = Post
    template_name = 'blog/index.html'
    ordering = '-pub_date'
    paginate_by = 10

    def get_queryset(self):
        return (Post.objects
                .select_related('category', 'author', 'location')
                .filter(
                    is_published=True,
                    category__is_published=True,
                    pub_date__lte=timezone.now())
                .order_by('-pub_date'))


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'
    context_object_name = 'post'

    def get_queryset(self):
        queryset = Post.objects.select_related(
            'location', 'author', 'category'
        ).prefetch_related('comments__author')

        if self.request.user.is_authenticated and (
            self.request.user.is_staff
            or Post.objects.filter(pk=self.kwargs['pk'],
                                   author=self.request.user).exists()):
            return queryset
        return queryset.filter(
            is_published=True,
            category__is_published=True,
            pub_date__lte=timezone.now(),
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comments'] = self.object.comments.all()
        context['form'] = CommentForm()
        return context


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('blog:profile', kwargs={
            'username': self.request.user.username
        })


class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def test_func(self):
        return self.request.user == self.get_object().author

    def handle_no_permission(self):
        return redirect('blog:post_detail', pk=self.kwargs['pk'])

    def get_success_url(self):
        return reverse_lazy('blog:post_detail', kwargs={
            'pk': self.object.pk})


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    template_name = 'blog/create.html'
    success_url = reverse_lazy('blog:index')

    def test_func(self):
        return self.request.user == self.get_object().author

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = PostForm(instance=self.object)
        return context

########################


class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = get_object_or_404(Post, pk=self.kwargs['pk'])
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('blog:post_detail',
                            kwargs={'pk': self.kwargs['pk']})


class CommentUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_pk'

    def test_func(self):
        return self.request.user == self.get_object().author

    def get_success_url(self):
        return reverse_lazy('blog:post_detail',
                            kwargs={'pk': self.object.post.pk})


class CommentDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Comment
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_pk'

    def test_func(self):
        return self.request.user == self.get_object().author

    def get_success_url(self):
        return reverse_lazy('blog:post_detail', kwargs={
            'pk': self.object.post.pk
        })

#########################


class CategoryPostsView(ListView):
    template_name = 'blog/category.html'
    context_object_name = 'post_list'
    paginate_by = 10

    def get_queryset(self):
        return Post.objects.select_related(
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
            category=self.category,
            pub_date__lte=timezone.now()
        )

    def dispatch(self, request, *args, **kwargs):
        self.category = get_object_or_404(
            Category.objects.all(),
            slug=self.kwargs['category_slug'],
            is_published=True
        )
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        return context

##################


class ProfileView(DetailView):
    model = User
    template_name = 'blog/profile.html'
    context_object_name = 'profile'

    def get_object(self, queryset=None):
        return get_object_or_404(User, username=self.kwargs['username'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.request.user == self.object:
            posts = self.object.posts.all().order_by('-pub_date')
        else:
            posts = self.object.posts.filter(
                is_published=True,
                pub_date__lte=timezone.now()
            ).order_by('-pub_date')

        paginator = Paginator(posts, 10)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        context['page_obj'] = page_obj  # ← теперь совпадает с шаблоном
        return context


class UserUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserUpdateForm
    template_name = 'blog/user.html'

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        return reverse_lazy('blog:profile', kwargs={
            'username': self.request.user.username})
