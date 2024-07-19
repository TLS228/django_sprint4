from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count
from django.utils import timezone

from blog.models import Category, Post, Comment, User
from blog.forms import ProfileUpdateForm, PostForm, CommentForm
from blog.constants import POSTS_PER_PAGE  # изменение имени константы


def public_posts(posts=None):
    """Функция для фильтрации видимых постов."""
    if posts is None:
        posts = Post.objects.all()

    return posts.select_related(
        'author',
        'category',
        'location'
    ).filter(
        pub_date__lte=timezone.now(),
        is_published=True,
        category__is_published=True
    ).annotate(
        comment_count=Count('comments')
    ).order_by('-pub_date')


def paginate_queryset(request, queryset, per_page=10):
    paginator = Paginator(queryset, per_page)
    page_number = request.GET.get('page', 1)
    return paginator.get_page(page_number)


def index(request):
    page_obj = paginate_queryset(request, public_posts(), POSTS_PER_PAGE)
    return render(request, 'blog/index.html', {'page_obj': page_obj})


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if post.author != request.user:
        post = get_object_or_404(
            Post, pk=post_id,
            is_published=True,
            pub_date__lte=timezone.now(),
            category__is_published=True
        )

    return render(request, 'blog/detail.html', {
        'post': post,
        'comments': post.comments.all(),
        'form': CommentForm()
    })


@login_required
def create_post(request):
    form = PostForm(request.POST or None, files=request.FILES or None)

    if not form.is_valid():
        return render(request, 'blog/create.html', {'form': form})

    post = form.save(commit=False)
    post.author = request.user
    post.save()

    return redirect('blog:profile', username=request.user)


@login_required
def edit_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if request.user != post.author:
        return redirect('blog:post_detail', post_id=post_id)

    form = PostForm(request.POST or None,
                    files=request.FILES or None, instance=post)
    if form.is_valid():
        if form.has_changed():
            post = form.save()
        return redirect('blog:post_detail', post_id=post_id)

    return render(request, 'blog/create.html', {'form': form})


@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id, author=request.user)
    if request.method == 'POST':
        post.delete()
        return redirect('blog:profile', username=request.user)
    return render(request,
                  'blog/create.html', {'form': PostForm(instance=post)})


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
        return redirect('blog:post_detail', post_id=post_id)
    return render(request, 'blog/comment.html')


@login_required
def edit_comment(request, post_id, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id, author=request.user)
    form = CommentForm(request.POST or None, instance=comment)
    if form.is_valid():
        comment.save()
        return redirect('blog:post_detail', post_id=post_id)
    return render(request, 'blog/comment.html',
                  {'form': form, 'comment': comment})


@login_required
def delete_comment(request, post_id, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id, author=request.user)
    if request.method == 'POST':
        comment.delete()
        return redirect('blog:post_detail', post_id=post_id)
    return render(request, 'blog/comment.html',
                  {'comment': comment})


def profile(request, username):
    profile_user = get_object_or_404(User, username=username)
    if request.user == profile_user:
        posts = profile_user.posts.annotate(
            comment_count=Count('comments')).order_by('-pub_date'
                                                      )
    else:
        posts = public_posts().filter(author=profile_user)

    page_obj = paginate_queryset(request, posts, POSTS_PER_PAGE)
    return render(request, 'blog/profile.html',
                  {'profile': profile_user, 'page_obj': page_obj})


@login_required
def edit_profile(request):
    form = ProfileUpdateForm(request.POST or None, instance=request.user)
    if form.is_valid():
        form.save()
        return redirect('blog:profile', username=request.user)
    return render(request, 'blog/user.html', {'form': form})


def category(request, category_slug):
    category = get_object_or_404(
        Category,
        slug=category_slug,
        is_published=True,
    )
    posts = public_posts(category.posts.all())
    page_obj = paginate_queryset(request, posts, POSTS_PER_PAGE)
    return render(request, 'blog/category.html', {
        'page_obj': page_obj,
        'category': category,
    })
