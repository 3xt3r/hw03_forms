from django.shortcuts import render, get_object_or_404
from .models import Post, Group, User
from yatube.settings import NUMBER_OF_POSTS
from django.core.paginator import Paginator
from posts.forms import PostForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect


def index(request):
    post_list = Post.objects.all().order_by('-pub_date')
    paginator = Paginator(post_list, NUMBER_OF_POSTS)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(
        Group.objects.all().prefetch_related('posts'),
        slug=slug)
    posts = group.posts.all().order_by('-pub_date')
    paginator = Paginator(posts, NUMBER_OF_POSTS)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):

    profile_user = User.objects.get(username=username)
    author = User.objects.get(username=username)
    profile = Post.objects.filter(author=profile_user)
    paginator = Paginator(profile, NUMBER_OF_POSTS)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'profile': profile,
        'page_obj': page_obj,
        'author': author,

    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    # Здесь код запроса к модели и создание словаря контекста
    post_info = get_object_or_404(Post, pk=post_id)
    author_posts = post_info.author.posts.count()
    context = {
        'post_info': post_info,
        'author_posts': author_posts,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    form = PostForm(request.POST or None)

    if not form.is_valid():
        context = {'form': form}
        return render(request, 'posts/create_post.html', context)

    post = form.save(commit=False)
    post.author = request.user
    post.save()
    username = request.user.username
    return redirect('posts:profile', username=username)


@login_required
def post_edit(request, post_id):
    if request.method == 'GET':
        post = get_object_or_404(Post, pk=post_id)
        form = PostForm(instance=post)
        if post.author.id == request.user.id:
            context = {'form': form,
                       'is_edit': True,
                       'post_id': post_id}
            return render(request, 'posts/create_post.html', context)
        else:
            return redirect('posts:post_detail', post_id=post_id)

    elif request.method == 'POST':
        post = get_object_or_404(Post, pk=post_id)
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('posts:post_detail', post_id=post.pk)
