from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import PostForm
from .models import Group, Post, User


NUMBER_OF_POSTS = 10


def get_page_context(queryset, request):
    paginator = Paginator(queryset, NUMBER_OF_POSTS)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return {
        'paginator': paginator,
        'page_number': page_number,
        'page_obj': page_obj,
    }


def index(request):
    posts = Post.objects.all()
    context = get_page_context(posts, request)
    template = 'posts/index.html'
    return render(request, template, context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.groups.all()
    title = f'Записи сообщества {group.title}'
    context = {
        'title': title,
        'group': group,
        'posts': posts,
    }
    context.update(get_page_context(posts, request))
    template = 'posts/group_list.html'
    return render(request, template, context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    posts = author.posts.all()
    context = {
        'author': author,
    }
    context.update(get_page_context(posts, request))
    template = 'posts/profile.html'
    return render(request, template, context)


def post_detail(request, post_id):
    posts = Post.objects.get(id=post_id)
    title = posts.text[:30]
    posts_number = Post.objects.filter(author=posts.author).count()
    context = {
        'post_num': posts_number,
        'post': posts,
        'title': title
    }
    template = 'posts/post_detail.html'
    return render(request, template, context)


@login_required
def post_create(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        # form = PostForm(
        # request.POST or None,
        # files=request.FILES or None,
        # instance=post
        # )
        

        if form.is_valid():
            new_form = form.save(commit=False)
            new_form.author = request.user
            new_form.save()
            return redirect('posts:profile', username=request.user.username)
    form = PostForm()
    context = {
        'form': form,
        'is_edit': False,
    }
    template = 'posts/create_post.html'
    return render(request, template, context)


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    template = 'posts/create_post.html'

    if request.user == post.author:
        if request.method == 'POST':
            form = PostForm(request.POST or None, instance=post)
            context = {
                'form': form,
                'is_edit': True,
            }
            if form.is_valid:
                form.save()
                return redirect('posts:post_detail',
                                post_id=post.id)
            return render(request, template, context)
        form = PostForm(instance=post)
        context = {
            'form': form,
            'is_edit': True,
        }
        return render(request, template, context)
    return redirect('posts:post_detail',
                    post_id=post.id)
