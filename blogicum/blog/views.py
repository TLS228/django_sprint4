from django.shortcuts import get_object_or_404, redirect, render

from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model

from django.core.paginator import Paginator
from django.db.models import Count
from django.utils import timezone

from blog.models import Category, Post, Comment
from blog.forms import ProfileUpdateForm, PostForm, CommentForm

from blog.constants import PAGE

User = get_user_model()


def public_posts():
    """Функция для фильтрации видимых постов."""
    return Post.objects.select_related(
        'author',
        'category'
    ).filter(
        pub_date__lte=timezone.now(),
        is_published=True,
        category__is_published=True
    ).annotate(
        comment_count=Count('comments')
    ).order_by(
        '-pub_date'
    )


def index(request):
    page_obj = public_posts()
    paginator = Paginator(page_obj, PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {'page_obj': page_obj}
    return render(request, 'blog/index.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if post.author != request.user:
        post = get_object_or_404(
            Post, pk=post_id,
            is_published=True,
            pub_date__lte=timezone.now(),
            category__is_published=True
        )
    comments = Comment.objects.filter(post_id=post_id).order_by('created_at')
    context = {
        'post': post,
        'comments': comments,
        'form': CommentForm()
    }
    return render(request, 'blog/detail.html', context)


def create_post(request):
    if request.user.is_authenticated:
        form = PostForm(request.POST or None, files=request.FILES or None)
        context = {'form': form}
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('blog:profile', username=request.user)
        return render(request, 'blog/create.html', context)
    else:
        return redirect('blog:index')


def edit_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if request.user.is_authenticated and request.user == post.author:
        form = PostForm(
            request.POST or None,
            files=request.FILES or None,
            instance=post
        )
        context = {'form': form}
        if form.is_valid():
            post.save()
            return redirect('blog:post_detail', post_id=post_id)
        return render(request, 'blog/create.html', context)
    else:
        return redirect('blog:post_detail', post_id=post_id)


@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id, author=request.user)
    form = PostForm(files=request.FILES or None, instance=post)
    context = {'form': form}
    if request.method == 'POST':
        post.delete()
        return redirect('blog:profile', username=request.user)
    return render(request, 'blog/create.html', context)


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
    context = {'form': form, 'comment': comment}
    if form.is_valid():
        comment.save()
        return redirect('blog:post_detail', post_id=post_id)
    return render(request, 'blog/comment.html', context)


@login_required
def delete_comment(request, post_id, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id, author=request.user)
    context = {'comment': comment}
    if request.method == 'POST':
        comment.delete()
        return redirect('blog:post_detail', post_id=post_id)
    return render(request, 'blog/comment.html', context)


def profile(request, username):
    profile = get_object_or_404(User, username=username)
    if request.user == profile:
        page_obj = Post.objects.filter(author=request.user).annotate(
            comment_count=Count('comments')).order_by('-pub_date')
    else:
        page_obj = public_posts().filter(author=profile)
    paginator = Paginator(page_obj, PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {'profile': profile, 'page_obj': page_obj}
    return render(request, 'blog/profile.html', context)


@login_required
def edit_profile(request):
    profile = get_object_or_404(User, username=request.user)
    form = ProfileUpdateForm(request.POST or None, instance=profile)
    context = {'form': form}
    if form.is_valid():
        profile.save()
        return redirect('blog:profile', username=profile)
    return render(request, 'blog/user.html', context)


def category(request, category_slug):
    category = get_object_or_404(
        Category, slug=category_slug, is_published=True)
    page_obj = public_posts().filter(category__slug=category_slug)
    paginator = Paginator(page_obj, PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {'page_obj': page_obj, 'category': category}
    return render(request, 'blog/category.html', context)
