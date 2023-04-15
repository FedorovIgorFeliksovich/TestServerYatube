from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .utils import paginate_page
from .forms import PostForm, CommentForm
from .models import Group, Post, Follow

User = get_user_model()


def index(request):
    post_list = Post.objects.select_related("group", "author")
    page_obj = paginate_page(request, post_list)
    context = {"page_obj": page_obj}
    return render(request, "posts/index.html", context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.select_related("group")
    page_obj = paginate_page(request, posts)
    context = {"group": group, "page_obj": page_obj}
    return render(request, "posts/group_list.html", context)


def profile(request, username):
    author_profile = get_object_or_404(User, username=username)
    post_list = author_profile.posts.all()
    page_obj = paginate_page(request, post_list)
    following = (
        request.user.is_authenticated
        and Follow.objects.filter(
            author=author_profile, user=request.user
        ).exists()
    )
    context = {
        "page_obj": page_obj,
        "author": author_profile,
        "following": following,
    }
    return render(request, "posts/profile.html", context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm()
    comments_for_post = post.comments.all()
    context = {"post": post, "form": form, "comments": comments_for_post}
    return render(request, "posts/post_detail.html", context)


@login_required
def post_create(request):
    form = PostForm(request.POST or None, files=request.FILES or None)
    if form.is_valid():
        create_post = form.save(commit=False)
        create_post.author = request.user
        create_post.save()
        return redirect("posts:profile", create_post.author)
    context = {"form": form}
    return render(request, "posts/create_post.html", context)


@login_required
def post_edit(request, post_id):
    edit_post = get_object_or_404(Post, id=post_id)
    if request.user != edit_post.author:
        return redirect("posts:post_detail", post_id)
    form = PostForm(
        request.POST or None, files=request.FILES or None, instance=edit_post
    )
    if form.is_valid():
        form.save()
        return redirect("posts:post_detail", post_id)
    context = {"form": form, "is_edit": True}
    return render(request, "posts/create_post.html", context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect("posts:post_detail", post_id=post_id)


@login_required
def follow_index(request):
    post_list = Post.objects.filter(
        author__following__user=request.user
    ).select_related("group")
    page_obj = paginate_page(request, post_list)
    context = {"page_obj": page_obj}
    return render(request, "posts/follow.html", context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if request.user != author:
        Follow.objects.get_or_create(user=request.user, author=author)
    return redirect("posts:profile", username=username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    Follow.objects.filter(user=request.user, author=author).delete()
    return redirect("posts:profile", username=username)
