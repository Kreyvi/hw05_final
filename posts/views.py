from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import cache_page

from .forms import PostForm, CommentForm
from .models import Group, Post, Follow


@cache_page(20)
def index(request):
    """Main page '/' """
    posts = Post.objects.all()
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {
        'page': page,
        'paginator': paginator,
    }
    return render(
        request,
        'posts/index.html',
        context
    )


def group_posts(request, slug):
    """Group posts page '/group/slug/' """
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    return render(
        request,
        'group.html',
        {'group': group, 'page': page, 'paginator': paginator}
    )


def profile(request, username):
    """Profile page '/username/' """
    author = get_object_or_404(User, username=username)
    posts = author.author.all()
    post_counter = posts.count()
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {
        'counter': post_counter,
        'author': author,
        'page': page,
        'paginator': paginator,
    }
    return render(request, 'posts/profile.html', context)


def post_view(request, username, post_id):
    """Post page '/username/post-id/' """
    form = CommentForm()
    post = get_object_or_404(Post, id=post_id)
    author = post.author
    counter = author.author.count()
    comments = post.comments.all()
    context = {
        'post': post,
        'counter': counter,
        'author': author,
        'comments': comments,
        'form': form,
    }
    return render(request, 'posts/post.html', context)


@login_required
def post_edit(request, username, post_id):
    """Edit post page '/username/post-id/edit' """
    post = get_object_or_404(Post, id=post_id)
    if request.user != post.author:
        return redirect('post', post_id=post.id, username=username)
    else:
        edit = True
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if form.is_valid():
        form.save()
        return redirect('post', post_id=post.id, username=username)
    context = {
        'form': form,
        'edit': edit,
        'post': post,
    }
    return render(request, 'posts/new.html', context)


@login_required
def new_post(request):
    """New post page '/new/' """
    form = PostForm(
        request.POST or None,
        files=request.FILES or None
    )
    if form.is_valid():
        form.instance.author = request.user
        form.save()
        return redirect('index')
    return render(request, 'posts/new.html', {'form': form})


def page_not_found(request, exception):
    return render(
        request,
        "misc/404.html",
        {"path": request.path},
        status=404
    )


@login_required
def add_comment(request, username, post_id):
    """Add comment """
    form = CommentForm(request.POST or None)
    if form.is_valid():
        form.instance.post = Post.objects.get(id=post_id)
        form.instance.author = request.user
        form.save()
        return redirect('post', post_id=post_id, username=username)
    return render(request, 'includes/comments.html', {'form': form})


@login_required
def follow_index(request):
    posts = Post.objects.filter(author__following__user=request.user)
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {
        'posts': posts,
        'paginator': paginator,
        'page': page
    }
    return render(request, "posts/follow.html", context)


@login_required
def profile_follow(request, username):
    user_to_follow = get_object_or_404(User, username=username)

    if user_to_follow.following.filter(user=request.user.id).exists():
        return redirect('profile', username=username)
    elif request.user == user_to_follow:
        return redirect('index')

    Follow.objects.create(author=user_to_follow, user=request.user)
    return redirect('profile', username=username)


@login_required
def profile_unfollow(request, username):
    user_to_follow = get_object_or_404(User, username=username)
    follow = Follow.objects.filter(author=user_to_follow, user=request.user)
    if follow.exists():
        follow.delete()
    return redirect('profile', username=username)


def server_error(request):
    return render(request, "misc/500.html", status=500)
